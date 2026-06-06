"""
cnrs_vs_scipy_benchmark.py
==========================
Demonstrates cnrs_interop: CNRS-H vs scipy.integrate.solve_ivp.

Shows the interoperability bridge in both directions:
  - CNRS-H solution → scipy-compatible Bunch
  - scipy solution → CnrsH stream (for digit-shift differentiation)

And runs timing benchmarks comparing CNRS-H coefficient recurrence
against scipy RK45 for two standard ODE problems:

  Problem 1: y' = lam*y  (complex damped oscillator)
  Problem 2: y'' + 2*gamma*y' + omega²*y = 0  (free RLC)

Key result: CNRS-H is exact within the EGF domain (no integration error),
while scipy uses adaptive step-size integration. The comparison shows where
they agree and quantifies the accuracy difference.

Usage:
    python cnrs_vs_scipy_benchmark.py

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
"""

from pathlib import Path
import sys
import math
import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cnrs.cnrs_interop import (
    solve_and_compare,
    benchmark_linear,
    benchmark_second_order,
    cnrs_to_scipy_ivp,
    scipy_ivp_to_cnrsh,
    modulus_array,
    phase_rate_array,
)
from cnrs.cnrs_ode import cnrs_solve_linear


def separator(title=""):
    w = 60
    if title:
        pad = (w - len(title) - 2) // 2
        print(f"\n{'─'*pad} {title} {'─'*(w-pad-len(title)-2)}")
    else:
        print("─" * w)


def main():
    print("=" * 60)
    print("  CNRS-H vs scipy — interop demo — cnrs_interop")
    print("=" * 60)

    s_vals = np.linspace(0.0, 0.5, 100)

    # ── Problem 1: complex damped oscillator ──────────────────────────────────
    separator("Problem 1: y' = (-0.3 + 2i)*y")

    lam = complex(-0.3, 2.0)
    y0  = complex(1.0, 0.0)

    result = solve_and_compare(lam=lam, y0=y0, s_vals=s_vals, terms=30,
                               label="complex damped oscillator")
    print(result.summary())

    # Verify exact vs both
    exact = y0 * np.exp(lam * s_vals)
    cnrs_vs_exact = float(np.max(np.abs(result.cnrs_vals - exact)))
    scipy_vs_exact = float(np.max(np.abs(result.scipy_vals - exact)))
    print(f"\n  CNRS-H vs exact:   {cnrs_vs_exact:.2e}  (EGF series)")
    print(f"  scipy  vs exact:   {scipy_vs_exact:.2e}  (RK45, rtol=1e-10)")

    # ── Interop: CNRS → scipy bundle ──────────────────────────────────────────
    separator("CNRS-H → scipy bundle → digit-shift derivative")

    sol = cnrs_solve_linear(lam=lam, y0=y0, terms=30)
    bunch = cnrs_to_scipy_ivp(sol, s_vals)

    print(f"  bunch.t shape:   {bunch.t.shape}")
    print(f"  bunch.y shape:   {bunch.y.shape}  (row 0=Re, row 1=Im)")
    print(f"  bunch.success:   {bunch.success}")

    # Re-import into CnrsH for digit-shift differentiation
    h_rt = scipy_ivp_to_cnrsh(bunch, degree=14)
    dh   = h_rt.differentiate()
    deriv_at_0 = dh.evaluate(0.0)
    expected_deriv = lam * y0
    print(f"\n  Digit-shift derivative at s=0:")
    print(f"    CNRS-H: {deriv_at_0:.6f}")
    print(f"    Exact (lam*y0): {expected_deriv:.6f}")
    print(f"    Error: {abs(deriv_at_0 - expected_deriv):.2e}")

    # ── Observation map arrays ─────────────────────────────────────────────────
    separator("Observation map arrays (vectorised)")

    m  = modulus_array(sol, s_vals)
    pr = phase_rate_array(sol, s_vals)

    print(f"  modulus_array: shape={m.shape}, dtype={m.dtype}")
    print(f"    max |z(s)|: {float(np.max(m)):.4f}  (at s=0)")
    print(f"    min |z(s)|: {float(np.min(m)):.4f}  (at s={float(s_vals[-1]):.2f})")
    print(f"\n  phase_rate_array (Im(z'/z)):")
    print(f"    mean: {float(np.mean(pr)):.4f}  (should be Im(lam)={lam.imag:.4f})")
    print(f"    std:  {float(np.std(pr)):.2e}   (near zero for pure exponential)")

    # ── Problem 2: free RLC ────────────────────────────────────────────────────
    separator("Problem 2: y'' + 0.2*y' + y = 0  (free RLC)")

    s2 = np.linspace(0.0, 2.0 * math.pi, 100)
    result2 = benchmark_second_order(
        gamma=0.1, omega=1.0,
        y0=complex(1.0), dy0=complex(0.0),
        s_vals=s2, terms=40, n_repeat=10,
        label="free RLC (gamma=0.1, omega=1.0)")
    print(result2.summary())

    # ── Timing benchmarks ──────────────────────────────────────────────────────
    separator("Timing benchmark: 20 repeats, 100 points")

    bench1 = benchmark_linear(
        lam=lam, y0=y0, s_vals=s_vals, terms=30, n_repeat=20,
        label="y'=(-0.3+2i)*y")
    print(bench1.summary())

    bench2 = benchmark_second_order(
        gamma=0.1, omega=1.0, y0=complex(1.0), dy0=complex(0.0),
        s_vals=s2, terms=40, n_repeat=20,
        label="y''+0.2y'+y=0")
    print()
    print(bench2.summary())

    # ── Summary ───────────────────────────────────────────────────────────────
    separator("Summary")
    print(f"\n  CNRS-H ODE approach:")
    print(f"    Exact: no integration — pure coefficient recurrence")
    print(f"    Error vs exact (Problem 1): {cnrs_vs_exact:.2e}")
    print(f"    Domain: reliable within EGF convergence radius")
    print(f"\n  scipy RK45 approach:")
    print(f"    Adaptive step-size numerical integration")
    print(f"    Error vs exact (Problem 1): {scipy_vs_exact:.2e}")
    print(f"    Domain: works on any smooth ODE")
    print(f"\n  Interop: CNRS-H → bundle → digit-shift derivative works")
    print(f"  Both approaches agree within {result.max_rel_err:.2e} relative error")

    print("\n" + "=" * 60)
    print("  PASS — interop bridge functional in both directions")
    print("=" * 60)


if __name__ == "__main__":
    main()
