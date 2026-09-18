"""Exact division bridge for finite CNRS-A strings.

Finite strings are evaluated as exact Gaussian fractions and delegated to the
v0.14 streaming-division engine.  This module intentionally defines no second
digit recurrence, cycle detector, canonical-periodic representation, or witness
schema.
"""
from __future__ import annotations

from .finite_sequence import CNRSFiniteSequence
from .finite_string import cnrs_string_to_finite_sequence
from .gaussian_types import GaussianInteger, GaussianRational
from .gaussian_valuation import BETA, gmul
from .streaming_division import DivisionResolution, stream_division


def _finite_value_fraction(
    value: CNRSFiniteSequence,
) -> tuple[GaussianInteger, GaussianInteger]:
    """Return the exact reduced Gaussian fraction represented by ``value``."""
    exact: GaussianRational = value.evaluate(BETA)
    return exact.numerator, exact.denominator


def divide_cnrs_exact(
    dividend: str,
    divisor: str,
    *,
    max_steps: int = 100_000,
) -> DivisionResolution:
    """Resolve the exact quotient of two finite CNRS-A strings.

    ``LIMIT_REACHED`` is an operational result only.  It does not assert that
    the quotient is aperiodic.
    """
    if type(max_steps) is not int:
        raise TypeError("max_steps must be a positive exact int")
    if max_steps <= 0:
        raise ValueError("max_steps must be positive")

    left = cnrs_string_to_finite_sequence(dividend)
    right = cnrs_string_to_finite_sequence(divisor)
    left_numerator, left_denominator = _finite_value_fraction(left)
    right_numerator, right_denominator = _finite_value_fraction(right)

    if right_numerator == (0, 0):
        raise ZeroDivisionError("CNRS division by zero")

    quotient_numerator = gmul(left_numerator, right_denominator)
    quotient_denominator = gmul(left_denominator, right_numerator)
    return stream_division(quotient_numerator, quotient_denominator).resolve(
        max_steps
    )


__all__ = ["divide_cnrs_exact"]

