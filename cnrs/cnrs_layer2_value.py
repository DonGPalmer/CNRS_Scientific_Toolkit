"""
cnrs_layer2_value.py
--------------------
Unified Layer-2 value interface.

Wraps the Layer2 (z, k) pair with:

  - construction from Gaussian / complex + branch
  - construction from CNRS-A string + branch
  - conversion back to Gaussian
  - Layer-2 add / sub / mul
  - semantic equality
"""

from __future__ import annotations
from dataclasses import dataclass

from .cnrs_layer2 import Layer2, layer2_from_complex, make_layer2
from .cnrs_repr import cnrs_to_gaussian


@dataclass(frozen=True)
class L2Val:
    """
    Layer-2 value wrapper.

    Internally stores a Layer2(z, k).
    """
    v: Layer2

    # -----------------------------
    # Constructors
    # -----------------------------

    @staticmethod
    def from_gaussian(g: complex, k: int = 0) -> "L2Val":
        return L2Val(layer2_from_complex(g, k))

    @staticmethod
    def from_str(z_str: str, k: int = 0) -> "L2Val":
        return L2Val(make_layer2(z_str, k))

    # -----------------------------
    # Conversions
    # -----------------------------

    def to_gaussian(self) -> complex:
        return self.v.to_gaussian()

    @property
    def z(self) -> str:
        return self.v.z

    @property
    def k(self) -> int:
        return self.v.k

    # -----------------------------
    # Arithmetic
    # -----------------------------

    def __add__(self, other: "L2Val") -> "L2Val":
        return L2Val(self.v + other.v)

    def __sub__(self, other: "L2Val") -> "L2Val":
        """
        Subtraction via Gaussian semantics, branch reset.

        Fixed (Thread 19 downstream check) for consistency with the
        corrected Layer2.__sub__: this method previously computed
        k1-k2 independently, bypassing Layer2.__sub__ entirely, which
        carried the same k1-k2 bug. Now resets to k=0, matching the
        proved branch-reset addition rule applied to a + (-b).
        """
        g = self.to_gaussian() - other.to_gaussian()
        return L2Val.from_gaussian(g, 0)

    def __mul__(self, other: "L2Val") -> "L2Val":
        return L2Val(self.v * other.v)

    # -----------------------------
    # Equality / repr
    # -----------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, L2Val):
            return NotImplemented
        return (self.to_gaussian() == other.to_gaussian()) and (self.k == other.k)

    def __str__(self) -> str:
        return f"{self.z} @ {self.k}"

    def __repr__(self) -> str:
        return f"L2Val({self.z!r}, {self.k})"
