"""
test_cnrs_regime.py
===================
Test suite for cnrs_regime.py (Component 8 of the CNRS Scientific Toolkit).

Covers:
  - ScaleParameter: constant, linear, quadratic, enforce_positive, values()
  - detect_transitions: no transitions, single, multiple, edge cases
  - ScaleSweepResult: active_intervals, repr
  - ScaleSweep: general constructor, scale_grid, run with/without classifier
  - ScaleSweep.from_ladder: bridge to Component 7 ScaleLadder
  - logarithmic_scale and length_from_scale: roundtrip, errors
  - RegimeTransition: midpoint, repr
  - Error handling: n < 2, s_max <= s_min, length mismatch

Session: 44, 2026-06-07
Author:  Donald G. Palmer
Design:  AI1 (June 2026 multi-scale review)
"""

import math

import pytest

from cnrs.cnrs_regime import (
    RegimeTransition,
    ScaleParameter,
    ScaleSweep,
    ScaleSweepResult,
    detect_transitions,
    length_from_scale,
    logarithmic_scale,
)
from cnrs.cnrs_multiscale import ScaleLadder, LadderEvalResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rel_err(a, b):
    return abs(a - b) / (abs(b) + 1e-300)


def make_ladder(lam=complex(-0.3, 1.0), s_total=1.0, n_rungs=4):
    return ScaleLadder.uniform(lam, y0=1.0, s_total=s_total, n_rungs=n_rungs, terms=30)


# ---------------------------------------------------------------------------
# 1. ScaleParameter
# ---------------------------------------------------------------------------

class TestScaleParameter:

    def test_constant_no_coefficients(self):
        p = ScaleParameter(base=10.0, coefficients=[])
        assert p(0.0) == 10.0
        assert p(2.0) == 10.0
        assert p(-3.0) == 10.0

    def test_constant_zero_coefficient(self):
        p = ScaleParameter(base=5.0, coefficients=[0.0])
        assert p(0.0) == 5.0
        assert p(1.0) == 5.0

    def test_linear_positive(self):
        p = ScaleParameter(base=100.0, coefficients=[0.1])
        assert p(0.0) == 100.0
        assert rel_err(p(1.0), 110.0) < 1e-12
        assert rel_err(p(-1.0), 90.0) < 1e-12

    def test_linear_negative(self):
        p = ScaleParameter(base=100.0, coefficients=[-0.3])
        assert rel_err(p(1.0), 70.0) < 1e-12

    def test_quadratic(self):
        # p(s) = 2 * (1 + 1*s + 1*s^2)
        # p(2) = 2 * (1 + 2 + 4) = 14
        p = ScaleParameter(base=2.0, coefficients=[1.0, 1.0])
        assert rel_err(p(2.0), 14.0) < 1e-12

    def test_at_zero_always_base(self):
        for coeffs in [[], [0.5], [-0.3, 0.1], [1.0, 2.0, 3.0]]:
            p = ScaleParameter(base=7.0, coefficients=coeffs)
            assert rel_err(p(0.0), 7.0) < 1e-12

    def test_enforce_positive_raises(self):
        p = ScaleParameter(base=1.0, coefficients=[-2.0], enforce_positive=True)
        with pytest.raises(ValueError, match="non-positive"):
            p(1.0)

    def test_enforce_positive_ok(self):
        p = ScaleParameter(base=10.0, coefficients=[-0.1], enforce_positive=True)
        assert p(1.0) == 9.0  # stays positive

    def test_values_list(self):
        p = ScaleParameter(base=1.0, coefficients=[1.0])
        result = p.values([0.0, 1.0, 2.0])
        assert result == [1.0, 2.0, 3.0]

    def test_name_attribute(self):
        p = ScaleParameter(base=1.0, coefficients=[], name="D_u")
        assert p.name == "D_u"

    def test_repr_contains_name(self):
        p = ScaleParameter(base=1.0, coefficients=[0.1], name="kappa")
        assert "kappa" in repr(p)

    def test_frozen(self):
        p = ScaleParameter(base=1.0, coefficients=[0.1])
        with pytest.raises((AttributeError, TypeError)):
            p.base = 2.0

    def test_cubic_coefficient(self):
        # p(s) = 3 * (1 + 0*s + 0*s^2 + 1*s^3)
        # p(2) = 3 * (1 + 0 + 0 + 8) = 27
        p = ScaleParameter(base=3.0, coefficients=[0.0, 0.0, 1.0])
        assert rel_err(p(2.0), 27.0) < 1e-12


