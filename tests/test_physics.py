"""
test_physics.py
===============
Pytest module verifying standard QM and GR exact solutions via CNRS-H
EGF streams. Checks that CNRS-H correctly represents known closed-form
solutions and that digit-shift differentiation recovers known derivatives.

All results compared against analytic formulae; not new physical claims.

Session: 43, 2026-06-06
Author:  Donald G. Palmer
"""

import cmath, math
import numpy as np
import pytest


from cnrs.cnrs_h import CnrsH
from cnrs.cnrs_physics_check import (
    # QM helpers
    qho_psi0_coeffs, qho_psi0_exact, qho_psi0_deriv_exact,
    qho_psi1_coeffs, qho_psi1_exact, qho_psi1_deriv_exact,
    qho_time_evolution_coeffs,
    hydrogen_1s_radial_coeffs, hydrogen_1s_radial_exact,
    hydrogen_1s_radial_deriv_exact,
    hydrogen_2s_radial_coeffs, hydrogen_2s_radial_exact,
    hydrogen_2s_radial_deriv_exact,
    # GR helpers
    schwarzschild_gtt_coeffs, schwarzschild_gtt_exact,
    schwarzschild_gtt_deriv_exact,
    schwarzschild_grr_inv_coeffs, schwarzschild_grr_inv_exact,
    schwarzschild_grr_inv_deriv_exact,
    veff_coeffs, veff_exact, veff_deriv_exact,
)

TOL = 1e-8
TERMS = 30


def rel_err(a, b):
    return abs(a - b) / (abs(b) + 1e-300)


# ============================================================================
# QM — Quantum Harmonic Oscillator ground state ψ_0
# ============================================================================

@pytest.mark.parametrize("x0", [0.0, 0.5, 1.0, -0.7, 1.5])
def test_qho_psi0_value_at_x0(x0):
    """ψ_0(x0) from CNRS-H stream matches analytic formula."""
    c = qho_psi0_coeffs(x0, TERMS)
    h = CnrsH.from_list(c)
    assert rel_err(h.evaluate(0.0), qho_psi0_exact(x0)) < TOL


@pytest.mark.parametrize("x0", [0.5, 1.0, -0.7, 1.5])
def test_qho_psi0_deriv_at_x0(x0):
    """ψ_0'(x0) from CNRS-H digit-shift matches analytic -x*ψ_0(x)."""
    c = qho_psi0_coeffs(x0, TERMS)
    h = CnrsH.from_list(c)
    dval = h.differentiate().evaluate(0.0)
    dexact = qho_psi0_deriv_exact(x0)
    if abs(dexact) > 1e-10:
        assert rel_err(dval, dexact) < TOL


def test_qho_psi0_stream_at_offset():
    """ψ_0 stream evaluated at small ρ≠0 matches analytic (50 terms, |δ|≤0.1)."""
    x0 = 0.5
    c = qho_psi0_coeffs(x0, 50)
    h = CnrsH.from_list(c)
    for delta in [-0.1, -0.05, 0.05, 0.1]:
        val = h.evaluate(complex(delta)).real
        exact = qho_psi0_exact(x0 + delta).real
        assert rel_err(val, exact) < 2e-4  # Gaussian coefficients limit convergence


# ============================================================================
# QM — QHO first excited state ψ_1
# ============================================================================

@pytest.mark.parametrize("x0", [0.3, 0.7, 1.2, -0.5])
def test_qho_psi1_value(x0):
    """ψ_1(x0) from CNRS-H stream matches analytic formula."""
    c = qho_psi1_coeffs(x0, TERMS)
    h = CnrsH.from_list(c)
    assert rel_err(h.evaluate(0.0), qho_psi1_exact(x0)) < TOL


@pytest.mark.parametrize("x0", [0.3, 0.7, 1.2, -0.5])
def test_qho_psi1_deriv(x0):
    """ψ_1'(x0) from CNRS-H digit-shift matches analytic (1-x²)*ψ_0 formula."""
    c = qho_psi1_coeffs(x0, TERMS)
    h = CnrsH.from_list(c)
    dval = h.differentiate().evaluate(0.0)
    dexact = qho_psi1_deriv_exact(x0)
    if abs(dexact) > 1e-10:
        assert rel_err(dval, dexact) < TOL


# ============================================================================
# QM — Time evolution phase rate encodes energy eigenvalue
# ============================================================================

