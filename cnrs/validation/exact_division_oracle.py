"""Independent rational-pair oracle for finite CNRS-A string division.

The oracle deliberately does not import production parsing, finite carriers,
streaming division, canonical-periodic code, or witness generation.
"""
from __future__ import annotations

from fractions import Fraction
import re

RationalPair = tuple[Fraction, Fraction]
_ZERO: RationalPair = (Fraction(0), Fraction(0))
_BETA: RationalPair = (Fraction(-2), Fraction(1))
_PATTERN = re.compile(r"(?:[0-4]+(?:\.[0-4]*)?|\.[0-4]+)\Z")


def _add(left: RationalPair, right: RationalPair) -> RationalPair:
    return left[0] + right[0], left[1] + right[1]


def _multiply(left: RationalPair, right: RationalPair) -> RationalPair:
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def _divide(left: RationalPair, right: RationalPair) -> RationalPair:
    a, b = left
    c, d = right
    denominator = c * c + d * d
    if denominator == 0:
        raise ZeroDivisionError("division by zero Gaussian rational")
    return (a * c + b * d) / denominator, (b * c - a * d) / denominator


def exact_string_value(value: str) -> RationalPair:
    """Evaluate a finite CNRS-A string using only independent pair arithmetic."""
    if type(value) is not str:
        raise TypeError("value must be an exact str")
    if _PATTERN.fullmatch(value) is None:
        raise ValueError("value must be a finite CNRS-A string using digits 0..4")

    integer, separator, fractional = value.partition(".")
    total = _ZERO
    for character in integer:
        total = _add(_multiply(total, _BETA), (Fraction(int(character)), Fraction(0)))

    fractional_total = _ZERO
    if separator:
        for character in reversed(fractional):
            fractional_total = _divide(
                _add(fractional_total, (Fraction(int(character)), Fraction(0))),
                _BETA,
            )
    return _add(total, fractional_total)


def exact_quotient_value(dividend: str, divisor: str) -> RationalPair:
    """Return the exact quotient without calling production division code."""
    return _divide(exact_string_value(dividend), exact_string_value(divisor))


__all__ = ["RationalPair", "exact_quotient_value", "exact_string_value"]

