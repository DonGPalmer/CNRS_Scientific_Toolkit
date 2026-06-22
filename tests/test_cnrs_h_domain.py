import math

from cnrs.cnrs_h_domain import CnrsHDomain, INF, infer_symbolic_domain, estimate_next_term_error
from cnrs.cnrs_h_jet import jet_from_symbolic, jet_identity
from cnrs.symbolic import Var, exp, log, sqrt


def test_domain_entire_for_polynomial():
    s = Var("s")
    d = infer_symbolic_domain(s * s + 2 * s + 1, s, center=0)
    assert d.radius == INF
    assert d.is_entire
    assert d.valid_for(0, 1e6) is True


def test_domain_radius_for_log_one_plus_s():
    s = Var("s")
    d = infer_symbolic_domain(log(1 + s), s, center=0)
    assert d.radius is not None
    assert abs(d.radius - 1.0) < 1e-12
    assert any(abs(z + 1) < 1e-12 for z in d.singularities)
    assert d.valid_for(0, 0.5) is True
    assert d.valid_for(0, 1.5) is False


def test_domain_radius_for_sqrt_shifted_center():
    s = Var("s")
    d = infer_symbolic_domain(sqrt(1 + s), s, center=0.25)
    assert d.radius is not None
    assert abs(d.radius - 1.25) < 1e-12


def test_jet_from_symbolic_infers_domain():
    s = Var("s")
    j = jet_from_symbolic(log(1 + s), s, center=0, order=8)
    assert j.domain is not None
    assert abs(j.domain.radius - 1.0) < 1e-12
    assert j.valid_for(0.25) is True
    assert j.valid_for(1.25) is False
    assert abs(j.distance_to_boundary(0.25) - 0.75) < 1e-12


def test_jet_entire_validity_for_exp():
    s = Var("s")
    j = jet_from_symbolic(exp(0.1 * s), s, center=-12, order=8)
    assert j.domain is not None
    assert j.domain.is_entire
    assert j.valid_for(1000) is True
    assert j.distance_to_boundary(1000) == INF


def test_jet_truncation_error_indicator():
    s = Var("s")
    j = jet_from_symbolic(exp(s), s, center=0, order=6)
    err = j.estimate_truncation_error(0.1)
    assert err is not None
    assert abs(err - (0.1 ** 5) / math.factorial(5)) < 1e-14
    assert estimate_next_term_error(j, 0.1) == err


def test_domain_hint_constructor_on_identity():
    j = jet_identity(center=2, order=4)
    assert j.domain is not None
    assert j.domain.is_entire
    assert j.valid_for(-100) is True


def test_user_radius_hint_becomes_domain():
    s = Var("s")
    j = jet_from_symbolic(s, s, center=0, order=4, radius_hint=3.0)
    assert j.domain is not None
    assert j.domain.radius == 3.0
    assert j.valid_for(2.0) is True
    assert j.valid_for(4.0) is False


def test_domain_object_valid_for_unknown_returns_none():
    d = CnrsHDomain()
    assert d.valid_for(0, 1) is None
