"""Legacy compatibility API for CNRS-A division classification.

The authoritative theorem-aligned implementation is :mod:`cnrs.division`.
This module remains available for compatibility with v0.8.x callers, but its
classification now delegates to ``cnrs.division.classify_denominator``.

Since ``5 = beta * conjugate(beta)`` for ``beta = -2+i``, a denominator
``5**s`` does not imply termination by itself.  Termination requires the
numerator to cancel ``conjugate(beta)**s`` after reduction.  In particular,
``1/5`` and ``1/25`` are shifted eventually periodic, while
``conjugate(beta)/5 = 1/beta`` terminates.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import gcd
from typing import Any
import warnings

from .cnrs_rational import CnrsRational, gaussian_rational_to_cnrs
from .division import DivisionStatus, classify_denominator


class DivisionKind(str, Enum):
    GAUSSIAN_INTEGER = "gaussian_integer"
    TERMINATING_Z0_POWER = "terminating_z0_power"
    EVENTUALLY_PERIODIC = "eventually_periodic"
    SHIFTED_EVENTUALLY_PERIODIC = "shifted_eventually_periodic"


@dataclass(frozen=True)
class DivisionClassification:
    numerator: complex
    denominator: int
    reduced_numerator: complex
    reduced_denominator: int
    kind: DivisionKind
    z0_power_shift: int = 0
    note: str = ""

    @property
    def terminates(self) -> bool:
        return self.kind in {
            DivisionKind.GAUSSIAN_INTEGER,
            DivisionKind.TERMINATING_Z0_POWER,
        }

    @property
    def has_periodic_tail(self) -> bool:
        return self.kind in {
            DivisionKind.EVENTUALLY_PERIODIC,
            DivisionKind.SHIFTED_EVENTUALLY_PERIODIC,
        }


@dataclass(frozen=True)
class CnrsDivisionExpansion:
    classification: DivisionClassification
    expansion: CnrsRational

    @property
    def prefix(self) -> list[int]:
        if self.expansion.period_start is None:
            return list(self.expansion.frac_digits)
        return list(self.expansion.frac_digits[: self.expansion.period_start])

    @property
    def period(self) -> list[int]:
        if self.expansion.period_start is None:
            return []
        return list(self.expansion.frac_digits[self.expansion.period_start :])

    @property
    def period_length(self) -> int | None:
        return self.expansion.period_length

    def to_str_with_period(self) -> str:
        return self.expansion.to_str_with_period()


def _as_gaussian_int(z: complex | int) -> tuple[int, int]:
    c = complex(z)
    a, b = round(c.real), round(c.imag)
    if abs(c.real - a) > 1e-9 or abs(c.imag - b) > 1e-9:
        raise ValueError(f"{z!r} is not a Gaussian integer")
    return int(a), int(b)


def _reduce(A: int, B: int, q: int) -> tuple[int, int, int]:
    if q == 0:
        raise ZeroDivisionError("denominator cannot be zero")
    if q < 0:
        A, B, q = -A, -B, -q
    g = gcd(gcd(abs(A), abs(B)), abs(q)) or 1
    return A // g, B // g, q // g


_STATUS_MAP = {
    DivisionStatus.GAUSSIAN_INTEGER: DivisionKind.GAUSSIAN_INTEGER,
    DivisionStatus.TERMINATING_BASE_POWER: DivisionKind.TERMINATING_Z0_POWER,
    DivisionStatus.PERIODIC_COPRIME_DENOMINATOR: DivisionKind.EVENTUALLY_PERIODIC,
    DivisionStatus.SHIFTED_PERIODIC_TAIL: DivisionKind.SHIFTED_EVENTUALLY_PERIODIC,
}

_STATUS_NOTES = {
    DivisionStatus.GAUSSIAN_INTEGER:
        "Reduced denominator is 1.",
    DivisionStatus.TERMINATING_BASE_POWER:
        "The reduced numerator cancels the required conjugate-base factor; "
        "the remaining denominator is a pure beta power.",
    DivisionStatus.PERIODIC_COPRIME_DENOMINATOR:
        "Reduced denominator is coprime to 5; the expansion has an eventually "
        "periodic beta-adic tail.",
    DivisionStatus.SHIFTED_PERIODIC_TAIL:
        "A beta-power shift is present, but an uncancelled denominator factor "
        "forces an eventually periodic tail.",
}


def classify_division(
    numerator: complex | int,
    denominator: int = 1,
) -> DivisionClassification:
    """Classify a Gaussian rational over an ordinary integer denominator.

    Deprecated compatibility wrapper.  New code should call
    :func:`cnrs.division.classify_denominator` directly.
    """
    warnings.warn(
        "cnrs.cnrs_division_status.classify_division is deprecated; use "
        "cnrs.division.classify_denominator instead",
        DeprecationWarning,
        stacklevel=2,
    )

    A, B = _as_gaussian_int(numerator)
    reduced_A, reduced_B, reduced_q = _reduce(A, B, int(denominator))
    authoritative = classify_denominator((A, B), int(denominator))

    return DivisionClassification(
        numerator=complex(numerator),
        denominator=int(denominator),
        reduced_numerator=complex(reduced_A, reduced_B),
        reduced_denominator=reduced_q,
        kind=_STATUS_MAP[authoritative.status],
        z0_power_shift=authoritative.base_power_exponent,
        note=_STATUS_NOTES[authoritative.status],
    )


def division_expansion(
    numerator: complex | int,
    denominator: int = 1,
    *,
    max_frac: int = 200,
) -> CnrsDivisionExpansion:
    """Return compatibility classification plus the exact rational expansion."""
    classification = classify_division(numerator, denominator)
    expansion = gaussian_rational_to_cnrs(
        numerator,
        denominator,
        max_frac=max_frac,
    )
    return CnrsDivisionExpansion(classification, expansion)


__all__ = [
    "DivisionKind",
    "DivisionClassification",
    "CnrsDivisionExpansion",
    "classify_division",
    "division_expansion",
]
