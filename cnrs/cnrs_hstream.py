"""
cnrs_hstream.py
---------------
CNRS-H streams: finite (and extendable) CNRS digit prefixes.

A CNRS-H stream is a sequence of digits d0, d1, ..., dn (LSB-first)
that may represent the beginning of an infinite CNRS expansion.

This module provides:

  - HStream: a finite prefix with safe extension
  - evaluation of finite prefixes
  - concatenation and shift operators
  - compatibility with CNRS-A and Layer-2

This is the foundation for analytic continuation and Problem-2's
multi-sheet structure.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Iterable

from .cnrs_repr import (
    Z0,
    cnrs_remainder,
    cnrs_to_gaussian,
    gaussian_to_cnrs_str,
    normalize_cnrs,
)


# ---------------------------------------------------------------------------
# HStream class
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HStream:
    """
    A finite CNRS-H prefix stream.

    Internally stores digits LSB-first: [d0, d1, ..., dn].
    """
    digits: List[int]

    # -----------------------------
    # Constructors
    # -----------------------------

    @staticmethod
    def from_str(s: str) -> "HStream":
        """
        Build a stream from a CNRS-A string (integer part only).
        """
        if "." in s:
            raise ValueError("HStream only supports integer prefixes")
        ds = [int(ch) for ch in reversed(s)]
        return HStream(ds)

    @staticmethod
    def from_digits(d: Iterable[int]) -> "HStream":
        return HStream(list(d))

    @staticmethod
    def from_gaussian(g: complex) -> "HStream":
        """
        Convert a Gaussian integer to a finite CNRS prefix.
        """
        s = gaussian_to_cnrs_str(g)
        return HStream.from_str(s)

    # -----------------------------
    # Basic operations
    # -----------------------------

    def to_str(self) -> str:
        """Return MSB-first string."""
        if not self.digits:
            return "0"
        # trim leading zeros in MSB direction
        i = len(self.digits) - 1
        while i > 0 and self.digits[i] == 0:
            i -= 1
        trimmed = self.digits[: i + 1]
        return "".join(str(d) for d in reversed(trimmed))

    def to_gaussian(self) -> complex:
        """
        Evaluate the finite prefix as a Gaussian integer.
        """
        z = 0 + 0j
        for d in reversed(self.digits):
            z = z * Z0 + d
        return z

    # -----------------------------
    # Stream extension
    # -----------------------------

    def extend(self, d: int) -> "HStream":
        """
        Append a digit to the prefix (LSB-first).
        """
        if d not in (0, 1, 2, 3, 4):
            raise ValueError("Digit must be in {0..4}")
        return HStream(self.digits + [d])

    def extend_many(self, ds: Iterable[int]) -> "HStream":
        out = self.digits[:]
        for d in ds:
            if d not in (0, 1, 2, 3, 4):
                raise ValueError("Digit must be in {0..4}")
            out.append(d)
        return HStream(out)

    # -----------------------------
    # Shift operators
    # -----------------------------

    def shift_left(self, k: int = 1) -> "HStream":
        """
        Multiply the represented value by Z0^k.
        Equivalent to inserting k zeros at the beginning (LSB side).
        """
        if k < 0:
            raise ValueError("shift_left requires k >= 0")
        return HStream([0] * k + self.digits)

    def shift_right(self, k: int = 1) -> "HStream":
        """
        Divide the represented value by Z0^k (if divisible).
        Equivalent to removing k LSB digits.
        """
        if k < 0:
            raise ValueError("shift_right requires k >= 0")
        if k > len(self.digits):
            return HStream([])
        return HStream(self.digits[k:])

    # -----------------------------
    # Concatenation
    # -----------------------------

    def concat(self, other: "HStream") -> "HStream":
        """
        Concatenate two streams (LSB-first).
        """
        return HStream(self.digits + other.digits)

    # -----------------------------
    # Pretty printing
    # -----------------------------

    def __str__(self) -> str:
        return f"HStream({self.to_str()})"

    def __repr__(self) -> str:
        return f"HStream(digits={self.digits})"
