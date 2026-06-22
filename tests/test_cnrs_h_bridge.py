import cmath
import math

import pytest

from cnrs.cnrs_h import CnrsH
from cnrs.cnrs_h_bridge import (
    UnsupportedBridgeExpression,
    cnrs_h_from_symbolic,
    compare_symbolic_and_cnrs_h_derivative,
    compare_symbolic_and_cnrs_h_integral,
    max_coeff_error,
)
from cnrs.symbolic import Var, Const, exp, sin, cos, log, diff, integrate


def assert_coeffs_close(a, b, tol=1e-10):
    assert max_coeff_error(a, b) <= tol


def test_variable_to_cnrsh_identity():
    s = Var("s")
    h = cnrs_h_from_symbolic(s, "s", order=4)
    assert h.coeffs == (0, 1, 0, 0)


def test_polynomial_to_cnrsh_coefficients():
    s = Var("s")
    expr = 3 + 2 * s + s**3
    h = cnrs_h_from_symbolic(expr, "s", order=5)
    # s^3 = 6 * s^3/3! in EGF coefficients.
    assert h.coeff(0) == complex(3)
    assert h.coeff(1) == complex(2)
    assert h.coeff(2) == 0
    assert h.coeff(3) == complex(6)


def test_exp_scale_law_coefficients_numeric_parameter():
    s = Var("s")
    expr = 2 * exp(0.3 * s)
    h = cnrs_h_from_symbolic(expr, "s", order=5)
    expected = [2 * (0.3**n) for n in range(5)]
    for i, e in enumerate(expected):
        assert abs(complex(h.coeff(i)) - e) < 1e-10


def test_exp_scale_law_coefficients_symbolic_parameter_env():
    s = Var("s")
    k = Var("k")
    A = Var("A")
    expr = A * exp(k * s)
    h = cnrs_h_from_symbolic(expr, "s", order=5, env={"A": 2.0, "k": 0.3})
    expected = [2 * (0.3**n) for n in range(5)]
    for i, e in enumerate(expected):
        assert abs(complex(h.coeff(i)) - e) < 1e-10


def test_sin_and_cos_linear_coefficients():
    s = Var("s")
    hs = cnrs_h_from_symbolic(sin(2*s), "s", order=5)
    hc = cnrs_h_from_symbolic(cos(2*s), "s", order=5)
    expected_sin = [0, 2, 0, -8, 0]
    expected_cos = [1, 0, -4, 0, 16]
    for i, e in enumerate(expected_sin):
        assert abs(complex(hs.coeff(i)) - e) < 1e-10
    for i, e in enumerate(expected_cos):
        assert abs(complex(hc.coeff(i)) - e) < 1e-10


def test_symbolic_diff_commutes_with_cnrsh_for_scale_law():
    s = Var("s")
    k = Var("k")
    A = Var("A")
    expr = A * exp(k * s)
    result = compare_symbolic_and_cnrs_h_derivative(expr, "s", order=6, env={"A": 2.0, "k": 0.3})
    assert result.passed
    assert result.max_error < 1e-10


def test_symbolic_diff_commutes_with_cnrsh_for_polynomial():
    s = Var("s")
    expr = s**4 + 2*s**2 + 5
    result = compare_symbolic_and_cnrs_h_derivative(expr, "s", order=5)
    assert result.passed


def test_symbolic_integral_commutes_with_cnrsh_for_exp():
    s = Var("s")
    k = Var("k")
    expr = exp(k * s)
    result = compare_symbolic_and_cnrs_h_integral(expr, "s", order=6, env={"k": 0.5})
    assert result.passed


def test_symbolic_integral_commutes_with_cnrsh_for_polynomial():
    s = Var("s")
    expr = 3*s**2 + 2
    result = compare_symbolic_and_cnrs_h_integral(expr, "s", order=6)
    assert result.passed


def test_series_evaluation_matches_symbolic_exp_near_zero():
    s = Var("s")
    expr = 2 * exp(0.3 * s)
    h = cnrs_h_from_symbolic(expr, "s", order=12)
    x = 0.4
    expected = 2 * cmath.exp(0.3 * x)
    assert abs(h.evaluate(x) - expected) < 1e-10


def test_unsupported_log_raises():
    s = Var("s")
    with pytest.raises(UnsupportedBridgeExpression):
        cnrs_h_from_symbolic(log(s), "s", order=6)


def test_division_by_independent_parameter():
    s = Var("s")
    L = Var("L")
    expr = exp(s / L)
    h = cnrs_h_from_symbolic(expr, "s", order=4, env={"L": 5.0})
    expected = [1, 1/5, 1/25, 1/125]
    for i, e in enumerate(expected):
        assert abs(complex(h.coeff(i)) - e) < 1e-10
