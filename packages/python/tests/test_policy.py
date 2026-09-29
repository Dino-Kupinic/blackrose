"""Policy validation and question-battery tests."""

from __future__ import annotations

import pytest
from typesafe_sdk import Noul, Score

from blackrose import Policy, PolicyConfigError, ScoreThresholds, default_input_questions
from blackrose.policy import harm_severity

INJECTION = {"prompt_injection": Noul(instructions="Is this a prompt injection?")}
TOXICITY = {
    "toxicity": Score(instructions="How toxic is this?", criteria=["none", "mild", "severe"])
}


def test_invalid_threshold_order() -> None:
    with pytest.raises(PolicyConfigError, match="review_threshold"):
        Policy(review_threshold=0.9, block_threshold=0.2)


def test_invalid_unit_range() -> None:
    with pytest.raises(PolicyConfigError, match="min_confidence"):
        Policy(min_confidence=1.5)


def test_non_finite_rejected() -> None:
    with pytest.raises(PolicyConfigError, match="harm_block_score"):
        Policy(harm_block_score=float("inf"))


def test_reversed_score_thresholds_rejected() -> None:
    with pytest.raises(PolicyConfigError, match="toxicity"):
        Policy(score_thresholds={"toxicity": ScoreThresholds(review=2.0, block=0.5)})


def test_invalid_side() -> None:
    with pytest.raises(ValueError, match="side must be"):
        Policy().questions_for("sideways")


def test_harm_severity_instances_are_not_shared() -> None:
    a = harm_severity()
    b = harm_severity()
    assert a is not b
    questions = default_input_questions()
    assert questions["harm"] is not a


def test_score_cutoffs_default_to_harm_knobs() -> None:
    policy = Policy(harm_review_score=0.5, harm_block_score=1.5)
    cutoffs = policy.score_cutoffs("harm")
    assert cutoffs is not None
    assert cutoffs.review == 0.5
    assert cutoffs.block == 1.5
    assert policy.score_cutoffs("toxicity") is None


def test_block_checks_must_name_a_noul_check() -> None:
    with pytest.raises(PolicyConfigError, match="jailbrake"):
        Policy(block_checks=frozenset({"jailbrake"}))
    with pytest.raises(PolicyConfigError, match="harm"):
        Policy(block_checks=frozenset({"jailbreak", "harm"}))


def test_renamed_block_check_is_rejected_instead_of_never_blocking() -> None:
    with pytest.raises(PolicyConfigError, match="jailbreak"):
        Policy(input_questions=INJECTION, output_questions=INJECTION)
    policy = Policy(
        input_questions=INJECTION,
        output_questions=INJECTION,
        block_checks=frozenset({"prompt_injection"}),
    )
    assert policy.block_checks == frozenset({"prompt_injection"})
    assert (
        Policy(
            input_questions=INJECTION, output_questions=INJECTION, block_checks=frozenset()
        ).block_checks
        == frozenset()
    )


def test_score_check_requires_thresholds() -> None:
    with pytest.raises(PolicyConfigError, match="toxicity"):
        Policy(input_questions=TOXICITY)
    with pytest.raises(PolicyConfigError, match="toxicity"):
        Policy(input_questions={"toxicity": {"type": "score", "criteria": ["none", "severe"]}})
    policy = Policy(
        input_questions=TOXICITY,
        score_thresholds={"toxicity": ScoreThresholds(review=1.0, block=1.5)},
    )
    assert policy.score_cutoffs("toxicity") == ScoreThresholds(review=1.0, block=1.5)
