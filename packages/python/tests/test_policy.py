"""Policy validation and question-battery tests."""

from __future__ import annotations

import pytest

from blackrose import Policy, PolicyConfigError, ScoreThresholds, default_input_questions
from blackrose.policy import harm_severity


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