# ---------------------------------------------------------------------------
# 2. RegimeTransition
# ---------------------------------------------------------------------------

class TestRegimeTransition:

    def test_midpoint(self):
        t = RegimeTransition(s_left=1.0, s_right=2.0, state_left=False, state_right=True)
        assert t.midpoint == 1.5

    def test_midpoint_asymmetric(self):
        t = RegimeTransition(s_left=0.3, s_right=0.7, state_left=True, state_right=False)
        assert abs(t.midpoint - 0.5) < 1e-12

    def test_state_attributes(self):
        t = RegimeTransition(s_left=0.0, s_right=1.0, state_left=False, state_right=True)
        assert t.state_left is False
        assert t.state_right is True

    def test_repr(self):
        t = RegimeTransition(s_left=1.0, s_right=2.0, state_left=False, state_right=True)
        r = repr(t)
        assert "RegimeTransition" in r
        assert "1.5" in r

    def test_frozen(self):
        t = RegimeTransition(s_left=0.0, s_right=1.0, state_left=False, state_right=True)
        with pytest.raises((AttributeError, TypeError)):
            t.s_left = 0.5


# ---------------------------------------------------------------------------
# 3. detect_transitions
# ---------------------------------------------------------------------------

class TestDetectTransitions:

    def test_no_transitions(self):
        scales = [0.0, 1.0, 2.0]
        states = [True, True, True]
        assert detect_transitions(scales, states) == []

    def test_single_false_to_true(self):
        scales = [0.0, 1.0, 2.0, 3.0]
        states = [False, False, True, True]
        trans = detect_transitions(scales, states)
        assert len(trans) == 1
        assert trans[0].s_left == 1.0
        assert trans[0].s_right == 2.0
        assert trans[0].state_left is False
        assert trans[0].state_right is True
        assert trans[0].midpoint == 1.5

    def test_single_true_to_false(self):
        scales = [0.0, 1.0, 2.0]
        states = [True, True, False]
        trans = detect_transitions(scales, states)
        assert len(trans) == 1
        assert trans[0].state_left is True
        assert trans[0].state_right is False

    def test_multiple_transitions(self):
        scales = [0.0, 1.0, 2.0, 3.0, 4.0]
        states = [False, True, True, False, False]
        trans = detect_transitions(scales, states)
        assert len(trans) == 2
        assert trans[0].state_right is True
        assert trans[1].state_right is False

    def test_alternating_transitions(self):
        scales = [0.0, 1.0, 2.0, 3.0]
        states = [True, False, True, False]
        trans = detect_transitions(scales, states)
        assert len(trans) == 3

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="same length"):
            detect_transitions([0.0, 1.0, 2.0], [True, False])

    def test_single_point(self):
        assert detect_transitions([0.0], [True]) == []

    def test_two_points_no_change(self):
        assert detect_transitions([0.0, 1.0], [True, True]) == []

    def test_two_points_change(self):
        trans = detect_transitions([0.0, 1.0], [False, True])
        assert len(trans) == 1


# ---------------------------------------------------------------------------
# 4. ScaleSweepResult
# ---------------------------------------------------------------------------

class TestScaleSweepResult:

    def test_active_intervals_none_regime(self):
        result = ScaleSweepResult(scales=[0.0, 1.0], outputs=[None, None])
        assert result.active_intervals() == []

    def test_active_intervals_all_active(self):
        result = ScaleSweepResult(
            scales=[0.0, 1.0, 2.0],
            outputs=[None] * 3,
            regime=[True, True, True],
        )
        intervals = result.active_intervals()
        assert len(intervals) == 1
        assert intervals[0] == (0.0, 2.0)

    def test_active_intervals_none_active(self):
        result = ScaleSweepResult(
            scales=[0.0, 1.0, 2.0],
            outputs=[None] * 3,
            regime=[False, False, False],
        )
        assert result.active_intervals() == []

    def test_active_intervals_middle_window(self):
        result = ScaleSweepResult(
            scales=[0.0, 1.0, 2.0, 3.0],
            outputs=[None] * 4,
            regime=[False, True, True, False],
        )
        intervals = result.active_intervals()
        assert len(intervals) == 1
        assert intervals[0] == (1.0, 3.0)

    def test_active_intervals_two_windows(self):
        result = ScaleSweepResult(
            scales=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
            outputs=[None] * 6,
            regime=[False, True, False, False, True, True],
        )
        intervals = result.active_intervals()
        assert len(intervals) == 2

    def test_repr(self):
        result = ScaleSweepResult(
            scales=[0.0, 1.0, 2.0],
            outputs=[1, 2, 3],
            regime=[False, True, True],
            transitions=[],
        )
        r = repr(result)
        assert "ScaleSweepResult" in r


