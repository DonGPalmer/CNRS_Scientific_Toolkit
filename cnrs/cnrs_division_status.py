"""
cnrs.cnrs_division_status
=========================

Theory-aligned division classification for CNRS-A.

This module does not claim finite field closure of CNRS-A digit strings.  It
classifies Gaussian-rational division into the cases used in the main CNRS
architecture paper and wraps the existing exact ``cnrs_rational`` expansion
machinery when an explicit expansion is requested.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import gcd
from typing import Any

from .cnrs_rational import gaussian_rational_to_cnrs, CnrsRational

Z0_PAIR = (-2, 1)


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
        return self.kind in {DivisionKind.GAUSSIAN_INTEGER, DivisionKind.TERMINATING_Z0_POWER}

    @property
    def has_periodic_tail(self) -> bool:
        return self.kind in {DivisionKind.EVENTUALLY_PERIODIC, DivisionKind.SHIFTED_EVENTUALLY_PERIODIC}


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
    g = gcd(gcd(abs(A), abs(B)), abs(q))
    if g > 1:
        return A // g, B // g, q // g
    return A, B, q


def classify_division(numerator: complex | int, denominator: int = 1) -> DivisionClassification:
    """Classify a Gaussian rational numerator / integer denominator.

    The current public API covers the same denominator convention as
    ``gaussian_rational_to_cnrs``: Gaussian-integer numerator over ordinary
    integer denominator.  Integer denominators divisible by 5 correspond to a
    finite ``z0``-power shift followed by a coprime periodic problem.
    """

    A, B = _as_gaussian_int(numerator)
    A, B, q = _reduce(A, B, int(denominator))
    reduced = complex(A, B)
    if q == 1:
        return DivisionClassification(complex(numerator), int(denominator), reduced, q, DivisionKind.GAUSSIAN_INTEGER, 0, "Reduced denominator is 1.")

    shift = 0
    qq = q
    while qq % 5 == 0:
        shift += 1
        qq //= 5

    if qq == 1:
        return DivisionClassification(complex(numerator), int(denominator), reduced, q, DivisionKind.TERMINATING_Z0_POWER, shift, "Integer denominator is a power of 5 = z0*z0bar; represented by finite z0/Laurent shift in existing rational layer.")
    if shift:
        return DivisionClassification(complex(numerator), int(denominator), reduced, q, DivisionKind.SHIFTED_EVENTUALLY_PERIODIC, shift, "Power-of-5 factor gives a finite shift; coprime remainder gives periodic tail.")
    return DivisionClassification(complex(numerator), int(denominator), reduced, q, DivisionKind.EVENTUALLY_PERIODIC, 0, "Reduced denominator is coprime to 5; expansion has an eventually periodic z0-adic tail.")


def division_expansion(numerator: complex | int, denominator: int = 1, *, max_frac: int = 200) -> CnrsDivisionExpansion:
    """Return theory classification plus the exact existing CNRS rational expansion."""
    classification = classify_division(numerator, denominator)
    expansion = gaussian_rational_to_cnrs(numerator, denominator, max_frac=max_frac)
    return CnrsDivisionExpansion(classification, expansion)


__all__ = [
    "DivisionKind",
    "DivisionClassification",
    "CnrsDivisionExpansion",
    "classify_division",
    "division_expansion",
]
