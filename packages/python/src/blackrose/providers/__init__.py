"""Decision-model providers and env-based selection."""

from __future__ import annotations

import os

from blackrose.providers.base import AsyncProvider, Provider, ProviderError
from blackrose.providers.openai import AsyncOpenAIDecisionsProvider, OpenAIDecisionsProvider
from blackrose.providers.typesafe import AsyncTypeSafeProvider, TypeSafeProvider

PROVIDER_ENV = "BLACKROSE_PROVIDER"
_KNOWN = ("typesafe", "openai")


def provider_name_from_env() -> str:
    """Read ``BLACKROSE_PROVIDER`` (default ``typesafe``)."""
    name = os.environ.get(PROVIDER_ENV, "").strip().lower() or "typesafe"
    if name not in _KNOWN:
        raise ProviderError(f"{PROVIDER_ENV}={name!r} is not one of {', '.join(_KNOWN)}")
    return name


__all__ = [
    "PROVIDER_ENV",
    "AsyncOpenAIDecisionsProvider",
    "AsyncProvider",
    "AsyncTypeSafeProvider",
    "OpenAIDecisionsProvider",
    "Provider",
    "ProviderError",
    "TypeSafeProvider",
    "provider_name_from_env",
]
