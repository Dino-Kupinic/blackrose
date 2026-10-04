"""Core result types for Blackrose guardrail checks."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

Verdict = Literal["allow", "review", "block"]


@dataclass(frozen=True)
class CheckResult:
    """Outcome of a single input or output guardrail check.

    Attributes:
        verdict: Application decision — allow, review, or block.
        reasons: Human-readable triggers that produced the verdict.
        scores: Named probabilities / scores from the provider's answers.
        raw: Untyped snapshot of the underlying provider response (or mock).
        provider: Name of the provider that answered (``typesafe``, ``openai``, …).
        calibrated: Whether that provider claims outcome-verified calibration.
            ``False`` means probabilities are model-reported estimates.
    """

    verdict: Verdict
    reasons: list[str] = field(default_factory=list)
    scores: Mapping[str, float] = field(default_factory=dict)
    raw: Any = None
    provider: str | None = None
    calibrated: bool | None = None
