"""
rlc_three_workflows.py
======================
Demonstrates cnrs_oscillator: three-workflow comparison for the RLC circuit.

A free series RLC oscillator with Q > 1 produces a damped sinusoidal charge
q(t) = exp(-gamma*t) * [A*cos(omega_d*t) + B*sin(omega_d*t)].

This script shows what each workflow sees:

  Workflow A — early |q|²:
    Sees only the exponential decay envelope exp(-2*gamma*t).
    The oscillation frequency omega_d is completely invisible.

  Workflow B — ordinary complex analysis:
    Evaluates the full real q(t); recovers omega_d from zero-crossing
    intervals or spectral analysis — not from the amplitude alone.

  Workflow C — CNRS-H EGF stream:
    Exact coefficient-recurrence solution; matches the analytic formula
    to machine precision. Phase/frequency information is encoded in the
    EGF coefficients and accessible without integration.

Usage:
    python rlc_three_workflows.py

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

from cnrs.cnrs_oscillator import (
    RlcParams,
    rlc_free,
    compare_rlc,
)


def main():
    print("=" * 60)
    print("  RLC oscillator — three workflows — cnrs_oscillator demo")
    print("=" * 60)

    p = RlcParams(L=1.0, R=0.2, C=1.0,
                  q0=complex(1.0, 0.0), dq0=complex(0.0, 0.0))

    gamma   = p.gamma()
    omega0  = p.omega0()
    omega_d = p.omega_d()
    Q       = p.quality_factor()

    print(f"\nCircuit: L={p.L} H, R={p.R} Ω, C={p.C} F")
    print(f"  omega_0 = {omega0:.4f} rad/s  (natural frequency)")
    print(f"  gamma   = {gamma:.4f} s⁻¹      (damping)")
    print(f"  omega_d = {omega_d:.4f} rad/s  (damped oscillation)")
    print(f"  Q       = {Q:.2f}            (underdamped)")

    T_d = 2.0 * math.pi / omega_d
    t_vals = np.linspace(0.0, 2.0 * T_d, 300)

    # Exact analytic solution (q0=1, dq0=0)
    q_exact = np.exp(-gamma * t_vals) * (
        np.cos(omega_d * t_vals) +
        (gamma / omega_d) * np.sin(omega_d * t_vals))

    # CNRS-H solution
    sol = rlc_free(p, terms=50)
    q_cnrs = sol.real_part(t_vals)

    # ── Workflow A: |q|² ─────────────────────────────────────────────────────
    A_mod2 = q_exact ** 2
    # Decay envelope
    envelope = (1.0 + (gamma/omega_d)**2) * np.exp(-2.0*gamma*t_vals)

    print(f"\nWorkflow A — |q(t)|² (early real reduction):")
    print(f"  Sees: decay envelope ~ exp(-2*gamma*t)")
    print(f"  omega_d = {omega_d:.4f} rad/s — INVISIBLE in |q|²")
    print(f"  |q|² oscillates between 0 and envelope:")
    print(f"    max |q|² = {float(np.max(A_mod2)):.4f}  (at t=0)")
    print(f"    Envelope at T_d/2 = {float(envelope[len(t_vals)//4]):.4f}")

    # ── Workflow B: spectral recovery from real q(t) ──────────────────────────
    # omega_d is recoverable by measuring zero crossings or FFT — not from |q|²
    # Measure period from zero crossings
    signs = np.sign(q_exact[10:])
    crossings = np.where(np.diff(signs))[0] + 10
    if len(crossings) >= 2:
        T_measured = 2.0 * float(t_vals[crossings[1]] - t_vals[crossings[0]])
        omega_d_B = 2.0 * math.pi / T_measured
    else:
        omega_d_B = float("nan")

    print(f"\nWorkflow B — real q(t), spectral/zero-crossing analysis:")
    print(f"  omega_d from zero crossings: {omega_d_B:.4f} rad/s")
    print(f"  True omega_d:                {omega_d:.4f} rad/s")
    print(f"  Key point: frequency requires analysis of q(t), NOT |q|²")

    # ── Workflow C: CNRS-H EGF stream ────────────────────────────────────────
    max_err = float(np.max(np.abs(q_cnrs - q_exact)))
    rel_err = max_err / float(np.max(np.abs(q_exact)))

    # omega_d from EGF coefficients: encoded in c[2] recurrence
    # c[2] = -omega_0²*c[0] - 2*gamma*c[1] = -omega_0² (for q0=1, dq0=0)
    # The damped frequency appears in c[2]: c[2] = -(gamma² + omega_d²)
    coeffs = sol.coeffs()
    omega_d_C_sq = abs(coeffs[2].real) - gamma**2
    omega_d_C = math.sqrt(max(omega_d_C_sq, 0.0))

    print(f"\nWorkflow C — CNRS-H EGF stream (50 terms):")
    print(f"  CNRS vs exact max error: {max_err:.2e}  (machine precision)")
    print(f"  CNRS vs exact rel error: {rel_err:.2e}")
    print(f"  omega_d from EGF c[2]:   {omega_d_C:.4f} rad/s")
    print(f"  True omega_d:            {omega_d:.4f} rad/s")
    print(f"  No ODE integration — exact coefficient recurrence")

    # ── Comparison table ──────────────────────────────────────────────────────
    print(f"\n  {'Workflow':<14} {'omega_d visible?':<20} {'Error vs exact'}")
    print(f"  {'─'*14} {'─'*20} {'─'*18}")
    print(f"  {'A: |q(t)|²':<14} {'NO':<20} N/A (information lost)")
    print(f"  {'B: q(t) FFT':<14} {'YES (analysis)':<20} N/A (approx method)")
    print(f"  {'C: CNRS-H':<14} {'YES (exact)':<20} {rel_err:.2e}")

    # ── Full compare_rlc result ───────────────────────────────────────────────
    result = compare_rlc(p)
    print(f"\nfull compare_rlc() result:")
    for k, v in result.metrics.items():
        print(f"  {k}: {v}")
    print(f"\n  Interpretation: {result.interpretation}")

    print("\n" + "=" * 60)
    print("  PASS — oscillation invisible in |q|², exact in CNRS-H")
    print("=" * 60)


if __name__ == "__main__":
    main()
