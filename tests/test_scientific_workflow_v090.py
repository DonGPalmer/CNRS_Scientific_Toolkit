import numpy as np

from cnrs.cnrs_h_native import CnrsHNative, compose_native
from cnrs.science.workflow import (
    sample_state,
    preservation_metrics,
    build_preservation_report,
    compare_state_pair,
)


class SimpleState:
    def __init__(self, f):
        self.f = f
    def evaluate(self, x):
        return self.f(x)


def test_sample_state_works_for_cnrs_h_native():
    # f(s)=1+2s in EGF coefficients [1,2]
    h = CnrsHNative.from_gaussian_list([1, 2])
    vals = sample_state(h, [0, 1, 2])
    assert vals == (1+0j, 3+0j, 5+0j)


def test_preservation_metrics_detect_phase_lost_by_modulus():
    theta = np.linspace(0, 2*np.pi, 100)
    z = np.exp(1j * theta)
    metrics = preservation_metrics(z, coord=theta)
    assert metrics["phase_span"] > 6.0
    assert metrics["modulus_variation"] < 1e-12
    assert metrics["intensity_variation"] < 1e-12
    assert metrics["real_projection_rel_error"] > 0.5


def test_build_preservation_report_from_callable_state():
    state = SimpleState(lambda s: np.exp(1j*s))
    pts = np.linspace(0, 1, 12)
    report = build_preservation_report(state, pts, name="phasor")
    summary = report.summary()
    assert summary["name"] == "phasor"
    assert summary["n_points"] == 12
    assert "phase_span" in summary["metrics"]
    assert "phase" in report.observations


def test_compare_state_pair_observation_maps():
    a = SimpleState(lambda s: np.exp(1j*s))
    b = SimpleState(lambda s: np.exp(2j*s))
    pts = np.linspace(0, 1, 20)
    out = compare_state_pair(a, b, pts)
    assert "phase" in out
    assert "abs2" in out
    assert out["phase"] > 0


def test_cnrs_h_native_composition_feeds_workflow_report():
    f = CnrsHNative.from_gaussian_list([1] * 8)  # exp
    g = CnrsHNative.from_gaussian_list([0, 2])   # 2s
    h = compose_native(f, g, 6)
    pts = [0, 0.1, 0.2]
    report = build_preservation_report(h, pts, name="native_exp_2s")
    assert report.metrics["modulus_variation"] > 0
    assert report.summary()["name"] == "native_exp_2s"
