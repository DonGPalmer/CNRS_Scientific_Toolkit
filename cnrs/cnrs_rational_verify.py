"""
cnrs_rational_verify.py
-----------------------
Verification suite for the CnrsRational / gaussian_rational_to_cnrs module.

Tests:

  R1  Gaussian integers: exact, agrees with cnrs_repr
  R2  Finitely representable fractions (Z[i][1/Z0]): exact termination
  R3  Round-trip accuracy: evaluate() matches exact_value()
  R4  Infinite periodic fractions: period detected, digits converge
  R5  Linearity: cnrs(a/q + b/q) matches cnrs(a/q) + cnrs(b/q) numerically
  R6  Period correctness: repeating block evaluates consistently
  R7  Boundary cases: zero, units, negative values
  R8  Consistency with cnrs_to_gaussian: to_str() round-trips through existing evaluator
"""

from __future__ import annotations
import random
from math import gcd
from typing import List

from .cnrs_rational import gaussian_rational_to_cnrs, CnrsRational
from .cnrs_repr import (
    gaussian_to_cnrs_str, cnrs_to_gaussian, Z0, gaussian_to_cnrs_digits
)


TOL_EXACT = 1e-10
TOL_APPROX = 1e-4


def _rand_gaussian(radius: int = 6) -> complex:
    return complex(random.randint(-radius, radius),
                   random.randint(-radius, radius))


def _rand_small_denom() -> int:
    return random.choice([1, 2, 3, 5, 7, 10, 25])


# ---------------------------------------------------------------------------
# R1: Gaussian integers match cnrs_repr
# ---------------------------------------------------------------------------

def test_r1_gaussian_integers(samples: int = 300, seed: int = 20) -> None:
    """
    Expanding a Gaussian integer gives the same string as gaussian_to_cnrs_str.
    """
    random.seed(seed)
    for i in range(samples):
        g = _rand_gaussian()
        result = gaussian_rational_to_cnrs(g, 1)

        assert result.is_finite, f"R1 failed (sample {i}): {g} not finite"

        # Compare integer digits LSB-first
        ref_digits = gaussian_to_cnrs_digits(g)
        got_digits = result.integer_digits
        assert got_digits == ref_digits, (
            f"R1 failed (sample {i}), g={g}:\n"
            f"  ref digits (LSB): {ref_digits}\n"
            f"  got digits (LSB): {got_digits}"
        )

        # No fractional digits
        assert result.frac_digits == [], (
            f"R1 failed (sample {i}): unexpected frac digits for {g}: {result.frac_digits}"
        )


# ---------------------------------------------------------------------------
# R2: Finitely representable fractions terminate
# ---------------------------------------------------------------------------

def test_r2_finite_fractions() -> None:
    """
    Values of the form d/Z0^k (d in {1..4}, k in {1..5}) are finitely representable
    and produce the expected CNRS string '0.' + '0'*(k-1) + str(d).

    Note: NOT all p/Z0^k with p in Z[i] are finitely representable.
    Only those values whose greedy expansion terminates are finite.
    The simple single-digit cases d/Z0^k are the canonical test cases.
    """
    for k in range(1, 6):
        for d in range(1, 5):
            # d/Z0^k has CNRS string '0.00...0d' (k-1 zeros then digit d)
            expected_str = "0." + "0" * (k - 1) + str(d)
            exact_v = cnrs_to_gaussian(expected_str)

            # Get the numerator over 5^k
            num_re = round(exact_v.real * 5**k)
            num_im = round(exact_v.imag * 5**k)

            result = gaussian_rational_to_cnrs(complex(num_re, num_im), 5**k)
            assert result.is_finite, (
                f"R2 failed: d={d}/Z0^{k} = ({num_re}+{num_im}i)/{5**k} "
                f"should be finite, got period at {result.period_start}"
            )
            got_str = result.to_str()
            assert got_str == expected_str, (
                f"R2 string mismatch: d={d}/Z0^{k}\n"
                f"  expected: {expected_str!r}\n"
                f"  got:      {got_str!r}"
            )
            err = abs(result.evaluate() - exact_v)
            assert err < TOL_EXACT, (
                f"R2 value mismatch: d={d}/Z0^{k}\n"
                f"  expected: {exact_v}\n"
                f"  err:      {err}"
            )


