"""
test_cnrs_scale.py
==================
Test suite for cnrs_scale.py (Component 3 of the CNRS Scientific Toolkit).

Covers:
  - ScaleLaw construction (exponential, from_coeffs, from_cnrsh)
  - Evaluation and __call__ (scalar and array)
  - Derivative (digit shift) and integral
  - Log-derivative
  - Observation maps (modulus, modulus_sq, real_part, imag_part, phase, phase_rate)
  - fit_exponential
  - fit_egf
  - fit_allometric
  - turing_threshold
  - Domain warning
  - Edge cases

Session: 43, 2026-06-06
Author:  Donald G. Palmer
"""

import cmath
import math
from pathlib import Path

import numpy as np
import pytest


from cnrs.cnrs_scale import (
    AllometricResult,
    FitResult,
    ScaleLaw,
    TuringResult,
    fit_allometric,
    fit_egf,
    fit_exponential,
    turing_threshold,
)


def rel_err(a, b):
    return abs(a - b) / (abs(b) + 1e-300)


# ============================================================================
# 1. Construction
# ============================================================================

class TestConstruction:

    def test_exponential_real(self):
        law = ScaleLaw.exponential(lam=1.0, scale=1.0, terms=30)
        assert abs(law.evaluate(0.0) - 1.0) < 1e-10
        assert rel_err(law.evaluate(1.0).real, math.e) < 1e-8

    def test_exponential_complex(self):
        lam = complex(-0.5, 2.0)
        law = ScaleLaw.exponential(lam=lam, scale=2.0, terms=40)
        s = 0.5
        expected = 2.0 * cmath.exp(lam * s)
        assert rel_err(law.evaluate(s), expected) < 1e-8

    def test_exponential_zero_lam(self):
        law = ScaleLaw.exponential(lam=0.0, scale=3.0, terms=20)
        assert abs(law.evaluate(0.0) - 3.0) < 1e-10
        assert abs(law.evaluate(1.0) - 3.0) < 1e-6

    def test_from_coeffs(self):
        # EGF: f(s) = c0 + c1*s + c2*s^2/2! = 1 + 2s + 3s^2/2
        law = ScaleLaw.from_coeffs([1.0, 2.0, 3.0])
        assert abs(law.evaluate(0.0) - 1.0) < 1e-12
        # f(1) = 1 + 2 + 1.5 = 4.5
        assert abs(law.evaluate(1.0) - 4.5) < 1e-10

    def test_from_coeffs_name(self):
        law = ScaleLaw.from_coeffs([1.0, 2.0], name="my_law")
        assert law.name == "my_law"

    def test_from_cnrsh(self):
        from cnrs.cnrs_h import CnrsH
        h = CnrsH.from_list([1.0, 0.5, 0.25])
        law = ScaleLaw.from_cnrsh(h, name="from_h")
        assert law.name == "from_h"
        assert abs(law.evaluate(0.0) - 1.0) < 1e-12

    def test_repr(self):
        law = ScaleLaw.exponential(lam=1.0, terms=25)
        r = repr(law)
        assert "ScaleLaw" in r
        assert "s_max" in r


# ============================================================================
# 2. Evaluation
# ============================================================================

class TestEvaluation:

    def test_scalar(self):
        law = ScaleLaw.exponential(lam=1.0, terms=30)
        v = law.evaluate(0.5)
        assert isinstance(v, complex)
        assert rel_err(v.real, math.exp(0.5)) < 1e-8

    def test_call_scalar(self):
        law = ScaleLaw.exponential(lam=2.0, terms=40)
        s = 0.3
        assert rel_err(law(s).real, math.exp(2.0 * s)) < 1e-8

    def test_call_array(self):
        law = ScaleLaw.exponential(lam=1.0, terms=30)
        s = np.array([0.0, 0.5, 1.0])
        result = law(s)
        assert result.shape == (3,)
        expected = np.exp(s)
        assert np.allclose(result.real, expected, rtol=1e-7)

    def test_call_2d_array(self):
        law = ScaleLaw.exponential(lam=1.0, terms=30)
        s = np.array([[0.0, 0.5], [1.0, 1.5]])
        result = law(s)
        assert result.shape == (2, 2)

    def test_s_max_positive(self):
        law = ScaleLaw.exponential(lam=1.0, terms=25)
        assert law.s_max > 1.0

    def test_domain_warning(self):
        law = ScaleLaw.exponential(lam=5.0, terms=10, name="narrow")
        with pytest.warns(UserWarning, match="reliable domain"):
            law.evaluate(20.0)


# ============================================================================
# 3. Derivative and Integral
# ============================================================================

