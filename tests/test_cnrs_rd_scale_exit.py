import math

from cnrs.cnrs_rd_scale_exit import (
    ExponentialDiffusionLaw,
    RDLinearKinetics,
    exponential_gm_scale_exit,
    gm_default_kinetics,
    scan_scale_exit,
    turing_diagnostic,
    turing_thresholds,
)


def test_rd_linear_kinetics_stability():
    kinetics = RDLinearKinetics(f_u=-1.0, f_v=-1.0, g_u=2.0, g_v=-3.0)
    assert kinetics.trace == -4.0
    assert kinetics.determinant == 5.0
    assert kinetics.homogeneous_stable()


def test_default_gm_thresholds_match_expected_window():
    kinetics = gm_default_kinetics()
    thresholds = turing_thresholds(kinetics)
    assert thresholds.stable_kinetics
    assert thresholds.d_low is not None
    assert thresholds.d_high is not None
    assert math.isclose(thresholds.d_low, 0.2154, rel_tol=2e-3)
    assert math.isclose(thresholds.d_high, 41.785, rel_tol=2e-3)


def test_default_gm_active_at_s_zero():
    kinetics = gm_default_kinetics()
    point = turing_diagnostic(kinetics, d_u=0.01, d_v=1.0, s=0.0)
    assert point.ratio == 100.0
    assert point.active
    assert point.q_star is not None
    assert point.margin > 0.0


def test_default_gm_inactive_after_scale_exit():
    kinetics = gm_default_kinetics()
    du = ExponentialDiffusionLaw(0.01, -1.0 / 3.0)
    dv = ExponentialDiffusionLaw(1.0, -2.0)
    point = turing_diagnostic(kinetics, du(2.0), dv(2.0), s=2.0)
    assert point.ratio < 41.785
    assert not point.active


def test_default_gm_scale_exit_detected_near_paper18_value():
    kinetics = gm_default_kinetics()
    result = exponential_gm_scale_exit(
        kinetics,
        d_u0=0.01,
        d_v0=1.0,
        lambda_u=-1.0 / 3.0,
        lambda_v=-2.0,
        s_min=0.0,
        s_max=2.0,
        n=101,
    )
    exit_s = result.first_exit()
    assert exit_s is not None
    assert math.isclose(exit_s, 0.523, rel_tol=2e-2)
    assert len(result.transitions) == 1
    assert result.transitions[0].kind == "exit"


def test_scan_detects_entry_when_ratio_increases_with_scale():
    kinetics = gm_default_kinetics()
    du = ExponentialDiffusionLaw(1.0, 0.0)
    dv = ExponentialDiffusionLaw(10.0, 1.0)
    result = scan_scale_exit(kinetics, du, dv, s_min=0.0, s_max=3.0, n=151)
    entry_s = result.first_entry()
    assert entry_s is not None
    assert result.transitions[0].kind == "entry"


# ---------------------------------------------------------------------------
# ScaleLadder and ScaleLaw bridge tests
# ---------------------------------------------------------------------------

import math
from cnrs.cnrs_rd_scale_exit import (
    ladder_diffusion_law,
    scalelaw_diffusion_law,
    scan_scale_exit_ladder,
)
from cnrs.cnrs_multiscale import ScaleLadder
from cnrs.cnrs_bio import da_profile, dh_profile
from cnrs.cnrs_scale import ScaleLaw


def make_exponential_ladder(lam_real, d0, s_total=2.0, n_rungs=4, terms=40):
    """Helper: ScaleLadder matching D(s) = d0 * exp(lam_real * s)."""
    import cmath
    lam = complex(lam_real, 0.0)
    return ScaleLadder.uniform(lam, y0=complex(d0, 0.0),
                               s_total=s_total, n_rungs=n_rungs, terms=terms)


