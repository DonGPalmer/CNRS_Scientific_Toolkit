import math

from cnrs.cnrs_h_taylor_model import (
    CnrsHTaylorModel,
    taylor_model_from_symbolic,
    taylor_model_from_jet,
    verify_taylor_model_chain_rule,
)
from cnrs.cnrs_h_jet import jet_from_symbolic
from cnrs.symbolic import Var, exp, sin


def test_taylor_model_from_symbolic_uses_last_term_indicator():
    s = Var("s")
    tm = taylor_model_from_symbolic(exp(s), s, center=0, order=6, sample_point=0.1)
    assert isinstance(tm, CnrsHTaylorModel)
    assert tm.remainder_bound is not None
    assert abs(tm.remainder_bound - (0.1 ** 5) / math.factorial(5)) < 1e-14
    value, radius = tm.enclosure(0.1)
    assert abs(value - sum((0.1 ** n) / math.factorial(n) for n in range(6))) < 1e-14
    assert radius == tm.remainder_bound


def test_taylor_model_adds_remainder_bounds():
    s = Var("s")
    a = taylor_model_from_symbolic(exp(s), s, center=0, order=6, remainder_bound=0.01)
    b = taylor_model_from_symbolic(sin(s), s, center=0, order=6, remainder_bound=0.02)
    c = a + b
    assert c.remainder_bound == 0.03
    assert c.bound_kind == "propagated"


def test_taylor_model_scalar_multiplication_scales_bound():
    s = Var("s")
    tm = taylor_model_from_symbolic(exp(s), s, center=0, order=6, remainder_bound=0.01)
    scaled = 3 * tm
    assert scaled.remainder_bound == 0.03
    assert abs(scaled.evaluate(0.0) - 3) < 1e-12


def test_taylor_model_product_bound_at_center():
    s = Var("s")
    a = taylor_model_from_symbolic(exp(s), s, center=0, order=6, remainder_bound=0.01)
    b = taylor_model_from_symbolic(exp(s), s, center=0, order=6, remainder_bound=0.02)
    p = a * b
    # |1|*.02 + |1|*.01 + .01*.02
    assert abs(p.remainder_bound - 0.0302) < 1e-14


def test_diff_marks_remainder_unknown():
    s = Var("s")
    tm = taylor_model_from_symbolic(exp(s), s, center=0, order=6, remainder_bound=0.01)
    d = tm.diff(order=5)
    assert d.remainder_bound is None
    assert d.bound_kind == "unknown_after_diff"
    assert d.order == 5


def test_taylor_model_chain_rule_uses_jet_parts():
    s = Var("s")
    x = Var("x")
    outer = taylor_model_from_symbolic(exp(x), x, center=1, order=9)
    inner = taylor_model_from_symbolic(1 + s * s, s, center=0, order=9)
    cmp = verify_taylor_model_chain_rule(outer, inner, order=8)
    assert cmp.passed
    assert cmp.max_error < 1e-10


def test_taylor_model_from_existing_jet():
    s = Var("s")
    jet = jet_from_symbolic(exp(s), s, center=-12, order=5)
    tm = taylor_model_from_jet(jet, sample_point=-11.9)
    assert tm.remainder_bound is not None
    assert tm.valid_for(-11.9) is True
