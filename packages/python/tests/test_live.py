"""Optional live TypeSafe calls — skipped unless TYPESAFE_API_KEY is set."""

from __future__ import annotations

import os

import pytest

from blackrose import Guard

pytestmark = pytest.mark.live


@pytest.fixture(autouse=True)
def _require_api_key() -> None:
    if not os.environ.get("TYPESAFE_API_KEY", "").strip():
        pytest.skip("TYPESAFE_API_KEY not set")


def test_live_safe_input_is_not_block() -> None:
    with Guard() as guard:
        result = guard.check_input("What is the capital of Austria?")
    assert result.verdict in {"allow", "review"}
    assert "jailbreak" in result.scores or len(result.scores) >= 1
