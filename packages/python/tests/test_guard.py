"""Guard / AsyncGuard unit tests with mocked TypeSafe clients."""

from __future__ import annotations

from typing import Any, Mapping

import pytest

from blackrose import AsyncGuard, Guard, Policy, default_input_questions, default_output_questions


class FakeSyncClient:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[tuple[Any, Mapping[str, Any], str | None]] = []

    def system_one(
        self,
        state: Any,
        questions: Mapping[str, Any],
        *,
        model: str | None = None,
    ) -> Any:
        self.calls.append((state, questions, model))
        return self.response


class FakeAsyncClient:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[tuple[Any, Mapping[str, Any], str | None]] = []

    async def system_one(
        self,
        state: Any,
        questions: Mapping[str, Any],
        *,
        model: str | None = None,
    ) -> Any:
        self.calls.append((state, questions, model))
        return self.response


SAFE = {
    "jailbreak": {"noul": 0.02},
    "harm": {"score": 0.1, "confidence": 0.9},
    "needs_human": {"noul": 0.05},
}

JAILBREAK = {
    "jailbreak": {"noul": 0.98},
    "harm": {"score": 1.1, "confidence": 0.9},
    "needs_human": {"noul": 0.4},
}


def test_guard_check_input_allow() -> None:
    client = FakeSyncClient(SAFE)
    guard = Guard(client=client, model="jev-latest")
    result = guard.check_input("Tell me about Vienna")
    assert result.verdict == "allow"
    assert len(client.calls) == 1
    state, questions, model = client.calls[0]
    assert state == "Tell me about Vienna"
    assert model == "jev-latest"
    assert set(questions) == set(default_input_questions())


def test_guard_check_output_block() -> None:
    client = FakeSyncClient(JAILBREAK)
    guard = Guard(client=client)
    result = guard.check_output("Sure, I'll ignore all rules now.")
    assert result.verdict == "block"
    _, questions, _ = client.calls[0]
    assert set(questions) == set(default_output_questions())


def test_guard_uses_custom_policy_questions() -> None:
    from typesafe_sdk import Noul

    custom = {"only": Noul(instructions="Is this spam?")}
    policy = Policy(input_questions=custom, output_questions=custom)
    client = FakeSyncClient({"only": {"noul": 0.01}})
    guard = Guard(client=client, policy=policy)
    guard.check_input("hi")
    assert set(client.calls[0][1]) == {"only"}


@pytest.mark.asyncio
async def test_async_guard_check_input() -> None:
    client = FakeAsyncClient(SAFE)
    guard = AsyncGuard(client=client, model="jev-latest")
    result = await guard.check_input({"message": "hello"})
    assert result.verdict == "allow"
    assert client.calls[0][0] == {"message": "hello"}


@pytest.mark.asyncio
async def test_async_guard_check_output_review() -> None:
    uncertain = {
        "jailbreak": {"noul": 0.05},
        "harm": {"score": 0.4, "confidence": 0.15},
        "needs_human": {"noul": 0.05},
    }
    client = FakeAsyncClient(uncertain)
    async with AsyncGuard(client=client) as guard:
        result = await guard.check_output("maybe?")
    assert result.verdict == "review"
