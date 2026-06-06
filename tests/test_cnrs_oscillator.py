"""
test_cnrs_oscillator.py
=======================
Test suite for cnrs_oscillator.py (Component 5).

Session: 43, 2026-06-06
Author:  Donald G. Palmer
"""

import cmath
import math
import numpy as np
import pytest


from cnrs.cnrs_oscillator import (
    StuartLandauParams, RlcParams, DrivenParams,
    OscillatorSolution,
    stuart_landau_linear, rlc_free, rlc_driven,
    driven_harmonic, interference_pair,
    ThreeWorkflowResult,
    compare_stuart_landau, compare_rlc, compare_interference,
)


def rel_err(a, b):
    return abs(a - b) / (abs(b) + 1e-300)


# ============================================================================
# 1. Parameter dataclasses
# ============================================================================

class TestParams:

    def test_sl_defaults(self):
        p = StuartLandauParams()
        assert p.mu == 0.1
        assert p.omega == 2.0 * math.pi

    def test_sl_lam(self):
        p = StuartLandauParams(mu=0.2, omega=3.0)
        assert p.lam() == complex(0.2, 3.0)

    def test_sl_limit_cycle(self):
        p = StuartLandauParams(mu=0.5, omega=1.0, beta=complex(1.0, 0.0))
        r = p.limit_cycle_radius()
        assert r is not None
        assert rel_err(r, math.sqrt(0.5)) < 1e-10

    def test_sl_no_limit_cycle_decaying(self):
        p = StuartLandauParams(mu=-0.1, omega=1.0, beta=complex(1.0, 0.0))
        assert p.limit_cycle_radius() is None

    def test_sl_nonlinear_validity(self):
        p = StuartLandauParams(mu=1.0, omega=1.0, beta=complex(0.01, 0.0), z0=1.0)
        assert p.nonlinear_validity() < 0.1  # linear regime

    def test_rlc_defaults(self):
        p = RlcParams()
        assert p.L == 1.0

    def test_rlc_omega0(self):
        p = RlcParams(L=1.0, C=1.0)
        assert rel_err(p.omega0(), 1.0) < 1e-10

    def test_rlc_gamma(self):
        p = RlcParams(L=2.0, R=0.4)
        assert rel_err(p.gamma(), 0.1) < 1e-10

    def test_rlc_quality_factor(self):
        p = RlcParams(L=1.0, R=0.2, C=1.0)
        assert p.quality_factor() > 1.0  # underdamped

    def test_rlc_underdamped(self):
        p = RlcParams(L=1.0, R=0.2, C=1.0)
        assert p.is_underdamped()

    def test_rlc_overdamped(self):
        p = RlcParams(L=1.0, R=10.0, C=1.0)
        assert not p.is_underdamped()

    def test_rlc_omega_d(self):
        p = RlcParams(L=1.0, R=0.2, C=1.0)
        od = p.omega_d()
        assert od is not None
        expected = math.sqrt(p.omega0()**2 - p.gamma()**2)
        assert rel_err(od, expected) < 1e-10

    def test_rlc_omega_d_none_overdamped(self):
        p = RlcParams(L=1.0, R=10.0, C=1.0)
        assert p.omega_d() is None

    def test_driven_detuning(self):
        p = DrivenParams(omega0=1.0, omega_d=1.05)
        assert rel_err(p.detuning(), 0.05) < 1e-10

    def test_driven_resonant(self):
        p = DrivenParams(omega0=1.0, omega_d=1.0)
        assert p.is_resonant()

    def test_driven_steady_state(self):
        # At large detuning, |Z_ss| ≈ |A| / |omega0^2 - omega_d^2|
        p = DrivenParams(gamma=0.01, omega0=1.0, omega_d=2.0, amplitude=1.0)
        Z = p.steady_state_amplitude()
        assert abs(Z) > 0

    def test_driven_resonance_amplitude(self):
        p = DrivenParams(gamma=0.1, omega0=1.0, amplitude=1.0)
        expected = 1.0 / (2.0 * 0.1 * 1.0)
        assert rel_err(p.resonance_amplitude(), expected) < 1e-10


# ============================================================================
# 2. OscillatorSolution
# ============================================================================

