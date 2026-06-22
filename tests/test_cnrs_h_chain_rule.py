import math
import cmath

import pytest

from cnrs.cnrs_h import CnrsH
from cnrs.cnrs_h_chain import (
    identity,
    monomial,
    exp_series,
    sin_series,
    cos_series,
    compose_series,
    power_series,
    chain_rule_lhs,
    chain_rule_rhs,
    verify_chain_rule,
    evaluate_composition,
)


def assert_coeffs_close(a, b, tol=1e-10):
    n = max(a.length, b.length)
    for i in range(n):
        assert abs(complex(a.coeff(i)) - complex(b.coeff(i))) <= tol


def test_monomial_egf_encoding():
    h = monomial(3, 2, order=6)  # 2*s^3 -> d3 = 2*3!
    assert h.coeff(0) == 0
    assert h.coeff(3) == 12
    assert abs(h.evaluate(0.5) - 2 * (0.5 ** 3)) < 1e-12


def test_power_series_identity_squared():
    s = identity(6)
    s2 = power_series(s, 2, order=6)
    expected = monomial(2, 1, order=6)
    assert_coeffs_close(s2, expected)


def test_compose_polynomial_exact():
    # f(x)=x^2, g(s)=s+s^2.  f(g)=s^2+2s^3+s^4.
    f = monomial(2, 1, order=8)
    g = identity(8) + monomial(2, 1, order=8)
    composed = compose_series(f, g, order=8)
    expected = monomial(2, 1, order=8) + monomial(3, 2, order=8) + monomial(4, 1, order=8)
    assert_coeffs_close(composed, expected)


def test_compose_exponential_square_values():
    # exp(s^2), evaluated through finite composition, should match truncated exp(s^2).
    order = 12
    outer = exp_series(1, 0, order=order)
    inner = monomial(2, 1, order=order)
    x = 0.2
    got = evaluate_composition(outer, inner, x, order=order)
    assert abs(got - math.exp(x * x)) < 1e-10


def test_direct_chain_rule_exp_square():
    order = 12
    outer = exp_series(1, 0, order=order + 2)
    inner = monomial(2, 1, order=order + 2)
    cmp = verify_chain_rule(outer, inner, order=order, atol=1e-10)
    assert cmp.passed, cmp
    # The derivative should be 2*s*exp(s^2).
    expected = (monomial(1, 2, order=order) * compose_series(outer, inner, order=order)).truncate(order).pad(order)
    assert_coeffs_close(cmp.lhs, expected, tol=1e-10)


def test_direct_chain_rule_sin_exp_small_order():
    # D sin(exp(s)-1) = cos(exp(s)-1) * exp(s).
    # Use inner with zero constant for cleaner finite composition.
    order = 10
    outer_sin = sin_series(1, 0, order=order + 3)
    inner = exp_series(1, 0, order=order + 3) - CnrsH.from_list([1] + [0] * (order + 2))
    cmp = verify_chain_rule(outer_sin, inner, order=order, atol=1e-8)
    assert cmp.passed, cmp.max_error


def test_chain_rule_lhs_rhs_helpers_match_for_polynomial():
    order = 8
    outer = monomial(3, 1, order=order + 2) + monomial(1, 2, order=order + 2)
    inner = identity(order + 2) + monomial(2, -1, order=order + 2)
    lhs = chain_rule_lhs(outer, inner, order=order)
    rhs = chain_rule_rhs(outer, inner, order=order)
    assert_coeffs_close(lhs, rhs)


def test_verify_chain_rule_failure_tolerance_can_fail():
    order = 6
    outer = exp_series(1, 0, order=order + 2)
    inner = monomial(2, 1, order=order + 2)
    cmp = verify_chain_rule(outer, inner, order=order, atol=-1.0)
    assert not cmp.passed
    assert cmp.max_error >= 0


def test_compose_identity_outer_returns_inner():
    order = 7
    outer = identity(order)
    inner = exp_series(0.3, 0.2, order=order)
    got = compose_series(outer, inner, order=order)
    assert_coeffs_close(got, inner)


def test_compose_constant_outer_returns_constant():
    order = 7
    outer = CnrsH.from_list([3] + [0] * (order - 1))
    inner = exp_series(1, 0, order=order)
    got = compose_series(outer, inner, order=order)
    assert_coeffs_close(got, outer)


def test_chain_rule_affine_inner_exp():
    # With a nonzero inner constant, finite outer truncation approximates the
    # analytic exp(2+3s) series, but the CNRS-H chain-rule identity should
    # still hold internally for the finite representation.
    order = 9
    outer = exp_series(1, 0, order=order + 6)
    inner = CnrsH.from_list([2, 3] + [0] * (order + 4))  # 2 + 3s
    cmp = verify_chain_rule(outer, inner, order=order, atol=1e-8)
    assert cmp.passed, cmp.max_error
    assert_coeffs_close(cmp.lhs, cmp.rhs, tol=1e-8)


def test_composition_numeric_for_affine_inner():
    order = 12
    outer = cos_series(1, 0, order=order)
    inner = CnrsH.from_list([0.2, 0.5] + [0] * (order - 2))
    x = 0.1
    got = compose_series(outer, inner, order=order).evaluate(x)
    assert abs(got - cmath.cos(0.2 + 0.5 * x)) < 1e-10