class TestCalculus:

    def test_derivative_exp(self):
        lam = complex(0.7, -0.3)
        law = ScaleLaw.exponential(lam=lam, scale=1.0, terms=40)
        dlam = law.derivative()
        s = 0.5
        expected = lam * cmath.exp(lam * s)
        assert rel_err(dlam.evaluate(s), expected) < 1e-8

    def test_derivative_polynomial(self):
        # f = 1 + 2s + 3s^2/2!  → f' = 2 + 3s
        law = ScaleLaw.from_coeffs([1.0, 2.0, 3.0, 0.0])
        dlaw = law.derivative()
        assert abs(dlaw.evaluate(0.0) - 2.0) < 1e-10
        assert abs(dlaw.evaluate(1.0) - 5.0) < 1e-8

    def test_derivative_twice(self):
        lam = 2.0
        law = ScaleLaw.exponential(lam=lam, terms=40)
        d2law = law.derivative().derivative()
        s = 0.4
        expected = lam ** 2 * math.exp(lam * s)
        assert rel_err(d2law.evaluate(s).real, expected) < 1e-7

    def test_integral_recovers_original(self):
        lam = 1.5
        law = ScaleLaw.exponential(lam=lam, terms=40)
        ilaw = law.integral(constant=0.0)
        dilaw = ilaw.derivative()
        s = 0.6
        assert rel_err(dilaw.evaluate(s).real, law.evaluate(s).real) < 1e-7

    def test_log_derivative_exp(self):
        lam = complex(0.5, 1.2)
        law = ScaleLaw.exponential(lam=lam, terms=40)
        ld = law.log_derivative(0.3)
        assert rel_err(ld.real, lam.real) < 1e-7
        assert rel_err(ld.imag, lam.imag) < 1e-7

    def test_log_derivative_near_zero(self):
        law = ScaleLaw.from_coeffs([0.0, 0.0, 0.0])
        ld = law.log_derivative(0.0)
        assert math.isnan(ld.real)


# ============================================================================
# 4. Observation maps
# ============================================================================

class TestObservationMaps:

    def setup_method(self):
        self.lam = complex(-0.3, 2.0)
        self.law = ScaleLaw.exponential(lam=self.lam, terms=40)

    def test_modulus(self):
        s = 0.5
        expected = math.exp(-0.3 * s)
        assert rel_err(self.law.modulus(s), expected) < 1e-7

    def test_modulus_sq(self):
        s = 0.5
        expected = math.exp(-0.6 * s)
        assert rel_err(self.law.modulus_sq(s), expected) < 1e-7

    def test_real_part(self):
        s = 0.5
        expected = cmath.exp(self.lam * s).real
        assert rel_err(self.law.real_part(s), expected) < 1e-7

    def test_imag_part(self):
        s = 0.5
        expected = cmath.exp(self.lam * s).imag
        assert rel_err(self.law.imag_part(s), expected) < 1e-7

    def test_phase(self):
        s = 0.5
        expected = cmath.phase(cmath.exp(self.lam * s))
        assert abs(self.law.phase(s) - expected) < 1e-7

    def test_phase_rate(self):
        s = 0.4
        pr = self.law.phase_rate(s)
        assert rel_err(pr, self.lam.imag) < 1e-7

    def test_modulus_array(self):
        s = np.array([0.0, 0.3, 0.6])
        m = self.law.modulus(s)
        expected = np.exp(-0.3 * s)
        assert np.allclose(m, expected, rtol=1e-7)

    def test_phase_array_shape(self):
        s = np.array([0.0, 0.2, 0.4])
        ph = self.law.phase(s)
        assert ph.shape == (3,)

    def test_early_vs_late_reduction_agree(self):
        s = 0.5
        early = self.law.modulus_sq(s)
        late = abs(self.law.evaluate(s)) ** 2
        assert rel_err(early, late) < 1e-10

    def test_oscillatory_content_invisible_to_modulus_sq(self):
        # |exp((-a + i*omega)*s)|^2 = exp(-2a*s): omega drops out
        a, omega = 0.3, 4.5
        law1 = ScaleLaw.exponential(lam=complex(-a, omega), terms=40)
        law2 = ScaleLaw.exponential(lam=complex(-a, 0.0), terms=40)
        s = 0.5
        assert rel_err(law1.modulus_sq(s), law2.modulus_sq(s)) < 1e-6
        # phase_rate shows the omega content
        assert abs(law1.phase_rate(s) - law2.phase_rate(s)) > 1.0


# ============================================================================
# 5. fit_exponential
# ============================================================================

