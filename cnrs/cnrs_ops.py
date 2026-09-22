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
import re
from .cnrs_add import add_cnrs
from .cnrs_mul import mul_cnrs
from .cnrs_repr import cnrs_to_gaussian, gaussian_to_cnrs_str, normalize_cnrs


_FINITE_CNRS_PATTERN = re.compile(r"(?:[0-4]+(?:\.[0-4]*)?|\.[0-4]+)\Z")
_NEGATIVE_ONE = "144"


def _is_finite_cnrs_string(value: object) -> bool:
    return type(value) is str and _FINITE_CNRS_PATTERN.fullmatch(value) is not None


def _legacy_cnrs_neg(a: str) -> str:
    """Preserve v0.17 behavior outside the claimed finite grammar."""
    ga = cnrs_to_gaussian(a)
    return normalize_cnrs(gaussian_to_cnrs_str(-ga))


def cnrs_add(a: str, b: str) -> str:
    """a + b in CNRS-A."""
    return add_cnrs(a, b)


def cnrs_neg(a: str) -> str:
    """Unary negation in CNRS-A, exact for accepted finite strings."""
    if _is_finite_cnrs_string(a):
        return mul_cnrs(_NEGATIVE_ONE, a)
    return _legacy_cnrs_neg(a)


def cnrs_sub(a: str, b: str) -> str:
    """a - b in CNRS-A."""
    if _is_finite_cnrs_string(a) and _is_finite_cnrs_string(b):
        return add_cnrs(a, cnrs_neg(b))
    return add_cnrs(a, _legacy_cnrs_neg(b))


def cnrs_mul(a: str, b: str) -> str:
    """a * b in CNRS-A."""
    return mul_cnrs(a, b)


def cnrs_eq(a: str, b: str) -> bool:
    """Semantic equality: compare via value map, not string form."""
    return cnrs_to_gaussian(a) == cnrs_to_gaussian(b)
