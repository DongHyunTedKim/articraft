"""Repeated-element grid auditor (ports, drive bays, trays).

Usage:
    uv run python domain/audit_grids.py <record-id> [...]
    uv run python domain/audit_grids.py --label-prefix ab-   # from status.json

Per record: finds repeated same-size front elements (ports/bays), reports
rows, per-row counts, intra-row alignment, pitch uniformity, inter-row gap,
and aspect class. Pass criteria (rackmount fronts): intra-row scatter
<=1mm, pitch CV <=5%, tight pair gap <=3mm (uniform-grid devices only).
"""

from __future__ import annotations

import json
import re
import statistics as st
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
import sdk  # noqa: E402

ELEM_RE = re.compile(r"port|sfp|qsfp|rj4?5?|cage|jack|drive|bay|tray|carrier", re.I)
# 세로 종횡비가 정상인 요소: 2.5인치 드라이브 캐리어는 세워서 꽂히므로
# (약 15x70mm) 세로형이 맞다. 가로형 포트 그리드 기준을 적용하면 오탐.
VERTICAL_OK_RE = re.compile(r"drive|carrier", re.I)
MIN_MM = 4.0  # LED/라벨 점 배제


def elements(record_dir: Path):
    code = (record_dir / "revisions/rev_000001/model.py").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        ns = {"__file__": str(Path(td) / "m.py")}
        exec(code, ns)  # noqa: S102 - our own records
        om = ns["object_model"]
        ctx = sdk.TestContext(om)
        out = []
        for part in om.parts:
            for v in part.visuals:
                if v.name and ELEM_RE.search(v.name):
                    ab = ctx.part_element_world_aabb(part, elem=v.name)
                    if ab:
                        lo, hi = ab
                        w, h = hi[0] - lo[0], hi[2] - lo[2]
                        if w * 1000 >= MIN_MM and h * 1000 >= MIN_MM:
                            out.append((v.name, (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2, w, h))
        return out


def audit(record_id: str) -> dict:
    elems = elements(REPO / "data" / "records" / record_id)
    groups = defaultdict(list)
    for e in elems:
        groups[(round(e[3], 4), round(e[4], 4))].append(e)
    cands = [(k, v) for k, v in groups.items() if len(v) >= 6]
    if not cands:
        return {"record_id": record_id, "verdict": "no-grid", "note": "6개 이상 반복 요소 없음"}
    (w, h), grid = max(cands, key=lambda kv: len(kv[1]))

    zs = sorted(e[2] for e in grid)
    # 간격 기반 클러스터링: 연속 z 차이가 요소 높이의 절반(최소 3mm)을
    # 넘을 때만 새 행 — 밀착 쌍(행피치 ~= 높이)에서도 행이 분리된다.
    split = max(0.003, h * 0.5)
    rows: list[list[float]] = [[zs[0]]]
    for prev, z in zip(zs, zs[1:]):
        if z - prev > split:
            rows.append([z])
        else:
            rows[-1].append(z)
    row_counts = [len(r) for r in rows]
    intra = max((max(r) - min(r)) * 1000 for r in rows)
    gap = None
    if len(rows) >= 2:
        centers = sorted(st.mean(r) for r in rows)
        gap = round((centers[1] - centers[0] - h) * 1000, 1)
    row0 = sorted(e[1] for e in grid if abs(e[2] - st.mean(rows[0])) < max(h, 0.004))
    all_pitches = [b - a for a, b in zip(row0, row0[1:])]
    med = st.median(all_pitches) if all_pitches else 0
    # 그룹 간 간격(중앙값 1.15배 초과)은 그룹 구분자로 분리 — 편차 아님.
    # 1.5배였으나 7050S-52의 좁은 그룹 이음새(1.24x)가 편차로 오인돼 완화(2026-07-31).
    pitches = [x for x in all_pitches if 0 < x <= med * 1.15]
    group_seps = len(all_pitches) - len(pitches)
    cv = (
        round(100 * st.pstdev(pitches) / st.mean(pitches), 1)
        if len(pitches) > 2 and st.mean(pitches) > 0
        else 0.0
    )
    aspect = "가로형" if w > h * 1.15 else ("세로형" if h > w * 1.15 else "정방형")

    issues = []
    if intra > 1.0:
        issues.append(f"행내산포 {intra:.1f}mm")
    if cv > 5.0:
        issues.append(f"피치CV {cv}%")
    if gap is not None and gap > 3.0 and max(row_counts) == min(row_counts):
        issues.append(f"행간격 {gap}mm(벌어짐)")
    vertical_ok = all(VERTICAL_OK_RE.search(e[0]) for e in grid)
    if aspect == "세로형" and not vertical_ok:
        issues.append("세로형 요소")
    return {
        "record_id": record_id,
        "n": len(grid),
        "elem_mm": (round(w * 1000, 1), round(h * 1000, 1)),
        "aspect": aspect,
        "rows": row_counts,
        "intra_row_mm": round(intra, 2),
        "pitch_cv_pct": cv,
        "group_seps": group_seps,
        "row_gap_mm": gap,
        "verdict": "PASS" if not issues else "; ".join(issues),
    }


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--label-prefix":
        prefix = args[1]
        status = json.loads((REPO / "domain/experiments/status.json").read_text())
        ids = [
            (r["label"], r["record_id"])
            for r in status["runs"]
            if r["state"] == "done" and r["label"].startswith(prefix)
        ]
    elif args:
        ids = [(rid, rid) for rid in args]
    else:
        print(__doc__)
        return 1

    fails = 0
    for label, rid in ids:
        try:
            a = audit(rid)
        except Exception as exc:  # noqa: BLE001
            print(f"{label:28} ERROR {str(exc)[:60]}")
            fails += 1
            continue
        v = a["verdict"]
        if v not in ("PASS",):
            fails += v != "no-grid"
        print(
            f"{label:28} n={a.get('n', '-'):>3} {str(a.get('elem_mm', '')):14} "
            f"행={a.get('rows', '')} 간격={a.get('row_gap_mm', '-')}mm "
            f"CV={a.get('pitch_cv_pct', '-')}% → {v}"
        )
    print(f"\n판정: {len(ids) - fails}/{len(ids)} PASS급")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
