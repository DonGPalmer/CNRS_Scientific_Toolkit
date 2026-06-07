"""
test_cnrs_multiscale.py
=======================
Test suite for cnrs_multiscale.py (Component 7 of the CNRS Scientific Toolkit).

Covers:
  - ScaleLadder construction (uniform, from_profile, from_solutions)
  - Rung lookup (rung_at)
  - Core evaluation and boundary propagation
  - Continuity at rung boundaries
  - Scale-aware observable maps (all seven)
  - Exact scale_derivative via digit-shift
  - LadderEvalResult
  - ladder_profile utility
  - ladder_to_scalelaws utility
  - scale_gradient_correction (Paper 18, Theorem 1)
  - Placeholder stubs raise NotImplementedError
  - Domain edge cases and error handling

Session: 44, 2026-06-07
Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
"""

import cmath
import math
from typing import List

import numpy as np
import pytest

from cnrs.cnrs_multiscale import (
    FieldEquationCheck,
    JunctionCondition,
    LadderEvalResult,
    PsiZeroDeterminer,
    ScaleGradientResult,
    ScaleLadder,
    ladder_profile,
    ladder_to_scalelaws,
    scale_gradient_correction,
)
from cnrs.cnrs_ode import OdeSolution, cnrs_solve_linear
from cnrs.cnrs_scale import ScaleLaw


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rel_err(a, b):
    return abs(a - b) / (abs(b) + 1e-300)


def make_uniform(lam=complex(-0.5, 1.0), y0=1.0, s_total=1.0, n_rungs=4, terms=30):
    return ScaleLadder.uniform(lam, y0=y0, s_total=s_total, n_rungs=n_rungs, terms=terms)


# ---------------------------------------------------------------------------
# 1. Construction
# ---------------------------------------------------------------------------

class TestConstruction:

    def test_uniform_returns_scalelader(self):
        ladder = make_uniform()
        assert isinstance(ladder, ScaleLadder)

    def test_uniform_rung_count(self):
        ladder = ScaleLadder.uniform(lam=1.0, n_rungs=5, s_total=1.0)
        assert ladder.n_rungs == 5

    def test_uniform_s_edges_count(self):
        ladder = ScaleLadder.uniform(lam=1.0, n_rungs=4, s_total=1.0)
        assert len(ladder.s_edges) == 5

    def test_uniform_s_edges_values(self):
        ladder = ScaleLadder.uniform(lam=1.0, n_rungs=4, s_total=1.0)
        expected = [0.0, 0.25, 0.5, 0.75, 1.0]
        for a, b in zip(ladder.s_edges, expected):
            assert abs(a - b) < 1e-12

    def test_uniform_s_total(self):
        ladder = ScaleLadder.uniform(lam=1.0, n_rungs=4, s_total=2.0)
        assert abs(ladder.s_total - 2.0) < 1e-12

    def test_from_profile_constant(self):
        # Constant profile should match uniform
        lam = complex(-0.3, 0.8)
        ladder_u = ScaleLadder.uniform(lam, y0=2.0, s_total=1.0, n_rungs=3, terms=30)
        ladder_p = ScaleLadder.from_profile(
            lambda s: lam, y0=2.0, s_total=1.0, n_rungs=3, terms=30
        )
        for s in [0.0, 0.3, 0.7, 1.0]:
            assert rel_err(ladder_u.evaluate(s), ladder_p.evaluate(s)) < 1e-6

    def test_from_profile_varying(self):
        # Eigenvalue ramps from -0.5 to -1.0 across scale
        lam_profile = lambda s: complex(-0.5 - 0.5 * s, 1.0)
        ladder = ScaleLadder.from_profile(
            lam_profile, y0=1.0, s_total=1.0, n_rungs=5, terms=30
        )
        assert ladder.n_rungs == 5
        # Just check it evaluates without error
        v = ladder.evaluate(0.5)
        assert math.isfinite(abs(v))

    def test_from_profile_explicit_edges(self):
        edges = [0.0, 0.2, 0.5, 1.0]
        ladder = ScaleLadder.from_profile(
            lambda s: complex(-0.3, 0.5),
            y0=1.0,
            s_edges=edges,
            terms=25,
        )
        assert ladder.n_rungs == 3
        assert ladder.s_edges == edges

    def test_from_solutions(self):
        sol1 = cnrs_solve_linear(complex(-0.5, 1.0), 1.0, terms=25)
        y_mid = sol1.evaluate(0.5)
        sol2 = cnrs_solve_linear(complex(-0.3, 0.8), y_mid, terms=25)
        ladder = ScaleLadder.from_solutions([sol1, sol2], s_edges=[0.0, 0.5, 1.0])
        assert ladder.n_rungs == 2

    def test_from_solutions_mismatch_raises(self):
        sol = cnrs_solve_linear(1.0, 1.0, terms=20)
        with pytest.raises(ValueError, match="len\\(s_edges\\)"):
            ScaleLadder.from_solutions([sol, sol], s_edges=[0.0, 0.5])

    def test_repr(self):
        ladder = make_uniform()
        r = repr(ladder)
        assert "ScaleLadder" in r
        assert "rungs" in r