# ---------------------------------------------------------------------------
# 5. ScaleSweep — general constructor
# ---------------------------------------------------------------------------

class TestScaleSweepGeneral:

    def test_scale_grid_uniform(self):
        sweep = ScaleSweep(
            model=lambda s, p: s,
            parameters={},
            s_min=0.0, s_max=2.0, n=5,
        )
        grid = sweep.scale_grid()
        assert len(grid) == 5
        assert abs(grid[0] - 0.0) < 1e-12
        assert abs(grid[-1] - 2.0) < 1e-12
        assert abs(grid[2] - 1.0) < 1e-12

    def test_n_less_than_2_raises(self):
        with pytest.raises(ValueError, match="n >= 2"):
            ScaleSweep(model=lambda s, p: s, parameters={},
                       s_min=0.0, s_max=1.0, n=1)

    def test_s_max_le_s_min_raises(self):
        with pytest.raises(ValueError, match="s_max > s_min"):
            ScaleSweep(model=lambda s, p: s, parameters={},
                       s_min=1.0, s_max=0.0, n=5)

    def test_s_max_equal_s_min_raises(self):
        with pytest.raises(ValueError, match="s_max > s_min"):
            ScaleSweep(model=lambda s, p: s, parameters={},
                       s_min=1.0, s_max=1.0, n=5)

    def test_run_no_classifier(self):
        sweep = ScaleSweep(
            model=lambda s, p: s * 2,
            parameters={},
            s_min=0.0, s_max=1.0, n=3,
        )
        result = sweep.run()
        assert result.regime is None
        assert result.transitions is None
        assert len(result.outputs) == 3

    def test_run_with_classifier(self):
        sweep = ScaleSweep(
            model=lambda s, p: s,
            parameters={},
            s_min=0.0, s_max=2.0, n=3,
            classifier=lambda x: x > 1.0,
        )
        result = sweep.run()
        assert result.regime == [False, False, True]
        assert len(result.transitions) == 1

    def test_run_with_parameters(self):
        params = {"a": ScaleParameter(base=1.0, coefficients=[1.0])}
        sweep = ScaleSweep(
            model=lambda s, p: p["a"],
            parameters=params,
            s_min=0.0, s_max=2.0, n=3,
            classifier=lambda x: x > 1.5,
        )
        result = sweep.run()
        # a(0)=1, a(1)=2, a(2)=3 → regime [False, True, True]
        assert result.regime == [False, True, True]
        assert len(result.transitions) == 1

    def test_ai1_test_constant_parameter(self):
        """AI1 original test: constant ScaleParameter."""
        p = ScaleParameter(base=10.0, coefficients=[])
        assert p(0.0) == 10.0
        assert p(2.0) == 10.0

    def test_ai1_test_linear_parameter(self):
        """AI1 original test: linear ScaleParameter (isclose for fp precision)."""
        p = ScaleParameter(base=100.0, coefficients=[0.1])
        assert p(0.0) == 100.0
        assert math.isclose(p(1.0), 110.0, rel_tol=1e-10)
        assert math.isclose(p(-1.0), 90.0, rel_tol=1e-10)

    def test_ai1_test_quadratic_parameter(self):
        """AI1 original test: quadratic ScaleParameter."""
        p = ScaleParameter(base=2.0, coefficients=[1.0, 1.0])
        assert p(2.0) == 14.0

    def test_ai1_test_positive_guard(self):
        """AI1 original test: enforce_positive guard."""
        p = ScaleParameter(base=1.0, coefficients=[-2.0], enforce_positive=True)
        with pytest.raises(ValueError):
            p(1.0)

    def test_ai1_test_transitions(self):
        """AI1 original test: detect_transitions."""
        scales = [0.0, 1.0, 2.0, 3.0]
        states = [False, False, True, True]
        transitions = detect_transitions(scales, states)
        assert len(transitions) == 1
        assert transitions[0].s_left == 1.0
        assert transitions[0].s_right == 2.0
        assert transitions[0].midpoint == 1.5

    def test_ai1_test_scale_sweep_with_classifier(self):
        """AI1 original test: full sweep with classifier."""
        def model(s, params):
            return {"value": params["a"]}

        def classifier(output):
            return output["value"] > 1.5

        parameters = {"a": ScaleParameter(base=1.0, coefficients=[1.0])}
        sweep = ScaleSweep(
            model=model,
            parameters=parameters,
            s_min=0.0, s_max=2.0, n=3,
            classifier=classifier,
        )
        result = sweep.run()
        assert result.scales == [0.0, 1.0, 2.0]
        assert result.regime == [False, True, True]
        assert result.transitions is not None
        assert len(result.transitions) == 1

    def test_repr(self):
        sweep = ScaleSweep(
            model=lambda s, p: s,
            parameters={},
            s_min=0.0, s_max=1.0, n=10,
            label="test_sweep",
        )
        r = repr(sweep)
        assert "ScaleSweep" in r
        assert "test_sweep" in r


