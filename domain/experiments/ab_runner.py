"""A/B experiment runner: 32 generations with live status for the dashboard.

Usage:
    uv run python domain/experiments/ab_runner.py            # full matrix
    uv run python domain/experiments/ab_runner.py --limit 2  # smoke test

Writes domain/experiments/status.json after every state change (atomic
rename), logs each run to domain/experiments/logs/<label>.log. Serve the
dashboard with:
    python3 -m http.server 8777 --directory domain/experiments
then open http://127.0.0.1:8777/dashboard.html
"""

from __future__ import annotations

import argparse
import json
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASELINE = REPO / ".worktrees" / "ab-baseline"
STATUS_PATH = HERE / "status.json"
LOGS = HERE / "logs"
QC_BLURB = "qc/network_equipment_checklist.md"
TAG = "ab-202607"
MAX_COST = "50"
CONCURRENCY = 3

MODELS = {
    "sol": "openai/gpt-5.6-sol",
    "opus": "anthropic/claude-opus-4.8",
}

DEVICES = {
    "nexus": {
        "image": "nexus.png",
        "prompt": (
            "A Cisco Nexus 93180YC-EX 1U rackmount data-center switch. 439 mm wide, "
            "44 mm (1U) tall, 571 mm deep, 7.8 kg. Front: 48 SFP28 cages in two rows "
            "of 24 with paired port LEDs, six QSFP28 uplink cages on the right in a "
            "2x3 block, status LEDs and management ports on the left edge."
        ),
    },
    "arista": {
        "image": "arista.png",
        "prompt": (
            "An Arista 7010T-48 1U rackmount access switch, shallow chassis: 445 mm "
            "wide, 44 mm (1U) tall, only 254 mm deep, 4.6 kg. Front: 48 RJ45 copper "
            "ports in three 16-port groups (each two rows of eight) with per-port link "
            "LEDs, four SFP+ uplink cages in a 2x2 block to their right, then console "
            "and management RJ45 ports, USB, and a small status LED column at the far "
            "right edge."
        ),
    },
    "r760": {
        "image": "r760.png",
        "prompt": (
            "A Dell PowerEdge R760 2U rackmount server with its front bezel installed. "
            "482 mm face, 86.8 mm (2U) tall, 772 mm deep, 36.1 kg. Front: a black "
            "perforated bezel with a large hexagonal-hole pattern and a centered DELL "
            "logo, drive carrier LEDs faintly visible through the openings, a slim "
            "left ear panel with status light strip, power button and ports on the "
            "right ear panel."
        ),
    },
    "dl360": {
        "image": "dl360.png",
        "prompt": (
            "An HPE ProLiant DL360 Gen10 1U rackmount server. 434.6 mm wide, 42.9 mm "
            "(1U) tall, 707 mm deep, 16.78 kg. Front: eight 2.5-inch SFF hot-swap "
            "drive bays across the center-left with ejector levers, a right end-cap "
            "with power button, health LEDs and USB, HPE quick-release mounting ears."
        ),
    },
}

_lock = threading.Lock()
_state: dict = {}


def build_jobs() -> list[dict]:
    jobs = []
    for rep in ("r1", "r2"):
        for device in DEVICES:
            for mkey in MODELS:
                for cond in ("A", "B"):
                    jobs.append(
                        {
                            "label": f"ab-{cond}-{device}-{rep}-{mkey}",
                            "cond": cond,
                            "device": device,
                            "model_key": mkey,
                            "model": MODELS[mkey],
                            "rep": rep,
                            "state": "pending",
                            "record_id": None,
                            "minutes": None,
                            "cost_usd": None,
                            "tokens_in": None,
                            "tokens_out": None,
                            "error": None,
                        }
                    )
    return jobs


def flush_status() -> None:
    with _lock:
        _state["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        done = [r for r in _state["runs"] if r["state"] == "done"]
        _state["totals"] = {
            "total": len(_state["runs"]),
            "done": len(done),
            "running": sum(1 for r in _state["runs"] if r["state"] == "running"),
            "failed": sum(1 for r in _state["runs"] if r["state"] == "failed"),
            "cost_usd": round(sum(r["cost_usd"] or 0 for r in _state["runs"]), 2),
        }
        tmp = STATUS_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(_state, indent=1, ensure_ascii=False), encoding="utf-8")
        tmp.replace(STATUS_PATH)