# ---------------------------------------------------------------------------
# 2. Rung lookup
# ---------------------------------------------------------------------------

class TestRungAt:

    def test_rung_at_start(self):
        ladder = make_uniform(n_rungs=4, s_total=1.0)
        k, s_local = ladder.rung_at(0.0)
        assert k == 0
        assert abs(s_local) < 1e-12

    def test_rung_at_end(self):
        ladder = make_uniform(n_rungs=4, s_total=1.0)
        k, s_local = ladder.rung_at(1.0)
        assert k == 3  # last rung
        assert abs(s_local - 0.25) < 1e-10

    def test_rung_at_interior(self):
        ladder = make_uniform(n_rungs=4, s_total=1.0)
        k, s_local = ladder.rung_at(0.6)
        # s=0.6 is in rung 2 ([0.5, 0.75]), local s = 0.1
        assert k == 2
        assert abs(s_local - 0.1) < 1e-10

    def test_rung_at_boundary_between_rungs(self):
        ladder = make_uniform(n_rungs=4, s_total=1.0)
        k, s_local = ladder.rung_at(0.5)
        # Could be rung 1 (s_local=0.25) or rung 2 (s_local=0.0);
        # either is acceptable — just check consistency
        assert k in (1, 2)
        if k == 1:
            assert abs(s_local - 0.25) < 1e-10
        else:
            assert abs(s_local) < 1e-10

    def test_rung_at_below_raises(self):
        ladder = make_uniform()
        with pytest.raises(ValueError, match="below"):
            ladder.rung_at(-0.1)

    def test_rung_at_above_raises(self):
        ladder = make_uniform(s_total=1.0)
        with pytest.raises(ValueError, match="above"):
            ladder.rung_at(1.1)


# ---------------------------------------------------------------------------
# 3. Boundary propagation and continuity
# ---------------------------------------------------------------------------

