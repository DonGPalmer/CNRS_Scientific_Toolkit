"""
tests/test_rational_arithmetic.py
-----------------------------------
Tests for CnrsRational exact arithmetic operators: __add__, __sub__,
__mul__, __neg__, __eq__.

All arithmetic is exact: results are verified at the Fraction level
(no floating-point tolerance) where possible, and to 1e-12 otherwise.

Cases covered:
  - gcd(q,5)=1 + gcd(q,5)=1   (pure z0-adic + pure z0-adic)
  - gcd(q,5)>1 + gcd(q,5)>1   (Laurent + Laurent)
  - gcd(q,5)=1 + gcd(q,5)>1   (pure z0-adic + Laurent)
  - finite + z0-adic             (Gaussian integer + periodic)
  - complex Gaussian rationals   ((a+bi)/q arithmetic)
  - additive inverse and zero
  - equality operator

Session 42, 2026-06-06.
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fractions import Fraction
from cnrs.cnrs_rational import gaussian_rational_to_cnrs, CnrsRational


# ── Helpers ───────────────────────────────────────────────────────────────────

def _r(p_re, p_im, q, max_frac=500):
    return gaussian_rational_to_cnrs(complex(p_re, p_im), q, max_frac=max_frac)

def _val(r):
    """Exact float value of a CnrsRational."""
    if r.is_z0_adic:
        return r.z0_adic_value_exact()
    return r.exact_value()

def _frac(r):
    """Exact Fraction pair (re, im) of a CnrsRational."""
    if r.is_z0_adic:
        return r.z0_adic_value_fractions()
    return Fraction(r.numerator_re, r.denominator), Fraction(r.numerator_im, r.denominator)

def _check(label, r, expected_re, expected_im=0, tol=1e-12):
    v = _val(r)
    assert abs(v.real - expected_re) < tol, f"{label} real: {v.real} != {expected_re}"
    assert abs(v.imag - expected_im) < tol, f"{label} imag: {v.imag} != {expected_im}"

def _check_exact(label, r, expected_re_frac, expected_im_frac=Fraction(0)):
    """Exact Fraction-level check — no floating-point tolerance."""
    re, im = _frac(r)
    assert re == expected_re_frac, f"{label} exact re: {re} != {expected_re_frac}"
    assert im == expected_im_frac, f"{label} exact im: {im} != {expected_im_frac}"


# ══════════════════════════════════════════════════════════════════════════════
# Addition
# ══════════════════════════════════════════════════════════════════════════════

def test_add_laurent_plus_laurent():
    """1/5 + 2/5 = 3/5 (Laurent + Laurent)."""
    _check_exact('1/5 + 2/5', _r(1,0,5) + _r(2,0,5), Fraction(3,5))

def test_add_laurent_plus_laurent_different_denom():
    """1/5 + 1/10 = 3/10 (Laurent + Laurent, different denominators)."""
    _check_exact('1/5 + 1/10', _r(1,0,5) + _r(1,0,10), Fraction(3,10))

def test_add_z0adic_plus_laurent():
    """1/3 + 1/5 = 8/15 (pure z0-adic + Laurent)."""
    _check_exact('1/3 + 1/5', _r(1,0,3) + _r(1,0,5), Fraction(8,15))

def test_add_z0adic_plus_z0adic():
    """1/3 + 2/3 = 1 (pure z0-adic + pure z0-adic)."""
    _check_exact('1/3 + 2/3', _r(1,0,3) + _r(2,0,3), Fraction(1))

def test_add_z0adic_plus_z0adic_half():
    """1/2 + 1/2 = 1."""
    _check_exact('1/2 + 1/2', _r(1,0,2) + _r(1,0,2), Fraction(1))

def test_add_finite_plus_z0adic():
    """(3+2i) + 1/3 = 10/3 + 2i (finite + pure z0-adic)."""
    _check_exact('(3+2i)+1/3 re', _r(3,2,1) + _r(1,0,3),
                 Fraction(10,3), Fraction(2))

def test_add_finite_plus_laurent():
    """3 + 1/5 = 16/5 (finite + Laurent)."""
    _check_exact('3 + 1/5', _r(3,0,1) + _r(1,0,5), Fraction(16,5))

def test_add_complex_gaussian_rationals():
    """(1+i)/5 + (1-i)/5 = 2/5 (complex Laurent + complex Laurent)."""
    _check_exact('(1+i)/5 + (1-i)/5', _r(1,1,5) + _r(1,-1,5),
                 Fraction(2,5), Fraction(0))

def test_add_same_denom_laurent():
    """1/10 + 1/10 = 1/5."""
    _check_exact('1/10 + 1/10', _r(1,0,10) + _r(1,0,10), Fraction(1,5))


# ══════════════════════════════════════════════════════════════════════════════
# Subtraction
# ══════════════════════════════════════════════════════════════════════════════

def test_sub_laurent():
    """2/5 - 1/5 = 1/5."""
    _check_exact('2/5 - 1/5', _r(2,0,5) - _r(1,0,5), Fraction(1,5))

def test_sub_z0adic_minus_laurent():
    """1/3 - 1/5 = 2/15."""
    _check_exact('1/3 - 1/5', _r(1,0,3) - _r(1,0,5), Fraction(2,15))

def test_sub_gives_zero():
    """1/5 - 1/5 = 0."""
    _check_exact('1/5 - 1/5', _r(1,0,5) - _r(1,0,5), Fraction(0))

def test_sub_finite_minus_z0adic():
    """1 - 1/3 = 2/3."""
    _check_exact('1 - 1/3', _r(1,0,1) - _r(1,0,3), Fraction(2,3))


# ══════════════════════════════════════════════════════════════════════════════
# Negation
# ══════════════════════════════════════════════════════════════════════════════

def test_neg_laurent():
    """-(1/5) = -1/5."""
    _check_exact('-(1/5)', -_r(1,0,5), Fraction(-1,5))

def test_neg_z0adic():
    """-(1/3) = -1/3."""
    _check_exact('-(1/3)', -_r(1,0,3), Fraction(-1,3))

def test_neg_complex():
    """-(1+i)/5 = (-1-i)/5."""
    _check_exact('-(1+i)/5', -_r(1,1,5), Fraction(-1,5), Fraction(-1,5))

def test_neg_double():
    """-(-1/5) = 1/5 (double negation)."""
    _check_exact('--1/5', -(-_r(1,0,5)), Fraction(1,5))


# ══════════════════════════════════════════════════════════════════════════════
# Multiplication
# ══════════════════════════════════════════════════════════════════════════════

def test_mul_laurent_times_z0adic():
    """1/5 * 1/3 = 1/15."""
    _check_exact('1/5 * 1/3', _r(1,0,5) * _r(1,0,3), Fraction(1,15))

def test_mul_laurent_times_laurent():
    """2/5 * 2/5 = 4/25."""
    _check_exact('2/5 * 2/5', _r(2,0,5) * _r(2,0,5), Fraction(4,25))

def test_mul_inverse_of_5():
    """1/5 * 5 = 1."""
    _check_exact('1/5 * 5', _r(1,0,5) * _r(5,0,1), Fraction(1))

def test_mul_inverse_of_10():
    """1/10 * 10 = 1."""
    _check_exact('1/10 * 10', _r(1,0,10) * _r(10,0,1), Fraction(1))

def test_mul_complex_conjugates():
    """(1+i)/5 * (1-i)/5 = 2/25 (norm calculation)."""
    _check_exact('(1+i)/5*(1-i)/5 re', _r(1,1,5) * _r(1,-1,5),
                 Fraction(2,25), Fraction(0))

def test_mul_complex_by_real():
    """(1/5) * (3+2i) = 3/5 + 2i/5."""
    _check_exact('1/5*(3+2i)', _r(1,0,5) * _r(3,2,1),
                 Fraction(3,5), Fraction(2,5))

def test_mul_z0adic_times_z0adic():
    """1/3 * 1/3 = 1/9."""
    _check_exact('1/3 * 1/3', _r(1,0,3) * _r(1,0,3), Fraction(1,9))

def test_mul_by_zero():
    """1/5 * 0 = 0."""
    _check_exact('1/5 * 0', _r(1,0,5) * _r(0,0,1), Fraction(0))

def test_mul_complex_general():
    """(1+2i)/5 * (3-i)/5 = (5+5i)/25 = (1+i)/5."""
    # (1+2i)(3-i) = 3-i+6i-2i^2 = 3+5i+2 = 5+5i
    _check_exact('(1+2i)/5*(3-i)/5', _r(1,2,5) * _r(3,-1,5),
                 Fraction(1,5), Fraction(1,5))


# ══════════════════════════════════════════════════════════════════════════════
# Equality
# ══════════════════════════════════════════════════════════════════════════════

def test_eq_same_value_same_case():
    """1/5 == 1/5."""
    assert _r(1,0,5) == _r(1,0,5)

def test_eq_same_value_different_expansion():
    """(1/5 + 2/5) == 3/5 (arithmetic result equals direct expansion)."""
    assert (_r(1,0,5) + _r(2,0,5)) == _r(3,0,5)

def test_eq_cross_case():
    """(3/5 - 1/5) == 2/5 (Laurent arithmetic result equals direct)."""
    assert (_r(3,0,5) - _r(1,0,5)) == _r(2,0,5)

def test_neq_different_values():
    """1/5 != 2/5."""
    assert not (_r(1,0,5) == _r(2,0,5))

def test_eq_z0adic():
    """1/3 == 1/3."""
    assert _r(1,0,3) == _r(1,0,3)

def test_eq_cross_pure_and_laurent():
    """(1/3 + 1/5) evaluated result is consistent with direct 8/15."""
    assert (_r(1,0,3) + _r(1,0,5)) == _r(8,0,15)


# ══════════════════════════════════════════════════════════════════════════════
# Algebraic laws
# ══════════════════════════════════════════════════════════════════════════════

def test_commutativity_add():
    """1/5 + 1/3 == 1/3 + 1/5."""
    assert (_r(1,0,5) + _r(1,0,3)) == (_r(1,0,3) + _r(1,0,5))

def test_commutativity_mul():
    """1/5 * 1/3 == 1/3 * 1/5."""
    assert (_r(1,0,5) * _r(1,0,3)) == (_r(1,0,3) * _r(1,0,5))

def test_associativity_add():
    """(1/5 + 1/3) + 1/2 == 1/5 + (1/3 + 1/2)."""
    a, b, c = _r(1,0,5), _r(1,0,3), _r(1,0,2)
    assert (a + b) + c == a + (b + c)

def test_distributivity():
    """1/5 * (1/3 + 1/2) == 1/5 * 1/3 + 1/5 * 1/2."""
    a, b, c = _r(1,0,5), _r(1,0,3), _r(1,0,2)
    assert a * (b + c) == a * b + a * c

def test_additive_inverse():
    """r + (-r) == 0 for Laurent case."""
    r = _r(1,0,5)
    result = r + (-r)
    re, im = _frac(result)
    assert re == Fraction(0) and im == Fraction(0)

def test_multiplicative_identity():
    """1/5 * 1 == 1/5."""
    assert _r(1,0,5) * _r(1,0,1) == _r(1,0,5)
