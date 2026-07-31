"""Export one Articraft record as an AssetHub-contract URDF package.

Usage:
    uv run python scripts/export_assethub.py <record-id> [options]

Produces `<out>/<asset_name>/` with the layout AssetHub expects, then zips it
with the URDF at the ZIP top level (AssetHub-confirmed layout, 2026-07-30):

    <asset_name>.zip
    ├── <asset_name>.urdf
    └── meshes/*.obj

AssetHub confirmations (2026-07-30): multi-link URDF accepted as-is (no need
to merge into one visual/collision mesh pair), inline box/cylinder primitives
and URDF rgba materials supported, UV/texture/MTL optional, fixed-joint-only
assets import fine, mesh filenames free as long as URDF relative paths match
the ZIP contents case-exactly.

The record must be compiled first (`uv run articraft compile <record-id>
--target full --validate --strict-geom-qc`); this script only repackages the
materialized URDF. It never edits the record.

Two transforms are applied to the materialized URDF:
  1. mesh paths are rewritten `assets/meshes/X.obj` -> `meshes/X.obj`
  2. collision meshes above `--collision-face-budget` faces are replaced by
     their local-frame AABB box, satisfying the AssetHub requirement that
     collision geometry be simpler than visual geometry. Rotated collision
     origins are handled exactly (the local AABB center is rotated by rpy
     before offsetting the origin). Visual meshes are never touched.

Every check in the AssetHub export checklist that can be verified locally is
run against the finished package; a failure exits non-zero.
"""

from __future__ import annotations

import argparse
import math
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Iterable, Optional

REPO = Path(__file__).resolve().parents[1]
BAD_PATH_MARKERS = ("package://", "file://", "/Users/", "/home/", "C:\\")


# --------------------------------------------------------------------------
# OBJ helpers


def obj_face_count(path: Path) -> int:
    return sum(1 for line in path.read_text().splitlines() if line.startswith("f "))


def obj_aabb(path: Path) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    for line in path.read_text().splitlines():
        if not line.startswith("v "):
            continue
        parts = line.split()
        for axis in range(3):
            value = float(parts[axis + 1])
            lo[axis] = min(lo[axis], value)
            hi[axis] = max(hi[axis], value)
    if lo[0] == float("inf"):
        raise ValueError(f"{path} has no vertices")
    return (lo[0], lo[1], lo[2]), (hi[0], hi[1], hi[2])


# --------------------------------------------------------------------------
# URDF helpers


def parse_triplet(raw: Optional[str], default: float) -> list[float]:
    if not raw:
        return [default] * 3
    return [float(v) for v in raw.split()]


def format_triplet(values: Iterable[float]) -> str:
    out = []
    for value in values:
        text = f"{value:.9g}"
        out.append("0" if text in ("-0", "-0.0") else text)
    return " ".join(out)


def mesh_basename(filename: str) -> str:
    return filename.rsplit("/", 1)[-1]


def rpy_matrix(rpy: list[float]) -> list[list[float]]:
    """URDF fixed-axis rotation matrix R = Rz(yaw) @ Ry(pitch) @ Rx(roll)."""
    r, p, y = rpy
    cr, sr = math.cos(r), math.sin(r)
    cp, sp = math.cos(p), math.sin(p)
    cy, sy = math.cos(y), math.sin(y)
    return [
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr],
    ]


