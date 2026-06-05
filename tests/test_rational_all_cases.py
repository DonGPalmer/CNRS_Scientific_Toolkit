"""
tests/test_rational_all_cases.py
---------------------------------
Tests for the full CNRS Gaussian rational representation.

Cases with gcd(q, 5) == 1 use the pure z0-adic algorithm (power_offset=0).
Cases with gcd(q, 5) > 1 use the Laurent-periodic algorithm (power_offset<0).
All evaluate correctly to machine precision via z0_adic_value().

Three cases are covered:
  1. Finite Z[i][1/z0] fractions (stable boundary tests).
  2. Pure z0-adic periodic rationals: gcd(q, 5) = 1, power_offset = 0.
  3. Laurent-periodic z0-adic rationals: q divisible by 5, power_offset < 0.

In all cases the value is assigned by the rational closed form

    value = pre_val + period_block / (1 - z0^T)

and is NOT a convergent series in C.  Use z0_adic_value_exact() for
guaranteed precision at long periods.

Long-period rationals (e.g. 1/23, period length 528) require increased
max_frac; exhausting max_frac without period detection raises RuntimeError.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from cnrs.cnrs_rational import gaussian_rational_to_cnrs


# ── Helper ────────────────────────────────────────────────────────────────────

def _check_z0_adic(p_re, p_im, q, tol=1e-10, expected_offset=0):
    r = gaussian_rational_to_cnrs(complex(p_re, p_im), q, max_frac=200)
    assert r.is_z0_adic, f"Expected z0-adic expansion but is_z0_adic=False"
    assert r.power_offset == expected_offset, (
        f"Expected power_offset={expected_offset}, got {r.power_offset}"
    )
    val = r.z0_adic_value()
    target = (p_re + p_im * 1j) / q
    err = abs(val - target)
    assert err < tol, (
        f"({p_re}+{p_im}i)/{q}: z0_adic_value error {err:.2e} > {tol}. "
        f"period_start={r.period_start}, power_offset={r.power_offset}, "
        f"value={val!r}, target={target!r}"
    )
    assert not r.is_finite, "Should be infinite/periodic"


# ── gcd(q,5)==1: pure z0-adic (power_offset=0) ───────────────────────────────

def test_one_half():
    _check_z0_adic(1, 0, 2, expected_offset=0)

def test_one_third():
    _check_z0_adic(1, 0, 3, expected_offset=0)

def test_one_seventh():
    _check_z0_adic(1, 0, 7, expected_offset=0)

def test_two_thirds():
    _check_z0_adic(2, 0, 3, expected_offset=0)

def test_one_plus_i_over_2():
    _check_z0_adic(1, 1, 2, expected_offset=0)

def test_two_minus_i_over_3():
    _check_z0_adic(2, -1, 3, expected_offset=0)

def test_i_over_7():
    _check_z0_adic(0, 1, 7, expected_offset=0)


# ── gcd(q,5)>1: Laurent-periodic (power_offset<0) ────────────────────────────

def test_one_fifth():
    """1/5 = z0^{-1} * 1/z0bar; Laurent-periodic with power_offset=-1."""
    _check_z0_adic(1, 0, 5, expected_offset=-1)

def test_one_tenth():
    """1/10 = 1/(5*2); power_offset=-1."""
    _check_z0_adic(1, 0, 10, expected_offset=-1)

def test_one_twenty_fifth():
    """1/25 = z0^{-2} * 1/z0bar^2; power_offset=-2."""
    _check_z0_adic(1, 0, 25, expected_offset=-2)

def test_two_fifths():
    """2/5; power_offset=-1."""
    _check_z0_adic(2, 0, 5, expected_offset=-1)

def test_one_plus_i_over_5():
    """(1+i)/5; power_offset=-1."""
    _check_z0_adic(1, 1, 5, expected_offset=-1)

def test_one_fifteenth():
    """1/15 = 1/(5*3); power_offset=-1."""
    _check_z0_adic(1, 0, 15, expected_offset=-1)


# ── Stable boundary: must not regress ────────────────────────────────────────

def test_one_over_z0_still_works():
    r = gaussian_rational_to_cnrs(complex(-2, -1), 5, max_frac=10)
    assert r.is_finite
    assert not r.is_z0_adic
    assert abs(r.evaluate() - (-2-1j)/5) < 1e-9

def test_gaussian_integer_still_works():
    r = gaussian_rational_to_cnrs(3+2j, 1)
    assert r.is_finite
    assert not r.is_z0_adic
    assert abs(r.evaluate() - (3+2j)) < 1e-9


# ── Long-period rationals ────────────────────────────────────────────────────

def test_long_period_1_over_23():
    """1/23 has period length 528; requires max_frac=1000."""
    r = gaussian_rational_to_cnrs(1, 23, max_frac=1000)
    assert r.is_z0_adic
    assert r.period_start == 0
    assert r.period_length == 528
    err = abs(r.z0_adic_value_exact() - 1/23)
    assert err < 1e-14, f"1/23 exact error {err:.2e}"

def test_long_period_1_over_31():
    """1/31 has period length 96; moderate period."""
    r = gaussian_rational_to_cnrs(1, 31, max_frac=200)
    assert r.is_z0_adic
    assert r.period_start == 0
    assert r.period_length == 96
    err = abs(r.z0_adic_value_exact() - 1/31)
    assert err < 1e-14, f"1/31 exact error {err:.2e}"

def test_moderate_period_1_over_11():
    """1/11 has period length 15."""
    r = gaussian_rational_to_cnrs(1, 11, max_frac=100)
    assert r.is_z0_adic
    assert r.period_start is not None
    assert r.period_length == 15
    err = abs(r.z0_adic_value_exact() - 1/11)
    assert err < 1e-14, f"1/11 exact error {err:.2e}"

def test_laurent_long_7_3i_over_125():
    """(7+3i)/125: Laurent-periodic, power_offset=-3, moderate period."""
    r = gaussian_rational_to_cnrs(7+3j, 125, max_frac=500)
    assert r.is_z0_adic
    assert r.power_offset == -3
    err = abs(r.z0_adic_value_exact() - (7+3j)/125)
    assert err < 1e-14, f"(7+3i)/125 exact error {err:.2e}"

def test_laurent_long_123_45i_over_250():
    """(123-45i)/250: Laurent-periodic, power_offset=-3  (250 = 2*5^3)."""
    r = gaussian_rational_to_cnrs(123-45j, 250, max_frac=500)
    assert r.is_z0_adic
    assert r.power_offset == -3
    err = abs(r.z0_adic_value_exact() - (123-45j)/250)
    assert err < 1e-13, f"(123-45i)/250 exact error {err:.2e}"

def test_z0_adic_exact_vs_float_agreement():
    """z0_adic_value_exact() and z0_adic_value() agree for short periods."""
    for q in [2, 3, 7, 5, 10, 15]:
        r = gaussian_rational_to_cnrs(1, q, max_frac=500)
        exact = r.z0_adic_value_exact()
        fast = r.z0_adic_value()
        err = abs(exact - fast)
        assert err < 1e-8, f"1/{q}: exact vs float disagree by {{err:.2e}}"


# ── max_frac exhaustion raises RuntimeError ──────────────────────────────────

def test_max_frac_too_small_raises():
    """max_frac=200 is too small for 1/23 (period 528); must raise."""
    with pytest.raises(RuntimeError, match="No period detected"):
        gaussian_rational_to_cnrs(1, 23, max_frac=200)

def test_max_frac_too_small_raises_1_over_23_small():
    """max_frac=50 is too small for 1/23 (period 528); must raise."""
    with pytest.raises(RuntimeError, match="No period detected"):
        gaussian_rational_to_cnrs(1, 23, max_frac=50)


# ── Exact Fraction equality tests ────────────────────────────────────────────

def test_fraction_exact_one_half():
    """1/2: exact Fraction equality."""
    from fractions import Fraction
    r = gaussian_rational_to_cnrs(1, 2, max_frac=50)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(1, 2)
    assert im == Fraction(0)

def test_fraction_exact_one_third():
    """1/3: exact Fraction equality."""
    from fractions import Fraction
    r = gaussian_rational_to_cnrs(1, 3, max_frac=50)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(1, 3)
    assert im == Fraction(0)

def test_fraction_exact_one_fifth():
    """1/5: Laurent-periodic, exact Fraction equality."""
    from fractions import Fraction
    r = gaussian_rational_to_cnrs(1, 5, max_frac=50)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(1, 5)
    assert im == Fraction(0)

def test_fraction_exact_one_over_23():
    """1/23: long period (528), exact Fraction equality."""
    from fractions import Fraction
    r = gaussian_rational_to_cnrs(1, 23, max_frac=1000)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(1, 23)
    assert im == Fraction(0)

def test_fraction_exact_laurent_7_3i_over_125():
    """(7+3i)/125: Laurent-periodic, power_offset=-3, exact Fraction equality."""
    from fractions import Fraction
    r = gaussian_rational_to_cnrs(7+3j, 125, max_frac=500)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(7, 125)
    assert im == Fraction(3, 125)

def test_fraction_exact_gaussian_rational_mixed():
    """(2-i)/3: complex Gaussian rational, exact Fraction equality."""
    from fractions import Fraction
    r = gaussian_rational_to_cnrs(2-1j, 3, max_frac=100)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(2, 3)
    assert im == Fraction(-1, 3)
