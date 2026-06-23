"""
cnrs.division
=============

Theory-aligned CNRS-A division classification utilities.

This module does not claim finite-string field closure for CNRS-A.  It wraps
and classifies the existing exact rational expansion machinery in
``cnrs_rational`` according to the theoretical division trichotomy:

  1. Gaussian-integer quotient.
  2. Terminating denominator that is a pure power of the CNRS base factor.
  3. Eventually periodic persistent denominator.
  4. Shifted periodic tail when base-power factors and persistent factors mix.

For ordinary integer denominators, powers of the complex base ``z0`` enter as
powers of its norm ``N(z0)=5``.  The implementation therefore distinguishes
pure powers of five from denominators that have a residual factor coprime to
five.  The expansion itself is delegated to ``gaussian_rational_to_cnrs``,
which stores finite, z0-adic periodic, and Laurent-periodic outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import gcd
from typing import Optional

from .cnrs_rational import CnrsRational, gaussian_rational_to_cnrs


class DivisionStatus(str, Enum):
    """Theory-level status of a CNRS-A rational division expansion."""

    GAUSSIAN_INTEGER = "gaussian_integer"
    TERMINATING_BASE_POWER = "terminating_base_power"
    PERIODIC_COPRIME_DENOMINATOR = "periodic_coprime_denominator"
    SHIFTED_PERIODIC_TAIL = "shifted_periodic_tail"


@dataclass(frozen=True)
class DenominatorClassification:
    """Reduced-denominator classification for integer-denominator rationals."""

    numerator_real: int
    numerator_imag: int
    denominator: int
    reduced_denominator: int
    base_power_exponent: int
    persistent_denominator: int
    status: DivisionStatus

    @property
    def terminates(self) -> bool:
        return self.status in {
            DivisionStatus.GAUSSIAN_INTEGER,
            DivisionStatus.TERMINATING_BASE_POWER,
        }

    @property
    def has_periodic_tail(self) -> bool:
        return self.status in {
            DivisionStatus.PERIODIC_COPRIME_DENOMINATOR,
            DivisionStatus.SHIFTED_PERIODIC_TAIL,
        }


@dataclass(frozen=True)
class CnrsDivisionExpansion:
    """Structured division result with theory classification and expansion."""

    classification: DenominatorClassification
    expansion: CnrsRational

    @property
    def status(self) -> DivisionStatus:
        return self.classification.status

    @property
    def terminates(self) -> bool:
        return self.classification.terminates

    @property
    def period_start(self) -> Optional[int]:
        return self.expansion.period_start

    @property
    def period_length(self) -> Optional[int]:
        return self.expansion.period_length

    @property
    def prefix_digits(self) -> list[int]:
        if self.expansion.period_start is None:
            return list(self.expansion.frac_digits)
        return list(self.expansion.frac_digits[: self.expansion.period_start])

    @property
    def period_digits(self) -> list[int]:
        if self.expansion.period_start is None:
            return []
        return list(self.expansion.frac_digits[self.expansion.period_start :])

    @property
    def shifted_by_base_power(self) -> bool:
        """Whether a finite base-power denominator shift occurs before the tail."""
        return self.classification.base_power_exponent > 0

    @property
    def persistent_denominator(self) -> int:
        """Reduced denominator factor not removed by powers of N(z0)=5."""
        return self.classification.persistent_denominator

    @property
    def preperiod_length(self) -> int:
        """Length of the non-repeating fractional prefix currently detected."""
        return 0 if self.period_start is None else int(self.period_start)

    @property
    def tail_kind(self) -> str:
        """Human-readable tail classification for reports and tests."""
        if self.status == DivisionStatus.GAUSSIAN_INTEGER:
            return "finite_gaussian_integer"
        if self.status == DivisionStatus.TERMINATING_BASE_POWER:
            return "finite_base_power_shift"
        if self.status == DivisionStatus.PERIODIC_COPRIME_DENOMINATOR:
            return "eventually_periodic"
        return "shifted_eventually_periodic"

    def structured_digits(self) -> dict[str, object]:
        """Return prefix/period metadata without implying finite-string closure."""
        return {
            "status": self.status.value,
            "terminates": self.terminates,
            "power_offset": self.expansion.power_offset,
            "prefix_digits": self.prefix_digits,
            "period_digits": self.period_digits,
            "period_start": self.period_start,
            "period_length": self.period_length,
            "tail_kind": self.tail_kind,
        }

    def to_str_with_period(self) -> str:
        return self.expansion.to_str_with_period()

    def exact_value(self) -> complex:
        return self.expansion.exact_value()

    def round_trip_ok(self, tol: float = 1e-10) -> bool:
        return self.expansion.round_trip_ok(tol=tol)


def _as_gaussian_integer_parts(numerator: complex | int | tuple[int, int]) -> tuple[int, int]:
    if isinstance(numerator, tuple):
        return int(numerator[0]), int(numerator[1])
    z = complex(numerator)
    return int(round(z.real)), int(round(z.imag))


def _reduce_denominator(A: int, B: int, q: int) -> int:
    g = gcd(gcd(abs(A), abs(B)), abs(q))
    return abs(q) // (g if g else 1)


def _factor_five(q: int) -> tuple[int, int]:
    """Return (v5(q), q_without_factors_of_5)."""
    q = abs(q)
    exponent = 0
    while q and q % 5 == 0:
        q //= 5
        exponent += 1
    return exponent, q


def classify_denominator(
    numerator: complex | int | tuple[int, int],
    denominator: int = 1,
) -> DenominatorClassification:
    """Classify the reduced integer denominator for a Gaussian rational.

    This function is intentionally conservative and theory-facing: it classifies
    the denominator structure before constructing any expansion.
    """
    if denominator == 0:
        raise ZeroDivisionError("denominator must be nonzero")
    if denominator < 0:
        denominator = -denominator
        if isinstance(numerator, tuple):
            numerator = (-int(numerator[0]), -int(numerator[1]))
        else:
            numerator = -complex(numerator)

    A, B = _as_gaussian_integer_parts(numerator)
    q = _reduce_denominator(A, B, denominator)
    v5, persistent = _factor_five(q)

    if q == 1:
        status = DivisionStatus.GAUSSIAN_INTEGER
    elif persistent == 1:
        status = DivisionStatus.TERMINATING_BASE_POWER
    elif v5 == 0:
        status = DivisionStatus.PERIODIC_COPRIME_DENOMINATOR
    else:
        status = DivisionStatus.SHIFTED_PERIODIC_TAIL

    return DenominatorClassification(
        numerator_real=A,
        numerator_imag=B,
        denominator=denominator,
        reduced_denominator=q,
        base_power_exponent=v5,
        persistent_denominator=persistent,
        status=status,
    )


def expand_division(
    numerator: complex | int | tuple[int, int],
    denominator: int = 1,
    *,
    max_frac: int = 500,
) -> CnrsDivisionExpansion:
    """Return a theory-classified CNRS rational division expansion."""
    classification = classify_denominator(numerator, denominator)
    expansion = gaussian_rational_to_cnrs(numerator, denominator, max_frac=max_frac)
    return CnrsDivisionExpansion(classification=classification, expansion=expansion)


def terminating_expansion(
    numerator: complex | int | tuple[int, int],
    denominator: int = 1,
    *,
    max_frac: int = 500,
) -> CnrsDivisionExpansion:
    """Return a terminating expansion or raise ``ValueError`` if it is periodic."""
    result = expand_division(numerator, denominator, max_frac=max_frac)
    if not result.terminates:
        raise ValueError(f"division does not terminate: status={result.status.value}")
    return result


def periodic_expansion(
    numerator: complex | int | tuple[int, int],
    denominator: int,
    *,
    max_frac: int = 500,
) -> CnrsDivisionExpansion:
    """Return a periodic/shifted-periodic expansion or raise if it terminates."""
    result = expand_division(numerator, denominator, max_frac=max_frac)
    if result.terminates:
        raise ValueError(f"division terminates: status={result.status.value}")
    return result


def division_summary(
    numerator: complex | int | tuple[int, int],
    denominator: int = 1,
    *,
    max_frac: int = 500,
) -> dict[str, object]:
    """Return a compact theory-facing division report."""
    result = expand_division(numerator, denominator, max_frac=max_frac)
    data = result.structured_digits()
    data.update(
        {
            "reduced_denominator": result.classification.reduced_denominator,
            "base_power_exponent": result.classification.base_power_exponent,
            "persistent_denominator": result.classification.persistent_denominator,
            "round_trip_ok": result.round_trip_ok(),
        }
    )
    return data


__all__ = [
    "DivisionStatus",
    "DenominatorClassification",
    "CnrsDivisionExpansion",
    "classify_denominator",
    "expand_division",
    "terminating_expansion",
    "periodic_expansion",
    "division_summary",
]
