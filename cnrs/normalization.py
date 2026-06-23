"""
cnrs.normalization
==================

Scoped CNRS-A normalisation helpers.

The CNRS main-paper v4 review sharpened an important implementation point:
there is not one undifferentiated "normalizer" claim.  Addition has a bounded
raw alphabet and may be routed through the compact addition transducer, while
arbitrary finite coefficient strings (including multiplication convolution
outputs) require the general CNRS-A canonical-normalisation algorithm.

This module makes that distinction explicit for code, tests, and documentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence

from .cnrs_repr import Z0, cnrs_remainder, normalize_cnrs
from .cnrs_add import add_cnrs


class NormalizationScope(str, Enum):
    """Mathematical scope of a CNRS-A normalisation call."""

    ADDITION_BOUNDED = "addition_bounded"
    GENERAL_FINITE_COEFFICIENTS = "general_finite_coefficients"
    MULTIPLICATION_CONVOLUTION = "multiplication_convolution"


@dataclass(frozen=True)
class NormalizationResult:
    """Structured result recording which normalisation route was used."""

    value: str
    scope: NormalizationScope
    algorithm: str
    raw_coefficients: tuple[int, ...] = ()
    drain_steps: int = 0
    note: str = ""


def _digits_lsb_from_integer_string(s: str) -> list[int]:
    if "." in s:
        raise ValueError("expected an integer CNRS-A string without a decimal point")
    s = normalize_cnrs(s)
    return [int(ch) for ch in reversed(s)] if s else [0]


def normalize_general_coefficients(coefficients: Sequence[int]) -> NormalizationResult:
    """Normalise an arbitrary finite integer coefficient string.

    ``coefficients`` is LSB-first and represents ``sum c_k z0^k``.  The raw
    coefficients may be unbounded; this is the route to use after multiplication
    convolution and other finite coefficient construction.  It is deliberately
    not described as the 14-state addition transducer.
    """

    if not coefficients:
        return NormalizationResult(
            value="0",
            scope=NormalizationScope.GENERAL_FINITE_COEFFICIENTS,
            algorithm="general CNRS-A carry normalisation",
            raw_coefficients=(),
            drain_steps=0,
            note="empty coefficient list normalises to zero",
        )

    digits: list[int] = []
    carry = 0 + 0j
    raw = tuple(int(c) for c in coefficients)

    for c in raw:
        a = int(c) + carry
        d = cnrs_remainder(a)
        digits.append(d)
        q = (a - d) / Z0
        carry = complex(round(q.real), round(q.imag))

    drain_steps = 0
    while carry != 0:
        d = cnrs_remainder(carry)
        digits.append(d)
        q = (carry - d) / Z0
        carry = complex(round(q.real), round(q.imag))
        drain_steps += 1
        if drain_steps > 10000:
            raise RuntimeError("CNRS-A general normalisation carry did not drain")

    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()

    value = "".join(str(d) for d in reversed(digits)) or "0"
    return NormalizationResult(
        value=normalize_cnrs(value),
        scope=NormalizationScope.GENERAL_FINITE_COEFFICIENTS,
        algorithm="general CNRS-A carry normalisation",
        raw_coefficients=raw,
        drain_steps=drain_steps,
        note="valid for arbitrary finite integer coefficient strings",
    )


def normalize_addition(a: str, b: str) -> NormalizationResult:
    """Normalise a bounded addition input using the addition transducer route."""

    result = normalize_cnrs(add_cnrs(a, b))
    return NormalizationResult(
        value=result,
        scope=NormalizationScope.ADDITION_BOUNDED,
        algorithm="bounded-input CNRS-A addition transducer",
        note="raw digit sums are bounded by the addition alphabet",
    )


def multiplication_raw_coefficients(a: str, b: str) -> tuple[int, ...]:
    """Return LSB-first raw convolution coefficients for integer CNRS-A strings."""

    ad = _digits_lsb_from_integer_string(a)
    bd = _digits_lsb_from_integer_string(b)
    out = [0] * (len(ad) + len(bd) - 1)
    for i, da in enumerate(ad):
        for j, db in enumerate(bd):
            out[i + j] += da * db
    return tuple(out)


def normalize_multiplication_convolution(a: str, b: str) -> NormalizationResult:
    """Normalise multiplication raw convolution through the general route."""

    coeffs = multiplication_raw_coefficients(a, b)
    base = normalize_general_coefficients(coeffs)
    return NormalizationResult(
        value=base.value,
        scope=NormalizationScope.MULTIPLICATION_CONVOLUTION,
        algorithm="convolution followed by general CNRS-A normalisation",
        raw_coefficients=coeffs,
        drain_steps=base.drain_steps,
        note=(
            "multiplication coefficients are not uniformly bounded by the "
            "addition transducer alphabet"
        ),
    )


__all__ = [
    "NormalizationScope",
    "NormalizationResult",
    "normalize_general_coefficients",
    "normalize_addition",
    "multiplication_raw_coefficients",
    "normalize_multiplication_convolution",
]
