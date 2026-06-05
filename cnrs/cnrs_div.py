"""
cnrs_div.py
-----------
CNRS-A division utilities.

Implements:
  - division by Gaussian units (±1, ±i)
  - division by the base z0 = -2 + i
  - division by powers of the base
  - full CNRS-A division via Gaussian semantics

This module is consistent with:
  - cnrs_repr
  - cnrs_add
  - cnrs_mul
  - cnrs_ops
"""

from __future__ import annotations
from typing import Tuple

from .cnrs_repr import (
    Z0,
    cnrs_to_gaussian,
    gaussian_to_cnrs_str,
    normalize_cnrs,
)


# ---------------------------------------------------------------------------
# Unit division (±1, ±i)
# ---------------------------------------------------------------------------

UNITS = {
    "1": 1 + 0j,
    "-1": -1 + 0j,
    "i": 0 + 1j,
    "-i": 0 - 1j,
}

def div_by_unit(z_str: str, unit: str) -> str:
    """
    Divide a CNRS-A value by a Gaussian unit (±1, ±i).
    """
    if unit not in UNITS:
        raise ValueError("Unit must be one of: '1', '-1', 'i', '-i'")

    g = cnrs_to_gaussian(z_str)
    u = UNITS[unit]
    q = g / u
    return normalize_cnrs(gaussian_to_cnrs_str(q))


# ---------------------------------------------------------------------------
# Division by the base z0 = -2 + i
# ---------------------------------------------------------------------------

def div_by_base(z_str: str) -> str:
    """
    Divide a CNRS-A value by the base z0 = -2 + i.
    """
    g = cnrs_to_gaussian(z_str)
    q = g / Z0
    return normalize_cnrs(gaussian_to_cnrs_str(q))


def div_by_base_power(z_str: str, k: int) -> str:
    """
    Divide by z0^k for integer k >= 0.
    """
    if k < 0:
        raise ValueError("Exponent k must be non-negative")

    g = cnrs_to_gaussian(z_str)
    q = g / (Z0 ** k)
    return normalize_cnrs(gaussian_to_cnrs_str(q))


# ---------------------------------------------------------------------------
# Full CNRS-A division
# ---------------------------------------------------------------------------

def div_cnrs(a: str, b: str) -> str:
    """
    Full CNRS-A division via Gaussian semantics.

    This is mathematically exact:
        (a / b)_CNRS = CNRS( Gaussian(a) / Gaussian(b) )

    Notes:
      - If b = 0, raises ZeroDivisionError.
      - Result may be a Gaussian rational, not necessarily a Gaussian integer.
    """
    ga = cnrs_to_gaussian(a)
    gb = cnrs_to_gaussian(b)

    if gb == 0:
        raise ZeroDivisionError("Division by zero in CNRS-A")

    q = ga / gb
    return normalize_cnrs(gaussian_to_cnrs_str(q))
