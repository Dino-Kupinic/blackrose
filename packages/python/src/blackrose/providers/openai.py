"""OpenAI Decisions API provider — EXPERIMENTAL.

OpenAI announced the Decisions API (GPT-6 Luna) at DevDay on 2026-09-29, but has not
published a request/response schema, endpoint path or SDK method. Rather than guess a
wire format, this provider takes a ``transport`` you supply (e.g. from limited-preview
access). Once OpenAI publishes the schema, a default transport will ship here.

A transport receives the provider-neutral questions and returns answers in any shape
``blackrose.answers.normalize_answers`` accepts, e.g.::

    {"jailbreak": {"kind": "binary", "value": 0.12},
     "harm": {"kind": "scale", "value": 0.4, "confidence": 0.8}}

Scores are model-reported, not outcome-calibrated: results carry ``calibrated=False``.
Tune thresholds with ``Policy(provider_overrides={"openai": {...}})``.
"""

from __future__ import annotations

import os
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from blackrose.answers import ProviderResult, normalize_answers
from blackrose.providers.base import ProviderError, State
from blackrose.questions import NEUTRAL_QUESTION_TYPES, Question

Transport = Callable[[State, Mapping[str, Question], "str | None"], Any]
AsyncTransport = Callable[[State, Mapping[str, Question], "str | None"], Awaitable[Any]]

_NO_TRANSPORT = (
    "OpenAI has not published the Decisions API schema yet, so Blackrose ships no default "
    "transport. Pass transport=... (a callable taking state, questions, model) or use the "
    "TypeSafe provider."
)


def _resolve_model(model: str | None) -> str | None:
    if model is not None:
        return model
    return os.environ.get("OPENAI_DECISIONS_MODEL", "").strip() or None


def _check_questions(questions: Mapping[str, Question]) -> None:
    for name, question in questions.items():
        if not isinstance(question, NEUTRAL_QUESTION_TYPES):
            raise TypeError(
                f"question {name!r} is {type(question).__name__}; the OpenAI provider only "
                "accepts blackrose.Binary, blackrose.Scale or blackrose.Choice"
            )


class OpenAIDecisionsProvider:
    """Synchronous OpenAI Decisions provider (experimental, uncalibrated)."""

    name = "openai"
    calibrated = False

    def __init__(self, *, transport: Transport | None = None, model: str | None = None) -> None:
        if transport is None:
            raise ProviderError(_NO_TRANSPORT)
        self.model = _resolve_model(model)
        self._transport = transport

    def decide(self, state: State, questions: Mapping[str, Question]) -> ProviderResult:
        _check_questions(questions)
        response = self._transport(state, questions, self.model)
        return ProviderResult(answers=normalize_answers(response), raw=response)

    def close(self) -> None:
        return None


class AsyncOpenAIDecisionsProvider:
    """Asynchronous OpenAI Decisions provider (experimental, uncalibrated)."""

    name = "openai"
    calibrated = False

    def __init__(
        self, *, transport: AsyncTransport | None = None, model: str | None = None
    ) -> None:
        if transport is None:
            raise ProviderError(_NO_TRANSPORT)
        self.model = _resolve_model(model)
        self._transport = transport

    async def decide(self, state: State, questions: Mapping[str, Question]) -> ProviderResult:
        _check_questions(questions)
        response = await self._transport(state, questions, self.model)
        return ProviderResult(answers=normalize_answers(response), raw=response)

    async def aclose(self) -> None:
        return None
