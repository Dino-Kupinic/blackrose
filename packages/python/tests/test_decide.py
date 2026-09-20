"""Unit tests for threshold → verdict mapping (no live TypeSafe calls)."""

from __future__ import annotations

from blackrose.decide import decide, extract_scores
from blackrose.policy import Policy


def test_allow_when_all_signals_low() -> None:
    raw = {
        "jailbreak": {"noul": 0.02},
        "harm": {"score": 0.1, "confidence": 0.9},
        "needs_human": {"noul": 0.05},
    }
    result = decide(raw, Policy())
    assert result.verdict == "allow"
    assert result.reasons == []
    assert result.scores["jailbreak"] == 0.02
    assert result.scores["harm"] == 0.1


def test_review_on_mid_noul() -> None:
    raw = {
        "jailbreak": {"noul": 0.40},
        "harm": {"score": 0.2, "confidence": 0.9},
        "needs_human": {"noul": 0.1},
    }
    result = decide(raw, Policy())
    assert result.verdict == "review"
    assert any("jailbreak" in r for r in result.reasons)


def test_block_on_high_jailbreak() -> None:
    raw = {
        "jailbreak": {"noul": 0.95},
        "harm": {"score": 0.5, "confidence": 0.9},
        "needs_human": {"noul": 0.2},
    }
    result = decide(raw, Policy())
    assert result.verdict == "block"


def test_needs_human_high_is_review_not_block() -> None:
    """needs_human is not in block_checks by default."""
    raw = {
        "jailbreak": {"noul": 0.05},
        "harm": {"score": 0.2, "confidence": 0.9},
        "needs_human": {"noul": 0.92},
    }
    result = decide(raw, Policy())
    assert result.verdict == "review"
    assert any("needs_human" in r for r in result.reasons)


def test_harm_score_block() -> None:
    raw = {
        "jailbreak": {"noul": 0.05},
        "harm": {"score": 2.4, "confidence": 0.85},
        "needs_human": {"noul": 0.1},
    }
    result = decide(raw, Policy())
    assert result.verdict == "block"


def test_low_confidence_forces_review_not_allow() -> None:
    raw = {
        "jailbreak": {"noul": 0.05},
        "harm": {"score": 0.3, "confidence": 0.2},
        "needs_human": {"noul": 0.05},
    }
    result = decide(raw, Policy())
    assert result.verdict == "review"
    assert any("confidence" in r for r in result.reasons)


def test_low_confidence_does_not_downgrade_block() -> None:
    raw = {
        "jailbreak": {"noul": 0.95},
        "harm": {"score": 0.3, "confidence": 0.1},
        "needs_human": {"noul": 0.05},
    }
    result = decide(raw, Policy())
    assert result.verdict == "block"


def test_custom_thresholds() -> None:
    policy = Policy(review_threshold=0.2, block_threshold=0.5)
    raw = {
        "jailbreak": {"noul": 0.55},
        "harm": {"score": 0.0, "confidence": 0.99},
        "needs_human": {"noul": 0.0},
    }
    assert decide(raw, policy).verdict == "block"


def test_extract_scores_from_nested_sdk_shape() -> None:
    class Answer:
        def __init__(self, **kwargs: float) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Response:
        nouls = {"jailbreak": Answer(noul=0.8)}
        scores = {"harm": Answer(score=1.5, confidence=0.7)}
        choices = {}

    scores = extract_scores(Response())
    assert scores == {"jailbreak": 0.8, "harm": 1.5}