class TestFitExponential:

    def test_real_exponential(self):
        lam_true = -0.5
        scale_true = 2.0
        s = np.linspace(0.1, 2.0, 50)
        y = scale_true * np.exp(lam_true * s)
        result = fit_exponential(s, y, terms=30)
        assert isinstance(result, FitResult)
        assert rel_err(result.lam.real, lam_true) < 0.01
        assert result.residual < 1e-5

    def test_complex_exponential(self):
        lam_true = complex(-0.2, 3.0)
        scale_true = complex(1.0, 0.5)
        s = np.linspace(0.1, 1.5, 80)
        y = scale_true * np.exp(lam_true * s)
        result = fit_exponential(s, y, terms=40)
        assert rel_err(result.lam.real, lam_true.real) < 0.01
        assert rel_err(result.lam.imag, lam_true.imag) < 0.01
        assert result.residual < 1e-4

    def test_result_law_callable(self):
        s = np.linspace(0.0, 1.0, 20)
        y = np.exp(-0.3 * s) * (1.0 + 0j)
        result = fit_exponential(s, y)
        v = result.law(0.5)
        assert isinstance(v, complex)

    def test_result_fields(self):
        s = np.linspace(0.1, 1.0, 20)
        y = np.exp(0.5 * s)
        result = fit_exponential(s, y)
        assert hasattr(result, "lam")
        assert hasattr(result, "scale")
        assert hasattr(result, "residual")
        assert hasattr(result, "law")


# ============================================================================
# 6. fit_egf
# ============================================================================

class TestFitEgf:

    def test_constant(self):
        s = np.linspace(0.0, 1.0, 30)
        y = 3.0 * np.ones_like(s, dtype=complex)
        law = fit_egf(s, y, degree=3, name="const")
        assert rel_err(law.evaluate(0.0).real, 3.0) < 0.01
        assert rel_err(law.evaluate(0.5).real, 3.0) < 0.01

    def test_polynomial(self):
        s = np.linspace(0.0, 1.0, 50)
        y = 1.0 + 2.0 * s + s ** 2
        law = fit_egf(s, y, degree=5)
        assert rel_err(law.evaluate(0.0).real, 1.0) < 0.01
        assert rel_err(law.evaluate(1.0).real, 4.0) < 0.01

    def test_returns_scale_law(self):
        s = np.linspace(0.0, 1.0, 20)
        y = np.exp(0.5 * s)
        law = fit_egf(s, y, degree=8)
        assert isinstance(law, ScaleLaw)

    def test_differentiation_after_fit(self):
        lam = 0.8
        s = np.linspace(0.0, 1.0, 40)
        y = np.exp(lam * s)
        law = fit_egf(s, y, degree=12)
        dlam = law.derivative()
        s_test = 0.5
        expected = lam * math.exp(lam * s_test)
        assert rel_err(dlam.evaluate(s_test).real, expected) < 0.01


# ============================================================================
# 7. fit_allometric
# ============================================================================

