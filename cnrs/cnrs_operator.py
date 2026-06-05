"""
cnrs_operator.py
----------------
Operator calculus for CNRS-H streams.

This module provides:

  - Shift operators S (forward) and S^{-1} (backward)
  - Discrete derivative Δ
  - Discrete integral Σ (partial sums)
  - Operator composition
  - Application of operators to HStream objects

This is the foundation for Problem-2's operator calculus.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from .cnrs_hstream import HStream
from .cnrs_hstream_ops import hstream_add
from .cnrs_repr import Z0


# ---------------------------------------------------------------------------
# Shift operators
# ---------------------------------------------------------------------------

def shift_forward(stream: HStream, k: int = 1) -> HStream:
    """
    Forward shift S^k: multiply by Z0^k.
    Equivalent to inserting k zeros at the LSB side.
    """
    return stream.shift_left(k)


def shift_backward(stream: HStream, k: int = 1) -> HStream:
    """
    Backward shift S^{-k}: divide by Z0^k (if divisible).
    Equivalent to removing k LSB digits.
    """
    return stream.shift_right(k)


# ---------------------------------------------------------------------------
# Discrete derivative Δ
# ---------------------------------------------------------------------------

def discrete_derivative(stream: HStream) -> HStream:
    """
    Δ f = f - S^{-1} f

    This is the natural discrete derivative on CNRS-H streams.
    """
    f = stream
    f_shift = shift_backward(stream, 1)
    return hstream_add(f, HStream.from_gaussian(-f_shift.to_gaussian()))


# ---------------------------------------------------------------------------
# Discrete integral Σ
# ---------------------------------------------------------------------------

def discrete_integral(stream: HStream) -> HStream:
    """
    Σ f = partial sums of f under backward shifts.

    For finite prefixes, this is:
        Σ f = f + S^{-1} f + S^{-2} f + ... (until shift empties)
    """
    out = HStream.from_digits([])
    current = stream

    while current.digits:
        out = hstream_add(out, current)
        current = shift_backward(current, 1)

    return out


# ---------------------------------------------------------------------------
# Operator class
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Operator:
    """
    A linear operator on HStreams.

    Stores a callable f: HStream -> HStream.
    """
    f: Callable[[HStream], HStream]

    def __call__(self, stream: HStream) -> HStream:
        return self.f(stream)

    def __matmul__(self, other: "Operator") -> "Operator":
        """
        Composition: (A @ B)(x) = A(B(x))
        """
        return Operator(lambda s: self.f(other.f(s)))

    def __add__(self, other: "Operator") -> "Operator":
        """
        Pointwise operator addition.
        """
        return Operator(lambda s: hstream_add(self.f(s), other.f(s)))


# ---------------------------------------------------------------------------
# Predefined operators
# ---------------------------------------------------------------------------

S = Operator(lambda s: shift_forward(s, 1))      # forward shift
S_inv = Operator(lambda s: shift_backward(s, 1)) # backward shift
Delta = Operator(discrete_derivative)            # discrete derivative
Sigma = Operator(discrete_integral)              # discrete integral
