import math
import numpy as np

from cnrs.science.branch import CnrsBranch, reconstruct_phase, winding_number
from cnrs.science.observation import observe, observation_table
from cnrs.science.scale_law import CnrsScaleLaw, fit_egf_scale_law
from cnrs.science.three_workflows import compare_interference, compare_complex_scale_law, compare_branch_winding


def test_branch_log_reconstructs_value():
    z = CnrsBranch.from_complex(1+1j, k=3)
    assert abs(z.exp_log() - (1+1j)) < 1e-12
    assert abs(z.arg() - (math.pi/4 + 6*math.pi)) < 1e-12


def test_observation_maps():
    z = np.array([1+0j, 1j, -1+0j])
    table = observation_table(z)
    assert set(table) == {"real", "imag", "abs", "abs2", "phase", "phase_current"}
    assert np.allclose(observe(z, "abs2"), [1, 1, 1])


def test_scale_law_derivative_complex_exponential():
    lam = -0.2 + 1.7j
    law = CnrsScaleLaw.exponential(lam, scale=1.2, terms=36)
    dlaw = law.derivative()
    rho = np.linspace(-1, 1, 21)
    assert np.linalg.norm(dlaw(rho) - lam * law(rho)) / np.linalg.norm(lam * law(rho)) < 1e-10


def test_fit_egf_scale_law():
    rho = np.linspace(-1, 1, 50)
    y = 2.0 * np.exp(0.3 * rho)
    fit = fit_egf_scale_law(rho, y, degree=8)
    assert np.linalg.norm(fit(rho).real - y) / np.linalg.norm(y) < 1e-6


def test_three_workflow_interference():
    res = compare_interference(n=200, L=12)
    assert res.metrics["A_phase_variation"] < 1e-12
    assert res.metrics["B_intensity_max"] > 3.9
    assert res.metrics["C_intensity_rel_L2_error"] < 1e-3


def test_three_workflow_complex_scale_law():
    res = compare_complex_scale_law(terms=55, L=12)
    assert res.metrics["A_mod2_difference_when_omega_changed"] < 1e-12
    assert abs(res.metrics["B_phase_derivative_mean"] - 4.25) < 1e-10
    assert res.metrics["C_CNRS_H_state_rel_L2_error"] < 1e-9


def test_three_workflow_branch_winding():
    res = compare_branch_winding(n=300, L=12)
    assert res.metrics["A_modulus_squared_variation"] < 1e-12
    assert res.metrics["B_branch_max"] > 0
    assert res.metrics["C_phase_max_abs_error"] < 0.01
