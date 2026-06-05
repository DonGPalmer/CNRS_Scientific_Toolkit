"""
cnrs_repr.py
------------
CNRS‑A representation and value‑map utilities.

Base:   z0 = -2 + i
Digits: D = {0, 1, 2, 3, 4}

This module provides:

  - gaussian_to_cnrs_digits(z):  Gaussian integer -> CNRS-A digit list (LSB first)
  - gaussian_to_cnrs_str(z):     Gaussian integer -> CNRS-A string (MSB first)
  - cnrs_to_gaussian(s):         CNRS-A string -> Gaussian integer (as complex)
  - normalize_cnrs(s):           Canonical formatting of CNRS-A strings
"""

from __future__ import annotations
from typing import List

# ---------------------------------------------------------------------------
# System constants
# ---------------------------------------------------------------------------

Z0 = complex(-2, 1)
DIGITS = (0, 1, 2, 3, 4)


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

def _is_gaussian(z: complex, tol: float = 1e-12) -> bool:
    """
    Return True if z is within tol of a Gaussian integer.
    """
    return abs(z.real - round(z.real)) < tol and abs(z.imag - round(z.imag)) < tol


def cnrs_remainder(a: complex) -> int:
    """
    Return the unique digit d in {0..4} such that (a - d) / Z0 is a Gaussian integer.

    This is the core remainder logic used in the greedy CNRS-A expansion.
    """
    for d in DIGITS:
        q = (a - d) / Z0
        if _is_gaussian(q):
            return d
    raise ValueError(f"No CNRS remainder exists for {a}")


# ---------------------------------------------------------------------------
# Greedy CNRS-A expansion
# ---------------------------------------------------------------------------

def gaussian_to_cnrs_digits(alpha: complex, max_digits: int = 10000) -> List[int]:
    """
    Greedy CNRS-A expansion of a Gaussian integer.

    Algorithm (demo/exact style):
      1. Snap alpha to nearest Gaussian integer.
      2. While current != 0:
           - d = cnrs_remainder(current)
           - append d to digit list (LSB first)
           - current = (current - d) / Z0, snapped back to Z[i]
      3. Trim trailing zeros (except if the number is exactly zero).

    Returns
    -------
    digits : list[int]
        Least-significant digit first: [d0, d1, ..., dn].
    """
    # Snap to nearest Gaussian integer
    current = complex(round(alpha.real), round(alpha.imag))

    if current == 0:
        return [0]

    digits: List[int] = []

    for _ in range(max_digits):
        if current == 0:
            break

        d = cnrs_remainder(current)
        digits.append(d)

        q = (current - d) / Z0
        current = complex(round(q.real), round(q.imag))
    else:
        raise RuntimeError(f"CNRS-A expansion did not terminate for {alpha}")

    # Trim trailing zeros (highest positions) while keeping at least one digit
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()

    return digits


def gaussian_to_cnrs_str(alpha: complex, max_digits: int = 10000) -> str:
    """
    Convenience wrapper: Gaussian integer -> CNRS-A string (MSB first, no decimal).

    Example:
        gaussian_to_cnrs_str(0+0j) -> "0"
        gaussian_to_cnrs_str(1+0j) -> "1"
    """
    digits = gaussian_to_cnrs_digits(alpha, max_digits=max_digits)
    # digits are LSB first; reverse for string
    s = "".join(str(d) for d in reversed(digits))
    return normalize_cnrs(s)


# ---------------------------------------------------------------------------
# CNRS-A -> Gaussian integer
# ---------------------------------------------------------------------------

def cnrs_to_gaussian(s: str) -> complex:
    """
    Evaluate a CNRS-A digit string as a Gaussian integer.

    Supports optional fractional part "int.frac", where the fractional digits
    represent negative powers of the base z0.

    Parameters
    ----------
    s : str
        CNRS-A digit string, e.g. "104", "23.1", "0", etc.

    Returns
    -------
    complex
        The corresponding Gaussian integer (or Gaussian rational if fractional).
    """
    if "." in s:
        int_part, frac_part = s.split(".")
    else:
        int_part, frac_part = s, ""

    # Integer part: Horner scheme in base Z0
    z = 0 + 0j
    for ch in int_part:
        z = z * Z0 + int(ch)

    # Fractional part: negative powers of Z0
    w = 0 + 0j
    for ch in reversed(frac_part):
        w = (w + int(ch)) / Z0

    return z + w


# ---------------------------------------------------------------------------
# Canonical normalization
# ---------------------------------------------------------------------------

def normalize_cnrs(s: str) -> str:
    """
    Canonical CNRS-A formatting:

      - strip leading zeros in integer part (but leave at least one digit)
      - strip trailing zeros in fractional part
      - remove '.' if fractional part becomes empty

    Examples
    --------
        "000"      -> "0"
        "0012"     -> "12"
        "010.230"  -> "10.23"
        "010.000"  -> "10"
    """
    if "." in s:
        int_part, frac_part = s.split(".")
    else:
        int_part, frac_part = s, ""

    int_part = int_part.lstrip("0") or "0"
    frac_part = frac_part.rstrip("0")

    if frac_part:
        return int_part + "." + frac_part
    return int_part