@pytest.mark.parametrize("n,En", [(0, 0.5), (1, 1.5), (2, 2.5), (3, 3.5)])
def test_qho_energy_from_phase_rate(n, En):
    """
    Im(ψ'(t)/ψ(t))|_{t=0} = -E_n exactly for QHO time evolution.

    This is the key result: the energy eigenvalue is encoded as the
    instantaneous phase rate of the CNRS-H stream.
    """
    psi_x = complex(1.0)
    c = qho_time_evolution_coeffs(psi_x, En, TERMS)
    h = CnrsH.from_list(c)
    h_val = h.evaluate(0.0)
    dh_val = h.differentiate().evaluate(0.0)
    phase_rate = (dh_val / h_val).imag
    assert rel_err(phase_rate, -En) < TOL


# ============================================================================
# QM — Hydrogen atom radial wavefunctions
# ============================================================================

@pytest.mark.parametrize("r0", [0.5, 1.0, 2.0, 3.0])
def test_hydrogen_1s_value(r0):
    """R_{10}(r) = 2*exp(-r) from CNRS-H stream."""
    c = hydrogen_1s_radial_coeffs(r0, TERMS)
    h = CnrsH.from_list(c)
    assert rel_err(h.evaluate(0.0).real, hydrogen_1s_radial_exact(r0)) < TOL


@pytest.mark.parametrize("r0", [0.5, 1.0, 2.0, 3.0])
def test_hydrogen_1s_deriv(r0):
    """R_{10}'(r) = -2*exp(-r) from CNRS-H digit-shift."""
    c = hydrogen_1s_radial_coeffs(r0, TERMS)
    h = CnrsH.from_list(c)
    dval = h.differentiate().evaluate(0.0).real
    dexact = hydrogen_1s_radial_deriv_exact(r0)
    assert rel_err(dval, dexact) < TOL


def test_hydrogen_1s_stream_at_offset():
    """R_{10} stream evaluated away from r0 matches analytic (exponential: exact)."""
    r0 = 1.0
    c = hydrogen_1s_radial_coeffs(r0, TERMS)
    h = CnrsH.from_list(c)
    for delta in [-0.3, -0.1, 0.1, 0.3, 0.5]:
        val = h.evaluate(complex(delta)).real
        exact = hydrogen_1s_radial_exact(r0 + delta)
        assert rel_err(val, exact) < TOL


@pytest.mark.parametrize("r0", [0.5, 1.0, 2.5, 4.0])
def test_hydrogen_2s_value(r0):
    """R_{20}(r) = (1/2√2)(2-r)exp(-r/2) from CNRS-H stream."""
    c = hydrogen_2s_radial_coeffs(r0, TERMS)
    h = CnrsH.from_list(c)
    exact = hydrogen_2s_radial_exact(r0)
    if abs(exact) > 1e-10:
        assert rel_err(h.evaluate(0.0).real, exact) < TOL


@pytest.mark.parametrize("r0", [0.5, 1.0, 2.5, 4.0])
def test_hydrogen_2s_deriv(r0):
    """R_{20}'(r) from CNRS-H digit-shift matches analytic."""
    c = hydrogen_2s_radial_coeffs(r0, TERMS)
    h = CnrsH.from_list(c)
    dval = h.differentiate().evaluate(0.0).real
    dexact = hydrogen_2s_radial_deriv_exact(r0)
    if abs(dexact) > 1e-10:
        assert rel_err(dval, dexact) < TOL


# ============================================================================
# GR — Schwarzschild metric g_tt = 1 - 2M/r
# ============================================================================

@pytest.mark.parametrize("r0,M", [(5.0,1.0),(10.0,1.0),(20.0,1.0),(100.0,1.0)])
def test_schwarzschild_gtt_value(r0, M):
    """f(r0) = 1-2M/r from CNRS-H stream."""
    c = schwarzschild_gtt_coeffs(r0, M, TERMS)
    h = CnrsH.from_list(c)
    assert rel_err(h.evaluate(0.0).real, schwarzschild_gtt_exact(r0, M)) < TOL


