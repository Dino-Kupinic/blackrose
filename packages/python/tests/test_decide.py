"""Unit tests for threshold → verdict mapping (no live TypeSafe calls)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from blackrose.decide import answers_view, decide, extract_scores
from blackrose.policy import Policy

FIXTURES = Path(__file__).resolve().parents[2] / "shared" / "decide-cases.json"


def _load_cases() -> list[dict[str, Any]]:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def _policy(spec: dict[str, Any] | None) -> Policy:
    spec = spec or {}
    kwargs: dict[str, Any] = {}
    for key in (
        "review_threshold",
        "block_threshold",
        "harm_review_score",
        "harm_block_score",
        "min_confidence",
        "score_thresholds",
    ):
        if key in spec:
            kwargs[key] = spec[key]
    if "block_checks" in spec:
        kwargs["block_checks"] = spec["block_checks"]
    return Policy(**kwargs)


def test_shared_decide_cases() -> None:
    for case in _load_cases():
        result = decide(
            case["raw"],
            _policy(case.get("policy")),
            expected_checks=case.get("expected_checks"),
        )
        assert result.verdict == case["verdict"], case["name"]
        assert list(result.codes) == case["codes"], case["name"]
        assert result.reasons == [t.message for t in result.triggers], case["name"]


def test_allow_reasons_empty() -> None:
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


def test_extract_scores_from_nested_sdk_shape() -> None:
    class Answer:
        def __init__(self, **kwargs: float) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Response:
        nouls = {"jailbreak": Answer(noul=0.8)}
        scores = {"harm": Answer(score=1.5, confidence=0.7)}
        choices: dict[str, object] = {}

    scores = extract_scores(Response())
    assert scores == {"jailbreak": 0.8, "harm": 1.5}


def test_answers_view_ignores_non_answer_keys() -> None:
    raw = {
        "model": "jev-latest",
        "usage": {"input_tokens": 3},
        "jailbreak": {"noul": 0.2},
    }
    assert set(answers_view(raw)) == {"jailbreak"}


def test_bool_and_blank_are_not_scores() -> None:
    assert extract_scores({"flag": {"noul": True}}) == {}
    assert extract_scores({"harm": {"score": ""}}) == {}
    assert extract_scores({"harm": {"score": "  "}}) == {}
