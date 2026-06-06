"""
test_cnrs_interop.py
====================
Test suite for cnrs_interop.py (Component 6 of the CNRS Scientific Toolkit).

Session: 43, 2026-06-06
Author:  Donald G. Palmer
"""

import cmath, math
import numpy as np
import pytest

from cnrs.cnrs_interop import (
    cnrsh_to_numpy, numpy_to_cnrsh, ode_solution_to_numpy,
    cnrs_complex_to_numpy,
    modulus_array, modulus_sq_array, real_array, imag_array,
    phase_array, phase_rate_array,
    cnrs_to_scipy_ivp, scipy_ivp_to_cnrsh,
    solve_and_compare, ComparisonResult,
    benchmark_linear, benchmark_second_order, BenchmarkResult,
    to_dataframe,
)
from cnrs.cnrs_h import CnrsH
from cnrs.cnrs_ode import cnrs_solve_linear, cnrs_solve_second_order


def rel_err(a, b):
    return abs(a - b) / (abs(b) + 1e-300)


# ============================================================================
# 1. cnrsh_to_numpy
# ============================================================================

class TestCnrshToNumpy:

    def test_exp_at_zero(self):
        h = CnrsH.exponential(1, terms=20)
        result = cnrsh_to_numpy(h, [0.0])
        assert abs(result[0] - 1.0) < 1e-10

    def test_exp_values(self):
        h = CnrsH.exponential(1, terms=30)
        s_vals = np.linspace(0.0, 0.5, 20)
        result = cnrsh_to_numpy(h, s_vals)
        expected = np.exp(s_vals.astype(complex))
        assert np.allclose(result, expected, rtol=1e-8)

    def test_returns_complex128(self):
        h = CnrsH.exponential(1, terms=10)
        result = cnrsh_to_numpy(h, [0.0, 0.5])
        assert result.dtype == complex

    def test_shape(self):
        h = CnrsH.exponential(1, terms=10)
        result = cnrsh_to_numpy(h, np.linspace(0, 1, 50))
        assert result.shape == (50,)

    def test_complex_eigenvalue(self):
        lam = complex(-0.2, 2.0)
        h = CnrsH.from_list([complex(lam**n) for n in range(30)])
        s = 0.3
        result = cnrsh_to_numpy(h, [s])
        expected = cmath.exp(lam * s)
        assert rel_err(result[0], expected) < 1e-7


# ============================================================================
# 2. numpy_to_cnrsh
# ============================================================================

class TestNumpyToCnrsh:

    def test_constant(self):
        s = np.linspace(0.0, 1.0, 50)
        y = 3.0 * np.ones(50, dtype=complex)
        h = numpy_to_cnrsh(y, s, degree=5)
        assert abs(h.evaluate(0.0) - 3.0) < 0.1

    def test_exponential_roundtrip(self):
        lam = -0.5
        s = np.linspace(0.0, 1.0, 80)
        y = np.exp(lam * s).astype(complex)
        h = numpy_to_cnrsh(y, s, degree=12)
        # Evaluate at midpoint
        val = h.evaluate(0.5)
        expected = math.exp(lam * 0.5)
        assert rel_err(val.real, expected) < 0.01

    def test_returns_cnrsh(self):
        s = np.linspace(0.0, 1.0, 20)
        y = np.exp(0.5 * s).astype(complex)
        h = numpy_to_cnrsh(y, s, degree=8)
        assert isinstance(h, CnrsH)

    def test_differentiation_after_fit(self):
        # Fit exp(lam*s); derivative should ≈ lam*exp(lam*s)
        lam = 0.8
        s = np.linspace(0.0, 0.8, 60)
        y = np.exp(lam * s).astype(complex)
        h = numpy_to_cnrsh(y, s, degree=14)
        dh = h.differentiate()
        # d/ds exp(lam*s) at s=0 = lam
        assert rel_err(dh.evaluate(0.0).real, lam) < 0.05


# ============================================================================
# 3. ode_solution_to_numpy
# ============================================================================

