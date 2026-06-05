"""
cnrs_ops.py
-----------
High-level CNRS-A arithmetic operators.

Wraps:
  - add_cnrs  (from cnrs_add)
  - mul_cnrs  (from cnrs_mul)
  - cnrs_to_gaussian, gaussian_to_cnrs_str (from cnrs_repr)

Provides:
  - cnrs_add(a, b)
  - cnrs_sub(a, b)
  - cnrs_mul(a, b)
  - cnrs_neg(a)
  - cnrs_eq(a, b)
"""

from __future__ import annotations
from .cnrs_add import add_cnrs
from .cnrs_mul import mul_cnrs
from .cnrs_repr import cnrs_to_gaussian, gaussian_to_cnrs_str, normalize_cnrs


def cnrs_add(a: str, b: str) -> str:
    """a + b in CNRS-A."""
    return add_cnrs(a, b)


def cnrs_neg(a: str) -> str:
    """Unary negation in CNRS-A, via value map."""
    ga = cnrs_to_gaussian(a)
    return normalize_cnrs(gaussian_to_cnrs_str(-ga))


def cnrs_sub(a: str, b: str) -> str:
    """a - b in CNRS-A."""
    return cnrs_add(a, cnrs_neg(b))


def cnrs_mul(a: str, b: str) -> str:
    """a * b in CNRS-A."""
    return mul_cnrs(a, b)


def cnrs_eq(a: str, b: str) -> bool:
    """Semantic equality: compare via value map, not string form."""
    return cnrs_to_gaussian(a) == cnrs_to_gaussian(b)
