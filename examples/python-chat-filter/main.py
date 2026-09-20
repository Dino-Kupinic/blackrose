#!/usr/bin/env python3
"""Chat handler that decides before (and after) a fake streamed reply."""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Iterator

from blackrose import Guard


def require_api_key() -> str:
    key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not key:
        print(
            "Missing TYPESAFE_API_KEY.\n"
            "Set it in your environment (see repo .env.example), then re-run.\n"
            "Example: export TYPESAFE_API_KEY=ts_...",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return key


def fake_stream_reply(user_message: str) -> Iterator[str]:
    """Stand-in for an LLM stream. Replace with your provider's chunk iterator."""
    reply = (
        f"Thanks for your message. You asked about: {user_message[:120]!r}. "
        "Here is a short demo reply from a fake model."
    )
    for word in reply.split():
        yield word + " "
        time.sleep(0.03)


def handle_chat(user_message: str) -> None:
    api_key = require_api_key()
    with Guard(api_key=api_key) as guard:
        print(f"user> {user_message}")
        inbound = guard.check_input(user_message)
        print(f"input verdict: {inbound.verdict}")
        if inbound.reasons:
            print(f"  reasons: {inbound.reasons}")
        if inbound.scores:
            print(f"  scores:  {dict(inbound.scores)}")

        if inbound.verdict == "block":
            print("assistant> [blocked] I can't help with that request.")
            return
        if inbound.verdict == "review":
            print("note> input flagged for human review; demo still generates.")

        chunks: list[str] = []
        print("assistant> ", end="", flush=True)
        for chunk in fake_stream_reply(user_message):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        print()

        full_reply = "".join(chunks).strip()
        outbound = guard.check_output(full_reply)
        print(f"output verdict: {outbound.verdict}")
        if outbound.reasons:
            print(f"  reasons: {outbound.reasons}")
        if outbound.scores:
            print(f"  scores:  {dict(outbound.scores)}")

        if outbound.verdict == "block":
            print("note> reply withheld after output check.")
        elif outbound.verdict == "review":
            print("note> reply shown but queued for human review.")


def main(argv: list[str]) -> None:
    prompt = " ".join(argv[1:]).strip() or "What is the capital of Austria?"
    handle_chat(prompt)


if __name__ == "__main__":
    main(sys.argv)
