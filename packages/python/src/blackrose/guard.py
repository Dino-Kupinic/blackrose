"""Sync and async Guard clients wrapping the official TypeSafe SDK."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any, Protocol

from typesafe_sdk import AsyncTypeSafeClient, Question, TypeSafeClient

from blackrose.decide import decide
from blackrose.policy import Policy
from blackrose.types import CheckResult

State = Any  # JSONContent: str | Mapping | Sequence


def _resolve_model(model: str | None) -> str | None:
    if model is not None:
        return model
    for env in ("TYPESAFE_MODEL", "TYPESAFE_DEFAULT_MODEL"):
        value = os.environ.get(env, "").strip()
        if value:
            return value
    return "jev-latest"


class _SyncSystemOne(Protocol):
    def system_one(
        self,
        state: State,
        questions: Mapping[str, Question],
        *,
        model: str | None = None,
    ) -> Any: ...


class _AsyncSystemOne(Protocol):
    async def system_one(
        self,
        state: State,
        questions: Mapping[str, Question],
        *,
        model: str | None = None,
    ) -> Any: ...


class Guard:
    """Synchronous decision layer over TypeSafe ``system_one``."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        policy: Policy | None = None,
        client: _SyncSystemOne | None = None,
    ) -> None:
        self.policy = policy or Policy()
        self._model = _resolve_model(model)
        self._owns_client = client is None
        self._client: _SyncSystemOne = client or TypeSafeClient(
            api_key=api_key,
            model=self._model,
        )

    def close(self) -> None:
        if self._owns_client and hasattr(self._client, "close"):
            self._client.close()  # type: ignore[attr-defined]

    def __enter__(self) -> Guard:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def check_input(self, state: State) -> CheckResult:
        return self._check(state, "input")

    def check_output(self, state: State) -> CheckResult:
        return self._check(state, "output")

    def _check(self, state: State, side: str) -> CheckResult:
        questions = self.policy.questions_for(side)
        response = self._client.system_one(state, questions, model=self._model)
        return decide(response, self.policy)


class AsyncGuard:
    """Asynchronous decision layer over TypeSafe ``system_one``."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        policy: Policy | None = None,
        client: _AsyncSystemOne | None = None,
    ) -> None:
        self.policy = policy or Policy()
        self._model = _resolve_model(model)
        self._owns_client = client is None
        self._client: _AsyncSystemOne = client or AsyncTypeSafeClient(
            api_key=api_key,
            model=self._model,
        )

    async def aclose(self) -> None:
        if self._owns_client and hasattr(self._client, "aclose"):
            await self._client.aclose()  # type: ignore[attr-defined]

    async def __aenter__(self) -> AsyncGuard:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def check_input(self, state: State) -> CheckResult:
        return await self._check(state, "input")

    async def check_output(self, state: State) -> CheckResult:
        return await self._check(state, "output")

    async def _check(self, state: State, side: str) -> CheckResult:
        questions = self.policy.questions_for(side)
        response = await self._client.system_one(state, questions, model=self._model)
        return decide(response, self.policy)
