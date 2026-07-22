"""Fork guard tests.

These tests exercise fork-local behavior THROUGH upstream entry points, so
they fail loudly if an upstream merge wipes out the fork seams. If a test
here fails right after merging upstream, re-apply the seam it names.
"""

from __future__ import annotations

from agent.cost import pricing_for_provider_model


def test_openrouter_pricing_resolves_via_fork_seam() -> None:
    pricing = pricing_for_provider_model("openrouter", "openai/gpt-5.6-sol")
    assert pricing is not None, (
        "Fork seam lost: pricing_for_provider_model() no longer consults "
        "agent.cost_overrides.local_pricing_override (likely an upstream merge "
        "rewrote agent/cost.py). Re-apply the 3-line seam at the top of that function."
    )
    assert pricing["output"] == 30.0
    assert pricing["input_uncached"] == 5.0


def test_openrouter_opus_pricing_resolves() -> None:
    pricing = pricing_for_provider_model("openrouter", "anthropic/claude-opus-4.8")
    assert pricing is not None
    assert pricing["output"] == 25.0


def test_unknown_openrouter_model_still_defers() -> None:
    assert pricing_for_provider_model("openrouter", "vendor/unknown-model-xyz") is None


def test_upstream_native_pricing_table_unaffected() -> None:
    assert pricing_for_provider_model("openai", "gpt-5.5-2026-04-23") is not None
