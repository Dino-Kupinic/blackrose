"""Provider protocols: the seam between Blackrose policy and a decision model."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from blackrose.answers import ProviderResult
from blackrose.questions import Question

State = Any  # JSON-compatible: str | Mapping | Sequence | number | bool | None


class ProviderError(RuntimeError):
    """A provider is misconfigured or cannot be used yet."""


@runtime_checkable
class Provider(Protocol):
    """Synchronous decision-model backend.

    Attributes:
        name: Short identifier (``typesafe``, ``openai``) used for policy overrides.
        calibrated: ``True`` if the provider claims outcome-verified calibration.
    """

    name: str
    calibrated: bool

    def decide(self, state: State, questions: Mapping[str, Question]) -> ProviderResult: ...

    def close(self) -> None: ...


@runtime_checkable
class AsyncProvider(Protocol):
    """Asynchronous decision-model backend (see ``Provider``)."""

    name: str
    calibrated: bool

    async def decide(self, state: State, questions: Mapping[str, Question]) -> ProviderResult: ...

    async def aclose(self) -> None: ...
