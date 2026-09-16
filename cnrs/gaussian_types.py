"""Strict Gaussian-integer and Gaussian-rational scalar types."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from .gaussian_valuation import (
    gadd,
    gdiv_exact,
    gmul,
    gpow,
    reduce_gaussian_fraction,
)

GaussianInteger: TypeAlias = tuple[int, int]
GaussianLike: TypeAlias = int | GaussianInteger


def coerce_gaussian(value: GaussianLike) -> GaussianInteger:
    """Coerce the public scalar carrier, rejecting Boolean and approximate types."""
    if type(value) is int:
        return (value, 0)
    if type(value) is tuple and len(value) == 2:
        real, imag = value
        if type(real) is int and type(imag) is int:
            return (real, imag)
    raise TypeError("Gaussian value must be an exact int or a pair of exact ints")


@dataclass(frozen=True, init=False)
class GaussianRational:
    """Canonical exact fraction in the Gaussian integers."""

    numerator: GaussianInteger
    denominator: GaussianInteger

    def __init__(
        self, numerator: GaussianLike, denominator: GaussianLike = 1
    ) -> None:
        p = coerce_gaussian(numerator)
        q = coerce_gaussian(denominator)
        p, q = reduce_gaussian_fraction(p, q)
        object.__setattr__(self, "numerator", p)
        object.__setattr__(self, "denominator", q)

    def __add__(self, other: object) -> "GaussianRational":
        if isinstance(other, GaussianRational):
            rhs = other
        else:
            try:
                rhs = GaussianRational(other)  # type: ignore[arg-type]
            except TypeError:
                return NotImplemented
        return GaussianRational(
            gadd(gmul(self.numerator, rhs.denominator),
                 gmul(rhs.numerator, self.denominator)),
            gmul(self.denominator, rhs.denominator),
        )

    def __radd__(self, other: object) -> "GaussianRational":
        return self.__add__(other)

    def __mul__(self, other: object) -> "GaussianRational":
        if isinstance(other, GaussianRational):
            rhs = other
        else:
            try:
                rhs = GaussianRational(other)  # type: ignore[arg-type]
            except TypeError:
                return NotImplemented
        return GaussianRational(
            gmul(self.numerator, rhs.numerator),
            gmul(self.denominator, rhs.denominator),
        )

    def __rmul__(self, other: object) -> "GaussianRational":
        return self.__mul__(other)

    def __pow__(self, exponent: int) -> "GaussianRational":
        if type(exponent) is not int:
            raise TypeError("exponent must be an exact int")
        if exponent >= 0:
            return GaussianRational(
                gpow(self.numerator, exponent), gpow(self.denominator, exponent)
            )
        if self.numerator == (0, 0):
            raise ZeroDivisionError("zero cannot be raised to a negative power")
        return GaussianRational(
            gpow(self.denominator, -exponent), gpow(self.numerator, -exponent)
        )


__all__ = [
    "GaussianInteger",
    "GaussianLike",
    "GaussianRational",
    "coerce_gaussian",
]
