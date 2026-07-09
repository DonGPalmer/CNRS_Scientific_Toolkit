"""v0.11.0 evaluation behavior for finite, periodic, and Laurent-periodic values."""
from fractions import Fraction
import pytest
from cnrs.cnrs_rational import gaussian_rational_to_cnrs


def _r(a, b, q, max_frac=1000):
    return gaussian_rational_to_cnrs(complex(a, b), q, max_frac=max_frac)


@pytest.mark.parametrize("a,b,q", [
    (1,0,5), (1,0,10), (1,0,25), (2,0,5), (1,1,5), (1,0,15),
    (1,0,2), (1,0,3), (2,-1,3), (7,3,125),
])
def test_evaluate_exact_for_all_rational_expansion_classes(a,b,q):
    r = _r(a,b,q)
    assert abs(r.evaluate() - complex(a,b)/q) < 1e-13


def test_evaluate_long_period_exact():
    r = _r(1,0,23)
    assert r.period_length == 528
    assert abs(r.evaluate() - 1/23) < 1e-14


def test_partial_sum_respects_power_offset():
    r = _r(1,0,5)
    expected = sum(d * complex(-2,1)**(r.power_offset+k)
                   for k,d in enumerate(r.frac_digits[:4]))
    assert r.partial_sum(4) == expected
    assert r.evaluate(4) == expected


def test_exact_fraction_interface_unchanged():
    r = _r(1,1,15)
    re, im = r.z0_adic_value_fractions()
    assert re == Fraction(1,15)
    assert im == Fraction(1,15)


def test_finite_evaluate_unchanged():
    r = _r(3,2,1)
    assert r.evaluate() == 3+2j