class TestOdeSolutionToNumpy:

    def test_linear_ode_values(self):
        lam = complex(-0.3, 1.5)
        sol = cnrs_solve_linear(lam=lam, y0=complex(1.0), terms=40)
        s_vals = np.linspace(0.0, 0.5, 30)
        result = ode_solution_to_numpy(sol, s_vals)
        expected = np.exp(lam * s_vals)
        assert np.allclose(result, expected, rtol=1e-7)

    def test_returns_complex128(self):
        sol = cnrs_solve_linear(lam=1.0, y0=1.0, terms=20)
        result = ode_solution_to_numpy(sol, [0.0, 0.5])
        assert result.dtype == complex

    def test_shape(self):
        sol = cnrs_solve_linear(lam=1.0, y0=1.0, terms=20)
        result = ode_solution_to_numpy(sol, np.linspace(0, 0.5, 40))
        assert result.shape == (40,)

    def test_initial_condition(self):
        y0 = complex(2.0, -1.0)
        sol = cnrs_solve_linear(lam=complex(0.1, 0.5), y0=y0, terms=30)
        result = ode_solution_to_numpy(sol, [0.0])
        assert rel_err(result[0], y0) < 1e-10


# ============================================================================
# 4. Observation-map array extractors
# ============================================================================

class TestObservationMaps:

    def setup_method(self):
        lam = complex(-0.3, 2.0)
        self.sol = cnrs_solve_linear(lam=lam, y0=complex(1.0), terms=40)
        self.lam = lam
        self.s_vals = np.linspace(0.0, 0.5, 50)

    def test_modulus_array(self):
        m = modulus_array(self.sol, self.s_vals)
        expected = np.exp(-0.3 * self.s_vals)
        assert np.allclose(m, expected, rtol=1e-7)

    def test_modulus_sq_array(self):
        m2 = modulus_sq_array(self.sol, self.s_vals)
        expected = np.exp(-0.6 * self.s_vals)
        assert np.allclose(m2, expected, rtol=1e-7)

    def test_real_array(self):
        r = real_array(self.sol, self.s_vals)
        expected = (np.exp(self.lam * self.s_vals)).real
        assert np.allclose(r, expected, rtol=1e-7)

    def test_imag_array(self):
        i = imag_array(self.sol, self.s_vals)
        expected = (np.exp(self.lam * self.s_vals)).imag
        assert np.allclose(i, expected, rtol=1e-7)

    def test_phase_array(self):
        ph = phase_array(self.sol, self.s_vals)
        expected = np.angle(np.exp(self.lam * self.s_vals))
        assert np.allclose(ph, expected, atol=1e-6)

    def test_phase_rate_array(self):
        pr = phase_rate_array(self.sol, self.s_vals)
        # Im(lam) = 2.0 everywhere for pure exponential
        assert np.allclose(pr, self.lam.imag, atol=1e-5)

    def test_shapes(self):
        n = len(self.s_vals)
        for fn in [modulus_array, modulus_sq_array, real_array,
                   imag_array, phase_array, phase_rate_array]:
            result = fn(self.sol, self.s_vals)
            assert result.shape == (n,), f"{fn.__name__} shape mismatch"

    def test_modulus_sq_equals_modulus_squared(self):
        m = modulus_array(self.sol, self.s_vals)
        m2 = modulus_sq_array(self.sol, self.s_vals)
        assert np.allclose(m**2, m2, rtol=1e-10)

    def test_oscillatory_invisible_in_modulus_sq(self):
        # |exp((-a+iw)*s)|^2 = exp(-2a*s): w invisible
        a, w = 0.3, 5.0
        sol1 = cnrs_solve_linear(lam=complex(-a, w), y0=1.0, terms=40)
        sol2 = cnrs_solve_linear(lam=complex(-a, 0), y0=1.0, terms=40)
        m2_1 = modulus_sq_array(sol1, self.s_vals)
        m2_2 = modulus_sq_array(sol2, self.s_vals)
        assert np.allclose(m2_1, m2_2, rtol=1e-6)
        # But phase_rate differs
        pr1 = phase_rate_array(sol1, self.s_vals)
        pr2 = phase_rate_array(sol2, self.s_vals)
        assert np.mean(np.abs(pr1 - pr2)) > 1.0


# ============================================================================
# 5. SciPy bridge: cnrs_to_scipy_ivp
# ============================================================================

