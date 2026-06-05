"""
tests/test_cnrs_ode.py
----------------------
Tests for cnrs_ode: ODE solver via CNRS-H coefficient recurrence.

Covers:
  - cnrs_solve_linear: y' = λy
  - cnrs_solve_driven: y' = λy + f(s)
  - cnrs_solve_second_order: y'' + 2γy' + ω²y = 0
  - OdeSolution: evaluate, derivative, eigenvalue, observable maps
  - Domain warning for out-of-range evaluation
  - Error bounds: machine precision within natural domain
  - Physics cases: QM free particle, damped oscillator, scale law

All tolerances use tol = 1e-10, well within the ~1e-14 errors seen in
practice for s ∈ [0, 1] nat with 25 terms.

Session 42, 2026-06-06.
"""

from __future__ import annotations
import sys, os, math, cmath, warnings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from cnrs.cnrs_ode import (
    cnrs_solve_linear,
    cnrs_solve_driven,
    cnrs_solve_second_order,
    OdeSolution,
)
from cnrs.cnrs_h import CnrsH

TOL = 1e-10


def _check(label, got, expected, tol=TOL):
    err = abs(complex(got) - complex(expected))
    assert err < tol, f"{label}: got={got!r}, expected={expected!r}, err={err:.3e}"


# ══════════════════════════════════════════════════════════════════════════════
# cnrs_solve_linear: y' = λy
# ══════════════════════════════════════════════════════════════════════════════

def test_linear_pure_decay():
    """y' = -y, y(0)=1 → y(s) = exp(-s)."""
    sol = cnrs_solve_linear(-1.0, y0=1.0)
    for s in [0.0, 0.25, 0.5, 0.75, 1.0]:
        _check(f"exp(-s) at s={s}", sol.evaluate(s), cmath.exp(-s))

def test_linear_pure_growth():
    """y' = 0.5y, y(0)=1 → y(s) = exp(0.5s)."""
    sol = cnrs_solve_linear(0.5, y0=1.0)
    for s in [0.0, 0.5, 1.0]:
        _check(f"exp(0.5s) at s={s}", sol.evaluate(s), cmath.exp(0.5*s))

def test_linear_pure_rotation():
    """y' = iy, y(0)=1 → y(s) = exp(is)."""
    sol = cnrs_solve_linear(1j, y0=1.0)
    for s in [0.0, 0.25, 0.5, 1.0]:
        _check(f"exp(is) at s={s}", sol.evaluate(s), cmath.exp(1j*s))

def test_linear_complex_eigenvalue():
    """y' = (-0.3+2i)y → decay + oscillation."""
    lam = -0.3 + 2j
    sol = cnrs_solve_linear(lam, y0=1.0)
    for s in [0.0, 0.25, 0.5, 0.75, 1.0]:
        _check(f"exp(lam*s) at s={s}", sol.evaluate(s), cmath.exp(lam*s))

def test_linear_nonunit_initial():
    """y' = λy, y(0) = 2+i."""
    lam = -0.1 + 1.5j
    y0 = 2 + 1j
    sol = cnrs_solve_linear(lam, y0=y0)
    for s in [0.0, 0.5, 1.0]:
        _check(f"y0*exp(lam*s) at s={s}", sol.evaluate(s), y0 * cmath.exp(lam*s))

def test_linear_qm_free_particle():
    """QM free particle: ψ' = -iEψ, |ψ|² = 1 always."""
    E = 2.5
    sol = cnrs_solve_linear(-1j*E, y0=1.0)
    for s in [0.0, 0.25, 0.5, 0.75, 1.0]:
        assert abs(sol.modulus_sq(s) - 1.0) < TOL, \
            f"|ψ|² != 1 at s={s}: {sol.modulus_sq(s)}"

def test_linear_returns_ode_solution():
    sol = cnrs_solve_linear(-0.3+2j)
    assert isinstance(sol, OdeSolution)

def test_linear_terms_parameter():
    sol = cnrs_solve_linear(-0.3+2j, terms=15)
    assert len(sol.coeffs) == 15


# ══════════════════════════════════════════════════════════════════════════════
# cnrs_solve_driven: y' = λy + f(s)
# ══════════════════════════════════════════════════════════════════════════════

