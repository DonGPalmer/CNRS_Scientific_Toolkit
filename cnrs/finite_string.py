"""Exact conversion between finite CNRS-A strings and finite carriers."""
from __future__ import annotations

import re

from .finite_sequence import CNRSFiniteSequence
from .cnrs_repr import normalize_cnrs

_FINITE_CNRS_PATTERN = re.compile(r"(?:[0-4]+(?:\.[0-4]*)?|\.[0-4]+)\Z")


def cnrs_string_to_finite_sequence(value: str) -> CNRSFiniteSequence:
    """Parse a finite CNRS-A digit string into its exact Laurent carrier."""
    if type(value) is not str:
        raise TypeError("value must be an exact str")
    if _FINITE_CNRS_PATTERN.fullmatch(value) is None:
        raise ValueError("value must be a finite CNRS-A string using digits 0..4")

    integer, separator, fractional = value.partition(".")
    raw_digits = integer + fractional
    offset = -len(fractional) if separator else 0
    return CNRSFiniteSequence((int(ch) for ch in reversed(raw_digits)), offset)


def finite_sequence_to_cnrs_string(value: CNRSFiniteSequence) -> str:
    """Format a finite carrier whose coefficients are canonical CNRS digits."""
    if not isinstance(value, CNRSFiniteSequence):
        raise TypeError("value must be a CNRSFiniteSequence")
    if not value.coefficients:
        return "0"

    for coefficient in value.coefficients:
        real, imaginary = coefficient
        if imaginary != 0 or real not in (0, 1, 2, 3, 4):
            raise ValueError("every coefficient must be a canonical CNRS digit")

    highest = value.offset + len(value.coefficients) - 1
    integer_highest = max(highest, 0)
    fractional_lowest = min(value.offset, 0)

    integer = "".join(
        str(value.coefficient(exponent)[0])
        for exponent in range(integer_highest, -1, -1)
    )
    fractional = "".join(
        str(value.coefficient(exponent)[0])
        for exponent in range(-1, fractional_lowest - 1, -1)
    )
    raw = integer + ("." + fractional if fractional else "")
    return normalize_cnrs(raw)


__all__ = [
    "cnrs_string_to_finite_sequence",
    "finite_sequence_to_cnrs_string",
]

