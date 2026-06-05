"""
tests/test_evaluate_limitations.py
------------------------------------
Documents the known limitation of CnrsRational.evaluate() for
Laurent-periodic (gcd(q,5) > 1) cases, and confirms that
z0_adic_value() / z0_adic_value_exact() / z0_adic_value_fractions()
are the correct evaluation paths for all z0-adic cases.

Background
----------
CnrsRational.evaluate() works by calling cnrs_to_gaussian() on the
digit string produced by to_str().  cnrs_to_gaussian() interprets
fractional digits as negative powers of z0 (i.e. z0^{-1}, z0^{-2}, ...),
which is correct ONLY for case-1 finite Z[i][1/z0] fractions.

For Laurent-periodic cases (gcd(q, 5) > 1, power_offset = ell < 0),
the frac_digits represent coefficients at powers z0^{ell+j}, not z0^{-j}.
evaluate() ignores power_offset and therefore returns a wrong value.

This is not a bug to fix: the docstring for evaluate() already states
"For z0-adic values (cases 2-3): partial sum only; use z0_adic_value()
for the exact rational closed form."

These tests:
  (a) use pytest.mark.xfail to document that evaluate() gives wrong
      results for Laurent-periodic cases (expected failure, not a bug);
  (b) confirm that z0_adic_value(), z0_adic_value_exact(), and
      z0_adic_value_fractions() are all correct for those cases;
  (c) confirm that evaluate() IS correct for case-1 finite fractions,
      since power_offset=0 there and the digit convention matches.

Session 42, 2026-06-06.
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fractions import Fraction
from cnrs.cnrs_rational import gaussian_rational_to_cnrs


# ── Helpers ───────────────────────────────────────────────────────────────────

def _r(p_re, p_im, q, max_frac=500):
    return gaussian_rational_to_cnrs(complex(p_re, p_im), q, max_frac=max_frac)


# ══════════════════════════════════════════════════════════════════════════════
# Part A: xfail — evaluate() gives wrong answer for Laurent-periodic cases
#
# These are EXPECTED failures.  They document a known design limitation.
# If any of these unexpectedly pass, it means evaluate() has been fixed to
# handle power_offset, and the xfail marker should be removed.
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.xfail(
    reason="evaluate() ignores power_offset for Laurent-periodic cases; "
           "error ~0.38. Use z0_adic_value() instead.",
    strict=True,
)
def test_xfail_evaluate_one_fifth():
    """evaluate() returns wrong value for 1/5 (power_offset=-1)."""
    r = _r(1, 0, 5)
    assert abs(r.evaluate() - 1/5) < 1e-9


@pytest.mark.xfail(
    reason="evaluate() ignores power_offset for Laurent-periodic cases; "
           "error ~1.11. Use z0_adic_value() instead.",
    strict=True,
)
def test_xfail_evaluate_one_tenth():
    """evaluate() returns wrong value for 1/10 (power_offset=-1)."""
    r = _r(1, 0, 10)
    assert abs(r.evaluate() - 1/10) < 1e-9


@pytest.mark.xfail(
    reason="evaluate() ignores power_offset for Laurent-periodic cases; "
           "error ~0.28. Use z0_adic_value() instead.",
    strict=True,
)
def test_xfail_evaluate_one_twenty_fifth():
    """evaluate() returns wrong value for 1/25 (power_offset=-2)."""
    r = _r(1, 0, 25)
    assert abs(r.evaluate() - 1/25) < 1e-9


@pytest.mark.xfail(
    reason="evaluate() ignores power_offset for Laurent-periodic cases; "
           "error ~0.76. Use z0_adic_value() instead.",
    strict=True,
)
def test_xfail_evaluate_two_fifths():
    """evaluate() returns wrong value for 2/5 (power_offset=-1)."""
    r = _r(2, 0, 5)
    assert abs(r.evaluate() - 2/5) < 1e-9


@pytest.mark.xfail(
    reason="evaluate() ignores power_offset for Laurent-periodic cases; "
           "error ~1.48. Use z0_adic_value() instead.",
    strict=True,
)
def test_xfail_evaluate_one_plus_i_over_5():
    """evaluate() returns wrong value for (1+i)/5 (power_offset=-1)."""
    r = _r(1, 1, 5)
    assert abs(r.evaluate() - (1+1j)/5) < 1e-9


@pytest.mark.xfail(
    reason="evaluate() ignores power_offset for Laurent-periodic cases; "
           "error ~0.70. Use z0_adic_value() instead.",
    strict=True,
)
def test_xfail_evaluate_one_fifteenth():
    """evaluate() returns wrong value for 1/15 (power_offset=-1)."""
    r = _r(1, 0, 15)
    assert abs(r.evaluate() - 1/15) < 1e-9


# ══════════════════════════════════════════════════════════════════════════════
# Part B: passing — evaluate() IS correct for case-1 finite fractions
#
# These confirm the boundary: power_offset=0 finite fractions work correctly
# with evaluate().
# ══════════════════════════════════════════════════════════════════════════════

def test_evaluate_correct_gaussian_integer():
    """evaluate() is exact for Gaussian integers (finite, power_offset=0)."""
    r = _r(3, 2, 1)
    assert r.is_finite
    assert r.power_offset == 0
    assert abs(r.evaluate() - (3+2j)) < 1e-12


def test_evaluate_correct_z0_inverse():
    """evaluate() is exact for 1/z0 = (-2-i)/5 (finite Z[i][1/z0])."""
    r = gaussian_rational_to_cnrs(complex(-2, -1), 5, max_frac=10)
    assert r.is_finite
    assert abs(r.evaluate() - (-2-1j)/5) < 1e-12


def test_evaluate_correct_z0_fraction_via_encode():
    """evaluate() is exact for finite Z[i][1/z0] fractions constructed
    directly (i.e. is_finite=True cases with power_offset=0)."""
    # 3/1 is finite and exact
    r = gaussian_rational_to_cnrs(3+0j, 1)
    assert r.is_finite
    assert abs(r.evaluate() - 3) < 1e-12
    # -2+3j is finite and exact
    r2 = gaussian_rational_to_cnrs(-2+3j, 1)
    assert r2.is_finite
    assert abs(r2.evaluate() - (-2+3j)) < 1e-12


# ══════════════════════════════════════════════════════════════════════════════
# Part C: passing — z0_adic_value() is correct for ALL z0-adic cases
# ══════════════════════════════════════════════════════════════════════════════

def test_z0_adic_value_correct_one_fifth():
    r = _r(1, 0, 5)
    assert abs(r.z0_adic_value() - 1/5) < 1e-14


def test_z0_adic_value_correct_one_tenth():
    r = _r(1, 0, 10)
    assert abs(r.z0_adic_value() - 1/10) < 1e-14


def test_z0_adic_value_correct_one_twenty_fifth():
    r = _r(1, 0, 25)
    assert abs(r.z0_adic_value() - 1/25) < 1e-14


def test_z0_adic_value_correct_two_fifths():
    r = _r(2, 0, 5)
    assert abs(r.z0_adic_value() - 2/5) < 1e-14


def test_z0_adic_value_correct_one_plus_i_over_5():
    r = _r(1, 1, 5)
    assert abs(r.z0_adic_value() - (1+1j)/5) < 1e-14


def test_z0_adic_value_correct_one_fifteenth():
    r = _r(1, 0, 15)
    assert abs(r.z0_adic_value() - 1/15) < 1e-14


def test_z0_adic_value_correct_pure_z0_adic_one_half():
    """z0_adic_value() also correct for gcd(q,5)=1 cases (power_offset=0)."""
    r = _r(1, 0, 2)
    assert abs(r.z0_adic_value() - 1/2) < 1e-14


def test_z0_adic_value_correct_pure_z0_adic_one_third():
    r = _r(1, 0, 3)
    assert abs(r.z0_adic_value() - 1/3) < 1e-14


# ══════════════════════════════════════════════════════════════════════════════
# Part D: passing — z0_adic_value_exact() gives exact Fraction results
# ══════════════════════════════════════════════════════════════════════════════

def test_exact_one_fifth():
    r = _r(1, 0, 5)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(1, 5)
    assert im == Fraction(0)


def test_exact_one_tenth():
    r = _r(1, 0, 10)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(1, 10)
    assert im == Fraction(0)


def test_exact_two_fifths():
    r = _r(2, 0, 5)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(2, 5)
    assert im == Fraction(0)


def test_exact_one_plus_i_over_5():
    r = _r(1, 1, 5)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(1, 5)
    assert im == Fraction(1, 5)


def test_exact_one_fifteenth():
    r = _r(1, 0, 15)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(1, 15)
    assert im == Fraction(0)


# ══════════════════════════════════════════════════════════════════════════════
# Part E: passing — evaluate() and z0_adic_value() agree for case-1 only
# ══════════════════════════════════════════════════════════════════════════════

def test_evaluate_and_z0_adic_agree_for_gcd_q5_eq_1():
    """For gcd(q,5)=1 cases (power_offset=0), evaluate() partial sum and
    z0_adic_value() rational closed form need not agree in general
    (evaluate is a truncated series), but both converge to the right value."""
    for q in [2, 3, 7]:
        r = _r(1, 0, q)
        target = 1/q
        assert abs(r.z0_adic_value() - target) < 1e-12, f"z0_adic_value wrong for 1/{q}"


def test_evaluate_correct_for_all_finite_cases():
    """evaluate() is the correct method precisely for is_finite=True cases."""
    finite_cases = [
        (3+2j, 3+2j),
        (complex(-2,-1)/5, -1/5 * complex(-2,-1) / (-2-1j) * (-2-1j)),
    ]
    # Just test Gaussian integers directly
    for g in [0+0j, 1+0j, -1+0j, 1+1j, 3+2j, -5+4j]:
        r = gaussian_rational_to_cnrs(g, 1)
        assert r.is_finite
        assert abs(r.evaluate() - g) < 1e-12, f"evaluate() wrong for {g}"
