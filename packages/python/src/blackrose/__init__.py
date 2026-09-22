"""Blackrose: TypeSafe decision layer for LLM input/output."""

from blackrose.decide import answers_view, decide, extract_scores
from blackrose.errors import (
    BlackroseError,
    GuardClosedError,
    PolicyConfigError,
    TypeSafeRequestError,
)
from blackrose.guard import AsyncGuard, Guard
from blackrose.policy import (
    HARM_SEVERITY,
    Policy,
    PolicySide,
    ScoreThresholds,
    default_input_questions,
    default_output_questions,
    harm_severity,
)
from blackrose.types import CheckResult, Trigger, Verdict

__all__ = [
    "AsyncGuard",
    "BlackroseError",
    "CheckResult",
    "Guard",
    "GuardClosedError",
    "HARM_SEVERITY",
    "Policy",
    "PolicyConfigError",
    "PolicySide",
    "ScoreThresholds",
    "Trigger",
    "TypeSafeRequestError",
    "Verdict",
    "answers_view",
    "decide",
    "default_input_questions",
    "default_output_questions",
    "extract_scores",
    "harm_severity",
]

__version__ = "0.1.0"
