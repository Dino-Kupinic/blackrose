"""Normalized answers: the only shape ``decide`` reads, whatever the provider."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

AnswerKind = Literal["binary", "scale", "choice"]


@dataclass(frozen=True)
class Answer:
    """One provider answer, normalized.

    Attributes:
        kind: ``binary`` (yes/no), ``scale`` (ordered rubric) or ``choice`` (closed set).
        value: Probability of yes for binary, expected score for scale, winning
            option's probability for choice.
        confidence: Provider-reported confidence (scale / choice), if any.
        choice: Winning option label (choice only).
        probabilities: Per-option / per-level probabilities, if the provider returns them.
    """

    kind: AnswerKind
    value: float
    confidence: float | None = None
    choice: str | None = None
    probabilities: Mapping[str, float] | None = None


@dataclass(frozen=True)
class ProviderResult:
    """What a provider returns: normalized answers plus the untouched response."""

    answers: Mapping[str, Answer]
    raw: Any = None


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


def _float_map(value: Any) -> dict[str, float] | None:
    if not isinstance(value, Mapping):
        return None
    out: dict[str, float] = {}
    for key, prob in value.items():
        p = _as_float(prob)
        if p is not None:
            out[str(key)] = p
    return out


def _answers_view(raw: Any) -> Mapping[str, Any]:
    """Find the name → answer mapping in a response, wrapper or flat mock."""
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


def normalize_answer(answer: Any) -> Answer | None:
    """Coerce one answer (``Answer``, dict or SDK object) into an ``Answer``.

    Recognizes ``noul`` / ``score`` / ``choice`` fields (the TypeSafe shape) and
    ``kind`` + ``value`` (the neutral shape). Returns ``None`` if nothing matches.
    """
    if isinstance(answer, Answer):
        return answer

    confidence = _as_float(_attr(answer, "confidence"))
    probabilities = _float_map(_attr(answer, "probabilities"))

    kind = _attr(answer, "kind")
    value = _as_float(_attr(answer, "value"))
    if kind in ("binary", "scale", "choice") and value is not None:
        choice = _attr(answer, "choice")
        return Answer(
            kind=kind,
            value=value,
            confidence=confidence,
            choice=None if choice is None else str(choice),
            probabilities=probabilities,
        )

    noul = _as_float(_attr(answer, "noul"))
    if noul is not None:
        return Answer(kind="binary", value=noul)

    score = _as_float(_attr(answer, "score"))
    if score is not None:
        return Answer(kind="scale", value=score, confidence=confidence, probabilities=probabilities)

    choice = _attr(answer, "choice")
    if choice is not None:
        label = str(choice)
        p = probabilities.get(label) if probabilities else None
        return Answer(
            kind="choice",
            value=p if p is not None else (confidence if confidence is not None else 0.0),
            confidence=confidence,
            choice=label,
            probabilities=probabilities,
        )
    return None


def normalize_answers(raw: Any) -> dict[str, Answer]:
    """Coerce a provider response (or mock) into ``{name: Answer}``.

    Answers that cannot be recognized are dropped.
    """
    if isinstance(raw, ProviderResult):
        return dict(raw.answers)
    out: dict[str, Answer] = {}
    for name, answer in _answers_view(raw).items():
        normalized = normalize_answer(answer)
        if normalized is not None:
            out[name] = normalized
    return out