class TestCnrsToScipyIvp:

    def test_attributes_present(self):
        sol = cnrs_solve_linear(lam=-0.5, y0=1.0, terms=20)
        s_vals = np.linspace(0.0, 0.5, 20)
        bunch = cnrs_to_scipy_ivp(sol, s_vals)
        for attr in ['t', 'y', 'success', 'message']:
            assert hasattr(bunch, attr)

    def test_t_shape(self):
        sol = cnrs_solve_linear(lam=-0.5, y0=1.0, terms=20)
        s_vals = np.linspace(0.0, 0.5, 30)
        bunch = cnrs_to_scipy_ivp(sol, s_vals)
        assert bunch.t.shape == (30,)

    def test_y_shape(self):
        sol = cnrs_solve_linear(lam=-0.5, y0=1.0, terms=20)
        s_vals = np.linspace(0.0, 0.5, 30)
        bunch = cnrs_to_scipy_ivp(sol, s_vals)
        assert bunch.y.shape == (2, 30)

    def test_success_true(self):
        sol = cnrs_solve_linear(lam=-0.5, y0=1.0, terms=20)
        bunch = cnrs_to_scipy_ivp(sol, [0.0, 0.5])
        assert bunch.success is True

    def test_values_match_ode_solution(self):
        lam = complex(-0.3, 1.0)
        sol = cnrs_solve_linear(lam=lam, y0=complex(1.0), terms=40)
        s_vals = np.linspace(0.0, 0.4, 20)
        bunch = cnrs_to_scipy_ivp(sol, s_vals)
        direct = ode_solution_to_numpy(sol, s_vals)
        reconstructed = bunch.y[0] + 1j * bunch.y[1]
        assert np.allclose(reconstructed, direct, rtol=1e-10)


# ============================================================================
# 6. SciPy bridge: scipy_ivp_to_cnrsh
# ============================================================================

class TestScipyIvpToCnrsh:

    def test_returns_cnrsh(self):
        from scipy.integrate import solve_ivp
        lam = -0.5
        ivp = solve_ivp(lambda t, y: [lam * y[0], lam * y[1]],
                        [0.0, 1.0], [1.0, 0.0],
                        t_eval=np.linspace(0.0, 1.0, 50), rtol=1e-10)
        h = scipy_ivp_to_cnrsh(ivp, degree=12)
        assert isinstance(h, CnrsH)

    def test_value_at_zero(self):
        from scipy.integrate import solve_ivp
        lam = -0.3
        ivp = solve_ivp(lambda t, y: [lam * y[0], lam * y[1]],
                        [0.0, 1.0], [2.0, 0.0],
                        t_eval=np.linspace(0.0, 1.0, 80), rtol=1e-10)
        h = scipy_ivp_to_cnrsh(ivp, degree=12)
        assert rel_err(h.evaluate(0.0).real, 2.0) < 0.05

    def test_cnrs_bundle_roundtrip(self):
        # CNRS → scipy bundle → CnrsH → evaluate: should recover original
        lam = complex(-0.2, 1.0)
        sol = cnrs_solve_linear(lam=lam, y0=complex(1.0), terms=40)
        s_vals = np.linspace(0.0, 0.5, 60)
        bunch = cnrs_to_scipy_ivp(sol, s_vals)
        h_rt = scipy_ivp_to_cnrsh(bunch, degree=14)
        # Values at midpoint should agree
        s_mid = 0.25
        orig = sol.evaluate(s_mid).real
        rt = h_rt.evaluate(s_mid).real
        assert rel_err(rt, orig) < 0.02


# ============================================================================
# 7. solve_and_compare
# ============================================================================

class TestSolveAndCompare:

    def test_returns_comparison_result(self):
        result = solve_and_compare(lam=-0.5, y0=1.0,
                                   s_vals=np.linspace(0.0, 0.5, 30))
        assert isinstance(result, ComparisonResult)

    def test_result_fields(self):
        result = solve_and_compare(lam=-0.5, y0=1.0,
                                   s_vals=np.linspace(0.0, 0.5, 20))
        for field in ('s_vals', 'cnrs_vals', 'scipy_vals', 'exact_vals',
                      'abs_err', 'rel_err', 'max_abs_err', 'max_rel_err',
                      'cnrs_time_ms', 'scipy_time_ms'):
            assert hasattr(result, field)

    def test_low_error_real(self):
        result = solve_and_compare(lam=-0.5, y0=1.0,
                                   s_vals=np.linspace(0.0, 0.5, 50),
                                   terms=30)
        assert result.max_rel_err < 1e-5

    def test_low_error_complex(self):
        result = solve_and_compare(lam=complex(-0.2, 3.0), y0=complex(1.0, 0.5),
                                   s_vals=np.linspace(0.0, 0.3, 50),
                                   terms=40)
        assert result.max_rel_err < 1e-5

    def test_cnrs_matches_exact(self):
        lam = complex(-0.3, 1.0)
        s_vals = np.linspace(0.0, 0.4, 30)
        result = solve_and_compare(lam=lam, y0=complex(1.0),
                                   s_vals=s_vals, terms=40)
        cnrs_exact_err = np.max(np.abs(result.cnrs_vals - result.exact_vals))
        assert cnrs_exact_err < 1e-8

    def test_times_positive(self):
        result = solve_and_compare(lam=-0.5, y0=1.0,
                                   s_vals=np.linspace(0.0, 0.5, 20))
        assert result.cnrs_time_ms > 0
        assert result.scipy_time_ms > 0

    def test_summary_nonempty(self):
        result = solve_and_compare(lam=-0.5, y0=1.0,
                                   s_vals=np.linspace(0.0, 0.5, 20))
        assert len(result.summary()) > 20


