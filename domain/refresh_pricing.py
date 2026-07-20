"""Refresh domain/pricing_overrides.json from the OpenRouter models API.

Usage:
    uv run python domain/refresh_pricing.py [--dry-run]

Only models already listed in the overrides file are updated; adding a new
model is a deliberate manual edit. Stamps _meta.as_of so every cost.json can
be traced to a pricing date. Fails without touching the file when offline.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

OVERRIDES_PATH = Path(__file__).resolve().parent / "pricing_overrides.json"
API_URL = "https://openrouter.ai/api/v1/models"
PER_MILLION = 1_000_000


def fetch_api_pricing() -> dict[str, dict]:
    with urllib.request.urlopen(API_URL, timeout=30) as resp:
        payload = json.load(resp)
    return {m["id"].lower(): m.get("pricing", {}) for m in payload.get("data", [])}


def refreshed_entry(current: dict, api: dict) -> dict:
    updated = dict(current)
    mapping = {
        "prompt": "input_uncached",
        "completion": "output",
        "input_cache_read": "input_cached",
        "input_cache_write": "input_cache_write",
    }
    for api_key, our_key in mapping.items():
        raw = api.get(api_key)
        if raw in (None, ""):
            continue
        updated[our_key] = round(float(raw) * PER_MILLION, 4)
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    overrides = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    try:
        api_pricing = fetch_api_pricing()
    except Exception as exc:
        print(f"refresh failed, file untouched: {exc}", file=sys.stderr)
        return 1

    changes = 0
    table = overrides.get("openrouter", {})
    for model_id, entry in table.items():
        api = api_pricing.get(model_id)
        if api is None:
            print(f"  ! {model_id}: not on OpenRouter anymore — review manually")
            continue
        new_entry = refreshed_entry(entry, api)
        if new_entry != entry:
            print(f"  ~ {model_id}: {entry} -> {new_entry}")
            table[model_id] = new_entry
            changes += 1
        else:
            print(f"  = {model_id}: unchanged")

    overrides["_meta"] = {
        "as_of": date.today().isoformat(),
        "source": API_URL,
    }
    if args.dry_run:
        print(f"dry-run: {changes} change(s) not written")
        return 0
    OVERRIDES_PATH.write_text(
        json.dumps(overrides, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {OVERRIDES_PATH.name}: {changes} change(s), as_of={overrides['_meta']['as_of']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
