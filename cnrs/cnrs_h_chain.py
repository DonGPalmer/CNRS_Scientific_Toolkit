"""
cnrs.cnrs_h_chain
=================

Direct CNRS-H chain-rule support.

The autodiff layer implements the chain rule by carrying a derivative beside a
value.  This module implements the same idea directly inside the CNRS-H
coefficient calculus.  A ``CnrsH`` object stores exponential-generating-function
coefficients

    f(s) = sum_n d_n s^n / n!.

Differentiation is the native CNRS-H digit shift.  The missing operation for a
native chain rule is finite EGF-series composition.  Once composition is
available, the chain rule can be tested entirely in coefficient space:

    D(f o g) = (Df o g) * Dg.

All operations here are finite and truncated to a requested order.  This is a
computational CNRS-H chain-rule layer, not a complete analytic theorem for all
functions.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import factorial
from typing import Iterable

from .cnrs_h import CnrsH


class CnrsHChainError(ValueError):
    """Raised for unsupported CNRS-H chain-rule operations."""


def _check_order(order: int) -> None:
    if order <= 0:
        raise ValueError("order must be positive")


def truncate_pad(h: CnrsH, order: int) -> CnrsH:
    """Return ``h`` with exactly ``order`` EGF coefficients."""
    _check_order(order)
    return h.truncate(order).pad(order)


def constant(value: complex, order: int) -> CnrsH:
    """CNRS-H constant series with exactly ``order`` coefficients."""
    return CnrsH.from_list([value] + [0] * (order - 1))


def identity(order: int) -> CnrsH:
    """CNRS-H identity series ``s`` with exactly ``order`` coefficients."""
    return CnrsH.identity().pad(order).truncate(order)


def monomial(power: int, coefficient: complex = 1, *, order: int) -> CnrsH:
    """Return ``coefficient * s**power`` as a CNRS-H EGF series.

    Since CNRS-H stores EGF coefficients, the coefficient at index ``power`` is
    ``coefficient * power!``.
    """
    _check_order(order)
    if power < 0:
        raise ValueError("power must be non-negative")
    coeffs = [0] * order
    if power < order:
        coeffs[power] = coefficient * factorial(power)
    return CnrsH.from_list(coeffs)


def exp_series(a: complex = 1, b: complex = 0, *, order: int) -> CnrsH:
    """Return the EGF series for ``exp(a*s + b)`` to ``order`` terms."""
    import cmath

    _check_order(order)
    eb = cmath.exp(b)
    return CnrsH.from_list([eb * (a ** n) for n in range(order)])


def sin_series(a: complex = 1, b: complex = 0, *, order: int) -> CnrsH:
    """Return the EGF series for ``sin(a*s + b)`` to ``order`` terms."""
    import cmath
    import math

    _check_order(order)
    return CnrsH.from_list([a ** n * cmath.sin(b + n * math.pi / 2) for n in range(order)])


def cos_series(a: complex = 1, b: complex = 0, *, order: int) -> CnrsH:
    """Return the EGF series for ``cos(a*s + b)`` to ``order`` terms."""
    import cmath
    import math

    _check_order(order)
    return CnrsH.from_list([a ** n * cmath.cos(b + n * math.pi / 2) for n in range(order)])


def multiply_truncated(a: CnrsH, b: CnrsH, *, order: int) -> CnrsH:
    """EGF product of two CNRS-H series, truncated/padded to ``order``."""
    return truncate_pad(a * b, order)


def power_series(base: CnrsH, power: int, *, order: int) -> CnrsH:
    """Return ``base**power`` using CNRS-H multiplication, truncated to order."""
    _check_order(order)
    if power < 0:
        raise ValueError("power must be non-negative")
    out = CnrsH.one().pad(order)
    b = truncate_pad(base, order)
    for _ in range(power):
        out = multiply_truncated(out, b, order=order)
    return truncate_pad(out, order)


def compose_series(outer: CnrsH, inner: CnrsH, *, order: int) -> CnrsH:
    """Finite CNRS-H composition ``outer(inner(s))``.

    If ``outer(x) = sum d_n x**n / n!`` and ``inner`` represents ``g(s)``,
    then this computes the truncated series

        sum_{n=0}^{N-1} (d_n / n!) * g(s)**n.

    This is exact for finite polynomial data up to the requested order and is a
    finite-truncation approximation for infinite analytic series.
    """
    _check_order(order)
    outer = truncate_pad(outer, order)
    inner = truncate_pad(inner, order)

    result = CnrsH.zero(order).pad(order)
    inner_power = CnrsH.one().pad(order)  # g**0
    fact = 1
    for n in range(order):
        if n > 0:
            fact *= n
            inner_power = multiply_truncated(inner_power, inner, order=order)
        coeff = outer.coeff(n)
        if coeff != 0:
            result = result + (inner_power * (coeff / fact))
            result = truncate_pad(result, order)
    return truncate_pad(result, order)


def chain_rule_lhs(outer: CnrsH, inner: CnrsH, *, order: int) -> CnrsH:
    """Compute ``D(outer o inner)`` directly in CNRS-H coefficient space."""
    # One extra coefficient is needed before dropping the constant term.
    composed = compose_series(outer, inner, order=order + 1)
    return truncate_pad(composed.differentiate(), order)


def chain_rule_rhs(outer: CnrsH, inner: CnrsH, *, order: int) -> CnrsH:
    """Compute ``(D outer o inner) * D inner`` in CNRS-H coefficient space."""
    d_outer = truncate_pad(outer.differentiate(), order)
    d_inner = truncate_pad(inner.differentiate(), order)
    pulled = compose_series(d_outer, inner, order=order)
    return multiply_truncated(pulled, d_inner, order=order)


def max_coeff_error(a: CnrsH, b: CnrsH) -> float:
    """Maximum absolute coefficient difference over both coefficient lists."""
    n = max(a.length, b.length)
    return max(abs(complex(a.coeff(i)) - complex(b.coeff(i))) for i in range(n)) if n else 0.0


@dataclass(frozen=True)
class ChainRuleComparison:
    """Result of a direct CNRS-H chain-rule comparison."""

    lhs: CnrsH
    rhs: CnrsH
    max_error: float
    passed: bool


def verify_chain_rule(
    outer: CnrsH,
    inner: CnrsH,
    *,
    order: int = 12,
    atol: float = 1e-10,
) -> ChainRuleComparison:
    """Verify ``D(f o g) = (Df o g) * Dg`` to finite CNRS-H order."""
    lhs = chain_rule_lhs(outer, inner, order=order)
    rhs = chain_rule_rhs(outer, inner, order=order)
    err = max_coeff_error(lhs, rhs)
    return ChainRuleComparison(lhs, rhs, err, err <= atol)


def evaluate_composition(outer: CnrsH, inner: CnrsH, x: complex, *, order: int) -> complex:
    """Evaluate ``outer(inner(x))`` through the finite CNRS-H composition."""
    return compose_series(outer, inner, order=order).evaluate(x)


__all__ = [
    "CnrsHChainError",
    "ChainRuleComparison",
    "truncate_pad",
    "constant",
    "identity",
    "monomial",
    "exp_series",
    "sin_series",
    "cos_series",
    "multiply_truncated",
    "power_series",
    "compose_series",
    "chain_rule_lhs",
    "chain_rule_rhs",
    "verify_chain_rule",
    "max_coeff_error",
    "evaluate_composition",
]
