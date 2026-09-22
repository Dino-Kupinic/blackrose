"""Contract tests against realistic TypeSafe System One response shapes."""

from __future__ import annotations

from typing import Any

from blackrose.decide import decide, extract_scores
from blackrose.policy import Policy


def test_decide_on_attribute_bucketed_sdk_shape_blocks_jailbreak() -> None:
    class Answer:
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    class Response:
        nouls = {"jailbreak": Answer(noul=0.91)}
        scores = {"harm": Answer(score=0.5, confidence=0.9)}
        choices: dict[str, Any] = {}

    result = decide(Response(), Policy())
    assert result.verdict == "block"
    assert extract_scores(Response())["jailbreak"] == 0.91
    assert "noul_block:jailbreak" in result.codes
