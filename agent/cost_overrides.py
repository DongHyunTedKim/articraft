"""Fork-local pricing overrides.

Upstream's pricing table in agent/cost.py has no OpenRouter entries, so
OpenRouter runs get no CostTracker (no cost.json, no budget cap). This
module supplies pricing from domain/pricing_overrides.json and is consulted
first via a 3-line seam at the top of pricing_for_provider_model().

Fork-only file: upstream merges never touch it. The seam in cost.py is the
only exposed surface; tests/fork/test_cost_overrides.py guards it.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from articraft.values import normalize_provider_name

_OVERRIDES_PATH = Path(__file__).resolve().parents[1] / "domain" / "pricing_overrides.json"


@lru_cache(maxsize=1)
def _load_overrides() -> dict:
    try:
        data = json.loads(_OVERRIDES_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def local_pricing_override(provider: str, model_id: str) -> dict[str, float] | None:
    """Return a pricing dict for (provider, model_id), or None to defer upstream."""
    try:
        provider_key = normalize_provider_name(provider).value
    except (ValueError, AttributeError):
        return None
    table = _load_overrides().get(provider_key)
    if not isinstance(table, dict):
        return None
    entry = table.get((model_id or "").strip().lower())
    if not isinstance(entry, dict):
        return None
    return {key: float(value) for key, value in entry.items()}
