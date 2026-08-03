"""Detect z-fighting candidates: pairs of visuals whose same-facing AABB faces
are (near-)coplanar with an overlapping cross-section.

Usage:
    uv run python domain/audit_coplanar.py <record-id> [<record-id> ...]

Verdict per pair: FAIL when the face gap is < 0.05 mm (rendered z-fighting is
near-certain), WARN when < 0.3 mm (tessellation tolerance can still make the
boundary shimmer). Touching opposite faces (assembly contact) are not flagged.

AABBs approximate meshes, so non-boxy meshes (perforated panels, cylinders)
can produce false positives — treat FAIL pairs as a to-inspect list, and keep
known-benign pairs in ALLOW_RE.
"""

from __future__ import annotations

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAT = REPO / "data" / "cache" / "record_materialization"

FAIL_GAP = 0.00005
WARN_GAP = 0.0003
MIN_OVERLAP = 0.0005  # both cross-section dims must overlap by 0.5 mm

# Benign coincidences (screw heads seated in holes, joint seams, etc.).
ALLOW_RE = re.compile(r"$^")  # nothing allowed by default; extend as cases are triaged

AXES = ("x", "y", "z")


def _rpy_matrix(r: float, p: float, y: float):
    cr, sr, cp, sp, cy, sy = (
        math.cos(r),
        math.sin(r),
        math.cos(p),
        math.sin(p),
        math.cos(y),
        math.sin(y),
    )
    return (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )


def _mat_mul(a, b):
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3)
    )


def _mat_vec(m, v):
    return tuple(sum(m[i][k] * v[k] for k in range(3)) for i in range(3))


def _vec_add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def _parse_origin(el):
    xyz = (0.0, 0.0, 0.0)
    rpy = (0.0, 0.0, 0.0)
    if el is not None:
        o = el.find("origin")
        if o is not None:
            if o.get("xyz"):
                xyz = tuple(float(v) for v in o.get("xyz").split())
            if o.get("rpy"):
                rpy = tuple(float(v) for v in o.get("rpy").split())
    return xyz, rpy


def _obj_vertices(path: Path):
    verts = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("v "):
                _, xs, ys, zs = line.split()[:4]
                verts.append((float(xs), float(ys), float(zs)))
    return verts


def _visual_aabb(visual, link_pose, urdf_dir: Path):
    geo = visual.find("geometry")
    if geo is None:
        return None
    (vx, vy, vz), vrpy = _parse_origin(visual)
    link_rot, link_pos = link_pose
    rot = _mat_mul(link_rot, _rpy_matrix(*vrpy))
    pos = _vec_add(link_pos, _mat_vec(link_rot, (vx, vy, vz)))

    box = geo.find("box")
    mesh = geo.find("mesh")
    cyl = geo.find("cylinder")
    sph = geo.find("sphere")
    if box is not None:
        sx, sy, sz = (float(v) for v in box.get("size").split())
        corners = [
            (dx * sx / 2, dy * sy / 2, dz * sz / 2)
            for dx in (-1, 1)
            for dy in (-1, 1)
            for dz in (-1, 1)
        ]
    elif mesh is not None:
        fn = mesh.get("filename")
        scale = tuple(float(v) for v in (mesh.get("scale") or "1 1 1").split())
        mpath = (urdf_dir / fn).resolve()
        if not mpath.exists():
            return None
        corners = [(x * scale[0], y * scale[1], z * scale[2]) for x, y, z in _obj_vertices(mpath)]
        if not corners:
            return None
    elif cyl is not None:
        rr, ll = float(cyl.get("radius")), float(cyl.get("length"))
        corners = [
            (dx * rr, dy * rr, dz * ll / 2) for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)
        ]
    elif sph is not None:
        rr = float(sph.get("radius"))
        corners = [
            (dx * rr, dy * rr, dz * rr) for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)
        ]
    else:
        return None

    world = [_vec_add(pos, _mat_vec(rot, c)) for c in corners]
    lo = tuple(min(p[i] for p in world) for i in range(3))
    hi = tuple(max(p[i] for p in world) for i in range(3))
    return lo, hi


