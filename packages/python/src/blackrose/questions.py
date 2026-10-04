"""Provider-neutral question types.

Policies describe checks with these types; each provider translates them into its own
native question format (for example TypeSafe ``Noul`` / ``Score`` / ``Choice``).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Binary:
    """Yes/no question answered with the probability of *yes* (TypeSafe ``Noul``)."""

    instructions: str
    yes: str | None = None
    """Optional description of the yes outcome."""
    no: str | None = None
    """Optional description of the no outcome."""


@dataclass(frozen=True)
class Scale:
    """Ordered rubric answered with an expected score (TypeSafe ``Score``).

    ``criteria[i]`` describes score ``i``; at least two levels are required.
    """

    instructions: str
    criteria: Sequence[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "criteria", tuple(self.criteria))
        if len(self.criteria) < 2:
            raise ValueError("Scale needs at least two criteria (one per score from zero)")


@dataclass(frozen=True)
class Choice:
    """Closed set of options answered with per-option probabilities (TypeSafe ``Choice``)."""

    instructions: str
    options: Mapping[str, str | None] = field(default_factory=dict)
    """Option labels mapped to optional descriptions."""

    def __post_init__(self) -> None:
        object.__setattr__(self, "options", dict(self.options))
        if len(self.options) < 2:
            raise ValueError("Choice needs at least two options")


Question = Binary | Scale | Choice
NEUTRAL_QUESTION_TYPES = (Binary, Scale, Choice)
