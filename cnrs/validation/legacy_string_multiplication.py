"""Historical pre-v0.16 CNRS-A multiplication used only as a parity oracle.

This module intentionally preserves the former Python-complex and rounding
algorithm. Production code must never import it.
"""
from __future__ import annotations

import re
from typing import List

from ..cnrs_repr import Z0, cnrs_remainder, normalize_cnrs

_FINITE_CNRS_PATTERN = re.compile(r"(?:[0-4]+(?:\.[0-4]*)?|\.[0-4]+)\Z")


def _require_valid_string(value: str) -> None:
    if type(value) is not str:
        raise TypeError("value must be an exact str")
    if _FINITE_CNRS_PATTERN.fullmatch(value) is None:
        raise ValueError("value must be a finite CNRS-A string using digits 0..4")


def _split_int_frac(value: str) -> tuple[str, str]:
    if "." in value:
        integer, fractional = value.split(".")
    else:
        integer, fractional = value, ""
    return integer, fractional


def _digits_lsb_from_str(value: str) -> List[int]:
    return [int(ch) for ch in reversed(value)] if value else [0]


def _str_from_digits_msb(digits: List[int]) -> str:
    index = len(digits) - 1
    while index > 0 and digits[index] == 0:
        index -= 1
    return "".join(str(digit) for digit in reversed(digits[: index + 1]))


def _convolve_digits(left: List[int], right: List[int]) -> List[int]:
    output = [0] * (len(left) + len(right) - 1)
    for i, left_digit in enumerate(left):
        for j, right_digit in enumerate(right):
            output[i + j] += left_digit * right_digit
    return output


def _normalize_coeffs(coefficients: List[int]) -> List[int]:
    digits: List[int] = []
    carry = 0 + 0j
    for coefficient in coefficients:
        total = coefficient + carry
        digit = cnrs_remainder(total)
        digits.append(digit)
        quotient = (total - digit) / Z0
        carry = complex(round(quotient.real), round(quotient.imag))

    drain_guard = 0
    while carry != 0:
        digit = cnrs_remainder(carry)
        digits.append(digit)
        quotient = (carry - digit) / Z0
        carry = complex(round(quotient.real), round(quotient.imag))
        drain_guard += 1
        if drain_guard > 100:
            raise RuntimeError("Carry did not drain in normalization")

    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
    return digits


def legacy_mul_cnrs(a: str, b: str) -> str:
    """Return the historical multiplication output for valid finite strings."""
    _require_valid_string(a)
    _require_valid_string(b)
    a_integer, a_fractional = _split_int_frac(a)
    b_integer, b_fractional = _split_int_frac(b)
    total_fractional = len(a_fractional) + len(b_fractional)
    left = _digits_lsb_from_str(a_integer + a_fractional)
    right = _digits_lsb_from_str(b_integer + b_fractional)
    raw = _str_from_digits_msb(_normalize_coeffs(_convolve_digits(left, right)))
    if total_fractional:
        if len(raw) <= total_fractional:
            raw = raw.rjust(total_fractional + 1, "0")
        raw = raw[:-total_fractional] + "." + raw[-total_fractional:]
    return normalize_cnrs(raw)


__all__ = ["legacy_mul_cnrs"]