class TestLadderDiffusionLaw:

    def test_modulus_positive(self):
        ladder = make_exponential_ladder(-1.0/3.0, 0.01)
        fn = ladder_diffusion_law(ladder)
        for s in [0.0, 0.5, 1.0, 1.5]:
            assert fn(s) > 0

    def test_modulus_matches_exponential_exactly(self):
        """For a real exponential ladder, |Ψ(s)| = D0 * exp(λs) exactly."""
        lam = -1.0/3.0
        d0 = 0.01
        ladder = make_exponential_ladder(lam, d0, s_total=2.0, n_rungs=1, terms=40)
        fn = ladder_diffusion_law(ladder, observable='modulus')
        for s in [0.0, 0.3, 0.7, 1.2, 1.8]:
            expected = d0 * math.exp(lam * s)
            assert math.isclose(fn(s), expected, rel_tol=1e-8), (
                f"s={s}: expected {expected:.8f}, got {fn(s):.8f}"
            )

    def test_modulus_sq_matches_exponential(self):
        lam = -2.0
        d0 = 1.0
        ladder = make_exponential_ladder(lam, d0, s_total=2.0, n_rungs=1, terms=40)
        fn_sq = ladder_diffusion_law(ladder, observable='modulus_sq')
        fn_mod = ladder_diffusion_law(ladder, observable='modulus')
        for s in [0.1, 0.5, 1.0]:
            assert math.isclose(fn_sq(s), fn_mod(s)**2, rel_tol=1e-10)

    def test_real_part_positive_field(self):
        # Pure real positive field: Re(Ψ) = D0 * exp(λs) > 0
        ladder = make_exponential_ladder(-0.5, 1.0, s_total=1.0, n_rungs=1, terms=40)
        fn = ladder_diffusion_law(ladder, observable='real_part')
        assert fn(0.0) > 0
        assert fn(0.5) > 0

    def test_invalid_observable_raises(self):
        ladder = make_exponential_ladder(-1.0, 1.0)
        import pytest
        with pytest.raises(ValueError, match="observable"):
            ladder_diffusion_law(ladder, observable='phase')

    def test_multi_rung_continuity(self):
        """Multi-rung ladder gives continuous diffusion law."""
        ladder = make_exponential_ladder(-1.0/3.0, 0.01, s_total=2.0, n_rungs=8)
        fn = ladder_diffusion_law(ladder)
        vals = [fn(s) for s in [i * 0.25 for i in range(9)]]
        # All positive
        assert all(v > 0 for v in vals)
        # Monotonically decreasing (decaying field)
        for i in range(len(vals)-1):
            assert vals[i] > vals[i+1]


class TestScalelawDiffusionLaw:

    def test_da_profile_matches_exponential(self):
        """ScaleLaw da_profile gives same values as ExponentialDiffusionLaw."""
        from cnrs.cnrs_rd_scale_exit import ExponentialDiffusionLaw
        da = da_profile()
        fn = scalelaw_diffusion_law(da)
        exp_law = ExponentialDiffusionLaw(0.01, -1.0/3.0)
        for s in [0.0, 0.2, 0.5, 1.0]:
            assert math.isclose(fn(s), exp_law(s), rel_tol=1e-6), (
                f"s={s}: ScaleLaw={fn(s):.8f}, Exponential={exp_law(s):.8f}"
            )

    def test_dh_profile_matches_exponential(self):
        from cnrs.cnrs_rd_scale_exit import ExponentialDiffusionLaw
        dh = dh_profile()
        fn = scalelaw_diffusion_law(dh)
        exp_law = ExponentialDiffusionLaw(1.0, -2.0)
        for s in [0.0, 0.2, 0.5, 1.0]:
            assert math.isclose(fn(s), exp_law(s), rel_tol=1e-6)

    def test_positive_output(self):
        da = da_profile()
        fn = scalelaw_diffusion_law(da)
        for s in [0.0, 0.5, 1.0, 1.5]:
            assert fn(s) > 0

    def test_scan_via_scalelaws_matches_exponential_scan(self):
        """
        scan_scale_exit via ScaleLaw bridges must give the same s_exit as
        scan_scale_exit via ExponentialDiffusionLaw.
        """
        from cnrs.cnrs_rd_scale_exit import ExponentialDiffusionLaw, scan_scale_exit
        kinetics = gm_default_kinetics()

        # Exponential path (AI1 original)
        result_exp = scan_scale_exit(
            kinetics,
            ExponentialDiffusionLaw(0.01, -1.0/3.0),
            ExponentialDiffusionLaw(1.0, -2.0),
            s_min=0.0, s_max=2.0, n=101,
        )

        # ScaleLaw path (bridge)
        result_sl = scan_scale_exit(
            kinetics,
            scalelaw_diffusion_law(da_profile()),
            scalelaw_diffusion_law(dh_profile()),
            s_min=0.0, s_max=2.0, n=101,
        )

        assert result_exp.first_exit() is not None
        assert result_sl.first_exit() is not None
        assert math.isclose(
            result_exp.first_exit(), result_sl.first_exit(), rel_tol=1e-4
        ), (f"Exponential: {result_exp.first_exit():.6f}, "
            f"ScaleLaw: {result_sl.first_exit():.6f}")


