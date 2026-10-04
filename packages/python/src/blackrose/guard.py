"""Sync and async Guard clients over a pluggable decision-model provider."""

from __future__ import annotations

from typing import Any

from blackrose.decide import decide
from blackrose.policy import Policy
from blackrose.providers import (
    AsyncOpenAIDecisionsProvider,
    AsyncProvider,
    AsyncTypeSafeProvider,
    OpenAIDecisionsProvider,
    Provider,
    TypeSafeProvider,
    provider_name_from_env,
)
from blackrose.types import CheckResult

State = Any  # JSONContent: str | Mapping | Sequence


def _default_provider(api_key: str | None, model: str | None, client: Any) -> Provider:
    if client is not None or provider_name_from_env() == "typesafe":
        return TypeSafeProvider(api_key=api_key, model=model, client=client)
    return OpenAIDecisionsProvider(model=model)


def _default_async_provider(api_key: str | None, model: str | None, client: Any) -> AsyncProvider:
    if client is not None or provider_name_from_env() == "typesafe":
        return AsyncTypeSafeProvider(api_key=api_key, model=model, client=client)
    return AsyncOpenAIDecisionsProvider(model=model)


def _reject_mixed(provider: Any, api_key: str | None, model: str | None, client: Any) -> None:
    if provider is not None and (api_key is not None or model is not None or client is not None):
        raise ValueError("pass api_key/model/client to the provider, not alongside provider=")


class Guard:
    """Synchronous decision layer.

    Uses ``provider`` if given; otherwise ``BLACKROSE_PROVIDER`` (default ``typesafe``).
    ``client`` is kept for backwards compatibility and wraps a TypeSafe client.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        policy: Policy | None = None,
        client: Any = None,
        provider: Provider | None = None,
    ) -> None:
        _reject_mixed(provider, api_key, model, client)
        self.policy = policy or Policy()
        self._owns_provider = provider is None
        self.provider: Provider = provider or _default_provider(api_key, model, client)

    def close(self) -> None:
        if self._owns_provider:
            self.provider.close()

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
        result = self.provider.decide(state, questions)
        return decide(
            result,
            self.policy.for_provider(self.provider.name),
            provider=self.provider.name,
            calibrated=self.provider.calibrated,
        )


class AsyncGuard:
    """Asynchronous decision layer (see ``Guard``)."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        policy: Policy | None = None,
        client: Any = None,
        provider: AsyncProvider | None = None,
    ) -> None:
        _reject_mixed(provider, api_key, model, client)
        self.policy = policy or Policy()
        self._owns_provider = provider is None
        self.provider: AsyncProvider = provider or _default_async_provider(api_key, model, client)

    async def aclose(self) -> None:
        if self._owns_provider:
            await self.provider.aclose()

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
        result = await self.provider.decide(state, questions)
        return decide(
            result,
            self.policy.for_provider(self.provider.name),
            provider=self.provider.name,
            calibrated=self.provider.calibrated,
        )