class TestFitAllometric:

    def test_kleiber_exponent(self):
        b_true = 0.75
        s = np.linspace(0.0, 5.0, 60)
        y = 1.5 * np.exp(b_true * s)
        result = fit_allometric(s, y)
        assert isinstance(result, AllometricResult)
        assert rel_err(result.exponent, b_true) < 0.001
        assert rel_err(result.amplitude, 1.5) < 0.001
        assert result.r_squared > 0.999

    def test_isometric(self):
        b_true = 1.0
        s = np.linspace(0.0, 3.0, 40)
        y = np.exp(b_true * s)
        result = fit_allometric(s, y)
        assert rel_err(result.exponent, b_true) < 0.001

    def test_negative_exponent(self):
        b_true = -0.5
        s = np.linspace(0.1, 3.0, 40)
        y = 2.0 * np.exp(b_true * s)
        result = fit_allometric(s, y)
        assert rel_err(result.exponent, b_true) < 0.01
        assert rel_err(result.amplitude, 2.0) < 0.01

    def test_law_evaluates(self):
        s = np.linspace(0.0, 2.0, 30)
        y = np.exp(0.6 * s)
        result = fit_allometric(s, y)
        v = result.law.evaluate(1.0)
        assert isinstance(v, complex)
        assert rel_err(v.real, math.exp(0.6)) < 0.01

    def test_residual_small_for_power_law(self):
        s = np.linspace(0.0, 4.0, 50)
        y = 3.0 * np.exp(0.8 * s)
        result = fit_allometric(s, y)
        assert result.residual < 1e-8

    def test_raises_on_nonpositive_y(self):
        s = np.linspace(0.0, 1.0, 10)
        y = np.array([1.0, -1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
        with pytest.raises(ValueError, match="positive"):
            fit_allometric(s, y)

    def test_result_fields(self):
        s = np.linspace(0.0, 2.0, 20)
        y = np.exp(0.5 * s)
        result = fit_allometric(s, y)
        for field in ("exponent", "amplitude", "residual", "r_squared", "law"):
            assert hasattr(result, field)

    def test_law_log_derivative_gives_exponent(self):
        b_true = 0.75
        s = np.linspace(0.1, 3.0, 40)
        y = np.exp(b_true * s)
        result = fit_allometric(s, y)
        ld = result.law.log_derivative(1.0)
        assert rel_err(ld.real, b_true) < 0.001


# ============================================================================
# 8. turing_threshold
# ============================================================================

class TestTuringThreshold:

    def test_crossing_found(self):
        # log-deriv of exp(s - s^2) = 1 - 2s, crosses 0 at s = 0.5
        s_pts = np.linspace(0.0, 1.0, 200)
        y = np.exp(s_pts - s_pts ** 2)
        law = fit_egf(s_pts, y, degree=14)
        result = turing_threshold(law, threshold=0.0, s_lo=0.1, s_hi=0.9)
        assert result.crossed
        assert result.s_exit is not None
        assert 0.4 < result.s_exit < 0.6

    def test_no_crossing(self):
        # exp(1.0 * s): log-deriv = 1.0; threshold 0.0 → no crossing
        law = ScaleLaw.exponential(lam=1.0, terms=30)
        result = turing_threshold(law, threshold=0.0, s_lo=0.0, s_hi=2.0)
        assert not result.crossed
        assert result.s_exit is None

    def test_result_fields(self):
        law = ScaleLaw.exponential(lam=-0.5, terms=30)
        result = turing_threshold(law, threshold=-1.0, s_lo=0.0, s_hi=2.0)
        for field in ("s_exit", "threshold", "crossed", "lambda_lo", "lambda_hi"):
            assert hasattr(result, field)

    def test_lambda_lo_hi_constant(self):
        law = ScaleLaw.exponential(lam=2.0, terms=30)
        result = turing_threshold(law, threshold=0.0, s_lo=0.1, s_hi=1.0)
        assert rel_err(result.lambda_lo, 2.0) < 0.01
        assert rel_err(result.lambda_hi, 2.0) < 0.01

    def test_threshold_field(self):
        law = ScaleLaw.exponential(lam=1.0, terms=30)
        result = turing_threshold(law, threshold=0.5, s_lo=0.0, s_hi=1.0)
        assert result.threshold == 0.5

    def test_bisection_accuracy(self):
        s_pts = np.linspace(0.0, 1.0, 200)
        y = np.exp(s_pts - s_pts ** 2)
        law = fit_egf(s_pts, y, degree=14)
        result = turing_threshold(law, threshold=0.0, s_lo=0.05, s_hi=0.95,
                                  n_points=400)
        assert result.crossed
        assert abs(result.s_exit - 0.5) < 0.01

    def test_scale_space_s_exit(self):
        """
        Model for Scale Space Turing threshold near s_exit ≈ 0.52 nats.
        Construct f with log-deriv = 1 - s/s_exit, crossing 0 at s_exit.
        """
        s_exit_true = 0.52
        s_pts = np.linspace(0.0, 1.0, 300)
        y = np.exp(s_pts - s_pts ** 2 / (2 * s_exit_true))
        law = fit_egf(s_pts, y, degree=16)
        result = turing_threshold(law, threshold=0.0, s_lo=0.1, s_hi=0.9,
                                  n_points=500)
        assert result.crossed
        assert abs(result.s_exit - s_exit_true) < 0.02


# ============================================================================
# 9. Edge cases
# ============================================================================

class TestEdgeCases:

    def test_constant_law(self):
        law = ScaleLaw.from_coeffs([5.0])
        assert abs(law.evaluate(0.0) - 5.0) < 1e-10
        assert abs(law.evaluate(1.0) - 5.0) < 1e-6

    def test_purely_imaginary_lam(self):
        omega = 3.0
        law = ScaleLaw.exponential(lam=complex(0.0, omega), terms=40)
        for s in [0.0, 0.2, 0.5, 0.8]:
            assert rel_err(law.modulus(s), 1.0) < 1e-7

    def test_decay_monotone(self):
        law = ScaleLaw.exponential(lam=-2.0, terms=30)
        assert law.modulus(0.0) > law.modulus(0.5) > law.modulus(1.0)

    def test_integral_derivative_roundtrip(self):
        law = ScaleLaw.exponential(lam=complex(0.5, 1.0), terms=40)
        dlam = law.derivative()
        idlam = dlam.integral(constant=law.evaluate(0.0))
        s = 0.4
        assert rel_err(idlam.evaluate(s), law.evaluate(s)) < 1e-6

    def test_name_in_derivative(self):
        law = ScaleLaw.exponential(lam=1.0, name="test_law", terms=20)
        d = law.derivative()
        assert "test_law" in d.name
