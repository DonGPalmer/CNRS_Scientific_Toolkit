import cmath

import pytest

from cnrs.autodiff import CnrsDual
from cnrs.symbolic import Var, Const, exp, log, sin, cos, tan, sqrt, pow_branch, diff

TOL = 2e-4


def cval(x):
    return complex(x)


def assert_close(a, b, tol=TOL):
    assert abs(complex(a) - complex(b)) < tol


def test_diff_constant_is_zero():
    x = Var("x")
    assert_close(diff(Const(5), x).eval({"x": 2.0}), 0)


def test_diff_variable_is_one_or_zero():
    x = Var("x")
    y = Var("y")
    assert_close(diff(x, x).eval({"x": 2.0}), 1)
    assert_close(diff(y, x).eval({"y": 3.0}), 0)


def test_sum_rule():
    x = Var("x")
    expr = x + x + 3
    d = diff(expr, x)
    assert_close(d.eval({"x": 4.0}), 2)


def test_product_rule_polynomial():
    x = Var("x")
    expr = x * x + 3 * x
    d = diff(expr, x)
    assert_close(d.eval({"x": 4.0}), 11)


def test_quotient_rule():
    x = Var("x")
    expr = x / (x + 1)
    d = diff(expr, x)
    expected = 1 / ((2.0 + 1.0) ** 2)
    assert_close(d.eval({"x": 2.0}), expected)


def test_exp_chain_rule():
    x = Var("x")
    expr = exp(x * x)
    d = diff(expr, x)
    expected = 2 * 2.0 * cmath.exp(2.0 * 2.0)
    assert_close(d.eval({"x": 2.0}, L=20), expected, tol=2e-4)


def test_log_chain_rule():
    x = Var("x")
    expr = log(x * x + 1)
    d = diff(expr, x)
    expected = (2 * 2.0) / (2.0 * 2.0 + 1.0)
    assert_close(d.eval({"x": 2.0}, L=20), expected, tol=2e-4)


def test_sin_exp_nested_chain_rule():
    x = Var("x")
    expr = sin(exp(x / 5.0))
    d = diff(expr, x)
    z = cmath.exp(1.2 / 5.0)
    expected = cmath.cos(z) * z / 5.0
    assert_close(d.eval({"x": 1.2}, L=20), expected, tol=2e-4)


def test_scale_law_symbolic_derivative():
    s = Var("s")
    A = Var("A")
    k = Var("k")
    law = A * exp(k * s)
    dlaw = diff(law, s)
    env = {"A": 2.0, "k": 0.3, "s": 4.0}
    expected = 2.0 * 0.3 * cmath.exp(0.3 * 4.0)
    assert_close(dlaw.eval(env, L=20), expected, tol=2e-4)


def test_simplify_zero_one_rules():
    x = Var("x")
    assert str((x + 0).simplify()) == "x"
    assert str((0 * x).simplify()) == "0"
    assert str((x * 1).simplify()) == "x"
    assert str((x ** 1).simplify()) == "x"


def test_symbolic_eval_matches_autodiff():
    x = Var("x")
    expr = sin(exp(x / 5.0)) + log(x * x + 2)
    dexpr = diff(expr, x)

    # Symbolic derivative evaluated normally.
    symbolic_value = dexpr.eval({"x": 1.2}, L=20)

    # Same expression evaluated through the dual backend.
    dual_result = expr.eval({"x": CnrsDual.variable(1.2, L=20)}, L=20)
    assert isinstance(dual_result, CnrsDual)
    assert_close(symbolic_value, dual_result.deriv, tol=3e-4)


def test_branch_tag_preserved_in_log_value():
    x = Var("x")
    expr = log(x, branch=2)
    val = expr.eval({"x": 1.0}, L=20)
    assert abs(complex(val) - 4j * cmath.pi) < 2e-6
    d = diff(expr, x)
    assert_close(d.eval({"x": 2.0}, L=20), 0.5, tol=2e-4)


def test_sqrt_chain_rule():
    x = Var("x")
    expr = sqrt(x * x + 1)
    d = diff(expr, x)
    expected = 3.0 / cmath.sqrt(10.0)
    assert_close(d.eval({"x": 3.0}, L=20), expected, tol=2e-4)


def test_general_power_rule_variable_exponent():
    x = Var("x")
    expr = x ** x
    d = diff(expr, x)
    expected = (2.0 ** 2.0) * (cmath.log(2.0) + 1.0)
    assert_close(d.eval({"x": 2.0}, L=20), expected, tol=3e-4)


def test_pow_branch_keeps_branch_in_derivative_expression():
    x = Var("x")
    y = Var("y")
    expr = pow_branch(x, y, branch=3)
    d = diff(expr, y)
    # d/dy x^y = x^y Log_3(x); at x=1, y=2, derivative is 6*pi*i
    assert_close(d.eval({"x": 1.0, "y": 2.0}, L=20), 6j * cmath.pi, tol=2e-4)
