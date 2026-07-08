"""
cnrs_add.py
-----------
CNRS-A addition via the 14-state finite-state transducer.

This module builds the full addition transition table at import time
using the canonical carry set and the CNRS remainder logic.

Base:   z0 = -2 + i
Digits: D = {0, 1, 2, 3, 4}
"""

from __future__ import annotations
from typing import Dict, Tuple
from .cnrs_repr import Z0, cnrs_remainder, normalize_cnrs


# ---------------------------------------------------------------------------
# Canonical carry set (14 Gaussian integers)
# ---------------------------------------------------------------------------

CARRY_SET_PAIRS = [
    (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (-1, -1), (-2, 0), (2, 1), (-2, -1),
    (-2, -2), (2, 2), (-3, -1), (-3, -2),
]

CARRY_SET = [complex(re, im) for re, im in CARRY_SET_PAIRS]
CARRY_INDEX = {(re, im): idx for idx, (re, im) in enumerate(CARRY_SET_PAIRS)}


def _carry_to_idx(kappa: complex) -> int:
    """Convert Gaussian carry to canonical index."""
    key = (int(round(kappa.real)), int(round(kappa.imag)))
    return CARRY_INDEX[key]


# ---------------------------------------------------------------------------
# Build the full 14 × 5 × 5 transition table
# ---------------------------------------------------------------------------

def _build_addition_table() -> Dict[Tuple[int, int, int], Tuple[int, int]]:
    """
    Build the CNRS-A addition transition table:

        (carry_state, digit_a, digit_b) → (output_digit, next_carry_state)

    This is the same construction used in the demo/exact implementations.
    """
    table = {}

    for carry_idx, kappa in enumerate(CARRY_SET):
        for a in range(5):
            for b in range(5):
                raw = kappa + a + b
                d = cnrs_remainder(raw)
                next_kappa = (raw - d) / Z0

                nk_key = (int(round(next_kappa.real)), int(round(next_kappa.imag)))
                if nk_key not in CARRY_INDEX:
                    raise RuntimeError(
                        f"Carry escaped canonical set: {kappa}, a={a}, b={b}, next={next_kappa}"
                    )

                next_idx = CARRY_INDEX[nk_key]
                table[(carry_idx, a, b)] = (d, next_idx)

    return table


# Build once at import time
ADDITION_TABLE = _build_addition_table()


# ---------------------------------------------------------------------------
# CNRS-A addition
# ---------------------------------------------------------------------------

def add_cnrs(a: str, b: str) -> str:
    """
    Add two CNRS-A digit strings using the 14-state addition transducer.

    Steps:
      1. Align fractional parts (ljust with zeros).
      2. Align integer parts (zfill to equal width).
      3. Add digits right-to-left using the transition table.
      4. Drain remaining carry.
      5. Reinsert decimal point.
      6. Canonically normalize.

    Returns
    -------
    str
        CNRS-A digit string representing the sum.
    """
    # Split into integer and fractional parts
    if "." in a:
        a_int, a_frac = a.split(".")
    else:
        a_int, a_frac = a, ""

    if "." in b:
        b_int, b_frac = b.split(".")
    else:
        b_int, b_frac = b, ""

    # Align fractional lengths (pad right with zeros)
    max_frac = max(len(a_frac), len(b_frac))
    a_frac = a_frac.ljust(max_frac, "0")
    b_frac = b_frac.ljust(max_frac, "0")

    # Align integer lengths (pad left with zeros so zip sees all digits)
    max_int = max(len(a_int), len(b_int))
    a_int = a_int.zfill(max_int)
    b_int = b_int.zfill(max_int)

    # Combine into pure digit strings
    A = a_int + a_frac
    B = b_int + b_frac

    # Add from right to left
    carry_idx = 0
    out = []

    for da, db in zip(reversed(A), reversed(B)):
        key = (carry_idx, int(da), int(db))
        d, carry_idx = ADDITION_TABLE[key]
        out.append(str(d))

    # Drain carry.
    # The carry is always an element of the 14-state canonical set, so it
    # must reach state 0 within 14 steps.  Guard is set to 20 for safety margin.
    drain_guard = 0
    while carry_idx != 0:
        d, carry_idx = ADDITION_TABLE[(carry_idx, 0, 0)]
        out.append(str(d))
        drain_guard += 1
        if drain_guard > 20:
            raise RuntimeError("Carry did not drain in CNRS-A addition")

    # Reverse to MSB-first
    raw = "".join(reversed(out))

    # Reinsert decimal
    if max_frac > 0:
        raw = raw[:-max_frac] + "." + raw[-max_frac:]

    return normalize_cnrs(raw)
