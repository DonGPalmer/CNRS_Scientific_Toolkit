"""Exact branch-index multiplication and lifted logarithm algebra.

This module models the universal cover of C* as pairs ``(z, k)`` where
``z != 0`` is the principal complex value and ``k`` is the logarithmic sheet.
"""
from __future__ import annotations
from dataclasses import dataclass
import cmath, math

_TWO_PI = 2.0 * math.pi

def principal_arg(z: complex) -> float:
    if z == 0:
        raise ValueError("principal argument is undefined at zero")
    a = cmath.phase(z)
    # Python uses (-pi, pi]; normalize -pi to +pi for the chosen convention.
    if math.isclose(a, -math.pi, abs_tol=1e-15):
        return math.pi
    return a

def branch_wrap(z: complex, w: complex) -> int:
    """Integer cocycle correcting principal-argument wrap under multiplication."""
    if z == 0 or w == 0:
        raise ValueError("branch multiplication is defined only on nonzero complex values")
    raw = (principal_arg(z) + principal_arg(w) - principal_arg(z*w)) / _TWO_PI
    return int(round(raw))

@dataclass(frozen=True)
class LiftedComplex:
    """Element of the universal cover of the punctured complex plane."""
    z: complex
    k: int = 0

    def __post_init__(self) -> None:
        if self.z == 0:
            raise ValueError("LiftedComplex excludes zero")
        object.__setattr__(self, "z", complex(self.z))
        object.__setattr__(self, "k", int(self.k))

    @property
    def lifted_argument(self) -> float:
        return principal_arg(self.z) + _TWO_PI * self.k

    def log(self) -> complex:
        return math.log(abs(self.z)) + 1j * self.lifted_argument

    @staticmethod
    def exp(value: complex) -> "LiftedComplex":
        theta = float(value.imag)
        k = math.floor((theta + math.pi) / _TWO_PI)
        principal_theta = theta - _TWO_PI * k
        # keep principal angle in (-pi, pi]
        if principal_theta <= -math.pi:
            principal_theta += _TWO_PI; k -= 1
        z = math.exp(value.real) * complex(math.cos(principal_theta), math.sin(principal_theta))
        return LiftedComplex(z, k)

    def __mul__(self, other: "LiftedComplex") -> "LiftedComplex":
        return LiftedComplex(self.z * other.z, self.k + other.k + branch_wrap(self.z, other.z))

    def inverse(self) -> "LiftedComplex":
        """Multiplicative inverse on the universal cover."""
        return LiftedComplex.exp(-self.log())

    def __truediv__(self, other: "LiftedComplex") -> "LiftedComplex":
        return self * other.inverse()

    def __pow__(self, n: int) -> "LiftedComplex":
        if not isinstance(n, int):
            return NotImplemented
        if n == 0:
            return LiftedComplex(1+0j, 0)
        if n < 0:
            return self.inverse() ** (-n)
        out = LiftedComplex(1+0j, 0)
        base = self
        m = n
        while m:
            if m & 1:
                out = out * base
            base = base * base
            m >>= 1
        return out

__all__ = ["LiftedComplex", "principal_arg", "branch_wrap"]