class TestScanScaleExitLadder:

    def test_ladder_scan_returns_result(self):
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01, s_total=2.0)
        ladder_v = make_exponential_ladder(-2.0, 1.0, s_total=2.0)
        result = scan_scale_exit_ladder(kinetics, ladder_u, ladder_v, n=51)
        assert result is not None
        assert len(result.points) == 51

    def test_ladder_scan_matches_exponential_exit(self):
        """
        ScaleLadder scan must reproduce the Paper 18 s_exit value.

        For exponential diffusion laws, the ladder (exact EGF) and the
        scalar approximation agree to high precision.  This confirms that
        the CNRS-H path gives the same physical result.
        """
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01,
                                           s_total=2.0, n_rungs=1, terms=40)
        ladder_v = make_exponential_ladder(-2.0, 1.0,
                                           s_total=2.0, n_rungs=1, terms=40)
        result = scan_scale_exit_ladder(kinetics, ladder_u, ladder_v, n=201)
        exit_s = result.first_exit()
        assert exit_s is not None
        assert math.isclose(exit_s, 0.5236, rel_tol=2e-2), (
            f"Expected s_exit ≈ 0.5236, got {exit_s:.6f}"
        )

    def test_ladder_scan_paper18_value(self):
        """Tight tolerance test: ladder scan recovers Paper 18 value."""
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01,
                                           s_total=2.0, n_rungs=1, terms=40)
        ladder_v = make_exponential_ladder(-2.0, 1.0,
                                           s_total=2.0, n_rungs=1, terms=40)
        result = scan_scale_exit_ladder(kinetics, ladder_u, ladder_v, n=201)
        assert math.isclose(result.first_exit(), 0.523, rel_tol=2e-2)

    def test_ladder_scan_active_at_start(self):
        """Field starts in Turing-active regime at s=0."""
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01, s_total=2.0)
        ladder_v = make_exponential_ladder(-2.0, 1.0, s_total=2.0)
        result = scan_scale_exit_ladder(kinetics, ladder_u, ladder_v)
        assert result.points[0].active is True

    def test_ladder_scan_inactive_at_end(self):
        """Field exits Turing-active regime by s=2."""
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01, s_total=2.0)
        ladder_v = make_exponential_ladder(-2.0, 1.0, s_total=2.0)
        result = scan_scale_exit_ladder(kinetics, ladder_u, ladder_v)
        assert result.points[-1].active is False

    def test_ladder_scan_one_transition(self):
        """Exactly one exit transition for GM default parameters."""
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01,
                                           s_total=2.0, n_rungs=1, terms=40)
        ladder_v = make_exponential_ladder(-2.0, 1.0,
                                           s_total=2.0, n_rungs=1, terms=40)
        result = scan_scale_exit_ladder(kinetics, ladder_u, ladder_v, n=101)
        assert len(result.transitions) == 1
        assert result.transitions[0].kind == "exit"

    def test_ladder_scan_s_range_defaults(self):
        """Default s range comes from ladder edges."""
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01, s_total=2.0)
        ladder_v = make_exponential_ladder(-2.0, 1.0, s_total=1.5)
        # Overlapping range should be [0, 1.5]
        result = scan_scale_exit_ladder(kinetics, ladder_u, ladder_v, n=51)
        assert math.isclose(result.points[0].s, 0.0, abs_tol=1e-10)
        assert math.isclose(result.points[-1].s, 1.5, rel_tol=1e-8)

    def test_ladder_scan_custom_s_range(self):
        """Custom s_min, s_max respected."""
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01, s_total=2.0)
        ladder_v = make_exponential_ladder(-2.0, 1.0, s_total=2.0)
        result = scan_scale_exit_ladder(
            kinetics, ladder_u, ladder_v,
            s_min=0.2, s_max=1.0, n=21
        )
        assert math.isclose(result.points[0].s, 0.2, rel_tol=1e-8)
        assert math.isclose(result.points[-1].s, 1.0, rel_tol=1e-8)

    def test_non_overlapping_ladders_raise(self):
        """Non-overlapping ladder ranges raise ValueError."""
        import pytest
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01, s_total=1.0)
        # Force non-overlapping by using custom s_min > ladder_u range
        with pytest.raises(ValueError, match="overlapping"):
            scan_scale_exit_ladder(
                kinetics, ladder_u, ladder_u,
                s_min=1.5, s_max=2.0
            )

    def test_multi_rung_ladder_scan_consistent(self):
        """Multi-rung ladder gives consistent result with single-rung."""
        kinetics = gm_default_kinetics()
        ladder_u_1 = make_exponential_ladder(-1.0/3.0, 0.01,
                                              s_total=2.0, n_rungs=1, terms=40)
        ladder_v_1 = make_exponential_ladder(-2.0, 1.0,
                                              s_total=2.0, n_rungs=1, terms=40)
        ladder_u_8 = make_exponential_ladder(-1.0/3.0, 0.01,
                                              s_total=2.0, n_rungs=8, terms=40)
        ladder_v_8 = make_exponential_ladder(-2.0, 1.0,
                                              s_total=2.0, n_rungs=8, terms=40)
        result_1 = scan_scale_exit_ladder(kinetics, ladder_u_1, ladder_v_1, n=201)
        result_8 = scan_scale_exit_ladder(kinetics, ladder_u_8, ladder_v_8, n=201)
        assert math.isclose(
            result_1.first_exit(), result_8.first_exit(), rel_tol=1e-4
        )

    def test_modulus_sq_observable(self):
        """modulus_sq observable gives positive diffusion values."""
        kinetics = gm_default_kinetics()
        ladder_u = make_exponential_ladder(-1.0/3.0, 0.01, s_total=2.0)
        ladder_v = make_exponential_ladder(-2.0, 1.0, s_total=2.0)
        result = scan_scale_exit_ladder(
            kinetics, ladder_u, ladder_v,
            observable='modulus_sq', n=51
        )
        # All D values positive
        assert all(p.d_u > 0 and p.d_v > 0 for p in result.points)