class TestBoundaryPropagation:

    def test_initial_value_exact(self):
        """Ladder value at s=0 equals y0."""
        lam = complex(-0.4, 1.2)
        y0 = complex(2.0, 0.5)
        ladder = ScaleLadder.uniform(lam, y0=y0, s_total=1.0, n_rungs=4, terms=40)
        assert rel_err(ladder.evaluate(0.0), y0) < 1e-10

    def test_boundary_values_length(self):
        ladder = make_uniform(n_rungs=4)
        bvs = ladder.boundary_values
        assert len(bvs) == 5  # n_rungs + 1

    def test_boundary_continuity(self):
        """
        Ψ must be continuous at each rung boundary.

        The value from the upper edge of rung k must equal the value from
        the lower edge of rung k+1.
        """
        lam = complex(-0.3, 0.7)
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=5, terms=40)

        for k in range(1, ladder.n_rungs):
            s_boundary = ladder.s_edges[k]
            # Evaluate from left (rung k-1) and right (rung k)
            # Slight offset to stay within each rung
            eps = 1e-8
            v_left = ladder.evaluate(s_boundary - eps)
            v_right = ladder.evaluate(s_boundary + eps)
            # Should be nearly equal (within eps * |Ψ'|)
            assert abs(v_left - v_right) < 1e-4, (
                f"Discontinuity at boundary {k}: "
                f"|Ψ_left - Ψ_right| = {abs(v_left - v_right):.2e}"
            )

    def test_uniform_matches_exact_solution(self):
        """
        For y' = λy, the exact solution is y0 * exp(λs).
        A uniform ScaleLadder should match this.
        """
        lam = complex(-0.5, 1.0)
        y0 = 1.0
        ladder = ScaleLadder.uniform(lam, y0=y0, s_total=1.0, n_rungs=4, terms=40)
        for s in [0.0, 0.2, 0.5, 0.8, 1.0]:
            expected = y0 * cmath.exp(lam * s)
            got = ladder.evaluate(s)
            assert rel_err(got, expected) < 1e-8, (
                f"s={s}: expected {expected:.6f}, got {got:.6f}"
            )

    def test_from_solutions_continuity(self):
        """from_solutions with matching boundary values is continuous."""
        lam1 = complex(-0.5, 1.0)
        lam2 = complex(-0.3, 0.5)
        sol1 = cnrs_solve_linear(lam1, 1.0, terms=30)
        y_mid = sol1.evaluate(0.5)
        sol2 = cnrs_solve_linear(lam2, y_mid, terms=30)
        ladder = ScaleLadder.from_solutions([sol1, sol2], [0.0, 0.5, 1.0])
        # Continuity at s=0.5: two different eigenvalues, 0.002-wide window.
        # Tolerance accounts for O(δs * |dΨ/ds|) variation across the gap.
        v_lo = ladder.evaluate(0.499)
        v_hi = ladder.evaluate(0.501)
        assert abs(v_lo - v_hi) < 2e-3


# ---------------------------------------------------------------------------
# 4. Observable maps
# ---------------------------------------------------------------------------

class TestObservableMaps:

    def setup_method(self):
        lam = complex(-0.3, 1.2)
        self.ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=4, terms=40)
        self.s_test = 0.45
        self.v = self.ladder.evaluate(self.s_test)

    def test_modulus_sq(self):
        expected = abs(self.v) ** 2
        assert rel_err(self.ladder.modulus_sq(self.s_test), expected) < 1e-12

    def test_real_part(self):
        assert rel_err(self.ladder.real_part(self.s_test), self.v.real) < 1e-12

    def test_imag_part(self):
        assert rel_err(self.ladder.imag_part(self.s_test), self.v.imag) < 1e-12

    def test_phase(self):
        expected = cmath.phase(self.v)
        assert rel_err(self.ladder.phase(self.s_test), expected) < 1e-10

    def test_phase_rate_exact(self):
        """For y = exp(λs), phase_rate = Im(λ) exactly."""
        lam = complex(-0.3, 1.2)
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=1, terms=40)
        pr = ladder.phase_rate(0.5)
        assert rel_err(pr, lam.imag) < 1e-8

    def test_phase_current_formula(self):
        """phase_current = modulus_sq * phase_rate."""
        ms = self.ladder.modulus_sq(self.s_test)
        pr = self.ladder.phase_rate(self.s_test)
        pc = self.ladder.phase_current(self.s_test)
        assert rel_err(pc, ms * pr) < 1e-10

    def test_scale_derivative_exact(self):
        """
        For y = y0 * exp(λs), dΨ/ds = λ * Ψ exactly.
        """
        lam = complex(-0.4, 0.9)
        y0 = complex(2.0, 0.5)
        ladder = ScaleLadder.uniform(lam, y0=y0, s_total=1.0, n_rungs=1, terms=40)
        s = 0.3
        psi = ladder.evaluate(s)
        dpsi_ds = ladder.scale_derivative(s)
        expected = lam * psi
        assert rel_err(dpsi_ds, expected) < 1e-8

    def test_full_eval_fields(self):
        r = self.ladder.full_eval(self.s_test)
        assert isinstance(r, LadderEvalResult)
        assert r.s == self.s_test
        assert isinstance(r.rung, int)
        assert math.isfinite(r.modulus_sq)
        assert math.isfinite(r.phase)
        assert math.isfinite(r.phase_rate)
        assert math.isfinite(r.phase_current)

    def test_full_eval_value_matches_evaluate(self):
        r = self.ladder.full_eval(self.s_test)
        assert rel_err(r.value, self.v) < 1e-12

    def test_full_eval_at_start(self):
        r = self.ladder.full_eval(0.0)
        assert r.rung == 0
        assert abs(r.local_s) < 1e-12


