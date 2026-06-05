"""
Branch-aware complex values for CNRS scientific workflows.

CnrsBranch is a lightweight value object that carries:
  - a complex value, optionally stored through CNRS-float encoding/decoding
  - an integer branch index k

It is not a full analytic-continuation engine. It is a practical container
for preserving branch/history information that ordinary principal-branch
complex values often discard.
"""
from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
from typing import Iterable, List

from cnrs.cnrs_float import encode, decode

TAU = 2.0 * math.pi


@dataclass(frozen=True)
class CnrsBranch:
    """Complex value plus explicit branch index."""
    value: complex
    k: int = 0
    L: int | None = None

    @staticmethod
    def from_complex(value: complex, k: int = 0, L: int | None = None) -> "CnrsBranch":
        """Construct from a standard complex value, optionally quantized through CNRS-float."""
        z = complex(value)
        if L is not None:
            z = decode(encode(z, L=L))
        return CnrsBranch(z, int(k), L)

    @staticmethod
    def from_polar(radius: float, theta: float, k: int = 0, L: int | None = None) -> "CnrsBranch":
        """Construct from polar form, with theta interpreted on branch k."""
        z = radius * cmath.exp(1j * theta)
        return CnrsBranch.from_complex(z, k=k, L=L)

    def principal_arg(self) -> float:
        return cmath.phase(self.value)

    def arg(self) -> float:
        """Branch-aware argument."""
        return cmath.phase(self.value) + TAU * self.k

    def log(self) -> complex:
        """Branch-aware logarithm."""
        return math.log(abs(self.value)) + 1j * self.arg()

    def exp_log(self) -> complex:
        """Return exp(log(value,k)); should reconstruct value up to rounding."""
        return cmath.exp(self.log())

    def with_branch(self, k: int) -> "CnrsBranch":
        return CnrsBranch(self.value, int(k), self.L)

    def encode(self, L: int) -> "CnrsBranch":
        """Return a copy whose value has passed through CNRS-float at mantissa length L."""
        return CnrsBranch.from_complex(self.value, k=self.k, L=L)

    def __mul__(self, other: "CnrsBranch") -> "CnrsBranch":
        if not isinstance(other, CnrsBranch):
            return NotImplemented
        L = self.L if self.L == other.L else None
        return CnrsBranch.from_complex(self.value * other.value, self.k + other.k, L=L)

    def __truediv__(self, other: "CnrsBranch") -> "CnrsBranch":
        if not isinstance(other, CnrsBranch):
            return NotImplemented
        L = self.L if self.L == other.L else None
        return CnrsBranch.from_complex(self.value / other.value, self.k - other.k, L=L)

    def __add__(self, other: "CnrsBranch") -> "CnrsBranch":
        if not isinstance(other, CnrsBranch):
            return NotImplemented
        # Addition does not have a canonical branch-index rule; preserve only if equal.
        k = self.k if self.k == other.k else 0
        L = self.L if self.L == other.L else None
        return CnrsBranch.from_complex(self.value + other.value, k=k, L=L)

    def __sub__(self, other: "CnrsBranch") -> "CnrsBranch":
        if not isinstance(other, CnrsBranch):
            return NotImplemented
        k = self.k if self.k == other.k else 0
        L = self.L if self.L == other.L else None
        return CnrsBranch.from_complex(self.value - other.value, k=k, L=L)


def branch_indices_from_unwrapped(wrapped_phase: Iterable[float], unwrapped_phase: Iterable[float]) -> List[int]:
    """Compute integer branch indices k from wrapped and unwrapped phase arrays."""
    return [int(round((u - w) / TAU)) for w, u in zip(wrapped_phase, unwrapped_phase)]


def reconstruct_phase(wrapped_phase: Iterable[float], branch_indices: Iterable[int]) -> List[float]:
    """Reconstruct unwrapped phase from wrapped phase and integer branch index."""
    return [float(w) + TAU * int(k) for w, k in zip(wrapped_phase, branch_indices)]


def winding_number(unwrapped_phase: Iterable[float]) -> float:
    vals = list(unwrapped_phase)
    if len(vals) < 2:
        return 0.0
    return (vals[-1] - vals[0]) / TAU