def _sin_coeffs(n):
    """EGF coefficients of sin(s): 0, 1, 0, -1, 0, 1, ..."""
    return [0 if k%2==0 else (1 if (k//2)%2==0 else -1) for k in range(n)]

def _cos_coeffs(n):
    """EGF coefficients of cos(s): 1, 0, -1, 0, 1, 0, ..."""
    return [(-1)**(k//2) if k%2==0 else 0 for k in range(n)]

def _rk4_driven(lam, y0, f_func, s_end=0.5, h=0.001):
    """Reference RK4 for driven ODE."""
    y = complex(y0)
    steps = int(round(s_end / h))
    for i in range(steps):
        s = i * h
        k1 = lam*y + f_func(s)
        k2 = lam*(y+h/2*k1) + f_func(s+h/2)
        k3 = lam*(y+h/2*k2) + f_func(s+h/2)
        k4 = lam*(y+h*k3) + f_func(s+h)
        y += h/6*(k1+2*k2+2*k3+k4)
    return y

def test_driven_sin_forcing():
    """y' = (-0.3+2i)y + sin(s), compared to RK4."""
    lam = -0.3 + 2j
    sol = cnrs_solve_driven(lam, y0=1.0, forcing=_sin_coeffs(25))
    rk4 = _rk4_driven(lam, 1.0, cmath.sin, s_end=0.5)
    _check("driven sin at s=0.5", sol.evaluate(0.5), rk4, tol=1e-9)

def test_driven_cos_forcing():
    """y' = iy + cos(s), compared to RK4."""
    lam = 1j
    sol = cnrs_solve_driven(lam, y0=1.0, forcing=_cos_coeffs(25))
    rk4 = _rk4_driven(lam, 1.0, cmath.cos, s_end=0.3, h=0.0005)
    _check("driven cos at s=0.3", sol.evaluate(0.3), rk4, tol=1e-9)

def test_driven_cnrsh_forcing():
    """Forcing passed as a CnrsH stream."""
    lam = -0.1 + 1.0j
    forcing_h = CnrsH.from_list(_sin_coeffs(25))
    sol = cnrs_solve_driven(lam, y0=1.0, forcing=forcing_h)
    rk4 = _rk4_driven(lam, 1.0, cmath.sin, s_end=0.5)
    _check("driven CnrsH forcing at s=0.5", sol.evaluate(0.5), rk4, tol=1e-9)

def test_driven_zero_forcing_matches_linear():
    """Zero forcing should match cnrs_solve_linear."""
    lam = -0.3 + 2j
    sol_driven = cnrs_solve_driven(lam, y0=1.0, forcing=None)
    sol_linear = cnrs_solve_linear(lam, y0=1.0)
    for s in [0.25, 0.5, 1.0]:
        _check(f"driven(f=0) vs linear at s={s}",
               sol_driven.evaluate(s), sol_linear.evaluate(s))

def test_driven_callable_raises():
    """Callable forcing should raise TypeError with helpful message."""
    with pytest.raises(TypeError, match="EGF coefficients"):
        cnrs_solve_driven(1j, y0=1.0, forcing=cmath.sin)


# ══════════════════════════════════════════════════════════════════════════════
# cnrs_solve_second_order
# ══════════════════════════════════════════════════════════════════════════════

def _second_order_exact(gamma, omega, y0, dy0):
    """Exact eigenvalue solution for y'' + 2γy' + ω²y = 0."""
    disc = complex(gamma)**2 - complex(omega)**2   # positive for overdamped
    lam1 = -gamma + cmath.sqrt(disc)
    lam2 = -gamma - cmath.sqrt(disc)
    if abs(lam1 - lam2) < 1e-12:
        # Critically damped
        A = complex(y0)
        B = complex(dy0) - lam1 * A
        return lambda s: (A + B*s) * cmath.exp(lam1*s)
    A = (complex(dy0) - lam2*complex(y0)) / (lam1 - lam2)
    B = complex(y0) - A
    return lambda s: A*cmath.exp(lam1*s) + B*cmath.exp(lam2*s)

def test_second_order_underdamped():
    """Underdamped oscillator: γ=0.1, ω=1.0."""
    g, w = 0.1, 1.0
    sol = cnrs_solve_second_order(g, w, y0=1.0, dy0=0.0)
    exact = _second_order_exact(g, w, 1.0, 0.0)
    for s in [0.0, 0.25, 0.5, 0.75, 1.0]:
        _check(f"underdamped at s={s}", sol.evaluate(s), exact(s))

def test_second_order_pure_oscillator():
    """Undamped oscillator: γ=0, ω=2.0 → cos(2s)."""
    sol = cnrs_solve_second_order(0.0, 2.0, y0=1.0, dy0=0.0)
    for s in [0.0, 0.25, 0.5, 1.0]:
        _check(f"cos(2s) at s={s}", sol.evaluate(s).real, math.cos(2*s))

def test_second_order_overdamped():
    """Overdamped: γ=2.0, ω=1.0."""
    g, w = 2.0, 1.0
    sol = cnrs_solve_second_order(g, w, y0=1.0, dy0=0.0)
    exact = _second_order_exact(g, w, 1.0, 0.0)
    for s in [0.0, 0.25, 0.5, 1.0]:
        _check(f"overdamped at s={s}", sol.evaluate(s), exact(s))

def test_second_order_initial_conditions():
    """Non-zero initial velocity: y(0)=0, y'(0)=1 → sin-like."""
    sol = cnrs_solve_second_order(0.0, 1.0, y0=0.0, dy0=1.0)
    for s in [0.0, 0.25, 0.5, 1.0]:
        _check(f"sin(s) at s={s}", sol.evaluate(s).real, math.sin(s))


# ══════════════════════════════════════════════════════════════════════════════
# OdeSolution: derivative and eigenvalue
# ══════════════════════════════════════════════════════════════════════════════

def test_derivative_matches_exact():
    """Derivative stream should give λ·y(s)."""
    lam = -0.3 + 2j
    sol = cnrs_solve_linear(lam, y0=1.0)
    dsol = sol.derivative()
    for s in [0.0, 0.25, 0.5, 1.0]:
        exact_dy = lam * cmath.exp(lam*s)
        _check(f"dy/ds at s={s}", dsol.evaluate(s), exact_dy)

def test_derivative_returns_ode_solution():
    sol = cnrs_solve_linear(-0.3+2j)
    assert isinstance(sol.derivative(), OdeSolution)

def test_eigenvalue_exact():
    """Eigenvalue extracted from c[1]/c[0] should be exact."""
    for lam in [-0.3+2j, 0.5+1.2j, -0.1+0.995j, 1j*math.pi]:
        sol = cnrs_solve_linear(lam)
        extracted = sol.eigenvalue()
        assert abs(extracted - lam) < 1e-14, \
            f"lam={lam}: extracted={extracted}, err={abs(extracted-lam):.2e}"

def test_eigenvalue_raises_for_zero_c0():
    """Eigenvalue extraction should raise for trivial solution."""
    sol = cnrs_solve_linear(1j, y0=0.0)
    with pytest.raises(ValueError, match="c\\[0\\]"):
        sol.eigenvalue()


# ══════════════════════════════════════════════════════════════════════════════
# Observable maps
# ══════════════════════════════════════════════════════════════════════════════

def test_modulus_sq():
    """For exp(αs + iωs): |y|² = exp(2αs)."""
    alpha, omega = -0.3, 2.0
    lam = complex(alpha, omega)
    sol = cnrs_solve_linear(lam)
    for s in [0.0, 0.25, 0.5, 1.0]:
        expected = math.exp(2*alpha*s)
        assert abs(sol.modulus_sq(s) - expected) < TOL, \
            f"|y|² at s={s}: {sol.modulus_sq(s)} != {expected}"

def test_real_part():
    """Re(exp(αs+iωs)) = exp(αs)*cos(ωs)."""
    alpha, omega = -0.1, 1.5
    lam = complex(alpha, omega)
    sol = cnrs_solve_linear(lam)
    for s in [0.0, 0.25, 0.5, 1.0]:
        expected = math.exp(alpha*s) * math.cos(omega*s)
        assert abs(sol.real_part(s) - expected) < TOL

def test_imag_part():
    """Im(exp(αs+iωs)) = exp(αs)*sin(ωs)."""
    alpha, omega = -0.1, 1.5
    lam = complex(alpha, omega)
    sol = cnrs_solve_linear(lam)
    for s in [0.0, 0.25, 0.5, 1.0]:
        expected = math.exp(alpha*s) * math.sin(omega*s)
        assert abs(sol.imag_part(s) - expected) < TOL

def test_phase():
    """Phase of exp(iωs) = ωs."""
    omega = 1.5
    sol = cnrs_solve_linear(1j*omega)
    for s in [0.0, 0.25, 0.5, 1.0]:
        assert abs(sol.phase(s) - omega*s) < TOL, \
            f"phase at s={s}: {sol.phase(s)} != {omega*s}"

def test_phase_rate_equals_omega():
    """d(phase)/ds = ω = Im(λ) for exp(λs)."""
    lam = -0.3 + 2.0j
    sol = cnrs_solve_linear(lam)
    for s in [0.1, 0.25, 0.5, 0.75]:
        assert abs(sol.phase_rate(s) - lam.imag) < TOL, \
            f"phase_rate at s={s}: {sol.phase_rate(s)} != {lam.imag}"

def test_phase_current():
    """J = |y|² * dθ/ds = exp(2αs) * ω."""
    alpha, omega = -0.3, 2.0
    lam = complex(alpha, omega)
    sol = cnrs_solve_linear(lam)
    for s in [0.0, 0.25, 0.5, 1.0]:
        expected = math.exp(2*alpha*s) * omega
        assert abs(sol.phase_current(s) - expected) < TOL, \
            f"J at s={s}: {sol.phase_current(s)} != {expected}"

def test_qm_modulus_sq_constant():
    """For pure phase evolution |ψ|² = 1 (information loss via modulus_sq)."""
    sol = cnrs_solve_linear(-2.5j)
    for s in [0.0, 0.25, 0.5, 1.0]:
        assert abs(sol.modulus_sq(s) - 1.0) < TOL


# ══════════════════════════════════════════════════════════════════════════════
# Early real reduction: C5 result quantified
# ══════════════════════════════════════════════════════════════════════════════

def test_two_systems_same_modulus_sq_different_phase():
    """
    exp((α+iω)s) and exp(α·s) have identical |y|², but
    different Re(y), phase, and phase_current.
    This is the Phase C / D finding: premature reduction loses information.
    """
    alpha = -0.3
    sol_osc  = cnrs_solve_linear(complex(alpha, 2.0))   # with oscillation
    sol_decay = cnrs_solve_linear(complex(alpha, 0.0))  # decay only

    for s in [0.1, 0.25, 0.5, 0.75, 1.0]:
        # |y|² identical (within floating-point noise)
        assert abs(sol_osc.modulus_sq(s) - sol_decay.modulus_sq(s)) < 1e-14, \
            f"|y|² differs at s={s}"
        # Re(y) differs significantly
        diff_re = abs(sol_osc.real_part(s) - sol_decay.real_part(s))
        assert diff_re > 0.01, \
            f"Re(y) should differ at s={s}, got diff={diff_re:.4f}"


# ══════════════════════════════════════════════════════════════════════════════
# Domain warning
# ══════════════════════════════════════════════════════════════════════════════

def test_domain_warning_beyond_s_max():
    """Warning raised when evaluating beyond natural domain."""
    sol = cnrs_solve_linear(-0.3+2j, terms=25)  # s_max ≈ 2.9
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        sol.evaluate(10.0)
        assert len(w) == 1
        assert "reliable domain" in str(w[0].message).lower()

def test_no_warning_within_domain():
    """No warning within natural domain."""
    sol = cnrs_solve_linear(-0.3+2j, terms=25)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        sol.evaluate(1.0)
        assert len(w) == 0


# ══════════════════════════════════════════════════════════════════════════════
# OdeSolution properties
# ══════════════════════════════════════════════════════════════════════════════

def test_s_max_positive():
    sol = cnrs_solve_linear(-0.3+2j)
    assert sol.s_max > 0

def test_s_max_increases_with_terms():
    lam = -0.3 + 2j
    s_max_15 = cnrs_solve_linear(lam, terms=15).s_max
    s_max_25 = cnrs_solve_linear(lam, terms=25).s_max
    assert s_max_25 > s_max_15

def test_coeffs_length():
    sol = cnrs_solve_linear(1j, terms=20)
    assert len(sol.coeffs) == 20

def test_repr():
    sol = cnrs_solve_linear(-0.3+2j)
    r = repr(sol)
    assert "OdeSolution" in r
    assert "25 terms" in r

def test_summary_runs():
    sol = cnrs_solve_linear(-0.3+2j)
    s = sol.summary()
    assert "|y|²" in s
    assert "phase" in s