# ---------------------------------------------------------------------------
# 5. Profile utility
# ---------------------------------------------------------------------------

class TestLadderProfile:

    def setup_method(self):
        self.ladder = make_uniform(lam=complex(-0.3, 1.0), s_total=1.0, n_rungs=4, terms=30)
        self.s_vals = np.linspace(0.0, 1.0, 10)

    def test_returns_tuple(self):
        result = ladder_profile(self.ladder, self.s_vals)
        assert isinstance(result, tuple) and len(result) == 2

    def test_s_array_matches(self):
        s_out, _ = ladder_profile(self.ladder, self.s_vals)
        np.testing.assert_array_almost_equal(s_out, self.s_vals)

    def test_modulus_sq_profile(self):
        s_out, vals = ladder_profile(self.ladder, self.s_vals, "modulus_sq")
        # All values should be positive
        assert np.all(vals >= 0)

    def test_phase_profile(self):
        s_out, vals = ladder_profile(self.ladder, self.s_vals, "phase")
        assert np.all(np.abs(vals) <= math.pi + 1e-10)

    def test_real_part_profile(self):
        s_out, vals = ladder_profile(self.ladder, self.s_vals, "real_part")
        expected = np.array([self.ladder.real_part(float(sv)) for sv in self.s_vals])
        np.testing.assert_array_almost_equal(vals, expected)

    def test_scale_derivative_real_profile(self):
        s_out, vals = ladder_profile(self.ladder, self.s_vals, "scale_derivative_real")
        assert len(vals) == len(self.s_vals)

    def test_modulus_profile(self):
        s_out, vals = ladder_profile(self.ladder, self.s_vals, "modulus")
        assert np.all(vals >= 0)

    def test_unknown_observable_raises(self):
        with pytest.raises(ValueError, match="Unknown observable"):
            ladder_profile(self.ladder, self.s_vals, "not_a_thing")

    def test_phase_current_profile_formula(self):
        s_out, pc_vals = ladder_profile(self.ladder, self.s_vals, "phase_current")
        s_out, ms_vals = ladder_profile(self.ladder, self.s_vals, "modulus_sq")
        s_out, pr_vals = ladder_profile(self.ladder, self.s_vals, "phase_rate")
        np.testing.assert_array_almost_equal(pc_vals, ms_vals * pr_vals, decimal=8)


# ---------------------------------------------------------------------------
# 6. ladder_to_scalelaws
# ---------------------------------------------------------------------------

class TestLadderToScaleLaws:

    def test_returns_list_of_scalelaws(self):
        ladder = make_uniform(n_rungs=3)
        laws = ladder_to_scalelaws(ladder)
        assert len(laws) == 3
        assert all(isinstance(law, ScaleLaw) for law in laws)

    def test_rung_names(self):
        ladder = make_uniform(n_rungs=3)
        laws = ladder_to_scalelaws(ladder)
        assert laws[0].name == "rung_0"
        assert laws[2].name == "rung_2"

    def test_scalelaws_evaluate_consistently(self):
        """ScaleLaw rung values at s_local=0 match ladder boundary values."""
        lam = complex(-0.4, 0.8)
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=3, terms=30)
        laws = ladder_to_scalelaws(ladder)
        bvs = ladder.boundary_values
        for k, law in enumerate(laws):
            v_law = law.evaluate(0.0)
            v_bv = bvs[k]
            assert rel_err(v_law, v_bv) < 1e-10, (
                f"Rung {k}: ScaleLaw(0) = {v_law}, boundary = {v_bv}"
            )


