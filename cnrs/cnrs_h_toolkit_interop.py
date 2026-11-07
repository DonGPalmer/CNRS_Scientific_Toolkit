"""Bounded exact value-backend / Toolkit finite CNRS-A digit API interop.

No dependency on the Toolkit at import time: bind the API of a *pinned*
Toolkit installation explicitly using `ToolkitDigitOps(add_cnrs, mul_cnrs)`.
This is a self-checking reference adapter, not a replacement for native CVal
and not an assertion of full ABI verification or analytic continuation.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from .cnrs_h_finite_exact import RA, HurwitzJet, Z


class InteropMismatch(AssertionError):
    """A pinned Toolkit digit operation disagrees with the exact RA backend."""


@dataclass(frozen=True)
class ToolkitDigitOps:
    add_cnrs: Callable[[str, str], str]
    mul_cnrs: Callable[[str, str], str]
    max_digit_length: int = 4096
    max_jet_degree: int = 32

    def __post_init__(self) -> None:
        if not callable(self.add_cnrs) or not callable(self.mul_cnrs):
            raise TypeError("bind the pinned Toolkit addition and multiplication functions")
        for x in (self.max_digit_length, self.max_jet_degree):
            if type(x) is not int or x < 1:
                raise ValueError("interop bounds must be positive integers")

    def encode(self, x: RA) -> str:
        if not isinstance(x, RA):
            raise TypeError("expected exact R_A value")
        return x.to_cnrs_string(max_digits=self.max_digit_length)

    @staticmethod
    def decode(s: str) -> RA:
        return RA.from_cnrs_string(s)

    def add_checked(self, a: RA, b: RA) -> RA:
        want = a + b
        raw = self.add_cnrs(self.encode(a), self.encode(b))
        observed = self.decode(raw)
        if observed != want or raw != self.encode(want):
            raise InteropMismatch("Toolkit digit addition disagrees in value or canonical form")
        return observed

    def multiply_checked(self, a: RA, b: RA) -> RA:
        want = a * b
        raw = self.mul_cnrs(self.encode(a), self.encode(b))
        observed = self.decode(raw)
        if observed != want or raw != self.encode(want):
            raise InteropMismatch("Toolkit digit multiplication disagrees in value or canonical form")
        return observed

    def hurwitz_product_checked(self, a: HurwitzJet, b: HurwitzJet,
                                through_degree: int) -> HurwitzJet:
        """Bounded divided-power convolution using Toolkit's digit operations.

        This is intentionally slower than the value-backend kernel and serves
        only as an exact interop witness for a finite declared order.
        """
        from math import comb
        if not isinstance(a, HurwitzJet) or not isinstance(b, HurwitzJet):
            raise TypeError("both operands must be finite HurwitzJet")
        if type(through_degree) is not int or not (0 <= through_degree <= self.max_jet_degree):
            raise ValueError("requested degree is outside the declared bounded interop scope")
        out = []
        for n in range(through_degree + 1):
            total = Z
            for k in range(n + 1):
                term = self.multiply_checked(a.coefficient(k), b.coefficient(n - k))
                term = self.multiply_checked(term, RA(comb(n, k)))
                total = self.add_checked(total, term)
            out.append(total)
        observed = HurwitzJet(tuple(out))
        if observed != a.product(b, through_degree=through_degree):
            raise InteropMismatch("digit-stream Hurwitz result disagrees with exact value backend")
        return observed


__all__ = ["ToolkitDigitOps", "InteropMismatch"]
