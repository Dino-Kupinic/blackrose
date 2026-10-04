"""TypeSafe (Jev) provider — the default backend."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any, Protocol

import typesafe_sdk as ts

from blackrose.answers import ProviderResult, normalize_answers
from blackrose.providers.base import State
from blackrose.questions import Binary, Choice, Question, Scale

DEFAULT_MODEL = "jev-latest"


def resolve_model(model: str | None) -> str:
    if model is not None:
        return model
    for env in ("TYPESAFE_MODEL", "TYPESAFE_DEFAULT_MODEL"):
        value = os.environ.get(env, "").strip()
        if value:
            return value
    return DEFAULT_MODEL


def to_typesafe(question: Question | Any) -> Any:
    """Translate a neutral question into a TypeSafe question; native ones pass through."""
    if isinstance(question, Binary):
        criteria = None
        if question.yes is not None or question.no is not None:
            criteria = ts.NoulCriteria(true=question.yes, false=question.no)
        return ts.Noul(instructions=question.instructions, criteria=criteria)
    if isinstance(question, Scale):
        return ts.Score(instructions=question.instructions, criteria=list(question.criteria))
    if isinstance(question, Choice):
        return ts.Choice(instructions=question.instructions, criteria=dict(question.options))
    return question


def to_typesafe_questions(questions: Mapping[str, Question | Any]) -> dict[str, Any]:
    return {name: to_typesafe(q) for name, q in questions.items()}


class _SyncSystemOne(Protocol):
    def system_one(
        self,
        state: State,
        questions: Mapping[str, ts.Question],
        *,
        model: str | None = None,
    ) -> Any: ...


class _AsyncSystemOne(Protocol):
    async def system_one(
        self,
        state: State,
        questions: Mapping[str, ts.Question],
        *,
        model: str | None = None,
    ) -> Any: ...


class TypeSafeProvider:
    """Synchronous provider over TypeSafe ``system_one`` (calibrated)."""

    name = "typesafe"
    calibrated = True

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        client: _SyncSystemOne | None = None,
    ) -> None:
        self.model = resolve_model(model)
        self._owns_client = client is None
        self._client: _SyncSystemOne = client or ts.TypeSafeClient(
            api_key=api_key,
            model=self.model,
        )

    def decide(self, state: State, questions: Mapping[str, Question]) -> ProviderResult:
        response = self._client.system_one(
            state, to_typesafe_questions(questions), model=self.model
        )
        return ProviderResult(answers=normalize_answers(response), raw=response)

    def close(self) -> None:
        if self._owns_client and hasattr(self._client, "close"):
            self._client.close()  # type: ignore[attr-defined]


class AsyncTypeSafeProvider:
    """Asynchronous provider over TypeSafe ``system_one`` (calibrated)."""

    name = "typesafe"
    calibrated = True

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        client: _AsyncSystemOne | None = None,
    ) -> None:
        self.model = resolve_model(model)
        self._owns_client = client is None
        self._client: _AsyncSystemOne = client or ts.AsyncTypeSafeClient(
            api_key=api_key,
            model=self.model,
        )

    async def decide(self, state: State, questions: Mapping[str, Question]) -> ProviderResult:
        response = await self._client.system_one(
            state, to_typesafe_questions(questions), model=self.model
        )
        return ProviderResult(answers=normalize_answers(response), raw=response)

    async def aclose(self) -> None:
        if self._owns_client and hasattr(self._client, "aclose"):
            await self._client.aclose()  # type: ignore[attr-defined]
