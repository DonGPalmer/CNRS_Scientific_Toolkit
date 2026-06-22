"""
Tests for cnrs.autodiff chain-rule capability.
"""

import cmath
import math

import pytest

from cnrs.autodiff import (
    CnrsDual,
    derivative,
    value_and_derivative,
    exp,
    log,
    sin,
    cos,
    tan,
    sqrt,
    pow_const,
)


TOL = 2e-4


def close(a, b, tol=TOL):
    return abs(complex(a) - complex(b)) < tol


def test_variable_and_constant_derivatives():
    x = CnrsDual.variable(3.0, L=16)
    c = CnrsDual.constant(3.0, L=16)

    assert close(x.value, 3.0)
    assert close(x.deriv, 1.0)
    assert close(c.value, 3.0)
    assert close(c.deriv, 0.0)


def test_addition_rule():
    x = CnrsDual.variable(2.0, L=16)
    y = x + 5
    assert close(y.value, 7.0)
    assert close(y.deriv, 1.0)


def test_product_rule():
    x = CnrsDual.variable(3.0, L=16)
    y = x * x
    assert close(y.value, 9.0)
    assert close(y.deriv, 6.0)


def test_quotient_rule():
    x = CnrsDual.variable(2.0, L=16)
    y = (x * x + 1) / (x + 1)

    expected_value = (2.0**2 + 1) / (2.0 + 1)
    expected_deriv = ((2 * 2.0) * (2.0 + 1) - (2.0**2 + 1)) / ((2.0 + 1) ** 2)

    assert close(y.value, expected_value)
    assert close(y.deriv, expected_deriv)


def test_exp_chain_rule_for_exp_x_squared():
    x0 = 2.0
    d = derivative(lambda x: exp(x * x), x0, L=18)
    expected = 2 * x0 * math.exp(x0 * x0)
    assert close(d, expected, tol=2e-3)


def test_log_chain_rule():
    x0 = 2.5
    d = derivative(lambda x: log(x * x + 1), x0, L=18)
    expected = (2 * x0) / (x0 * x0 + 1)
    assert close(d, expected)


def test_sin_cos_chain_rule():
    x0 = 0.7
    d = derivative(lambda x: sin(x * x), x0, L=18)
    expected = math.cos(x0 * x0) * 2 * x0
    assert close(d, expected)


def test_nested_exp_sin_scale_rule():
    s0 = 1.2
    Lscale = 5.0

    def f(s):
        return sin(exp(s / Lscale))

    d = derivative(f, s0, L=18)
    expected = cmath.cos(cmath.exp(s0 / Lscale)) * (1 / Lscale) * cmath.exp(s0 / Lscale)
    assert close(d, expected)


def test_scale_law_derivative():
    A = 2.0
    k = 0.3
    s0 = 4.0

    def scale_law(s):
        return A * exp(k * s)

    value, d = value_and_derivative(scale_law, s0, L=18)
    expected_value = A * math.exp(k * s0)
    expected_deriv = k * expected_value

    assert close(value, expected_value)
    assert close(d, expected_deriv)


def test_scalar_power_rule():
    x0 = 3.0
    d = derivative(lambda x: x ** 3, x0, L=18)
    assert close(d, 27.0)


def test_dual_exponent_power_rule():
    # f(x) = x^x, f'(x) = x^x * (log(x) + 1)
    x0 = 2.0
    d = derivative(lambda x: x ** x, x0, L=18)
    expected = (x0 ** x0) * (math.log(x0) + 1)
    assert close(d, expected)


def test_branch_log_value_changes_but_derivative_does_not():
    x = CnrsDual.variable(2.0, L=18)
    y0 = log(x, branch=0)
    y1 = log(x, branch=1)

    assert abs(complex(y1.value) - complex(y0.value) - 2j * math.pi) < 2e-4
    assert close(y0.deriv, y1.deriv)


def test_sqrt_chain_rule():
    x0 = 9.0
    d = derivative(sqrt, x0, L=18)
    expected = 1 / (2 * math.sqrt(x0))
    assert close(d, expected)


def test_tan_chain_rule():
    x0 = 0.3
    d = derivative(tan, x0, L=18)
    expected = 1 / (math.cos(x0) ** 2)
    assert close(d, expected)
