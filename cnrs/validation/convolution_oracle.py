"""Independent nested-loop oracle for finite Gaussian convolution.

This module intentionally does not import :mod:`cnrs.convolution`.
"""
from __future__ import annotations

from ..finite_sequence import CNRSFiniteSequence
from ..gaussian_types import GaussianInteger
from ..gaussian_valuation import gadd, gmul


def oracle_convolve(
    left: CNRSFiniteSequence, right: CNRSFiniteSequence
) -> CNRSFiniteSequence:
    if not isinstance(left, CNRSFiniteSequence):
        raise TypeError("left must be a CNRSFiniteSequence")
    if not isinstance(right, CNRSFiniteSequence):
        raise TypeError("right must be a CNRSFiniteSequence")
    if not left.coefficients or not right.coefficients:
        return CNRSFiniteSequence(())
    values: list[GaussianInteger] = [
        (0, 0)
        for _ in range(len(left.coefficients) + len(right.coefficients) - 1)
    ]
    for i in range(len(left.coefficients)):
        for j in range(len(right.coefficients)):
            values[i + j] = gadd(
                values[i + j],
                gmul(left.coefficients[i], right.coefficients[j]),
            )
    return CNRSFiniteSequence(values, left.offset + right.offset)


__all__ = ["oracle_convolve"]
