"""Typed errors for the Blackrose decision layer."""

from __future__ import annotations


class BlackroseError(Exception):
    """Base error for the Blackrose decision layer."""


class PolicyConfigError(BlackroseError, ValueError):
    """Invalid Policy thresholds or check configuration."""


class GuardClosedError(BlackroseError):
    """``check_input`` / ``check_output`` called after ``close()`` / ``aclose()``."""


class TypeSafeRequestError(BlackroseError):
    """TypeSafe ``system_one`` call failed.

    Callers must fail closed: do not treat this as ``allow`` or proceed with
    generation. Catching the error and continuing is fail-open.
    """