@pytest.mark.parametrize("r0,M", [(5.0,1.0),(10.0,1.0),(20.0,1.0),(100.0,1.0)])
def test_schwarzschild_gtt_deriv(r0, M):
    """f'(r0) = 2M/r² from CNRS-H digit-shift."""
    c = schwarzschild_gtt_coeffs(r0, M, TERMS)
    h = CnrsH.from_list(c)
    dval = h.differentiate().evaluate(0.0).real
    dexact = schwarzschild_gtt_deriv_exact(r0, M)
    assert rel_err(dval, dexact) < TOL


def test_schwarzschild_gtt_stream_at_offset():
    """g_tt stream evaluated away from r0 (rational function: fast convergence)."""
    r0, M = 10.0, 1.0
    c = schwarzschild_gtt_coeffs(r0, M, TERMS)
    h = CnrsH.from_list(c)
    for delta in [-1.0, -0.5, 0.5, 1.0, 2.0]:
        val = h.evaluate(complex(delta)).real
        exact = schwarzschild_gtt_exact(r0 + delta, M)
        assert rel_err(val, exact) < TOL


def test_weak_field_egf_coefficients():
    """
    Weak-field EGF: c_0 = 1-2M/r (Newtonian potential) and c_1 = 2M/r².
    Tests that the EGF stream correctly encodes the Newtonian gravity limit.
    """
    r0, M = 1000.0, 1.0
    c = schwarzschild_gtt_coeffs(r0, M, 5)
    assert abs(c[0].real - (1 - 2*M/r0)) < 1e-12
    assert abs(c[1].real - 2*M/r0**2) < 1e-15


# ============================================================================
# GR — Schwarzschild g_rr^{-1} = 1/(1-2M/r)
# ============================================================================

@pytest.mark.parametrize("r0,M", [(5.0,1.0),(10.0,1.0),(20.0,1.0),(50.0,1.0)])
def test_schwarzschild_grr_inv_value(r0, M):
    """h(r0) = 1/(1-2M/r) from CNRS-H Leibniz recurrence."""
    c = schwarzschild_grr_inv_coeffs(r0, M, TERMS)
    h = CnrsH.from_list(c)
    assert rel_err(h.evaluate(0.0).real, schwarzschild_grr_inv_exact(r0, M)) < TOL


@pytest.mark.parametrize("r0,M", [(5.0,1.0),(10.0,1.0),(20.0,1.0),(50.0,1.0)])
def test_schwarzschild_grr_inv_deriv(r0, M):
    """h'(r0) = -(2M/r²)h² from CNRS-H digit-shift (sign verified)."""
    c = schwarzschild_grr_inv_coeffs(r0, M, TERMS)
    h = CnrsH.from_list(c)
    dval = h.differentiate().evaluate(0.0).real
    dexact = schwarzschild_grr_inv_deriv_exact(r0, M)
    assert rel_err(dval, dexact) < TOL


# ============================================================================
# GR — Effective potential V_eff(r) = (1-2M/r)(1+L²/r²)
# ============================================================================

@pytest.mark.parametrize("r0,M,L", [
    (6.0,1.0,4.0),(10.0,1.0,4.0),(20.0,1.0,4.0),(50.0,1.0,4.0)
])
def test_veff_value(r0, M, L):
    """V_eff(r0) from CNRS-H Cauchy product stream."""
    c = veff_coeffs(r0, M, L, TERMS)
    h = CnrsH.from_list(c)
    assert rel_err(h.evaluate(0.0).real, veff_exact(r0, M, L)) < TOL


@pytest.mark.parametrize("r0,M,L", [
    (6.0,1.0,4.0),(10.0,1.0,4.0),(20.0,1.0,4.0),(50.0,1.0,4.0)
])
def test_veff_deriv(r0, M, L):
    """V_eff'(r0) from CNRS-H digit-shift."""
    c = veff_coeffs(r0, M, L, TERMS)
    h = CnrsH.from_list(c)
    dval = h.differentiate().evaluate(0.0).real
    dexact = veff_deriv_exact(r0, M, L)
    assert rel_err(dval, dexact) < TOL


def test_circular_orbit_veff_deriv_zero():
    """
    V_eff'(r_circ) = 0 exactly at the stable circular orbit r_circ = 12
    (M=1, L=4). CNRS-H digit-shift recovers this to machine precision.
    """
    M, L, r_circ = 1.0, 4.0, 12.0
    c = veff_coeffs(r_circ, M, L, TERMS)
    h = CnrsH.from_list(c)
    deriv = h.differentiate().evaluate(0.0).real
    assert abs(deriv) < 1e-10
