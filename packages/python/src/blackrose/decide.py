"""Map TypeSafe System One answers onto CheckResult verdicts."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any

from blackrose.policy import Policy
from blackrose.types import CheckResult, Trigger, Verdict

_PRECEDENCE: tuple[Verdict, ...] = ("block", "review", "allow")


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _has_field(obj: Any, name: str) -> bool:
    if obj is None:
        return False
    if isinstance(obj, Mapping):
        return name in obj
    return hasattr(obj, name)


def _as_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _is_answer_like(value: Any) -> bool:
    if value is None or isinstance(value, (str, int, float, bool)):
        return False
    return _has_field(value, "noul") or _has_field(value, "score") or _has_field(value, "choice")


def answers_view(raw: Any) -> Mapping[str, Any]:
    """Normalize SDK response / mock into a name → answer mapping."""
    if raw is None:
        return {}
    if _has_field(raw, "answers"):
        answers = _attr(raw, "answers")
        return answers if isinstance(answers, Mapping) else {}

    combined: dict[str, Any] = {}
    for bucket in ("nouls", "scores", "choices"):
        group = _attr(raw, bucket)
        if isinstance(group, Mapping):
            combined.update(group)
    if combined:
        return combined

    if isinstance(raw, Mapping):
        filtered = {name: value for name, value in raw.items() if _is_answer_like(value)}
        return filtered
    return {}


def extract_scores(raw: Any) -> dict[str, float]:
    """Pull named numeric signals from a TypeSafe response or mock dict."""
    scores: dict[str, float] = {}
    for name, answer in answers_view(raw).items():
        noul = _as_float(_attr(answer, "noul"))
        if noul is not None:
            scores[name] = noul
            continue
        score = _as_float(_attr(answer, "score"))
        if score is not None:
            scores[name] = score
            continue
        choice = _attr(answer, "choice")
        probs = _attr(answer, "probabilities")
        if choice is not None and isinstance(probs, Mapping):
            p = _as_float(probs.get(choice))
            if p is not None:
                scores[name] = p
    return scores


def _qualified(trigger: Trigger) -> str:
    return trigger.qualified()


def _low_confidence_trigger(
    name: str,
    confidence: float | None,
    *,
    missing: bool,
    min_confidence: float,
) -> Trigger:
    if missing:
        message = f"{name} confidence missing (< min_confidence {min_confidence})"
    else:
        value = 0.0 if confidence is None else confidence
        message = f"{name} confidence={value:.2f} < min_confidence ({min_confidence})"
    return Trigger(code="low_confidence", check=name, message=message)


def decide(
    raw: Any,
    policy: Policy,
    *,
    expected_checks: Iterable[str] | None = None,
) -> CheckResult:
    """Apply policy thresholds to TypeSafe answers.

    Precedence: any ``block`` wins over ``review``; otherwise ``allow``.
    Missing expected checks, empty responses, and low/missing Score/Choice
    confidence contribute ``review`` (never silent ``allow``).
    """
    answers = answers_view(raw)
    scores = extract_scores(raw)
    triggers: list[Trigger] = []
    triggered: set[Verdict] = set()

    expected = list(expected_checks) if expected_checks is not None else None
    if expected is not None:
        for name in expected:
            if name not in answers:
                triggered.add("review")
                triggers.append(
                    Trigger(
                        code="missing_check",
                        check=name,
                        message=f"{name} missing from TypeSafe response",
                    )
                )
        if not expected and not answers:
            triggered.add("review")
            triggers.append(
                Trigger(
                    code="empty_response",
                    check=None,
                    message="TypeSafe response contained no answers",
                )
            )
    elif not answers:
        triggered.add("review")
        triggers.append(
            Trigger(
                code="empty_response",
                check=None,
                message="TypeSafe response contained no answers",
            )
        )

    for name, answer in answers.items():
        noul = _as_float(_attr(answer, "noul")) if _has_field(answer, "noul") else None
        if _has_field(answer, "noul"):
            if noul is not None:
                if noul >= policy.block_threshold and name in policy.block_checks:
                    triggered.add("block")
                    triggers.append(
                        Trigger(
                            code="noul_block",
                            check=name,
                            message=(
                                f"{name}={noul:.2f} >= block_threshold ({policy.block_threshold})"
                            ),
                        )
                    )
                elif noul >= policy.review_threshold:
                    triggered.add("review")
                    triggers.append(
                        Trigger(
                            code="noul_review",
                            check=name,
                            message=(
                                f"{name}={noul:.2f} >= review_threshold ({policy.review_threshold})"
                            ),
                        )
                    )
            if _has_field(answer, "confidence"):
                confidence = _as_float(_attr(answer, "confidence"))
                if confidence is not None and confidence < policy.min_confidence:
                    triggered.add("review")
                    triggers.append(
                        _low_confidence_trigger(
                            name,
                            confidence,
                            missing=False,
                            min_confidence=policy.min_confidence,
                        )
                    )
            continue

        if _has_field(answer, "score"):
            score = _as_float(_attr(answer, "score"))
            confidence = _as_float(_attr(answer, "confidence"))
            missing_confidence = not _has_field(answer, "confidence") or confidence is None
            low_confidence = confidence is not None and confidence < policy.min_confidence
            if missing_confidence or low_confidence:
                triggered.add("review")
                triggers.append(
                    _low_confidence_trigger(
                        name,
                        confidence,
                        missing=missing_confidence,
                        min_confidence=policy.min_confidence,
                    )
                )
            cutoffs = policy.score_cutoffs(name)
            if score is not None and cutoffs is not None:
                if score >= cutoffs.block:
                    triggered.add("block")
                    triggers.append(
                        Trigger(
                            code="score_block",
                            check=name,
                            message=f"{name}={score:.2f} >= score_block ({cutoffs.block})",
                        )
                    )
                elif score >= cutoffs.review:
                    triggered.add("review")
                    triggers.append(
                        Trigger(
                            code="score_review",
                            check=name,
                            message=f"{name}={score:.2f} >= score_review ({cutoffs.review})",
                        )
                    )
            continue

        # Choice answers: low or missing confidence → review; no default block path.
        if _has_field(answer, "choice") or _has_field(answer, "confidence"):
            confidence = _as_float(_attr(answer, "confidence"))
            missing_confidence = not _has_field(answer, "confidence") or confidence is None
            low_confidence = confidence is not None and confidence < policy.min_confidence
            if missing_confidence or low_confidence:
                triggered.add("review")
                triggers.append(
                    _low_confidence_trigger(
                        name,
                        confidence,
                        missing=missing_confidence,
                        min_confidence=policy.min_confidence,
                    )
                )

    verdict: Verdict = next((v for v in _PRECEDENCE if v in triggered), "allow")
    return CheckResult(
        verdict=verdict,
        reasons=[t.message for t in triggers],
        scores=scores,
        raw=raw,
        triggers=tuple(triggers),
        codes=tuple(_qualified(t) for t in triggers),
    )
