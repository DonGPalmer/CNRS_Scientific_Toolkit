"""
cnrs_value.py
-------------
Unified CNRS-A value interface.

Provides a small wrapper class `CVal` around CNRS-A digit strings, with:

  - construction from Gaussian / complex
  - conversion back to Gaussian
  - CNRS-A add / sub / mul
  - semantic equality

This is a convenience layer on top of:
  - cnrs_repr
  - cnrs_add
  - cnrs_mul
"""

from __future__ import annotations
from dataclasses import dataclass

from .cnrs_repr import (
    gaussian_to_cnrs_str,
    cnrs_to_gaussian,
    normalize_cnrs,
)
from .cnrs_add import add_cnrs
from .cnrs_mul import mul_cnrs


@dataclass(frozen=True)
class CVal:
    """
    CNRS-A value wrapper.

    Internally stores a canonical CNRS-A digit string.
    """
    s: str  # canonical CNRS-A string

    # -----------------------------
    # Constructors
    # -----------------------------

    @staticmethod
    def from_gaussian(g: complex) -> "CVal":
        return CVal(normalize_cnrs(gaussian_to_cnrs_str(g)))

    @staticmethod
    def from_str(s: str) -> "CVal":
        return CVal(normalize_cnrs(s))

    # -----------------------------
    # Conversions
    # -----------------------------

    def to_gaussian(self) -> complex:
        return cnrs_to_gaussian(self.s)

    # -----------------------------
    # Arithmetic
    # -----------------------------

    def __add__(self, other: "CVal") -> "CVal":
        return CVal(normalize_cnrs(add_cnrs(self.s, other.s)))

    def __sub__(self, other: "CVal") -> "CVal":
        diff = cnrs_to_gaussian(self.s) - cnrs_to_gaussian(other.s)
        return CVal.from_gaussian(diff)

    def __mul__(self, other: "CVal") -> "CVal":
        return CVal(normalize_cnrs(mul_cnrs(self.s, other.s)))

    # -----------------------------
    # Equality / repr
    # -----------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CVal):
            return NotImplemented
        return self.to_gaussian() == other.to_gaussian()

    def __str__(self) -> str:
        return self.s

    def __repr__(self) -> str:
        return f"CVal({self.s!r})"
