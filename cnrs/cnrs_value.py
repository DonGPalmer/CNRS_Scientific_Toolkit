"""
cnrs_value.py
-------------
Unified CNRS-A value interface.

Provides a small wrapper class `CVal` around CNRS-A digit strings, with:

  - construction from Gaussian / complex
  - conversion back to Gaussian
  - CNRS-A add / sub / neg / mul  (native over finite CNRS-A strings)
  - semantic equality

This is a convenience layer on top of:
  - cnrs_repr
  - cnrs_add
  - cnrs_mul

Native negation
---------------
The CNRS-A representation of -1 in base z0 = -2+i is the finite string "144":

    1*z0^2 + 4*z0 + 4 = (3-4i) + (-8+4i) + 4 = -1

Negation of any CVal is therefore multiplication by CVal("144"), routing
entirely through mul_cnrs (convolution + carry normalisation).  Subtraction
follows as a + (-b), routing through add_cnrs (FST) and mul_cnrs.

No Gaussian arithmetic is used for negation or subtraction.
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


# CNRS-A representation of -1 in base z0 = -2+i.
# Derivation: greedy expansion of -1 gives digits [4, 4, 1] (LSB first),
# i.e. the string "144" (MSB first).
# Verification: 1*z0^2 + 4*z0 + 4 = (3-4i) + (-8+4i) + 4 = -1.  ✓
_NEG_ONE = "144"


@dataclass(frozen=True)
class CVal:
    """
    CNRS-A value wrapper.

    Internally stores a canonical CNRS-A digit string.

    All four arithmetic operations are CNRS-A native:
      __add__  — native bounded-input addition layer (add_cnrs)
      __neg__  — multiplication by the CNRS-A representation of -1 (mul_cnrs)
      __sub__  — a + (-b), i.e. FST after negation
      __mul__  — convolution followed by general CNRS-A normalisation (mul_cnrs)
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
    # Arithmetic — all CNRS-A native
    # -----------------------------

    def __add__(self, other: "CVal") -> "CVal":
        """Add via the CNRS-A native addition layer."""
        return CVal(normalize_cnrs(add_cnrs(self.s, other.s)))

    def __neg__(self) -> "CVal":
        """Negate via multiplication by the CNRS-A representation of -1.

        -1 in base z0 = -2+i is the finite digit string "144".
        Routing through mul_cnrs keeps negation entirely within
        CNRS-A multiplication and normalisation.
        """
        return CVal(normalize_cnrs(mul_cnrs(_NEG_ONE, self.s)))

    def __sub__(self, other: "CVal") -> "CVal":
        """Subtract as a + (-b) — FST addition after native negation."""
        return self + (-other)

    def __mul__(self, other: "CVal") -> "CVal":
        """Multiply via CNRS-A convolution and general normalisation."""
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
