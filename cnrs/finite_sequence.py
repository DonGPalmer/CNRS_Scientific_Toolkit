"""Immutable finite Gaussian-coefficient Laurent sequences."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .gaussian_types import (
    GaussianInteger,
    GaussianLike,
    GaussianRational,
    coerce_gaussian,
)

_ZERO: GaussianInteger = (0, 0)


@dataclass(frozen=True, init=False)
class CNRSFiniteSequence:
    coefficients: tuple[GaussianInteger, ...]
    offset: int

    def __init__(
        self, coefficients: Iterable[GaussianLike], offset: int = 0
    ) -> None:
        if type(offset) is not int:
            raise TypeError("offset must be an exact int")
        try:
            values = tuple(coerce_gaussian(value) for value in coefficients)
        except TypeError:
            raise
        except Exception as exc:
            raise TypeError("coefficients must be iterable") from exc

        low = 0
        while low < len(values) and values[low] == _ZERO:
            low += 1
        high = len(values)
        while high > low and values[high - 1] == _ZERO:
            high -= 1
        if low == len(values):
            canonical, canonical_offset = (), 0
        else:
            canonical, canonical_offset = values[low:high], offset + low
        object.__setattr__(self, "coefficients", canonical)
        object.__setattr__(self, "offset", canonical_offset)

    @property
    def support(self) -> tuple[int, int] | None:
        if not self.coefficients:
            return None
        return self.offset, self.offset + len(self.coefficients) - 1

    def coefficient(self, exponent: int) -> GaussianInteger:
        if type(exponent) is not int:
            raise TypeError("exponent must be an exact int")
        index = exponent - self.offset
        if 0 <= index < len(self.coefficients):
            return self.coefficients[index]
        return _ZERO

    def evaluate(self, base: GaussianLike) -> GaussianRational:
        scalar = GaussianRational(coerce_gaussian(base))
        if not self.coefficients:
            return GaussianRational(0)
        if scalar.numerator == _ZERO and self.offset < 0:
            raise ZeroDivisionError("zero base with negative support")
        total = GaussianRational(0)
        power = scalar ** self.offset
        for coefficient in self.coefficients:
            total = total + GaussianRational(coefficient) * power
            power = power * scalar
        return total

    def trimmed(self) -> "CNRSFiniteSequence":
        return CNRSFiniteSequence(self.coefficients, self.offset)


__all__ = ["CNRSFiniteSequence"]
