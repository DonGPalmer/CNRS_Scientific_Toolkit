"""Regression tests for CnrsHMode native integration constants.

These tests guard the bug where ``CnrsHMode.integrate`` called ``int()`` on
complex Gaussian-integer constants.  Python rejects ``int(3+0j)`` even though
``3+0j`` is a valid Gaussian integer for CNRS-A native coefficients.
"""

import pytest

from cnrs.cnrs_h_mode import CnrsHMode
from cnrs.cnrs_h_native import NonGaussianCoefficientError
from cnrs.cnrs_scale import ScaleLaw
from cnrs.cnrs_ode import cnrs_solve_linear


def test_native_integrate_accepts_complex_real_gaussian_constant():
    mode = CnrsHMode.from_coeffs([1, 2], native=True)
    out = mode.integrate(3 + 0j)
    assert out.native is True
    assert out.coeffs[0] == 3 + 0j
    assert out.coeffs[1:] == (1 + 0j, 2 + 0j)


def test_native_integrate_accepts_full_gaussian_complex_constant():
    mode = CnrsHMode.from_coeffs([1, 2], native=True)
    out = mode.integrate(1 + 2j)
    assert out.native is True
    assert out.coeffs[0] == 1 + 2j
    assert out.coeffs[1:] == (1 + 0j, 2 + 0j)


def test_native_integrate_rejects_non_gaussian_constant():
    mode = CnrsHMode.from_coeffs([1, 2], native=True)
    with pytest.raises(NonGaussianCoefficientError):
        mode.integrate(1.5 + 0j)


def test_fast_integrate_still_accepts_non_gaussian_constant():
    mode = CnrsHMode.from_coeffs([1.0, 1.5], native=False)
    out = mode.integrate(1.5 + 0.25j)
    assert out.native is False
    assert out.coeffs[0] == 1.5 + 0.25j


def test_scalelaw_native_integral_accepts_gaussian_complex_constant():
    law = ScaleLaw.from_coeffs([1, 2], native=True)
    integ = law.integral(1 + 2j)
    assert integ.native_mode is True
    assert integ._mode.coeffs[0] == 1 + 2j


def test_ode_derivative_then_native_integrate_accepts_gaussian_constant():
    sol = cnrs_solve_linear(lam=2, y0=1, terms=6, native=True)
    dsol = sol.derivative()
    restored_stream = dsol._mode.integrate(1 + 0j)
    assert restored_stream.native is True
    assert restored_stream.coeffs[0] == 1 + 0j
