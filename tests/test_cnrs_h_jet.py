import cmath
import math

import pytest

from cnrs.cnrs_h import CnrsH
from cnrs.cnrs_h_jet import (
    CnrsHJetError,
    jet_from_cnrsh,
    jet_from_symbolic,
    jet_identity,
    verify_jet_chain_rule,
)
from cnrs.symbolic import Var, exp, sin, cos


def assert_close(a, b, tol=1e-10):
    assert abs(complex(a) - complex(b)) <= tol


def assert_jet_coeffs_close(a, b, tol=1e-10):
    n = max(a.order, b.order)
    for i in range(n):
        assert_close(a.coeff(i), b.coeff(i), tol)


def test_jet_identity_nonzero_center():
    j = jet_identity(center=-12, order=5)
    assert_close(j.evaluate(-12), -12)
    assert_close(j.evaluate(-11.5), -11.5)
    assert j.center == complex(-12, 0)


def test_symbolic_expansion_around_nonzero_center():
    s = Var("s")
    j = jet_from_symbolic(exp(2 * s), s, center=1.5, order=6)
    expected0 = math.exp(3.0)
    assert_close(j.coeff(0), expected0)
    assert_close(j.coeff(1), 2 * expected0)
    assert_close(j.coeff(2), 4 * expected0)
    assert abs(j.evaluate(1.55) - math.exp(3.1)) < 1e-7


def test_diff_preserves_center():
    s = Var("s")
    j = jet_from_symbolic(s * s, s, center=3, order=5)
    dj = j.diff(order=4)
    assert dj.center == j.center
    assert_close(dj.evaluate(3), 6)
    assert_close(dj.evaluate(3.25), 6.5)


def test_integrate_preserves_center_and_constant():
    s = Var("s")
    j = jet_from_symbolic(2 * s, s, center=4, order=5)
    ij = j.integrate(constant=7, order=6)
    assert ij.center == j.center
    assert_close(ij.evaluate(4), 7)
    # Local antiderivative: 7 + 8*(s-4) + (s-4)^2
    assert_close(ij.evaluate(4.5), 7 + 8 * 0.5 + 0.25)


def test_compose_outer_center_matches_inner_value():
    # outer f(x)=exp(x) around x0=1, inner g(s)=1+2*(s-3) around s0=3
    x = Var("x")
    s = Var("s")
    outer = jet_from_symbolic(exp(x), x, center=1, order=8)
    inner = jet_from_symbolic(1 + 2 * (s - 3), s, center=3, order=8)
    comp = outer.compose(inner, order=8)
    assert comp.center == complex(3, 0)
    assert abs(comp.evaluate(3.1) - math.exp(1.2)) < 1e-9


def test_jet_chain_rule_nonzero_centers():
    # D exp(1 + 2*(s-3)) = 2 exp(1 + 2*(s-3))
    x = Var("x")
    s = Var("s")
    outer = jet_from_symbolic(exp(x), x, center=1, order=12)
    inner = jet_from_symbolic(1 + 2 * (s - 3), s, center=3, order=12)
    cmp = verify_jet_chain_rule(outer, inner, order=10, atol=1e-10)
    assert cmp.passed, cmp.max_error
    assert abs(cmp.lhs.evaluate(3.1) - 2 * math.exp(1.2)) < 1e-10


def test_jet_chain_rule_sin_exp_nonzero_center():
    x = Var("x")
    s = Var("s")
    outer = jet_from_symbolic(sin(x), x, center=math.exp(0.5), order=14)
    inner = jet_from_symbolic(exp(s), s, center=0.5, order=14)
    cmp = verify_jet_chain_rule(outer, inner, order=10, atol=1e-8)
    assert cmp.passed, cmp.max_error
    val = 0.55
    assert abs(cmp.lhs.evaluate(val) - (math.cos(math.exp(val)) * math.exp(val))) < 1e-8


def test_shift_center_for_polynomial_is_exact():
    s = Var("s")
    j = jet_from_symbolic(s * s + 2 * s + 1, s, center=0, order=5)
    shifted = j.shift_center(3, order=5)
    assert_close(shifted.evaluate(3), 16)
    assert_close(shifted.coeff(1), 8)  # derivative 2s+2 at s=3
    assert_close(shifted.coeff(2), 2)


def test_add_requires_same_center():
    a = jet_from_cnrsh(CnrsH.from_list([1, 1]), center=0)
    b = jet_from_cnrsh(CnrsH.from_list([1, 1]), center=1)
    with pytest.raises(CnrsHJetError):
        _ = a + b


def test_multiplication_of_local_jets():
    s = Var("s")
    a = jet_from_symbolic(s + 1, s, center=2, order=5)
    b = jet_from_symbolic(s - 1, s, center=2, order=5)
    prod = a * b
    assert_close(prod.evaluate(2.25), (3.25) * (1.25))