# ---------------------------------------------------------------------------
# 6. ScaleSweep.from_ladder (Component 7 bridge)
# ---------------------------------------------------------------------------

class TestScaleSweepFromLadder:

    def test_from_ladder_returns_sweep(self):
        ladder = make_ladder()
        sweep = ScaleSweep.from_ladder(
            ladder,
            classifier=lambda r: r.modulus_sq > 0.5,
            n=10,
        )
        assert isinstance(sweep, ScaleSweep)

    def test_from_ladder_run_returns_result(self):
        ladder = make_ladder(lam=complex(-0.3, 1.0), s_total=1.0)
        sweep = ScaleSweep.from_ladder(
            ladder,
            classifier=lambda r: r.modulus_sq > 0.1,
            n=10,
        )
        result = sweep.run()
        assert isinstance(result, ScaleSweepResult)
        assert len(result.scales) == 10
        assert len(result.outputs) == 10

    def test_from_ladder_outputs_are_ladder_eval_results(self):
        ladder = make_ladder()
        sweep = ScaleSweep.from_ladder(
            ladder,
            classifier=lambda r: r.phase > 0,
            n=8,
        )
        result = sweep.run()
        for output in result.outputs:
            assert isinstance(output, LadderEvalResult)

    def test_from_ladder_default_s_range(self):
        ladder = ScaleLadder.uniform(complex(-0.3, 1.0), s_total=2.0, n_rungs=4)
        sweep = ScaleSweep.from_ladder(ladder, classifier=lambda r: True, n=5)
        assert abs(sweep.s_min - 0.0) < 1e-12
        assert abs(sweep.s_max - 2.0) < 1e-12

    def test_from_ladder_custom_s_range(self):
        ladder = make_ladder(s_total=1.0)
        sweep = ScaleSweep.from_ladder(
            ladder, classifier=lambda r: True,
            s_min=0.1, s_max=0.9, n=5,
        )
        assert abs(sweep.s_min - 0.1) < 1e-12
        assert abs(sweep.s_max - 0.9) < 1e-12

    def test_from_ladder_regime_uses_modulus_sq(self):
        """
        For a decaying field (Re(λ) < 0), |Ψ|² decreases monotonically.
        Classifier |Ψ|² > threshold should give active window at small s.
        """
        lam = complex(-2.0, 0.0)  # strong decay
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=1, terms=40)
        # At s=0: |Ψ|²=1.  At s=1: |Ψ|²=exp(-4)≈0.018.
        sweep = ScaleSweep.from_ladder(
            ladder,
            classifier=lambda r: r.modulus_sq > 0.1,
            n=20,
        )
        result = sweep.run()
        # First point should be active (|Ψ|²=1 > 0.1)
        assert result.regime[0] is True
        # Last point should be inactive (|Ψ|²≈0.018 < 0.1)
        assert result.regime[-1] is False
        # There should be at least one transition
        assert len(result.transitions) >= 1

    def test_from_ladder_classifier_uses_phase_rate(self):
        """
        For y = exp(iωs), phase_rate = ω everywhere.
        Classifier on phase_rate should give uniform regime.
        """
        lam = complex(0.0, 2.0)  # pure oscillation, ω=2
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=1, terms=40)
        sweep = ScaleSweep.from_ladder(
            ladder,
            classifier=lambda r: r.phase_rate > 1.5,  # ω=2 > 1.5 everywhere
            n=10,
        )
        result = sweep.run()
        assert all(result.regime)  # active everywhere
        assert len(result.transitions) == 0

    def test_from_ladder_active_intervals(self):
        """Active intervals from a ladder sweep are well-formed."""
        lam = complex(-1.5, 1.0)
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=1, terms=40)
        sweep = ScaleSweep.from_ladder(
            ladder,
            classifier=lambda r: r.modulus_sq > 0.05,
            n=50,
        )
        result = sweep.run()
        intervals = result.active_intervals()
        # At least one active interval (field starts above threshold)
        assert len(intervals) >= 1
        # Intervals are properly ordered
        for lo, hi in intervals:
            assert lo < hi

    def test_from_ladder_phase_current_classifier(self):
        """Classifier on phase_current: J = |Ψ|² · dθ/ds."""
        lam = complex(-0.3, 1.5)
        ladder = ScaleLadder.uniform(lam, y0=1.0, s_total=1.0, n_rungs=4, terms=40)
        sweep = ScaleSweep.from_ladder(
            ladder,
            classifier=lambda r: r.phase_current > 0.5,
            n=20,
        )
        result = sweep.run()
        # All outputs should be LadderEvalResult
        assert all(isinstance(o, LadderEvalResult) for o in result.outputs)