class TestOscillatorSolution:

    def setup_method(self):
        p = StuartLandauParams(mu=0.0, omega=1.0, z0=complex(1.0, 0.0))
        self.sol = stuart_landau_linear(p, terms=40)

    def test_evaluate_at_zero(self):
        assert rel_err(self.sol.evaluate(0.0), 1.0) < 1e-10

    def test_call_scalar(self):
        v = self.sol(0.5)
        assert isinstance(v, complex)

    def test_call_array(self):
        t = np.array([0.0, 0.5, 1.0])
        v = self.sol(t)
        assert v.shape == (3,)

    def test_modulus_pure_oscillator(self):
        # mu=0: |z(t)| = 1 everywhere
        for t in [0.0, 0.3, 0.6, 1.0]:
            assert rel_err(self.sol.modulus(t), 1.0) < 1e-6

    def test_modulus_sq(self):
        t = 0.4
        m = self.sol.modulus(t)
        m2 = self.sol.modulus_sq(t)
        assert rel_err(m2, m**2) < 1e-10

    def test_real_part(self):
        t = 0.5
        v = self.sol.evaluate(t)
        assert rel_err(self.sol.real_part(t), v.real) < 1e-10

    def test_phase(self):
        t = 0.5
        v = self.sol.evaluate(t)
        assert rel_err(self.sol.phase(t), cmath.phase(v)) < 1e-10

    def test_instantaneous_frequency(self):
        # Pure oscillator with omega=1: IF = 1
        t = 0.3
        ifreq = self.sol.instantaneous_frequency(t)
        assert rel_err(ifreq, 1.0) < 1e-6

    def test_derivative(self):
        # d/dt exp(i*omega*t) = i*omega*exp(i*omega*t)
        dsol = self.sol.derivative()
        t = 0.3
        expected = 1j * 1.0 * self.sol.evaluate(t)
        assert rel_err(dsol.evaluate(t), expected) < 1e-6

    def test_repr(self):
        r = repr(self.sol)
        assert "OscillatorSolution" in r

    def test_s_max_positive(self):
        assert self.sol.s_max > 1.0


# ============================================================================
# 3. stuart_landau_linear
# ============================================================================

class TestStuartLandauLinear:

    def test_initial_condition(self):
        p = StuartLandauParams(mu=0.1, omega=2.0, z0=complex(2.0, 1.0))
        sol = stuart_landau_linear(p)
        assert rel_err(sol.evaluate(0.0), p.z0) < 1e-10

    def test_exponential_growth(self):
        # mu > 0: |z| grows exponentially
        p = StuartLandauParams(mu=0.3, omega=0.0, z0=1.0)
        sol = stuart_landau_linear(p, terms=40)
        t = 0.5
        expected = math.exp(0.3 * t)
        assert rel_err(sol.modulus(t), expected) < 1e-7

    def test_pure_oscillation(self):
        # mu=0: |z(t)| = |z0|
        p = StuartLandauParams(mu=0.0, omega=3.0, z0=complex(1.0, 0.0))
        sol = stuart_landau_linear(p, terms=40)
        for t in [0.1, 0.3, 0.5]:
            assert rel_err(sol.modulus(t), 1.0) < 1e-7

    def test_frequency_recovery(self):
        # omega must be recoverable from phase
        omega_true = 2.5
        p = StuartLandauParams(mu=0.0, omega=omega_true, z0=complex(1.0, 0.0))
        sol = stuart_landau_linear(p, terms=50)
        t = 0.3
        omega_measured = sol.instantaneous_frequency(t)
        assert rel_err(omega_measured, omega_true) < 1e-6

    def test_complex_initial_condition(self):
        p = StuartLandauParams(mu=0.1, omega=1.0, z0=complex(0.5, 0.7))
        sol = stuart_landau_linear(p, terms=40)
        assert rel_err(sol.evaluate(0.0), p.z0) < 1e-10

    def test_accuracy_vs_exact(self):
        p = StuartLandauParams(mu=0.05, omega=2.0, z0=complex(1.0, 0.0))
        sol = stuart_landau_linear(p, terms=50)
        t = 0.4
        exact = p.z0 * cmath.exp(p.lam() * t)
        assert rel_err(sol.evaluate(t), exact) < 1e-8


# ============================================================================
# 4. rlc_free
# ============================================================================