def _link_poses(root):
    """World pose of every link with all joints at zero."""
    joints = []
    for j in root.findall("joint"):
        parent = j.find("parent").get("link")
        child = j.find("child").get("link")
        xyz, rpy = _parse_origin(j)
        joints.append((parent, child, xyz, rpy))
    poses = {}
    children = {c for _, c, _, _ in joints}
    roots = [el.get("name") for el in root.findall("link") if el.get("name") not in children]
    ident = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    for r in roots:
        poses[r] = (ident, (0.0, 0.0, 0.0))
    pending = list(joints)
    while pending:
        progressed = False
        for j in list(pending):
            parent, child, xyz, rpy = j
            if parent in poses:
                prot, ppos = poses[parent]
                poses[child] = (
                    _mat_mul(prot, _rpy_matrix(*rpy)),
                    _vec_add(ppos, _mat_vec(prot, xyz)),
                )
                pending.remove(j)
                progressed = True
        if not progressed:
            break
    return poses


def audit(record_id: str):
    urdf = MAT / record_id / "model.urdf"
    if not urdf.exists():
        raise FileNotFoundError(f"no materialized URDF (run: uv run articraft compile {record_id})")
    root = ET.parse(urdf).getroot()
    poses = _link_poses(root)

    boxes = []
    for link in root.findall("link"):
        lname = link.get("name")
        if lname not in poses:
            continue
        for i, visual in enumerate(link.findall("visual")):
            vname = visual.get("name") or f"visual_{i}"
            aabb = _visual_aabb(visual, poses[lname], urdf.parent)
            if aabb is not None:
                boxes.append((f"{lname}/{vname}", aabb))

    findings = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (na, (loa, hia)), (nb, (lob, hib)) = boxes[i], boxes[j]
            if ALLOW_RE.search(na) or ALLOW_RE.search(nb):
                continue
            for ax in range(3):
                o1 = min(hia[(ax + 1) % 3], hib[(ax + 1) % 3]) - max(
                    loa[(ax + 1) % 3], lob[(ax + 1) % 3]
                )
                o2 = min(hia[(ax + 2) % 3], hib[(ax + 2) % 3]) - max(
                    loa[(ax + 2) % 3], lob[(ax + 2) % 3]
                )
                if o1 < MIN_OVERLAP or o2 < MIN_OVERLAP:
                    continue
                for side, va, vb in (
                    ("+" + AXES[ax], hia[ax], hib[ax]),
                    ("-" + AXES[ax], loa[ax], lob[ax]),
                ):
                    gap = abs(va - vb)
                    if gap < WARN_GAP:
                        findings.append(
                            (
                                "FAIL" if gap < FAIL_GAP else "WARN",
                                na,
                                nb,
                                side,
                                gap * 1000.0,
                                o1 * 1000.0,
                                o2 * 1000.0,
                            )
                        )
    return findings


def main() -> int:
    if not sys.argv[1:]:
        print(__doc__)
        return 1
    total_fail = 0
    for rid in sys.argv[1:]:
        print(f"== {rid}")
        try:
            findings = audit(rid)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR {exc}")
            total_fail += 1
            continue
        findings.sort(key=lambda f: (f[0] != "FAIL", f[4]))
        fails = [f for f in findings if f[0] == "FAIL"]
        for verdict, na, nb, side, gap, o1, o2 in findings:
            print(
                f"  [{verdict}] {na} <> {nb} face {side} gap={gap:.3f}mm overlap={o1:.1f}x{o2:.1f}mm"
            )
        print(
            f"  {'PASS' if not fails else str(len(fails)) + ' coplanar pair(s)'} ({len(findings)} finding(s) incl. WARN)"
        )
        total_fail += len(fails)
    return 1 if total_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
