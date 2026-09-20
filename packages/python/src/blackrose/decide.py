"""Map TypeSafe System One answers onto CheckResult verdicts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from blackrose.policy import Policy
from blackrose.types import CheckResult, Verdict

_PRECEDENCE: tuple[Verdict, ...] = ("block", "review", "allow")


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _answers_view(raw: Any) -> Mapping[str, Any]:
    """Normalize SDK response / mock into a name → answer mapping."""
    if raw is None:
        return {}
    answers = _attr(raw, "answers")
    if isinstance(answers, Mapping):
        return answers

    combined: dict[str, Any] = {}
    for bucket in ("nouls", "scores", "choices"):
        group = _attr(raw, bucket)
        if isinstance(group, Mapping):
            combined.update(group)
    if combined:
        return combined

    if isinstance(raw, Mapping):
        # Flat mock: {"jailbreak": {"noul": 0.9}, "harm": {"score": 2.1, "confidence": 0.8}}
        return raw
    return {}


def extract_scores(raw: Any) -> dict[str, float]:
    """Pull named numeric signals from a TypeSafe response or mock dict."""
    scores: dict[str, float] = {}
    for name, answer in _answers_view(raw).items():
        noul = _as_float(_attr(answer, "noul"))
        if noul is not None:
            scores[name] = noul
            continue
        score = _as_float(_attr(answer, "score"))
        if score is not None:
            scores[name] = score
            continue
        # Choice: store winning probability when available
        choice = _attr(answer, "choice")
        probs = _attr(answer, "probabilities")
        if choice is not None and isinstance(probs, Mapping):
            p = _as_float(probs.get(choice))
            if p is not None:
                scores[name] = p
    return scores


def decide(raw: Any, policy: Policy) -> CheckResult:
    """Apply policy thresholds to TypeSafe answers.

    Precedence: any ``block`` wins over ``review``; otherwise ``allow``.
    Low Score/Choice confidence always contributes ``review``.
    """
    answers = _answers_view(raw)
    scores = extract_scores(raw)
    reasons: list[str] = []
    triggered: set[Verdict] = set()

    for name, answer in answers.items():
        noul = _as_float(_attr(answer, "noul"))
        if noul is not None:
            if noul >= policy.block_threshold and name in policy.block_checks:
                triggered.add("block")
                reasons.append(f"{name}={noul:.2f} >= block_threshold ({policy.block_threshold})")
            elif noul >= policy.review_threshold:
                triggered.add("review")
                reasons.append(f"{name}={noul:.2f} >= review_threshold ({policy.review_threshold})")
            continue

        score = _as_float(_attr(answer, "score"))
        confidence = _as_float(_attr(answer, "confidence"))
        if score is not None:
            if confidence is not None and confidence < policy.min_confidence:
                triggered.add("review")
                reasons.append(
                    f"{name} confidence={confidence:.2f} < min_confidence ({policy.min_confidence})"
                )
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
            continue

        # Choice answers: low confidence → review; never silent allow on uncertainty
        confidence = _as_float(_attr(answer, "confidence"))
        if confidence is not None and confidence < policy.min_confidence:
            triggered.add("review")
            reasons.append(
                f"{name} confidence={confidence:.2f} < min_confidence ({policy.min_confidence})"
            )

    verdict: Verdict = next((v for v in _PRECEDENCE if v in triggered), "allow")
    return CheckResult(verdict=verdict, reasons=reasons, scores=scores, raw=raw)
