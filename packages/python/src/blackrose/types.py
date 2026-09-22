"""Core result types for Blackrose guardrail checks."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

Verdict = Literal["allow", "review", "block"]


@dataclass(frozen=True)
class Trigger:
    """Structured reason a check contributed to the verdict.

    ``code`` is stable for programmatic branching (e.g. ``noul_block``).
    ``message`` is the human-readable string also stored on ``CheckResult.reasons``.
    """

    code: str
    check: str | None = None
    message: str = ""

    def qualified(self) -> str:
        return f"{self.code}:{self.check}" if self.check else self.code


@dataclass(frozen=True)
class CheckResult:
    """Outcome of a single input or output guardrail check.

    Attributes:
        verdict: Application decision — allow, review, or block.
        reasons: Human-readable triggers that produced the verdict.
        scores: Named probabilities / scores from TypeSafe answers.
        raw: Untyped snapshot of the underlying TypeSafe response (or mock).
        triggers: Structured codes for the same events as ``reasons``.
        codes: Qualified trigger codes (``code`` or ``code:check``).
    """

    verdict: Verdict
    reasons: list[str] = field(default_factory=list)
    scores: Mapping[str, float] = field(default_factory=dict)
    raw: Any = None
    triggers: tuple[Trigger, ...] = ()
    codes: tuple[str, ...] = ()
