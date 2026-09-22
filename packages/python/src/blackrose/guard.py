"""Sync and async Guard clients wrapping the official TypeSafe SDK."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any, Protocol

from typesafe_sdk import AsyncTypeSafeClient, Question, TypeSafeClient

from blackrose.decide import decide
from blackrose.errors import BlackroseError, GuardClosedError, TypeSafeRequestError
from blackrose.policy import Policy, PolicySide
from blackrose.types import CheckResult

State = Any  # JSONContent: str | Mapping | Sequence
ClientConfig = Mapping[str, Any]


def _resolve_model(model: str | None) -> str:
    if model is not None:
        stripped = model.strip()
        if stripped:
            return stripped
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


def _client_kwargs(
    *,
    api_key: str | None,
    model: str,
    client_config: ClientConfig | None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = dict(client_config or {})
    kwargs["api_key"] = api_key
    kwargs["model"] = model
    return kwargs


class Guard:
    """Synchronous decision layer over TypeSafe ``system_one``."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        policy: Policy | None = None,
        client: _SyncSystemOne | None = None,
        client_config: ClientConfig | None = None,
    ) -> None:
        self.policy = policy or Policy()
        self._model = _resolve_model(model)
        self._owns_client = client is None
        self._closed = False
        self._client: _SyncSystemOne = client or TypeSafeClient(
            **_client_kwargs(api_key=api_key, model=self._model, client_config=client_config)
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._owns_client and hasattr(self._client, "close"):
            self._client.close()

    def __enter__(self) -> Guard:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def check_input(self, state: State) -> CheckResult:
        return self._check(state, "input")

    def check_output(self, state: State) -> CheckResult:
        return self._check(state, "output")

    def _check(self, state: State, side: PolicySide) -> CheckResult:
        if self._closed:
            raise GuardClosedError("Guard is closed")
        questions = self.policy.questions_for(side)
        try:
            response = self._client.system_one(state, questions, model=self._model)
        except BlackroseError:
            raise
        except Exception as exc:
            raise TypeSafeRequestError(
                "TypeSafe system_one failed; fail closed (do not allow)"
            ) from exc
        return decide(response, self.policy, expected_checks=questions.keys())


class AsyncGuard:
    """Asynchronous decision layer over TypeSafe ``system_one``."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        policy: Policy | None = None,
        client: _AsyncSystemOne | None = None,
        client_config: ClientConfig | None = None,
    ) -> None:
        self.policy = policy or Policy()
        self._model = _resolve_model(model)
        self._owns_client = client is None
        self._closed = False
        self._client: _AsyncSystemOne = client or AsyncTypeSafeClient(
            **_client_kwargs(api_key=api_key, model=self._model, client_config=client_config)
        )

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._owns_client and hasattr(self._client, "aclose"):
            await self._client.aclose()

    async def __aenter__(self) -> AsyncGuard:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def check_input(self, state: State) -> CheckResult:
        return await self._check(state, "input")

    async def check_output(self, state: State) -> CheckResult:
        return await self._check(state, "output")

    async def _check(self, state: State, side: PolicySide) -> CheckResult:
        if self._closed:
            raise GuardClosedError("AsyncGuard is closed")
        questions = self.policy.questions_for(side)
        try:
            response = await self._client.system_one(state, questions, model=self._model)
        except BlackroseError:
            raise
        except Exception as exc:
            raise TypeSafeRequestError(
                "TypeSafe system_one failed; fail closed (do not allow)"
            ) from exc
        return decide(response, self.policy, expected_checks=questions.keys())