# ---------------------------------------------------------------------------
# 7. logarithmic_scale and length_from_scale
# ---------------------------------------------------------------------------

class TestCoordinateUtilities:

    def test_roundtrip(self):
        L_ref = 2.0
        L = 10.0
        s = logarithmic_scale(L, L_ref)
        recovered = length_from_scale(s, L_ref)
        assert math.isclose(recovered, L, rel_tol=1e-12)

    def test_logarithmic_scale_at_reference(self):
        """s = 0 when L = L_ref."""
        assert logarithmic_scale(5.0, 5.0) == 0.0

    def test_logarithmic_scale_above_reference(self):
        s = logarithmic_scale(math.e, 1.0)
        assert math.isclose(s, 1.0, rel_tol=1e-12)

    def test_logarithmic_scale_below_reference(self):
        s = logarithmic_scale(1.0, math.e)
        assert math.isclose(s, -1.0, rel_tol=1e-12)

    def test_ai1_roundtrip(self):
        """AI1 original test."""
        L0 = 2.0
        L = 10.0
        s = logarithmic_scale(L, L0)
        recovered = length_from_scale(s, L0)
        assert math.isclose(recovered, L)

    def test_logarithmic_scale_negative_length_raises(self):
        with pytest.raises(ValueError, match="positive"):
            logarithmic_scale(-1.0, 1.0)

    def test_logarithmic_scale_zero_length_raises(self):
        with pytest.raises(ValueError, match="positive"):
            logarithmic_scale(0.0, 1.0)

    def test_logarithmic_scale_zero_reference_raises(self):
        with pytest.raises(ValueError, match="positive"):
            logarithmic_scale(1.0, 0.0)

    def test_length_from_scale_zero_reference_raises(self):
        with pytest.raises(ValueError, match="positive"):
            length_from_scale(1.0, 0.0)

    def test_length_from_scale_zero_s(self):
        assert length_from_scale(0.0, 3.0) == 3.0

    def test_length_from_scale_positive_s(self):
        result = length_from_scale(1.0, 1.0)
        assert math.isclose(result, math.e, rel_tol=1e-12)

    def test_multiple_roundtrips(self):
        for L in [0.1, 1.0, 5.0, 100.0]:
            for L_ref in [1.0, 2.0, 10.0]:
                s = logarithmic_scale(L, L_ref)
                assert math.isclose(length_from_scale(s, L_ref), L, rel_tol=1e-10)