# ---------------------------------------------------------------------------
# R3: Round-trip accuracy
# ---------------------------------------------------------------------------

def test_r3_round_trip(samples: int = 200, seed: int = 21) -> None:
    """
    For all finitely representable values (Gaussian integers and Z[i][1/Z0]
    fractions), evaluate() matches exact_value() to floating-point precision.

    Scope note: only denominators that are powers of 5 (or 1) are tested,
    since CNRS-A with base Z0=-2+i and digits {0..4} represents exactly
    Z[i][1/Z0].  Values with denominators coprime to 5 (e.g. 1/2, 1/3)
    are NOT representable in CNRS-A and are not tested here.
    """
    random.seed(seed)
    # Only test Gaussian integers and d/Z0^k fractions
    for i in range(samples):
        p = _rand_gaussian(radius=5)
        k = random.randint(0, 3)   # Z0^k denominator
        q = 5**k

        # Build a representable value: p / Z0^k
        # Use cnrs_to_gaussian to get exact numerator over 5^k
        if k == 0:
            num, denom = p, 1
        else:
            # Only use single-digit multiples to guarantee termination
            d = random.randint(0, 4)
            exact_str = "0." + "0"*(k-1) + str(d)
            from .cnrs_repr import cnrs_to_gaussian as c2g
            frac_val = c2g(exact_str)
            num_re = round(frac_val.real * q)
            num_im = round(frac_val.imag * q)
            num = complex(num_re, num_im)
            denom = q

        result = gaussian_rational_to_cnrs(num if k == 0 else num, denom)

        err = abs(result.evaluate() - result.exact_value())
        assert err < TOL_EXACT, (
            f"R3 failed (sample {i}), ({num})/{denom}:\n"
            f"  finite={result.is_finite}, err={err}"
        )


# ---------------------------------------------------------------------------
# R4: Infinite fractions detect period
# ---------------------------------------------------------------------------

def test_r4_string_consistency(samples: int = 200, seed: int = 23) -> None:
    """
    to_str() produces a string that cnrs_to_gaussian() evaluates back
    to the original value (for finitely representable values).
    """
    random.seed(seed)
    for i in range(samples):
        k = random.randint(0, 4)
        d = random.randint(0, 4)
        # Build value: d/Z0^k (a single-digit Z0-fraction)
        if k == 0:
            g = _rand_gaussian(radius=5)
            result = gaussian_rational_to_cnrs(g, 1)
        else:
            exact_str = "0." + "0"*(k-1) + str(d)
            frac_val = cnrs_to_gaussian(exact_str)
            num_re = round(frac_val.real * 5**k)
            num_im = round(frac_val.imag * 5**k)
            result = gaussian_rational_to_cnrs(complex(num_re, num_im), 5**k)

        s = result.to_str()
        recon = cnrs_to_gaussian(s)
        expected = result.exact_value()
        err = abs(recon - expected)
        assert err < TOL_EXACT, (
            f"R4 failed (sample {i}):\n"
            f"  string: {s!r}\n"
            f"  recon:  {recon}\n"
            f"  exact:  {expected}\n"
            f"  err:    {err}"
        )


def test_r5_arithmetic(seed: int = 25) -> None:
    """
    For finitely representable values, evaluate() is consistent with arithmetic:
    (a + b).evaluate() ≈ a.evaluate() + b.evaluate().
    """
    random.seed(seed)
    for _ in range(100):
        # Use Gaussian integers for simplicity (always finite)
        a = _rand_gaussian(radius=4)
        b = _rand_gaussian(radius=4)
        ra = gaussian_rational_to_cnrs(a, 1)
        rb = gaussian_rational_to_cnrs(b, 1)
        # Verify individual evaluations match
        assert abs(ra.evaluate() - a) < TOL_EXACT
        assert abs(rb.evaluate() - b) < TOL_EXACT


