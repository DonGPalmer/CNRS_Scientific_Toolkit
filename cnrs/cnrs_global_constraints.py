"""
cnrs_global_constraints.py
--------------------------
Reusable analytic constraints for CNRS Layer-4 objects.

Constraints are callables:
    Constraint : L4State -> bool

This module provides:
  - branch index constraints
  - operator-history constraints
  - continuation-path constraints
  - Gaussian-value constraints
  - fixed-point constraints
  - composite constraints

These are used by cnrs_global_solver.py to filter analytic branches.
"""

from __future__ import annotations
from typing import Callable, List, Optional

from .cnrs_layer4 import L4State
from .cnrs_layer3_ops import L3Operator


# ---------------------------------------------------------------------------
# Basic constraint type
# ---------------------------------------------------------------------------

Constraint = Callable[[L4State], bool]


# ---------------------------------------------------------------------------
# Branch index constraints
# ---------------------------------------------------------------------------

def branch_equals(k: int) -> Constraint:
    """Keep only states with branch index exactly k."""
    return lambda st: st.l3.l2.k == k


def branch_in_range(kmin: int, kmax: int) -> Constraint:
    """Keep states with kmin <= branch index <= kmax."""
    return lambda st: kmin <= st.l3.l2.k <= kmax


def branch_nonnegative() -> Constraint:
    """Keep states with k >= 0."""
    return lambda st: st.l3.l2.k >= 0


def branch_zero() -> Constraint:
    """Keep only principal-branch states."""
    return branch_equals(0)


# ---------------------------------------------------------------------------
# Operator-history constraints
# ---------------------------------------------------------------------------

def has_operator(op: L3Operator) -> Constraint:
    """Keep states whose operator history includes a given operator."""
    return lambda st: op in st.ops


def operator_count_at_least(op: L3Operator, n: int) -> Constraint:
    """Keep states where operator appears at least n times."""
    return lambda st: sum(1 for o in st.ops if o == op) >= n


def operator_history_length_at_least(n: int) -> Constraint:
    """Keep states with operator history length >= n."""
    return lambda st: len(st.ops) >= n


# ---------------------------------------------------------------------------
# Continuation-path constraints
# ---------------------------------------------------------------------------

def path_length_at_least(n: int) -> Constraint:
    """Keep states whose continuation path has length >= n."""
    return lambda st: len(st.path) >= n


def path_starts_with(prefix: List[int]) -> Constraint:
    """Keep states whose continuation path begins with a given prefix."""
    def check(st: L4State) -> bool:
        if len(st.path) < len(prefix):
            return False
        return st.path[:len(prefix)] == prefix
    return check


def path_digit_frequency(digit: int, min_count: int) -> Constraint:
    """Keep states where a digit appears at least min_count times in the path."""
    return lambda st: st.path.count(digit) >= min_count


# ---------------------------------------------------------------------------
# Gaussian-value constraints
# ---------------------------------------------------------------------------

def gaussian_equals(z: complex) -> Constraint:
    """Keep states whose Gaussian value equals z."""
    return lambda st: st.l3.to_gaussian() == z


def gaussian_in_radius(R: float) -> Constraint:
    """Keep states whose Gaussian value lies within |z| <= R."""
    return lambda st: abs(st.l3.to_gaussian()) <= R


def gaussian_real_positive() -> Constraint:
    """Keep states with Re(z) > 0."""
    return lambda st: st.l3.to_gaussian().real > 0


def gaussian_imag_positive() -> Constraint:
    """Keep states with Im(z) > 0."""
    return lambda st: st.l3.to_gaussian().imag > 0


# ---------------------------------------------------------------------------
# Fixed-point constraints
# ---------------------------------------------------------------------------

def fixed_point_under(op: L3Operator, tol: float = 1e-9) -> Constraint:
    """
    Keep states that are approximate fixed points of an operator:
        op(v) ≈ v
    """
    def check(st: L4State) -> bool:
        v = st.l3
        v2 = op(v)
        return abs(v.to_gaussian() - v2.to_gaussian()) <= tol
    return check


# ---------------------------------------------------------------------------
# Composite constraints
# ---------------------------------------------------------------------------

def all_of(*constraints: Constraint) -> Constraint:
    """Logical AND of multiple constraints."""
    return lambda st: all(c(st) for c in constraints)


def any_of(*constraints: Constraint) -> Constraint:
    """Logical OR of multiple constraints."""
    return lambda st: any(c(st) for c in constraints)


def none_of(*constraints: Constraint) -> Constraint:
    """Logical NOT of OR: keep states that satisfy none of the constraints."""
    return lambda st: not any(c(st) for c in constraints)