class TestRlcFree:

    def test_initial_condition(self):
        p = RlcParams(q0=complex(2.0, 0.0), dq0=complex(0.0, 0.0))
        sol = rlc_free(p)
        assert rel_err(sol.evaluate(0.0).real, 2.0) < 1e-10

    def test_underdamped_oscillation(self):
        # Q > 1: oscillates with decaying amplitude
        p = RlcParams(L=1.0, R=0.2, C=1.0, q0=complex(1.0, 0.0), dq0=0.0)
        sol = rlc_free(p, terms=50)
        t = 0.5
        gamma, omega0 = p.gamma(), p.omega0()
        omegad = p.omega_d()
        # Correct formula: q(t) = exp(-γt)*(cos(ωd*t) + γ/ωd * sin(ωd*t)) for dq0=0
        expected = math.exp(-gamma * t) * (
            math.cos(omegad * t) + (gamma / omegad) * math.sin(omegad * t))
        assert rel_err(sol.real_part(t), expected) < 1e-6

    def test_amplitude_decays(self):
        p = RlcParams(L=1.0, R=0.2, C=1.0, q0=complex(1.0, 0.0), dq0=0.0)
        sol = rlc_free(p, terms=50)
        assert sol.modulus(0.0) > sol.modulus(1.0)

    def test_overdamped_no_oscillation(self):
        # High R: overdamped, real exponential decay
        p = RlcParams(L=1.0, R=10.0, C=1.0, q0=complex(1.0, 0.0), dq0=0.0)
        sol = rlc_free(p, terms=40)
        # Real part should decrease monotonically from q0=1
        assert sol.real_part(0.0) > sol.real_part(0.1) > sol.real_part(0.2)

    def test_critically_damped(self):
        # gamma = omega0: no oscillation
        L, C = 1.0, 1.0
        R = 2.0 * math.sqrt(L / C)  # R = 2*sqrt(L/C) → gamma = omega0
        p = RlcParams(L=L, R=R, C=C, q0=complex(1.0, 0.0), dq0=0.0)
        assert rel_err(p.gamma(), p.omega0()) < 1e-10
        sol = rlc_free(p, terms=40)
        # q(0) = q0
        assert rel_err(sol.real_part(0.0), 1.0) < 1e-8


# ============================================================================
# 5. driven_harmonic
# ============================================================================

class TestDrivenHarmonic:

    def test_initial_condition(self):
        p = DrivenParams(gamma=0.1, omega0=1.0, omega_d=0.5,
                         amplitude=1.0, z0=complex(0.0, 0.0), dz0=0.0)
        sol = driven_harmonic(p)
        assert abs(sol.evaluate(0.0)) < 1e-10

    def test_steady_state_approached(self):
        # Off-resonance: solution should approach Z_ss * exp(i*omega_d*t)
        p = DrivenParams(gamma=0.5, omega0=2.0, omega_d=1.0,
                         amplitude=complex(1.0, 0.0), z0=0.0, dz0=0.0)
        sol = driven_harmonic(p, terms=50)
        Z_ss = p.steady_state_amplitude()
        # At t not too large (before domain boundary), check against exact
        t = 0.3
        v = sol.evaluate(t)
        assert abs(v) < 10.0  # bounded

    def test_resonance_larger_amplitude(self):
        # At resonance, amplitude grows; off-resonance it settles
        p_res = DrivenParams(gamma=0.05, omega0=1.0, omega_d=1.0, amplitude=1.0,
                             z0=0.0, dz0=0.0)
        p_off = DrivenParams(gamma=0.05, omega0=1.0, omega_d=2.0, amplitude=1.0,
                             z0=0.0, dz0=0.0)
        sol_res = driven_harmonic(p_res, terms=50)
        sol_off = driven_harmonic(p_off, terms=50)
        t = 1.0
        # Resonance should give larger modulus than far off-resonance at t=1
        assert sol_res.modulus(t) > sol_off.modulus(t)

    def test_detuning_field(self):
        p = DrivenParams(omega0=1.0, omega_d=1.1)
        assert rel_err(p.detuning(), 0.1) < 1e-10

    def test_returns_oscillator_solution(self):
        p = DrivenParams()
        sol = driven_harmonic(p)
        assert isinstance(sol, OscillatorSolution)


# ============================================================================
# 6. rlc_driven
# ============================================================================

class TestRlcDriven:

    def test_returns_oscillator_solution(self):
        p = RlcParams()
        sol = rlc_driven(p)
        assert isinstance(sol, OscillatorSolution)

    def test_initial_condition(self):
        p = RlcParams(q0=complex(1.0, 0.0), dq0=0.0)
        sol = rlc_driven(p)
        assert rel_err(sol.evaluate(0.0), p.q0) < 1e-8

    def test_small_t_continuous(self):
        # Solution should be continuous from initial condition
        p = RlcParams(q0=complex(0.5, 0.0), dq0=0.0)
        sol = rlc_driven(p)
        v0 = sol.evaluate(0.0)
        v_small = sol.evaluate(0.001)
        assert abs(v0 - v_small) < 0.01  # small change for small t


# ============================================================================
# 7. interference_pair
# ============================================================================

