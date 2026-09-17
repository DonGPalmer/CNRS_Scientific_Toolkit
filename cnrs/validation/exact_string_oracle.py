"""Independent exact value oracle for finite CNRS-A strings.

The implementation uses direct pairs of :class:`fractions.Fraction` and does
not import production parsing, convolution, normalization, or multiplication.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import re

RationalPair = tuple[Fraction, Fraction]
_ZERO: RationalPair = (Fraction(0), Fraction(0))
_BETA: RationalPair = (Fraction(-2), Fraction(1))
_FINITE_CNRS_PATTERN = re.compile(r"(?:[0-4]+(?:\.[0-4]*)?|\.[0-4]+)\Z")


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


@lru_cache(maxsize=None)
def exact_string_value(value: str) -> RationalPair:
    """Evaluate a finite CNRS-A string by independent exact arithmetic."""
    if type(value) is not str:
        raise TypeError("value must be an exact str")
    if _FINITE_CNRS_PATTERN.fullmatch(value) is None:
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


def exact_product_value(left: str, right: str) -> RationalPair:
    """Return the exact product value without production multiplication code."""
    return _multiply(exact_string_value(left), exact_string_value(right))


__all__ = ["RationalPair", "exact_product_value", "exact_string_value"]