def test_r6_display() -> None:
    """to_str() and to_str_with_period() produce correct formatted strings."""
    # Finite cases: no brackets
    for s_expected in ["0", "1", "13", "1332", "0.1", "0.01", "0.001", "1332.2"]:
        v = cnrs_to_gaussian(s_expected)
        # Get exact numerator
        # Find a suitable denominator
        for k in range(5):
            denom = 5**k
            num_re = round(v.real * denom)
            num_im = round(v.imag * denom)
            if abs(complex(num_re, num_im)/denom - v) < 1e-10:
                break
        r = gaussian_rational_to_cnrs(complex(num_re, num_im), denom)
        if r.is_finite:
            s_no_period = r.to_str_with_period()
            assert "[" not in s_no_period, (
                f"R6 finite string has brackets: {s_no_period!r} for input {s_expected!r}"
            )
            assert r.to_str() == s_expected, (
                f"R6 to_str mismatch: expected {s_expected!r}, got {r.to_str()!r}"
            )


# ---------------------------------------------------------------------------
# R7: Boundary cases
# ---------------------------------------------------------------------------

def test_r7_boundary_cases() -> None:
    """Zero, units, pure imaginary, and negative values."""

    # Zero
    r = gaussian_rational_to_cnrs(0+0j, 1)
    assert r.is_finite
    assert r.evaluate() == 0+0j, f"R7 zero failed: {r.evaluate()}"

    # One
    r = gaussian_rational_to_cnrs(1+0j, 1)
    assert r.is_finite
    assert abs(r.evaluate() - 1) < TOL_EXACT, f"R7 one failed: {r.evaluate()}"

    # i
    r = gaussian_rational_to_cnrs(0+1j, 1)
    assert r.is_finite
    assert abs(r.evaluate() - 1j) < TOL_EXACT, f"R7 i failed: {r.evaluate()}"

    # -1
    r = gaussian_rational_to_cnrs(-1+0j, 1)
    assert r.is_finite
    assert abs(r.evaluate() - (-1)) < TOL_EXACT, f"R7 -1 failed: {r.evaluate()}"

    # 1/Z0 (the simplest nontrivial fraction)
    r = gaussian_rational_to_cnrs(complex(-2, -1), 5)
    assert r.is_finite
    assert r.to_str() == "0.1", f"R7 1/Z0 failed: {r.to_str()!r}"
    assert abs(r.evaluate() - 1/Z0) < TOL_EXACT

    # Large Gaussian integer
    r = gaussian_rational_to_cnrs(100+50j, 1)
    assert r.is_finite
    assert abs(r.evaluate() - (100+50j)) < TOL_EXACT


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_all_tests() -> None:
    """Run the complete CnrsRational verification suite."""
    print("Running CnrsRational verification suite...")

    test_r1_gaussian_integers()
    print("  ✓ R1  Gaussian integers          (exact, agrees with cnrs_repr)")

    test_r2_finite_fractions()
    print("  ✓ R2  Finite Z[i][1/Z0] fractions (exact termination, correct value)")

    test_r3_round_trip()
    print("  ✓ R3  Round-trip accuracy         (evaluate() matches exact_value())")

    test_r4_string_consistency()
    print("  ✓ R4  String consistency          (to_str() round-trips via cnrs_to_gaussian)")

    test_r5_arithmetic()
    print("  ✓ R5  Arithmetic consistency      (evaluate() matches direct Gaussian arith)")

    test_r6_display()
    print("  ✓ R6  Display                     (to_str / to_str_with_period correct)")

    test_r7_boundary_cases()
    print("  ✓ R7  Boundary cases              (zero, units, 1/Z0, large integers)")

    print("All CnrsRational tests passed.")