# ---------------------------------------------------------------------------
# 7. Scale-gradient correction
# ---------------------------------------------------------------------------

class TestScaleGradientCorrection:

    def test_returns_result_object(self):
        ladder = make_uniform(lam=complex(-0.3, 1.0))
        result = scale_gradient_correction(ladder, s=0.3, delta_s=0.05)
        assert isinstance(result, ScaleGradientResult)

    def test_d_eff_formula(self):
        """d_eff = d_base * d_ratio."""
        ladder = make_uniform(lam=complex(-0.5, 1.0), s_total=1.0, n_rungs=1, terms=40)
        result = scale_gradient_correction(ladder, s=0.2, delta_s=0.1, d_base=2.0)
        assert rel_err(result.d_eff, 2.0 * result.d_ratio) < 1e-12

    def test_correction_formula(self):
        """correction = d_ratio - 1."""
        ladder = make_uniform(lam=complex(-0.3, 0.5))
        result = scale_gradient_correction(ladder, s=0.3, delta_s=0.05)
        assert rel_err(result.correction, result.d_ratio - 1.0) < 1e-12

    def test_flat_field_unit_ratio(self):
        """For constant |Ψ| (Im(λ)=0, Re(λ)=0), d_ratio ≈ 1."""
        # Pure imaginary eigenvalue: |Ψ(s)| = |y0| constant
        lam = complex(0.0, 1.0)
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=1, terms=40)
        result = scale_gradient_correction(ladder, s=0.2, delta_s=0.05)
        assert abs(result.d_ratio - 1.0) < 1e-8

    def test_decaying_field_ratio_less_than_one(self):
        """For Re(λ) < 0 (decaying field), |Ψ(s+δs)| < |Ψ(s)|, so d_ratio < 1."""
        lam = complex(-1.0, 0.0)
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=1, terms=40)
        result = scale_gradient_correction(ladder, s=0.2, delta_s=0.1)
        assert result.d_ratio < 1.0

    def test_growing_field_ratio_greater_than_one(self):
        """For Re(λ) > 0 (growing field), d_ratio > 1."""
        lam = complex(0.5, 0.0)
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=1, terms=40)
        result = scale_gradient_correction(ladder, s=0.2, delta_s=0.1)
        assert result.d_ratio > 1.0

    def test_at_upper_edge_clamped(self):
        """scale_gradient_correction at s_total clamps delta_s."""
        ladder = make_uniform(s_total=1.0)
        # Should not raise even though s + delta_s > s_total
        result = scale_gradient_correction(ladder, s=0.95, delta_s=0.1)
        assert isinstance(result, ScaleGradientResult)

    def test_d_eff_default_base_is_one(self):
        """Default d_base=1 → d_eff = d_ratio."""
        ladder = make_uniform(lam=complex(-0.4, 0.8))
        result = scale_gradient_correction(ladder, s=0.3, delta_s=0.05)
        assert rel_err(result.d_eff, result.d_ratio) < 1e-12

    def test_paper18_theorem1_decaying_mode(self):
        """
        Paper 18, Theorem 1 test: for a decaying activator mode with
        Re(λ) = -d_a (activator decay), the scale-gradient correction
        d_eff tracks the ratio of amplitudes across scale δs.

        For y(s) = exp(λs), the exact ratio is exp(Re(λ) * δs).
        """
        lam = complex(-0.5, 1.0)
        y0 = 1.0
        delta_s = 0.05
        s = 0.3
        ladder = ScaleLadder.uniform(lam, y0=y0, s_total=1.0, n_rungs=1, terms=40)
        result = scale_gradient_correction(ladder, s=s, delta_s=delta_s)
        expected_ratio = math.exp(lam.real * delta_s)
        assert rel_err(result.d_ratio, expected_ratio) < 1e-8


