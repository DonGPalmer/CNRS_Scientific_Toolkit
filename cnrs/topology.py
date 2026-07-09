"""Metric and topological utilities for CNRS-A and CNRS-H.

The module keeps four notions separate:
- symbolic prefix distance on digit strings;
- beta-adic valuation/distance for beta=-2+i;
- finite Laurent shifts;
- coefficientwise product distance for CNRS-H.

It does not identify beta-adic convergence with ordinary complex convergence.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Sequence, Any, Callable

from .gaussian_valuation import Gaussian, BETA, gadd, gsub, gmul, gaussian_valuation


def first_difference(a: Sequence[int], b: Sequence[int]) -> int | None:
    """Return the first differing digit index, or ``None`` when equal."""
    n = min(len(a), len(b))
    for i in range(n):
        if int(a[i]) != int(b[i]):
            return i
    if len(a) != len(b):
        return n
    return None


def symbolic_distance(a: Sequence[int], b: Sequence[int], *, residue_norm: int = 5) -> Fraction:
    """Prefix ultrametric ``residue_norm**(-r)`` for first difference ``r``."""
    if residue_norm <= 1:
        raise ValueError("residue_norm must exceed 1")
    r = first_difference(a, b)
    return Fraction(0) if r is None else Fraction(1, residue_norm**r)


def beta_adic_absolute(z: Gaussian) -> Fraction:
    """Return ``5**(-v_beta(z))`` exactly; zero has absolute value zero."""
    if z == (0, 0):
        return Fraction(0)
    v = gaussian_valuation(z, BETA)
    return Fraction(1, 5**v)


def beta_adic_distance(x: Gaussian, y: Gaussian) -> Fraction:
    return beta_adic_absolute(gsub(x, y))


def evaluate_finite_digits(digits: Sequence[int]) -> Gaussian:
    """Evaluate LSB-first finite digits in base ``-2+i`` exactly."""
    total: Gaussian = (0, 0)
    power: Gaussian = (1, 0)
    for raw in digits:
        d = int(raw)
        if d not in range(5):
            raise ValueError("digits must lie in {0,1,2,3,4}")
        total = gadd(total, (d * power[0], d * power[1]))
        power = gmul(power, BETA)
    return total


def first_difference_isometry(a: Sequence[int], b: Sequence[int]) -> bool:
    """Check the finite-prefix form of the CNRS-A isometry theorem."""
    return symbolic_distance(a, b) == beta_adic_distance(
        evaluate_finite_digits(a), evaluate_finite_digits(b)
    )


def coefficientwise_distance(
    a: Sequence[Any],
    b: Sequence[Any],
    *,
    coefficient_distance: Callable[[Any, Any], float] | None = None,
    terms: int | None = None,
) -> float:
    """Finite approximation to the standard product metric on coefficient strings.

    Missing coefficients are treated as zero.  ``terms`` must be supplied for
    genuinely lazy/infinite sequences; for finite sequences it defaults to the
    larger length.
    """
    if coefficient_distance is None:
        coefficient_distance = lambda x, y: abs(x - y)
    n = max(len(a), len(b)) if terms is None else int(terms)
    if n < 0:
        raise ValueError("terms must be nonnegative")
    total = 0.0
    for i in range(n):
        x = a[i] if i < len(a) else 0
        y = b[i] if i < len(b) else 0
        total += (2.0 ** (-(i + 1))) * min(1.0, float(coefficient_distance(x, y)))
    return total


__all__ = [
    "first_difference", "symbolic_distance", "beta_adic_absolute",
    "beta_adic_distance", "evaluate_finite_digits",
    "first_difference_isometry", "coefficientwise_distance",
]
