"""
cnrs_layer2.py
--------------
Layer-2 representation: (CNRS-A digit string, integer branch index).

This is a minimal but coherent Layer-2 abstraction:

  - A Layer2 value is (z_str, k) where:
        z_str : CNRS-A digit string (Layer-1 value)
        k     : integer branch index (Layer-2 sheet)

  - Arithmetic is defined as:
        add: (z1, k1) + (z2, k2) = (z1+z2, k1 + k2)
        mul: (z1, k1) * (z2, k2) = (z1*z2, k1 + k2)

    The branch rule here is deliberately simple and composable; you can
    refine it later to match the exact log-sheet structure you settle on.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from .cnrs_ops import cnrs_add, cnrs_mul
from .cnrs_repr import cnrs_to_gaussian, gaussian_to_cnrs_str, normalize_cnrs


@dataclass(frozen=True)
class Layer2:
    """
    Layer-2 value: (CNRS-A digit string, integer branch index).
    """
    z: str   # CNRS-A digit string (Layer-1)
    k: int   # branch index (Layer-2)

    # -----------------------------
    # Basic constructors
    # -----------------------------

    @staticmethod
    def from_gaussian(value: complex, k: int = 0) -> "Layer2":
        """
        Construct a Layer2 value from a Gaussian integer and branch index.
        """
        z_str = normalize_cnrs(gaussian_to_cnrs_str(value))
        return Layer2(z_str, int(k))

    def to_gaussian(self) -> complex:
        """
        Forget the branch index and return the Layer-1 Gaussian value.
        """
        return cnrs_to_gaussian(self.z)

    # -----------------------------
    # Arithmetic
    # -----------------------------

    def __add__(self, other: "Layer2") -> "Layer2":
        """
        Layer-2 addition.

        Current convention:
            (z1, k1) + (z2, k2) = (z1 + z2, k1 + k2)
        """
        z_sum = cnrs_add(self.z, other.z)
        k_sum = self.k + other.k
        return Layer2(z_sum, k_sum)

    def __sub__(self, other: "Layer2") -> "Layer2":
        """
        Layer-2 subtraction via addition and negation of branch index.
        """
        z_diff = cnrs_add(self.z, gaussian_to_cnrs_str(-cnrs_to_gaussian(other.z)))
        k_diff = self.k - other.k
        return Layer2(normalize_cnrs(z_diff), k_diff)

    def __mul__(self, other: "Layer2") -> "Layer2":
        """
        Layer-2 multiplication.

        Current convention:
            (z1, k1) * (z2, k2) = (z1 * z2, k1 + k2)

        This matches a simple log-sheet intuition:
            log(c1) ~ log|c1| + i(arg c1 + 2π k1)
            log(c2) ~ log|c2| + i(arg c2 + 2π k2)
            log(c1 c2) ~ log(c1) + log(c2)  ⇒ branch indices add.
        """
        z_prod = cnrs_mul(self.z, other.z)
        k_prod = self.k + other.k
        return Layer2(z_prod, k_prod)

    # -----------------------------
    # Pretty printing
    # -----------------------------

    def __str__(self) -> str:
        return f"{self.z} @ {self.k}"

    def __repr__(self) -> str:
        return f"Layer2(z={self.z!r}, k={self.k})"


# Convenience constructors / helpers

def make_layer2(z_str: str, k: int = 0) -> Layer2:
    """
    Build a Layer2 value directly from a CNRS-A string and branch index.
    """
    return Layer2(normalize_cnrs(z_str), int(k))


def layer2_from_complex(c: complex, k: int = 0) -> Layer2:
    """
    Build a Layer2 value from a complex/Gaussian value and branch index.
    """
    return Layer2.from_gaussian(c, k)
