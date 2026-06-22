"""
cnrs_verify.py
--------------
Verification suite for CNRS-A and Layer-2 arithmetic.

Tests included:
  - Representation round-trip
  - Addition correctness
  - Multiplication correctness
  - Layer-2 branch arithmetic
  - Randomized fuzzing

All tests compare CNRS results against Gaussian integer semantics.
"""

from __future__ import annotations
import random
from typing import List, Tuple

from .cnrs_repr import (
    gaussian_to_cnrs_str,
    cnrs_to_gaussian,
    normalize_cnrs,
)
from .cnrs_add import add_cnrs
from .cnrs_mul import mul_cnrs
from .cnrs_layer2 import Layer2


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _rand_gint(radius: int = 5) -> complex:
    """Random Gaussian integer a + bi with |a|,|b| <= radius."""
    return complex(random.randint(-radius, radius),
                   random.randint(-radius, radius))


def _assert_equal_gaussian(label: str, cnrs_val: str, expected: complex):
    """Check CNRS string equals expected Gaussian value."""
    got = cnrs_to_gaussian(cnrs_val)
    if got != expected:
        raise AssertionError(
            f"{label} failed:\n"
            f"  CNRS: {cnrs_val} -> {got}\n"
            f"  Expected: {expected}"
        )


# ---------------------------------------------------------------------------
# Representation tests
# ---------------------------------------------------------------------------

def test_representation_roundtrip(samples: int = 200):
    """
    Check gaussian_to_cnrs_str ∘ cnrs_to_gaussian = identity
    for random Gaussian integers.
    """
    for _ in range(samples):
        g = _rand_gint()
        s = gaussian_to_cnrs_str(g)
        g2 = cnrs_to_gaussian(s)
        if g != g2:
            raise AssertionError(
                f"Representation round-trip failed:\n"
                f"  g = {g}\n"
                f"  s = {s}\n"
                f"  g2 = {g2}"
            )


# ---------------------------------------------------------------------------
# Addition tests
# ---------------------------------------------------------------------------

def test_addition(samples: int = 200):
    """
    Check CNRS-A addition against Gaussian integer addition.
    """
    for _ in range(samples):
        a = _rand_gint()
        b = _rand_gint()
        sa = gaussian_to_cnrs_str(a)
        sb = gaussian_to_cnrs_str(b)
        sc = add_cnrs(sa, sb)
        _assert_equal_gaussian("Addition", sc, a + b)


# ---------------------------------------------------------------------------
# Multiplication tests
# ---------------------------------------------------------------------------

def test_multiplication(samples: int = 200):
    """
    Check CNRS-A multiplication against Gaussian integer multiplication.
    """
    for _ in range(samples):
        a = _rand_gint()
        b = _rand_gint()
        sa = gaussian_to_cnrs_str(a)
        sb = gaussian_to_cnrs_str(b)
        sc = mul_cnrs(sa, sb)
        _assert_equal_gaussian("Multiplication", sc, a * b)


# ---------------------------------------------------------------------------
# Layer-2 tests
# ---------------------------------------------------------------------------

def test_layer2(samples: int = 100):
    """
    Check Layer-2 arithmetic:
      (z1,k1) + (z2,k2) = (z1+z2, 0)        [branch reset, per P2 Capstone
                                              Prop. "Properties of (X~,+)" (iv)]
      (z1,k1) * (z2,k2) = (z1*z2, k1+k2)    [branch accumulation]

    Fixed (Thread 19 downstream check): this previously asserted k1+k2
    for addition, matching a bug in Layer2.__add__ rather than the
    proved capstone result. Multiplication's k1+k2 rule is unaffected
    and was already correct.
    """
    for _ in range(samples):
        g1 = _rand_gint()
        g2 = _rand_gint()
        k1 = random.randint(-5, 5)
        k2 = random.randint(-5, 5)

        L1 = Layer2.from_gaussian(g1, k1)
        L2 = Layer2.from_gaussian(g2, k2)

        # Addition (branch reset)
        Ls = L1 + L2
        if Ls.to_gaussian() != g1 + g2:
            raise AssertionError("Layer-2 addition Gaussian mismatch")
        if Ls.k != 0:
            raise AssertionError("Layer-2 addition branch mismatch (expected reset to 0)")

        # Multiplication (branch accumulation)
        Lm = L1 * L2
        if Lm.to_gaussian() != g1 * g2:
            raise AssertionError("Layer-2 multiplication Gaussian mismatch")
        if Lm.k != k1 + k2:
            raise AssertionError("Layer-2 multiplication branch mismatch")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_all_tests():
    """
    Run all CNRS verification tests.
    """
    print("Running CNRS verification suite...")

    test_representation_roundtrip()
    print("  ✓ Representation round-trip")

    test_addition()
    print("  ✓ Addition")

    test_multiplication()
    print("  ✓ Multiplication")

    test_layer2()
    print("  ✓ Layer-2 arithmetic")

    print("All CNRS tests passed.")
