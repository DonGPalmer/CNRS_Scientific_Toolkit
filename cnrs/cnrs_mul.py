"""
cnrs_mul.py
-----------
CNRS-A multiplication via convolution + general canonical normalisation.

Implements:
  - mul_cnrs(a, b): multiply two CNRS-A digit strings

Base:   z0 = -2 + i
Digits: D = {0, 1, 2, 3, 4}
"""

from __future__ import annotations
from typing import List
from .cnrs_repr import Z0, cnrs_remainder, normalize_cnrs


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _split_int_frac(s: str) -> tuple[str, str]:
    if "." in s:
        i, f = s.split(".")
    else:
        i, f = s, ""
    return i, f


def _digits_lsb_from_str(s: str) -> List[int]:
    """
    Convert a CNRS-A integer string (no '.') to digits LSB-first.
    """
    return [int(ch) for ch in reversed(s)] if s else [0]


def _str_from_digits_msb(digits: List[int]) -> str:
    """
    Convert digits LSB-first to a string MSB-first (no decimal).
    """
    # remove leading zeros in MSB direction, but keep at least one digit
    i = len(digits) - 1
    while i > 0 and digits[i] == 0:
        i -= 1
    trimmed = digits[: i + 1]
    return "".join(str(d) for d in reversed(trimmed))


# ---------------------------------------------------------------------------
# Convolution + normalization core
# ---------------------------------------------------------------------------

def _convolve_digits(a: List[int], b: List[int]) -> List[int]:
    """
    Discrete convolution of two LSB-first digit lists (integer coefficients).
    """
    na, nb = len(a), len(b)
    out = [0] * (na + nb - 1)
    for i in range(na):
        for j in range(nb):
            out[i + j] += a[i] * b[j]
    return out


def _normalize_coeffs(coeffs: List[int]) -> List[int]:
    """
    Normalize integer coefficients into CNRS-A digits using the CNRS remainder logic.

    We interpret:
        sum_k coeffs[k] * Z0^k

    and rewrite each coefficient as:
        coeffs[k] = d_k + Z0 * carry_{k+1}

    where d_k in {0..4} and carry_{k+1} is a Gaussian integer.
    """
    digits: List[int] = []
    carry = 0 + 0j

    for c in coeffs:
        a = c + carry
        d = cnrs_remainder(a)
        digits.append(d)
        q = (a - d) / Z0
        carry = complex(round(q.real), round(q.imag))

    # drain remaining carry
    drain_guard = 0
    while carry != 0:
        a = carry
        d = cnrs_remainder(a)
        digits.append(d)
        q = (a - d) / Z0
        carry = complex(round(q.real), round(q.imag))
        drain_guard += 1
        if drain_guard > 1000:
            raise RuntimeError("Carry did not drain in normalization")

    # trim highest zeros
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()

    return digits


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def mul_cnrs(a: str, b: str) -> str:
    """
    Multiply two CNRS-A digit strings using convolution + general normalisation.

    Steps:
      1. Split each operand into integer and fractional parts.
      2. Remove '.', treat as pure integer digit strings.
      3. Convert to LSB-first digit lists.
      4. Convolve the digit lists (integer coefficients).
      5. Normalize arbitrary convolution coefficients into CNRS-A digits via the general carry algorithm, not the bounded addition transducer.
      6. Insert decimal point with total_frac = frac_a_len + frac_b_len.
      7. Canonically normalize the resulting string.

    Parameters
    ----------
    a, b : str
        CNRS-A digit strings, e.g. "104", "23.1", "0", etc.

    Returns
    -------
    str
        CNRS-A digit string representing the product.
    """
    a_int, a_frac = _split_int_frac(a)
    b_int, b_frac = _split_int_frac(b)

    total_frac = len(a_frac) + len(b_frac)

    a_raw = a_int + a_frac
    b_raw = b_int + b_frac

    a_digits = _digits_lsb_from_str(a_raw)
    b_digits = _digits_lsb_from_str(b_raw)

    coeffs = _convolve_digits(a_digits, b_digits)
    norm_digits = _normalize_coeffs(coeffs)

    # build raw integer string (no decimal)
    raw = _str_from_digits_msb(norm_digits)

    # insert decimal point if needed
    if total_frac > 0:
        if len(raw) <= total_frac:
            raw = raw.rjust(total_frac + 1, "0")
        s = raw[:-total_frac] + "." + raw[-total_frac:]
    else:
        s = raw

    return normalize_cnrs(s)
