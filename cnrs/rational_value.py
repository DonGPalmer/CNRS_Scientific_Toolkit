"""
cnrs.rational_value
===================

Theory-aligned CNRS rational/periodic value objects.

``CnrsRationalValue`` promotes the v0.8.x structured division report into a
small value-facing object.  It does not claim that general division closes in
finite CNRS-A strings.  Instead it preserves the correct CNRS status:

  - finite Gaussian integer;
  - terminating base-power denominator;
  - eventually periodic denominator;
  - shifted eventually periodic denominator.

The object is intended for scientific workflows that need to carry rational
CNRS-A data without collapsing the representation-status information.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .division import CnrsDivisionExpansion, DivisionStatus, expand_division
from .cnrs_value import CVal


@dataclass(frozen=True)
class CnrsRationalValue:
    """CNRS-A rational value with explicit finite/periodic status."""

    division: CnrsDivisionExpansion
    label: str = ""

    @classmethod
    def from_fraction(
        cls,
        numerator: complex | int | tuple[int, int],
        denominator: int = 1,
        *,
        label: str = "",
        max_frac: int = 500,
    ) -> "CnrsRationalValue":
        return cls(expand_division(numerator, denominator, max_frac=max_frac), label=label)

    @property
    def status(self) -> DivisionStatus:
        return self.division.status

    @property
    def is_finite(self) -> bool:
        return self.division.terminates

    @property
    def has_periodic_tail(self) -> bool:
        return self.division.classification.has_periodic_tail

    @property
    def persistent_denominator(self) -> int:
        return self.division.persistent_denominator

    @property
    def period_length(self) -> int | None:
        return self.division.period_length

    @property
    def prefix_digits(self) -> list[int]:
        return self.division.prefix_digits

    @property
    def period_digits(self) -> list[int]:
        return self.division.period_digits

    def exact_value(self) -> complex:
        return self.division.exact_value()

    def exact_value_fractions(self) -> tuple[Fraction, Fraction]:
        """Return exact (real, imag) fractions when the backend supports it."""
        exp = self.division.expansion
        if hasattr(exp, "z0_adic_value_fractions") and exp.is_z0_adic:
            return exp.z0_adic_value_fractions()
        z = exp.exact_value()
        return Fraction(int(round(z.real)), 1), Fraction(int(round(z.imag)), 1)

    def finite_cval(self) -> CVal:
        """Return a CVal only for Gaussian-integer finite CNRS-A values.

        Terminating base-power denominators such as 1/5 are finite CNRS-A
        expansions with negative powers, but they are not Gaussian integers and
        therefore cannot be represented by the finite integer ``CVal`` wrapper.
        """
        if self.status != DivisionStatus.GAUSSIAN_INTEGER:
            raise ValueError(
                "only Gaussian-integer divisions collapse to CVal; "
                f"status={self.status.value} may still have a terminating fractional expansion"
            )
        return CVal.from_gaussian(self.exact_value())

    def structured_report(self) -> dict[str, Any]:
        """Return a JSON-friendly representation-status report."""
        return {
            "label": self.label,
            "status": self.status.value,
            "finite": self.is_finite,
            "has_periodic_tail": self.has_periodic_tail,
            "persistent_denominator": self.persistent_denominator,
            "period_start": self.division.period_start,
            "period_length": self.division.period_length,
            "prefix_digits": self.prefix_digits,
            "period_digits": self.period_digits,
            "power_offset": self.division.expansion.power_offset,
            "display": self.division.to_str_with_period(),
        }

    def __complex__(self) -> complex:
        return complex(self.exact_value())

    def __str__(self) -> str:
        tag = f"{self.label}: " if self.label else ""
        return f"{tag}{self.division.to_str_with_period()} [{self.status.value}]"


def rational_value(
    numerator: complex | int | tuple[int, int],
    denominator: int = 1,
    *,
    label: str = "",
    max_frac: int = 500,
) -> CnrsRationalValue:
    """Convenience constructor for ``CnrsRationalValue``."""
    return CnrsRationalValue.from_fraction(
        numerator,
        denominator,
        label=label,
        max_frac=max_frac,
    )


def rational_batch(items, *, max_frac: int = 500) -> list[CnrsRationalValue]:
    """Build a list of rational values from ``(numerator, denominator)`` pairs."""
    return [rational_value(n, d, max_frac=max_frac) for n, d in items]


__all__ = ["CnrsRationalValue", "rational_value", "rational_batch"]
