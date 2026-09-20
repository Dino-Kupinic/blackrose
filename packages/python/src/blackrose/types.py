"""Core result types for Blackrose guardrail checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping

Verdict = Literal["allow", "review", "block"]


@dataclass(frozen=True)
class CheckResult:
    """Outcome of a single input or output guardrail check.

    Attributes:
        verdict: Application decision — allow, review, or block.
        reasons: Human-readable triggers that produced the verdict.
        scores: Named probabilities / scores from TypeSafe answers.
        raw: Untyped snapshot of the underlying TypeSafe response (or mock).
    """

    verdict: Verdict
    reasons: list[str] = field(default_factory=list)
    scores: Mapping[str, float] = field(default_factory=dict)
    raw: Any = None