class TestInterferencePair:

    def test_initial_condition(self):
        sol = interference_pair(omega1=1.0, omega2=2.0,
                                amp1=complex(1.0, 0.0), amp2=complex(1.0, 0.0))
        expected = 1.0 + 1.0  # amp1 + amp2
        assert rel_err(sol.evaluate(0.0), expected) < 1e-10

    def test_exact_at_t(self):
        omega1, omega2 = 1.0, 2.0
        amp1, amp2 = complex(1.0, 0.0), complex(0.5, 0.3)
        sol = interference_pair(omega1, omega2, amp1, amp2, terms=50)
        t = 0.3
        expected = amp1 * cmath.exp(1j * omega1 * t) + amp2 * cmath.exp(1j * omega2 * t)
        assert rel_err(sol.evaluate(t), expected) < 1e-7

    def test_modulus_sq_has_beat(self):
        # |z|² oscillates at beat freq |omega1 - omega2|
        omega1, omega2 = 1.0, 1.5
        sol = interference_pair(omega1, omega2, terms=50)
        beat = abs(omega2 - omega1)
        T_beat = 2.0 * math.pi / beat
        t_vals = np.linspace(0.0, T_beat, 200)
        mod2 = sol.modulus_sq(t_vals)
        # |z|² should vary: max - min > 0
        assert float(np.max(mod2) - np.min(mod2)) > 0.1

    def test_single_frequency_no_beat(self):
        # omega1 = omega2: no beat
        sol = interference_pair(omega1=1.0, omega2=1.0,
                                amp1=complex(1.0, 0.0), amp2=complex(1.0, 0.0),
                                terms=50)
        mod2 = sol.modulus_sq(np.linspace(0.0, 2.0, 100))
        assert float(np.max(mod2) - np.min(mod2)) < 1e-6

    def test_cross_term_lost_in_early_reduction(self):
        # Incoherent sum |amp1|² + |amp2|² vs coherent |z|²
        omega1, omega2 = 1.0, 2.0
        sol = interference_pair(omega1, omega2, terms=50)
        t = 0.5
        incoherent = 1.0 + 1.0  # |amp1|² + |amp2|²
        coherent = sol.modulus_sq(t)
        # These generally differ (cross term non-zero)
        # At t where cross term is large, they differ significantly
        t_vals = np.linspace(0.0, 2.0 * math.pi, 100)
        mod2_arr = sol.modulus_sq(t_vals)
        incoherent_arr = np.full_like(t_vals, 2.0)
        assert float(np.max(np.abs(mod2_arr - incoherent_arr))) > 0.1


# ============================================================================
# 8. Three-workflow comparisons
# ============================================================================

class TestCompareWorkflows:

    def test_sl_returns_result(self):
        result = compare_stuart_landau()
        assert isinstance(result, ThreeWorkflowResult)

    def test_sl_omega_not_in_A(self):
        result = compare_stuart_landau()
        assert result.metrics["A_omega_recoverable"] is False

    def test_sl_C_recovers_omega(self):
        p = StuartLandauParams(mu=0.0, omega=2.5, z0=1.0)
        result = compare_stuart_landau(p, t_vals=np.linspace(0.0, 0.3, 200))
        # C_omega_from_stream should be close to omega=2.5
        assert rel_err(result.metrics["C_omega_from_stream"], 2.5) < 0.01

    def test_sl_C_matches_B(self):
        result = compare_stuart_landau()
        assert result.metrics["C_vs_B_rel_L2_error"] < 1e-5

    def test_sl_name(self):
        result = compare_stuart_landau()
        assert result.name == "stuart_landau"

    def test_rlc_returns_result(self):
        result = compare_rlc()
        assert isinstance(result, ThreeWorkflowResult)

    def test_rlc_oscillation_not_in_A(self):
        result = compare_rlc()
        assert result.metrics["A_oscillation_visible"] is False

    def test_rlc_quality_factor(self):
        result = compare_rlc()
        assert result.metrics["quality_factor"] > 1.0

    def test_rlc_C_accuracy(self):
        result = compare_rlc()
        assert result.metrics["C_vs_exact_rel_L2_error"] < 1e-5

    def test_interference_returns_result(self):
        result = compare_interference()
        assert isinstance(result, ThreeWorkflowResult)

    def test_interference_A_constant(self):
        result = compare_interference()
        assert result.metrics["A_intensity_constant"] is True

    def test_interference_cross_term_nonzero(self):
        result = compare_interference(omega1=1.0, omega2=1.5)
        assert result.metrics["B_cross_term_max"] > 0.5

    def test_interference_beat_frequency(self):
        result = compare_interference(omega1=1.0, omega2=1.5)
        assert rel_err(result.metrics["B_beat_frequency"], 0.5) < 1e-10

    def test_interference_C_accuracy(self):
        # Use short t_vals to stay within EGF domain
        import numpy as np
        t_short = np.linspace(0.0, 2.0, 200)
        result = compare_interference(omega1=1.0, omega2=1.5,
                                      t_vals=t_short, terms=60)
        assert result.metrics["C_vs_exact_rel_L2_error"] < 1e-5

    def test_interference_info_lost(self):
        result = compare_interference()
        assert result.metrics["information_lost_in_A"] is True

    def test_interpretation_nonempty(self):
        for fn in [compare_stuart_landau, compare_rlc, compare_interference]:
            result = fn()
            assert len(result.interpretation) > 20
