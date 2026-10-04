"""Blackrose: provider-neutral decision layer for LLM input/output."""

from blackrose.answers import Answer, ProviderResult
from blackrose.guard import AsyncGuard, Guard
from blackrose.policy import Policy, default_input_questions, default_output_questions
from blackrose.providers import (
    AsyncOpenAIDecisionsProvider,
    AsyncProvider,
    AsyncTypeSafeProvider,
    OpenAIDecisionsProvider,
    Provider,
    ProviderError,
    TypeSafeProvider,
)
from blackrose.questions import Binary, Choice, Question, Scale
from blackrose.types import CheckResult, Verdict

__all__ = [
    "Answer",
    "AsyncGuard",
    "AsyncOpenAIDecisionsProvider",
    "AsyncProvider",
    "AsyncTypeSafeProvider",
    "Binary",
    "CheckResult",
    "Choice",
    "Guard",
    "OpenAIDecisionsProvider",
    "Policy",
    "Provider",
    "ProviderError",
    "ProviderResult",
    "Question",
    "Scale",
    "TypeSafeProvider",
    "Verdict",
    "default_input_questions",
    "default_output_questions",
]

__version__ = "0.1.0"
