"""Map normalized provider answers onto CheckResult verdicts.

Vendor-neutral: reads only ``Answer`` objects (or shapes ``normalize_answers`` accepts).
"""

from __future__ import annotations

from typing import Any

from blackrose.answers import Answer, ProviderResult, normalize_answers
from blackrose.policy import Policy
from blackrose.types import CheckResult, Verdict

_PRECEDENCE: tuple[Verdict, ...] = ("block", "review", "allow")


def _score_of(answer: Answer) -> float | None:
    if answer.kind == "choice":
        # Only report a choice when the provider gave the winning option's probability.
        if answer.probabilities is None or answer.choice not in answer.probabilities:
            return None
    return answer.value


def extract_scores(raw: Any) -> dict[str, float]:
    """Pull named numeric signals from a provider result, response or mock dict."""
    scores: dict[str, float] = {}
    for name, answer in normalize_answers(raw).items():
        value = _score_of(answer)
        if value is not None:
            scores[name] = value
    return scores


def decide(
    raw: Any,
    policy: Policy,
    *,
    provider: str | None = None,
    calibrated: bool | None = None,
) -> CheckResult:
    """Apply policy thresholds to provider answers.

    Precedence: any ``block`` wins over ``review``; otherwise ``allow``.
    Low scale/choice confidence always contributes ``review``.
    """
    answers = normalize_answers(raw)
    scores = {name: value for name, a in answers.items() if (value := _score_of(a)) is not None}
    reasons: list[str] = []
    triggered: set[Verdict] = set()

    for name, answer in answers.items():
        if answer.kind == "binary":
            p = answer.value
            if p >= policy.block_threshold and name in policy.block_checks:
                triggered.add("block")
                reasons.append(f"{name}={p:.2f} >= block_threshold ({policy.block_threshold})")
            elif p >= policy.review_threshold:
                triggered.add("review")
                reasons.append(f"{name}={p:.2f} >= review_threshold ({policy.review_threshold})")
            continue

        # Scale and choice: low confidence → review; never silent allow on uncertainty
        confidence = answer.confidence
        if confidence is not None and confidence < policy.min_confidence:
            triggered.add("review")
            reasons.append(
                f"{name} confidence={confidence:.2f} < min_confidence ({policy.min_confidence})"
            )

        if answer.kind == "scale":
            score = answer.value
            if score >= policy.harm_block_score:
                triggered.add("block")
                reasons.append(
                    f"{name}={score:.2f} >= harm_block_score ({policy.harm_block_score})"
                )
            elif score >= policy.harm_review_score:
                triggered.add("review")
                reasons.append(
                    f"{name}={score:.2f} >= harm_review_score ({policy.harm_review_score})"
                )

    verdict: Verdict = next((v for v in _PRECEDENCE if v in triggered), "allow")
    return CheckResult(
        verdict=verdict,
        reasons=reasons,
        scores=scores,
        raw=raw.raw if isinstance(raw, ProviderResult) else raw,
        provider=provider,
        calibrated=calibrated,
    )
