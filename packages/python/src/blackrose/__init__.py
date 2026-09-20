"""Blackrose: TypeSafe decision layer for LLM input/output."""

from blackrose.guard import AsyncGuard, Guard
from blackrose.policy import Policy, default_input_questions, default_output_questions
from blackrose.types import CheckResult, Verdict

__all__ = [
    "AsyncGuard",
    "CheckResult",
    "Guard",
    "Policy",
    "Verdict",
    "default_input_questions",
    "default_output_questions",
]

__version__ = "0.1.0"
