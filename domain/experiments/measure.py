"""M1 measurement: compile every A/B record and compute metrics into results.csv.

Usage (after all runs finish):
    uv run python domain/experiments/measure.py

Per run: EIA dimension errors (exec model.py, union part AABBs), repair cost
(revision.json run_summary + cost.json), QC warnings (articraft compile
--validate report), and naming-convention hits.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASELINE = REPO / ".worktrees" / "ab-baseline"
STATUS = json.loads((HERE / "status.json").read_text(encoding="utf-8"))

# expected (W, H, D) meters per device, from the registry/prompts
EXPECTED = {
    "nexus": (0.439, 0.044, 0.571),
    "arista": (0.445, 0.044, 0.254),
    "r760": (0.482, 0.0868, 0.772),
    "dl360": (0.4346, 0.0429, 0.707),
}

NAMING_RE = re.compile(
    r"^(chassis|body|frame|faceplate|panel|bezel|cabinet|shell|door(_\w+)?|"
    r"rail(_\w+)?|ear(_left|_right|_\d+)?|tray|shelf(_\d+)?|"
    r"port(_\w+)?|label(_\w+)?|led(_\w+)?|fan(_\d+)?|psu(_\d+)?|"
    r"handle(_\d+)?|drive(_\w+)?|bay(_\w+)?|button(_\w+)?|status(_\w+)?|"
    r"vent(_\w+)?|grille(_\w+)?|cage(_\w+)?|bracket(_\w+)?|cable(_\w+)?)"
    r"(_\d+)*$"
)


def model_metrics(record_dir: Path) -> dict:
    """Exec model.py, union part AABBs, inspect names and joints."""
    import sdk

    model_py = record_dir / "revisions" / "rev_000001" / "model.py"
    code = model_py.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        ns = {"__file__": str(Path(td) / "model.py")}
        exec(code, ns)  # noqa: S102 - our own generated records
        om = ns["object_model"]
        ctx = sdk.TestContext(om)
        lo = [float("inf")] * 3
        hi = [float("-inf")] * 3
        names = []
        for part in om.parts:
            aabb = ctx.part_world_aabb(part)
            if aabb:
                for i in range(3):
                    lo[i] = min(lo[i], aabb[0][i])
                    hi[i] = max(hi[i], aabb[1][i])
            names.append(part.name or "")
            names.extend(v.name or "" for v in part.visuals)
        dims = tuple(hi[i] - lo[i] for i in range(3))
        named = [n for n in names if n]
        joints_defaulted = sum(
            1
            for j in om.articulations
            if j.motion_limits is not None
            and (j.motion_limits.effort == 1.0 or j.motion_limits.velocity == 1.0)
        )
        return {
            "dims": dims,
            "naming_total": len(named),
            "naming_hits": sum(1 for n in named if NAMING_RE.match(n)),
            "joint_count": len(om.articulations),
            "joints_defaulted": joints_defaulted,
        }


def compile_warnings(cwd: Path, record_id: str) -> tuple[int, str]:
    subprocess.run(
        ["uv", "run", "articraft", "compile", record_id, "--validate"],
        cwd=cwd,
        capture_output=True,
        timeout=900,
    )
    report_path = (
        cwd / "data" / "cache" / "record_materialization" / record_id / "compile_report.json"
    )
    if not report_path.exists():
        return -1, "no_report"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    return len(report.get("warnings", [])), str(report.get("status", "?"))


def main() -> int:
    rows = []
    for run in STATUS["runs"]:
        if run["state"] != "done" or not run["record_id"]:
            continue
        cwd = BASELINE if run["cond"] == "A" else REPO
        record_dir = cwd / "data" / "records" / run["record_id"]
        row = {
            "label": run["label"],
            "cond": run["cond"],
            "device": run["device"],
            "model": run["model_key"],
            "rep": run["rep"],
            "record_id": run["record_id"],
            "cost_usd": run["cost_usd"],
        }
        try:
            rev = json.loads(
                (record_dir / "revisions" / "rev_000001" / "revision.json").read_text()
            )
            summary = rev.get("run_summary", {})
            row["turns"] = summary.get("turn_count")
            row["compile_attempts"] = summary.get("compile_attempt_count")
        except (OSError, ValueError):
            row["turns"] = row["compile_attempts"] = None
        try:
            m = model_metrics(record_dir)
            exp = EXPECTED[run["device"]]
            row["width_err_mm"] = round(abs(m["dims"][0] - exp[0]) * 1000, 1)
            row["height_err_mm"] = round(abs(m["dims"][2] - exp[1]) * 1000, 1)
            row["depth_err_mm"] = round(abs(m["dims"][1] - exp[2]) * 1000, 1)
            row["naming_pct"] = (
                round(100 * m["naming_hits"] / m["naming_total"], 1) if m["naming_total"] else None
            )
            row["joints"] = m["joint_count"]
            row["joints_defaulted"] = m["joints_defaulted"]
        except Exception as exc:  # noqa: BLE001 - record and continue
            row["measure_error"] = str(exc)[:120]
        warn_count, compile_status = compile_warnings(cwd, run["record_id"])
        row["qc_warnings"] = warn_count
        row["compile_status"] = compile_status
        rows.append(row)
        print(
            f"{row['label']:28} W±{row.get('width_err_mm')} H±{row.get('height_err_mm')} "
            f"D±{row.get('depth_err_mm')}mm naming={row.get('naming_pct')}% "
            f"warn={row.get('qc_warnings')} turns={row.get('turns')}"
        )

    fieldnames = sorted({k for r in rows for k in r}, key=lambda k: k != "label")
    with open(HERE / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nwrote results.csv with {len(rows)} rows")

    def agg(rows_subset, key):
        vals = [r[key] for r in rows_subset if isinstance(r.get(key), (int, float))]
        return round(sum(vals) / len(vals), 2) if vals else None

    print("\n=== A vs B (전 지표 평균) ===")
    for cond in ("A", "B"):
        sub = [r for r in rows if r["cond"] == cond]
        print(
            f"  {cond}: n={len(sub)} width_err={agg(sub, 'width_err_mm')}mm "
            f"height_err={agg(sub, 'height_err_mm')}mm naming={agg(sub, 'naming_pct')}% "
            f"warnings={agg(sub, 'qc_warnings')} turns={agg(sub, 'turns')} "
            f"cost=${agg(sub, 'cost_usd')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
