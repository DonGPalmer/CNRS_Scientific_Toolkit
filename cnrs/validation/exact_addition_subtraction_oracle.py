"""Independent exact value oracle for finite CNRS-A additive operations."""
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


def _negate(value: RationalPair) -> RationalPair:
    return -value[0], -value[1]


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
    """Evaluate an accepted finite CNRS-A spelling using Fraction pairs."""
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


def exact_sum_value(left: str, right: str) -> RationalPair:
    return _add(exact_string_value(left), exact_string_value(right))


def exact_negated_value(value: str) -> RationalPair:
    return _negate(exact_string_value(value))


def exact_difference_value(left: str, right: str) -> RationalPair:
    return _add(exact_string_value(left), _negate(exact_string_value(right)))


__all__ = [
    "RationalPair",
    "exact_difference_value",
    "exact_negated_value",
    "exact_string_value",
    "exact_sum_value",
]