def simplify_collisions(
    root: ET.Element, source_meshes: Path, budget: int
) -> tuple[int, list[str]]:
    """Replace over-budget collision meshes with their AABB box.

    The box is axis-aligned in the mesh's local frame and keeps the collision
    origin's rpy, so rotated meshes substitute exactly: the local AABB center
    is rotated by rpy before being added to the origin xyz.
    """
    replaced = 0
    skipped: list[str] = []
    for link in root.findall("link"):
        for collision in link.findall("collision"):
            geometry = collision.find("geometry")
            if geometry is None:
                continue
            mesh = geometry.find("mesh")
            if mesh is None:
                continue
            src = source_meshes / mesh_basename(mesh.get("filename", ""))
            if not src.is_file():
                skipped.append(f"{link.get('name')}/{mesh.get('filename')} (mesh file missing)")
                continue
            faces = obj_face_count(src)
            if faces <= budget:
                continue
            scale = parse_triplet(mesh.get("scale"), 1.0)
            lo, hi = obj_aabb(src)
            size = [(hi[i] - lo[i]) * scale[i] for i in range(3)]
            center = [((hi[i] + lo[i]) / 2.0) * scale[i] for i in range(3)]

            origin = collision.find("origin")
            if origin is None:
                origin = ET.SubElement(collision, "origin")
                origin.set("rpy", "0 0 0")
                xyz = [0.0, 0.0, 0.0]
                rpy = [0.0, 0.0, 0.0]
            else:
                xyz = parse_triplet(origin.get("xyz"), 0.0)
                rpy = parse_triplet(origin.get("rpy"), 0.0)
            rot = rpy_matrix(rpy)
            world_center = [sum(rot[i][j] * center[j] for j in range(3)) for i in range(3)]
            origin.set("xyz", format_triplet(xyz[i] + world_center[i] for i in range(3)))

            geometry.remove(mesh)
            box = ET.SubElement(geometry, "box")
            box.set("size", format_triplet(size))
            replaced += 1
    return replaced, skipped


def rewrite_mesh_paths(root: ET.Element) -> set[str]:
    """Point every mesh reference at `meshes/<basename>`; return basenames used."""
    used: set[str] = set()
    for mesh in root.iter("mesh"):
        base = mesh_basename(mesh.get("filename", ""))
        if not base:
            continue
        mesh.set("filename", f"meshes/{base}")
        used.add(base)
    return used


# --------------------------------------------------------------------------
# Validation


class Checks:
    def __init__(self) -> None:
        self.rows: list[tuple[bool, str, str]] = []

    def add(self, ok: bool, name: str, detail: str = "") -> None:
        self.rows.append((ok, name, detail))

    @property
    def failed(self) -> int:
        return sum(1 for ok, _, _ in self.rows if not ok)

    def report(self) -> None:
        for ok, name, detail in self.rows:
            mark = "PASS" if ok else "FAIL"
            line = f"  [{mark}] {name}"
            if detail:
                line += f" - {detail}"
            print(line)


def validate(package: Path, urdf_path: Path, budget: int) -> Checks:
    checks = Checks()
    text = urdf_path.read_text()
    root = ET.fromstring(text)
    checks.add(True, "URDF XML parses")

    links = [link.get("name", "") for link in root.findall("link")]
    joints = root.findall("joint")
    children = {j.find("child").get("link", "") for j in joints if j.find("child") is not None}
    parents = {j.find("parent").get("link", "") for j in joints if j.find("parent") is not None}
    roots = sorted(set(links) - children)
    checks.add(len(roots) == 1, "exactly one root link", ", ".join(roots) or "none")
    dangling = sorted((children | parents) - set(links))
    checks.add(not dangling, "no dangling parent/child refs", ", ".join(dangling))

    bad_names = [n for n in links if not n.isascii() or " " in n]
    checks.add(not bad_names, "link names ASCII without spaces", ", ".join(bad_names))

    incomplete = [
        link.get("name", "")
        for link in root.findall("link")
        if link.find("visual") is None
        or link.find("collision") is None
        or link.find("inertial") is None
    ]
    checks.add(
        not incomplete,
        f"all {len(links)} links carry visual+collision+inertial",
        ", ".join(incomplete),
    )

    total_mass = 0.0
    bad_mass: list[str] = []
    for link in root.findall("link"):
        inertial = link.find("inertial")
        if inertial is None:
            continue
        mass_el = inertial.find("mass")
        mass = float(mass_el.get("value", "0")) if mass_el is not None else 0.0
        total_mass += mass
        inertia = inertial.find("inertia")
        diag = (
            [float(inertia.get(k, "0")) for k in ("ixx", "iyy", "izz")]
            if inertia is not None
            else [0.0, 0.0, 0.0]
        )
        if mass <= 0 or all(v == 0 for v in diag):
            bad_mass.append(link.get("name", ""))
    checks.add(not bad_mass, "every mass > 0 with non-degenerate inertia", ", ".join(bad_mass))
    print(f"  ..   total mass = {total_mass:g} kg")

    moving = [j for j in joints if j.get("type") not in ("fixed", None)]
    missing_dyn = []
    for joint in moving:
        limit = joint.find("limit")
        if (
            joint.find("axis") is None
            or limit is None
            or limit.get("effort") is None
            or limit.get("velocity") is None
        ):
            missing_dyn.append(joint.get("name", ""))
    checks.add(
        not missing_dyn,
        f"{len(moving)} moving joints declare axis+limit+effort+velocity",
        ", ".join(missing_dyn),
    )

    missing_files: list[str] = []
    over_budget: list[str] = []
    for mesh in root.iter("mesh"):
        rel = mesh.get("filename", "")
        target = package / rel
        # case-exact existence check
        parent = target.parent
        if not target.is_file() or target.name not in {p.name for p in parent.glob("*")}:
            missing_files.append(rel)
    for link in root.findall("link"):
        for collision in link.findall("collision"):
            geometry = collision.find("geometry")
            mesh = geometry.find("mesh") if geometry is not None else None
            if mesh is None:
                continue
            path = package / mesh.get("filename", "")
            if path.is_file() and obj_face_count(path) > budget:
                over_budget.append(f"{mesh.get('filename')} ({obj_face_count(path)} faces)")
    checks.add(
        not missing_files, "every referenced mesh exists (case-exact)", ", ".join(missing_files)
    )
    checks.add(
        not over_budget,
        f"collision meshes within {budget}-face budget",
        ", ".join(over_budget),
    )

    hits = [m for m in BAD_PATH_MARKERS if m in text]
    checks.add(not hits, "no package:// / file:// / absolute paths", ", ".join(hits))

    strays = [str(p.relative_to(package)) for p in package.rglob("*.cadquery.json")]
    checks.add(not strays, "no internal cache files in package", ", ".join(strays))
    return checks


# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("record")
    ap.add_argument("--data-dir", default=os.environ.get("ARTICRAFT_DATA_DIR"))
    ap.add_argument("--out", default=str(REPO / "data" / "local" / "assethub_export"))
    ap.add_argument("--asset-name", help="Defaults to the URDF <robot name>.")
    ap.add_argument(
        "--collision-face-budget",
        type=int,
        default=256,
        help="Collision meshes above this face count are replaced by their AABB box.",
    )
    ap.add_argument("--no-zip", action="store_true")
    args = ap.parse_args()

    data_root = Path(args.data_dir) if args.data_dir else REPO / "data"
    source = data_root / "cache" / "record_materialization" / args.record
    urdf_src = source / "model.urdf"
    if not urdf_src.is_file():
        print(f"error: {urdf_src} not found.")
        print(f"       run: uv run articraft compile {args.record} --target full --validate")
        return 2

    tree = ET.parse(urdf_src)
    root = tree.getroot()
    asset_name = args.asset_name or root.get("name") or args.record
    root.set("name", asset_name)

    out_root = Path(args.out)
    package = out_root / asset_name
    if package.exists():
        shutil.rmtree(package)
    (package / "meshes").mkdir(parents=True)

    source_meshes = source / "assets" / "meshes"
    replaced, skipped = simplify_collisions(root, source_meshes, args.collision_face_budget)
    used = rewrite_mesh_paths(root)
    for base in sorted(used):
        src = source_meshes / base
        if not src.is_file():
            print(f"error: referenced mesh missing from materialization: {src}")
            return 2
        shutil.copy2(src, package / "meshes" / base)

    urdf_out = package / f"{asset_name}.urdf"
    ET.indent(tree, space="  ")
    tree.write(urdf_out, encoding="utf-8", xml_declaration=True)

    print(f"asset: {asset_name}")
    print(f"package: {package}")
    print(f"meshes copied: {len(used)}   collision meshes boxed: {replaced}")
    for item in skipped:
        print(f"  ! left as mesh (unsound to box): {item}")

    print("checks:")
    checks = validate(package, urdf_out, args.collision_face_budget)
    checks.report()

    if not args.no_zip:
        # AssetHub wants the URDF at the ZIP top level with meshes/ beside it,
        # not wrapped in an extra <asset_name>/ folder (confirmed 2026-07-30).
        archive = out_root / f"{asset_name}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(package.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(package))
        print(f"zip: {archive} ({archive.stat().st_size / 1024:.0f} KB)")

    if checks.failed:
        print(f"\n{checks.failed} check(s) FAILED")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
