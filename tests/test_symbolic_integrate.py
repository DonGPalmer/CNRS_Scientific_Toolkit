
import cmath

import pytest

from cnrs.symbolic import Var, Const, exp, sin, cos, log, integrate, diff, Integral

TOL = 3e-4


def assert_close(a, b, tol=TOL):
    assert abs(complex(a) - complex(b)) < tol


def check_antiderivative(expr, var, env, expected_derivative=None):
    anti = integrate(expr, var).simplify()
    danti = diff(anti, var).simplify()
    val = danti.eval(env, L=20)
    expected = expr.eval(env, L=20) if expected_derivative is None else expected_derivative
    assert_close(val, expected)
    return anti


def test_integrate_constant():
    x = Var("x")
    anti = integrate(Const(5), x).simplify()
    assert_close(diff(anti, x).eval({"x": 2.0}, L=20), 5)


def test_integrate_variable_power():
    x = Var("x")
    anti = integrate(x, x).simplify()
    assert_close(anti.eval({"x": 3.0}, L=20), 4.5)
    assert_close(diff(anti, x).eval({"x": 3.0}, L=20), 3.0)


def test_integrate_power_rule():
    x = Var("x")
    expr = x ** 3
    anti = integrate(expr, x).simplify()
    assert_close(diff(anti, x).eval({"x": 2.0}, L=20), 8.0)


def test_integrate_reciprocal_to_log():
    x = Var("x")
    anti = integrate(1 / x, x).simplify()
    assert "log" in str(anti)
    assert_close(diff(anti, x).eval({"x": 2.0}, L=20), 0.5)


def test_integrate_linearity():
    x = Var("x")
    expr = 3 * x + 2
    anti = integrate(expr, x).simplify()
    assert_close(diff(anti, x).eval({"x": 4.0}, L=20), 14.0)


def test_integrate_exp_affine():
    x = Var("x")
    expr = exp(2 * x + 1)
    anti = integrate(expr, x).simplify()
    expected = cmath.exp(2 * 0.7 + 1)
    assert_close(diff(anti, x).eval({"x": 0.7}, L=20), expected)


def test_integrate_exp_symbolic_slope():
    x = Var("x")
    k = Var("k")
    expr = exp(k * x)
    anti = integrate(expr, x).simplify()
    expected = cmath.exp(0.3 * 1.2)
    assert_close(diff(anti, x).eval({"x": 1.2, "k": 0.3}, L=20), expected)


def test_integrate_sin_affine():
    x = Var("x")
    expr = sin(3 * x + 2)
    anti = integrate(expr, x).simplify()
    expected = cmath.sin(3 * 0.4 + 2)
    assert_close(diff(anti, x).eval({"x": 0.4}, L=20), expected)


def test_integrate_cos_affine():
    x = Var("x")
    expr = cos(4 * x - 1)
    anti = integrate(expr, x).simplify()
    expected = cmath.cos(4 * 0.4 - 1)
    assert_close(diff(anti, x).eval({"x": 0.4}, L=20), expected)


def test_integrate_independent_variable():
    x = Var("x")
    y = Var("y")
    anti = integrate(y, x).simplify()
    assert_close(diff(anti, x).eval({"x": 2.0, "y": 7.0}, L=20), 7.0)


def test_integrate_unknown_returns_integral():
    x = Var("x")
    expr = exp(x * x)
    anti = integrate(expr, x)
    assert isinstance(anti, Integral)
    assert str(anti).startswith("Integral")
    assert_close(diff(anti, x).eval({"x": 1.0}, L=20), cmath.exp(1.0))


def test_integral_eval_raises_until_rule_applies():
    x = Var("x")
    anti = integrate(exp(x * x), x)
    with pytest.raises(NotImplementedError):
        anti.eval({"x": 1.0})
