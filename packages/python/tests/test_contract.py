"""Contract tests against realistic TypeSafe System One response shapes."""

from __future__ import annotations

from typing import Any

from blackrose.decide import decide, extract_scores
from blackrose.policy import Policy


def _sdk_answers_payload() -> dict[str, Any]:
    """Shape similar to typesafe-sdk SystemOne response (answers map)."""
    return {
        "answers": {
            "jailbreak": {"type": "noul", "noul": 0.12, "confidence": None},
            "harm": {"type": "score", "score": 0.4, "confidence": 0.88},
            "needs_human": {"type": "noul", "noul": 0.08},
        },
        "model": "jev-latest",
        "usage": {"input_tokens": 42, "output_tokens": 0},
    }


def test_decide_on_answers_wrapper_allows() -> None:
    raw = _sdk_answers_payload()
    result = decide(raw, Policy())
    assert result.verdict == "allow"
    assert result.scores == {"jailbreak": 0.12, "harm": 0.4, "needs_human": 0.08}
    assert result.raw is raw


def test_decide_on_bucketed_sdk_shape_blocks_jailbreak() -> None:
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


def test_choice_low_confidence_reviews() -> None:
    raw = {
        "answers": {
            "topic": {
                "type": "choice",
                "choice": "billing",
                "confidence": 0.2,
                "probabilities": {"billing": 0.55, "other": 0.45},
            }
        }
    }
    result = decide(raw, Policy())
    assert result.verdict == "review"
    assert result.scores["topic"] == 0.55