def newest_record(data_root: Path, existing: set[str]) -> str | None:
    records = data_root / "records"
    if not records.exists():
        return None
    fresh = [p.name for p in records.iterdir() if p.is_dir() and p.name not in existing]
    if not fresh:
        return None
    return max(fresh, key=lambda n: (records / n).stat().st_mtime)


def read_cost(record_dir: Path, job: dict) -> None:
    cost_path = record_dir / "revisions" / "rev_000001" / "cost.json"
    if not cost_path.exists():
        return
    try:
        total = json.loads(cost_path.read_text(encoding="utf-8"))["total"]
        job["cost_usd"] = round(float(total["costs_usd"]["total"]), 3)
        job["tokens_in"] = total["tokens"].get("prompt_tokens")
        job["tokens_out"] = total["tokens"].get("candidates_tokens")
    except (KeyError, ValueError, TypeError):
        pass


def run_job(job: dict) -> None:
    cwd = BASELINE if job["cond"] == "A" else REPO
    data_root = cwd / "data"
    records_dir = data_root / "records"
    before = (
        {p.name for p in records_dir.iterdir() if p.is_dir()} if records_dir.exists() else set()
    )

    cmd = [
        "uv",
        "run",
        "articraft",
        "generate",
        "--provider",
        "openrouter",
        "--model",
        job["model"],
        "--thinking",
        "high",
        "--image",
        str(HERE / "ref_images" / DEVICES[job["device"]]["image"]),
        "--max-cost-usd",
        MAX_COST,
        "--label",
        job["label"],
        "--tag",
        TAG,
    ]
    if job["cond"] == "B":
        cmd += ["--qc-blurb", QC_BLURB]
    cmd.append(DEVICES[job["device"]]["prompt"])

    job["state"] = "running"
    job["started"] = time.strftime("%H:%M:%S")
    flush_status()

    t0 = time.time()
    log_path = LOGS / f"{job['label']}.log"
    try:
        with open(log_path, "w", encoding="utf-8") as log:
            proc = subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, timeout=3600)
        job["minutes"] = round((time.time() - t0) / 60, 1)
        record_id = newest_record(data_root, before)
        job["record_id"] = record_id
        if proc.returncode == 0 and record_id:
            job["state"] = "done"
            read_cost(records_dir / record_id, job)
        else:
            job["state"] = "failed"
            job["error"] = f"exit={proc.returncode}, record={record_id}"
    except subprocess.TimeoutExpired:
        job["minutes"] = round((time.time() - t0) / 60, 1)
        job["state"] = "failed"
        job["error"] = "timeout 60min"
    except Exception as exc:  # noqa: BLE001 - record any failure and continue
        job["state"] = "failed"
        job["error"] = str(exc)[:200]
    flush_status()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="run only the first N jobs")
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="reload status.json and re-run only failed/skipped jobs, keeping done results",
    )
    args = parser.parse_args()

    LOGS.mkdir(exist_ok=True)
    if args.retry_failed:
        _state.update(json.loads(STATUS_PATH.read_text(encoding="utf-8")))
        jobs = [r for r in _state["runs"] if r["state"] in ("failed", "skipped")]
        for job in jobs:
            job.update(state="pending", error=None, minutes=None, record_id=None, cost_usd=None)
        print(f"retrying {len(jobs)} failed job(s)")
    else:
        jobs = build_jobs()
        if args.limit:
            jobs = jobs[: args.limit]
        _state.update(
            {
                "experiment": "domain-pack A/B",
                "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "runs": jobs,
            }
        )
    flush_status()

    aborted = threading.Event()

    def guarded(job: dict) -> None:
        if aborted.is_set():
            job["state"] = "skipped"
            job["error"] = "aborted after early systemic failures"
            flush_status()
            return
        run_job(job)
        finished = [r for r in jobs if r["state"] in ("done", "failed")]
        if len(finished) >= 3 and all(r["state"] == "failed" for r in finished[:3]):
            aborted.set()

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        list(pool.map(guarded, jobs))

    flush_status()
    done = sum(1 for r in jobs if r["state"] == "done")
    print(f"finished: {done}/{len(jobs)} done, see {STATUS_PATH}")
    return 0 if done == len(jobs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
