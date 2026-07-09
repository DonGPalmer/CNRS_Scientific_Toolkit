"""Hybrid CNRS-A/CNRS-H representation utilities.

A hybrid series stores canonical CNRS-A coefficient objects while CNRS-H carries
EGF/Hurwitz order.  A codec supplies the canonical encode/decode bijection for
one coefficient domain.  Formal operations are transported through that codec.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Callable, Generic, Iterable, Sequence, TypeVar, Any

R = TypeVar("R")
C = TypeVar("C")


@dataclass(frozen=True)
class CoefficientCodec(Generic[R, C]):
    encode: Callable[[R], C]
    decode: Callable[[C], R]
    zero: R
    one: R

    def canonical(self, coefficient: C) -> C:
        return self.encode(self.decode(coefficient))


@dataclass(frozen=True)
class HybridSeries(Generic[R, C]):
    coefficients: tuple[C, ...]
    codec: CoefficientCodec[R, C]

    @classmethod
    def from_values(cls, values: Iterable[R], codec: CoefficientCodec[R, C]) -> "HybridSeries[R, C]":
        return cls(tuple(codec.encode(v) for v in values), codec)

    def values(self) -> tuple[R, ...]:
        return tuple(self.codec.decode(c) for c in self.coefficients)

    def canonical(self) -> "HybridSeries[R, C]":
        return type(self)(tuple(self.codec.canonical(c) for c in self.coefficients), self.codec)

    def derivative(self) -> "HybridSeries[R, C]":
        vals = self.values()
        if len(vals) <= 1:
            return type(self).from_values((self.codec.zero,), self.codec)
        return type(self).from_values(vals[1:], self.codec)

    def integral(self, constant: R | None = None) -> "HybridSeries[R, C]":
        c = self.codec.zero if constant is None else constant
        return type(self).from_values((c,) + self.values(), self.codec)

    def add(self, other: "HybridSeries[R, C]", *, order: int | None = None) -> "HybridSeries[R, C]":
        self._check_codec(other)
        a, b = self.values(), other.values()
        n = max(len(a), len(b)) if order is None else int(order)
        vals = tuple((a[i] if i < len(a) else self.codec.zero) +
                     (b[i] if i < len(b) else self.codec.zero) for i in range(n))
        return type(self).from_values(vals, self.codec)

    def hurwitz_product(self, other: "HybridSeries[R, C]", *, order: int | None = None) -> "HybridSeries[R, C]":
        self._check_codec(other)
        a, b = self.values(), other.values()
        n = (len(a) + len(b) - 1) if order is None else int(order)
        out: list[R] = []
        for m in range(max(0, n)):
            s = self.codec.zero
            for k in range(m + 1):
                ak = a[k] if k < len(a) else self.codec.zero
                bk = b[m-k] if m-k < len(b) else self.codec.zero
                s = s + comb(m, k) * ak * bk
            out.append(s)
        return type(self).from_values(out, self.codec)

    def exponential_eigenfunction(self, alpha: R, order: int) -> "HybridSeries[R, C]":
        return type(self).from_values((alpha**n for n in range(order)), self.codec)

    def as_dict(self, serializer: Callable[[C], Any] | None = None) -> dict[str, Any]:
        ser = serializer or (lambda x: x)
        return {"basis": "rho^n/n!", "coefficients": [ser(c) for c in self.coefficients]}

    def _check_codec(self, other: "HybridSeries[R, C]") -> None:
        if self.codec != other.codec:
            raise ValueError("hybrid operations require the same coefficient codec")


def hybrid_from_values(values: Iterable[R], codec: CoefficientCodec[R, C]) -> HybridSeries[R, C]:
    return HybridSeries.from_values(values, codec)


__all__ = ["CoefficientCodec", "HybridSeries", "hybrid_from_values"]