# ============================================================================
# 8. Benchmark utilities
# ============================================================================

class TestBenchmark:

    def test_linear_returns_benchmark_result(self):
        result = benchmark_linear(lam=-0.5, y0=1.0,
                                  s_vals=np.linspace(0.0, 0.5, 30),
                                  terms=25, n_repeat=3)
        assert isinstance(result, BenchmarkResult)

    def test_linear_fields(self):
        result = benchmark_linear(n_repeat=3,
                                  s_vals=np.linspace(0.0, 0.5, 20))
        for f in ('label', 'n_points', 'n_repeat', 'cnrs_ms',
                  'scipy_ms', 'max_rel_err', 'speedup_factor'):
            assert hasattr(result, f)

    def test_linear_accuracy(self):
        result = benchmark_linear(lam=complex(-0.3, 2.0),
                                  s_vals=np.linspace(0.0, 0.4, 50),
                                  terms=30, n_repeat=3)
        assert result.max_rel_err < 1e-5

    def test_second_order_returns_result(self):
        result = benchmark_second_order(gamma=0.1, omega=1.0, n_repeat=3,
                                        s_vals=np.linspace(0.0, 1.0, 30))
        assert isinstance(result, BenchmarkResult)

    def test_second_order_accuracy(self):
        result = benchmark_second_order(gamma=0.1, omega=1.0,
                                        s_vals=np.linspace(0.0, 1.0, 40),
                                        terms=40, n_repeat=3)
        assert result.max_rel_err < 1e-5

    def test_speedup_factor_positive(self):
        result = benchmark_linear(n_repeat=3,
                                  s_vals=np.linspace(0.0, 0.3, 20))
        assert result.speedup_factor > 0

    def test_summary_nonempty(self):
        result = benchmark_linear(n_repeat=3,
                                  s_vals=np.linspace(0.0, 0.3, 20))
        s = result.summary()
        assert 'CNRS' in s or 'scipy' in s

    def test_n_points_correct(self):
        s_vals = np.linspace(0.0, 0.5, 45)
        result = benchmark_linear(s_vals=s_vals, n_repeat=2)
        assert result.n_points == 45

    def test_n_repeat_correct(self):
        result = benchmark_linear(n_repeat=5,
                                  s_vals=np.linspace(0.0, 0.3, 20))
        assert result.n_repeat == 5


# ============================================================================
# 9. Pandas export
# ============================================================================

class TestToDataframe:

    def test_returns_dataframe_or_none(self):
        sol = cnrs_solve_linear(lam=-0.5, y0=1.0, terms=20)
        result = to_dataframe(sol, np.linspace(0.0, 0.5, 20))
        try:
            import pandas as pd
            assert isinstance(result, pd.DataFrame)
        except ImportError:
            assert result is None

    def test_columns_present(self):
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")
        sol = cnrs_solve_linear(lam=-0.5, y0=1.0, terms=20)
        df = to_dataframe(sol, np.linspace(0.0, 0.5, 20))
        for col in ['s', 'real', 'imag', 'modulus', 'modulus_sq', 'phase']:
            assert col in df.columns

    def test_shape(self):
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")
        sol = cnrs_solve_linear(lam=-0.5, y0=1.0, terms=20)
        df = to_dataframe(sol, np.linspace(0.0, 0.5, 25))
        assert len(df) == 25

    def test_col_selection(self):
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")
        sol = cnrs_solve_linear(lam=-0.5, y0=1.0, terms=20)
        df = to_dataframe(sol, np.linspace(0.0, 0.5, 10),
                          cols=['s', 'real', 'modulus'])
        assert list(df.columns) == ['s', 'real', 'modulus']

    def test_modulus_values_correct(self):
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")
        lam = -0.5
        sol = cnrs_solve_linear(lam=lam, y0=1.0, terms=30)
        s_vals = np.linspace(0.0, 0.5, 20)
        df = to_dataframe(sol, s_vals)
        expected_mod = np.exp(-0.5 * s_vals)
        assert np.allclose(df['modulus'].values, expected_mod, rtol=1e-7)
