"""Experimental, resource-bounded finite CNRS-H entry points.

This opt-in facade does not change the exact R_A or HurwitzJet algebra.
The underlying research classes remain unbounded and are not exposed as
resource-safe user-facing operations. Limits apply to inputs *and outputs*.
"""
from __future__ import annotations

from dataclasses import dataclass

from .cnrs_h_finite_exact import RA, HurwitzJet


@dataclass(frozen=True)
class FiniteLimits:
    max_digit_length: int = 512
    max_numerator_bits: int = 1024
    max_denominator_power: int = 128
    max_degree: int = 16
    max_convolution_terms: int = 153

    def __post_init__(self) -> None:
        for field in ("max_digit_length", "max_numerator_bits", "max_denominator_power",
                      "max_degree", "max_convolution_terms"):
            x = getattr(self, field)
            if type(x) is not int or x < 1:
                raise ValueError(f"{field} must be a positive integer")


class BoundedFiniteOps:
    """Checked interface for finite, exact experimental arithmetic.

    This is a computational limit, not a sandbox or timing guarantee.
    The input origin must still be trusted and Python process quotas used
    when processing untrusted data.
    """
    def __init__(self, limits: FiniteLimits | None = None) -> None:
        if limits is not None and not isinstance(limits, FiniteLimits):
            raise TypeError("limits must be FiniteLimits")
        self.limits = limits if limits is not None else FiniteLimits()

    def check(self, x: RA) -> RA:
        if not isinstance(x, RA):
            raise TypeError("coefficient must be R_A")
        if (max(abs(x.real).bit_length(), abs(x.imag).bit_length()) > self.limits.max_numerator_bits
                or x.denominator_power > self.limits.max_denominator_power):
            raise ValueError("coefficient exceeds the experimental resource budget")
        return x

    def coefficient(self, real: int, imag: int = 0, denominator_power: int = 0) -> RA:
        if any(type(x) is not int for x in (real, imag, denominator_power)):
            raise TypeError("numerator and exponent must be exact integers")
        if (denominator_power < 0 or denominator_power > self.limits.max_denominator_power
                or max(abs(real).bit_length(), abs(imag).bit_length()) > self.limits.max_numerator_bits):
            raise ValueError("coefficient input exceeds the experimental resource budget")
        return self.check(RA(real, imag, denominator_power))

    def decode(self, spelling: str) -> RA:
        if type(spelling) is not str:
            raise TypeError("CNRS spelling must be a string")
        if len(spelling) > self.limits.max_digit_length:
            raise ValueError("input spelling exceeds the experimental resource budget")
        return self.check(RA.from_cnrs_string(spelling))

    def encode(self, x: RA) -> str:
        return self.check(x).to_cnrs_string(max_digits=self.limits.max_digit_length)

    def jet(self, coefficients: tuple[RA, ...] | list[RA]) -> HurwitzJet:
        if type(coefficients) not in (tuple, list):
            raise TypeError("coefficients must be a list or tuple")
        if len(coefficients) > self.limits.max_degree + 1:
            raise ValueError("coefficient count exceeds the experimental resource budget")
        return HurwitzJet(tuple(self.check(c) for c in coefficients))

    def _check_jet(self, x: HurwitzJet) -> HurwitzJet:
        if not isinstance(x, HurwitzJet):
            raise TypeError("expected HurwitzJet")
        if len(x.coefficients) > self.limits.max_degree + 1:
            raise ValueError("jet degree exceeds the experimental resource budget")
        for c in x.coefficients:
            self.check(c)
        return x

    def add(self, a: RA, b: RA) -> RA:
        return self.check(self.check(a) + self.check(b))

    def multiply(self, a: RA, b: RA) -> RA:
        return self.check(self.check(a) * self.check(b))

    def product(self, a: HurwitzJet, b: HurwitzJet, through_degree: int) -> HurwitzJet:
        self._check_jet(a)
        self._check_jet(b)
        if type(through_degree) is not int or not (0 <= through_degree <= self.limits.max_degree):
            raise ValueError("requested truncation degree exceeds the experimental resource budget")
        # Safe conservative upper bound for the unoptimized binomial convolution.
        terms = (through_degree + 1) * (through_degree + 2) // 2
        if terms > self.limits.max_convolution_terms:
            raise ValueError("convolution work exceeds the experimental resource budget")
        return self._check_jet(a.product(b, through_degree=through_degree))

    def inverse_truncated(self, a: HurwitzJet, through_degree: int) -> HurwitzJet:
        self._check_jet(a)
        if type(through_degree) is not int or not (0 <= through_degree <= self.limits.max_degree):
            raise ValueError("requested inverse degree exceeds the experimental resource budget")
        terms = through_degree * (through_degree + 1) // 2
        if terms > self.limits.max_convolution_terms:
            raise ValueError("inverse work exceeds the experimental resource budget")
        return self._check_jet(a.inverse_truncated(through_degree))


__all__ = ["FiniteLimits", "BoundedFiniteOps"]