# ---------------------------------------------------------------------------
# 8. Placeholder stubs
# ---------------------------------------------------------------------------

class TestPlaceholderStubs:

    def test_junction_condition_raises(self):
        jc = JunctionCondition(s_junction=0.5)
        sol = cnrs_solve_linear(1.0, 1.0, terms=10)
        with pytest.raises(NotImplementedError, match="Thread 5"):
            jc.apply(sol, sol)

    def test_field_equation_check_raises(self):
        fec = FieldEquationCheck()
        ladder = make_uniform()
        with pytest.raises(NotImplementedError, match="Thread 5"):
            fec.check(ladder, L=4.0)

    def test_psi_zero_determiner_raises(self):
        pzd = PsiZeroDeterminer()
        ladder = make_uniform()
        with pytest.raises(NotImplementedError, match="Thread 5"):
            pzd.determine(ladder)


# ---------------------------------------------------------------------------
# 9. Summary and repr
# ---------------------------------------------------------------------------

class TestSummary:

    def test_summary_returns_string(self):
        ladder = make_uniform()
        s = ladder.summary()
        assert isinstance(s, str)
        assert "ScaleLadder" in s

    def test_summary_contains_rung_count(self):
        ladder = make_uniform(n_rungs=3)
        s = ladder.summary()
        assert "3" in s

    def test_repr_contains_key_info(self):
        ladder = make_uniform(n_rungs=4, s_total=1.0)
        r = repr(ladder)
        assert "4" in r
        assert "0.00" in r
        assert "1.00" in r


# ---------------------------------------------------------------------------
# 10. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_single_rung_ladder(self):
        ladder = ScaleLadder.uniform(lam=complex(-0.5, 1.0), n_rungs=1, s_total=1.0)
        assert ladder.n_rungs == 1
        v = ladder.evaluate(0.5)
        expected = cmath.exp(complex(-0.5, 1.0) * 0.5)
        assert rel_err(v, expected) < 1e-8

    def test_many_rungs(self):
        ladder = ScaleLadder.uniform(lam=complex(-0.3, 0.7), n_rungs=20, s_total=1.0)
        assert ladder.n_rungs == 20
        v = ladder.evaluate(0.99)
        assert math.isfinite(abs(v))

    def test_zero_eigenvalue(self):
        """For λ=0, y(s) = y0 constant."""
        ladder = ScaleLadder.uniform(lam=0.0, y0=complex(3.0, 1.0), n_rungs=4,
                                     s_total=1.0, terms=30)
        for s in [0.0, 0.3, 0.7, 1.0]:
            v = ladder.evaluate(s)
            assert rel_err(v, complex(3.0, 1.0)) < 1e-6

    def test_real_eigenvalue(self):
        """For λ real, Im(Ψ) should be zero if y0 is real."""
        lam = -0.5
        ladder = ScaleLadder.uniform(lam, y0=1.0, n_rungs=4, s_total=1.0, terms=40)
        for s in [0.1, 0.5, 0.9]:
            v = ladder.evaluate(s)
            assert abs(v.imag) < 1e-10

    def test_profile_ladder_two_regimes(self):
        """
        Ladder where the first half has Re(λ) > 0 (growing) and
        the second half has Re(λ) < 0 (decaying).
        """
        def profile(s):
            return complex(0.5 - s, 1.0)  # crosses Re=0 at s=0.5
        ladder = ScaleLadder.from_profile(
            profile, y0=1.0, s_total=1.0, n_rungs=8, terms=30
        )
        # Growing region: |Ψ(0.3)| > |Ψ(0.0)|
        assert ladder.modulus_sq(0.3) > ladder.modulus_sq(0.0)
        # Field is continuous throughout
        for s in np.linspace(0.01, 0.99, 20):
            assert math.isfinite(abs(ladder.evaluate(float(s))))

    def test_boundary_values_count(self):
        n = 6
        ladder = make_uniform(n_rungs=n)
        assert len(ladder.boundary_values) == n + 1
