"""Exact CNRS-A multiplication through the finite Gaussian carrier."""
from __future__ import annotations

from .convolution import convolve_exact
from .finite_string import (
    cnrs_string_to_finite_sequence,
    finite_sequence_to_cnrs_string,
)
from .gaussian_normalization import normalize_gaussian_laurent


def mul_cnrs(a: str, b: str) -> str:
    """Multiply two finite CNRS-A strings exactly.

    Parsing, convolution, carry normalization, and formatting all use integer
    or Gaussian-integer arithmetic. The public two-string signature is
    preserved from earlier releases.
    """
    left = cnrs_string_to_finite_sequence(a)
    right = cnrs_string_to_finite_sequence(b)
    raw = convolve_exact(left, right)
    normalized = normalize_gaussian_laurent(raw)
    return finite_sequence_to_cnrs_string(normalized)


__all__ = ["mul_cnrs"]
