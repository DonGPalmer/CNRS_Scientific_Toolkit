"""
cnrs_multiscale_turing_window.py
===========================
Scale-aware Turing-window demonstration.

Shows how Components 7 and 8 work together:

  Component 7 (cnrs_multiscale): ScaleLadder tracks the exact CNRS-H
  field Ψ(s) = exp(λs) across a scale range.  The amplitude |Ψ(s)|
  represents the activator mode at each scale level.

  Component 8 (cnrs_regime): ScaleSweep.from_ladder() wraps the ladder
  in a scale sweep; a classifier identifies the Turing-active window
  (|Ψ|² above a threshold, standing for the diffusion ratio being
  inside the pattern-forming window).

Also demonstrates the standalone ScaleParameter/ScaleSweep path (AI1
design) for comparison: the same Turing window is computed using ordinary
scalar parameters without CNRS-H, showing that both paths give
consistent transition locations.

Session: 44, 2026-06-07
Author:  Donald G. Palmer
"""
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import math

from cnrs.cnrs_multiscale import ScaleLadder
from cnrs.cnrs_regime import (
    ScaleParameter,
    ScaleSweep,
    logarithmic_scale,
    length_from_scale,
)


# ── Part A: Component 7 + 8 path (CNRS-H ladder + ScaleSweep) ────────────────

def demo_ladder_sweep():
    print("=" * 60)
    print("Part A: ScaleLadder + ScaleSweep.from_ladder()")
    print("=" * 60)
    print()

    # A decaying-oscillatory eigenvalue models the activator mode:
    # Re(λ) < 0 → amplitude decays with scale (like an inhibitor taking over)
    # Im(λ) ≠ 0 → oscillatory structure across scales
    lam = complex(-1.2, 1.5)
    ladder = ScaleLadder.uniform(
        lam, y0=1.0, s_total=2.0, n_rungs=8, terms=40,
        label="activator_mode"
    )

    # Turing-active window: |Ψ(s)|² above threshold (amplitude large enough
    # for pattern formation before inhibitor dominates)
    threshold = 0.05
    sweep = ScaleSweep.from_ladder(
        ladder,
        classifier=lambda r: r.modulus_sq > threshold,
        n=40,
        label="turing_window_ladder",
    )

    result = sweep.run()

    print(f"  λ = {lam},  threshold = {threshold}")
    print(f"  {'s':>6}  {'|Ψ|²':>10}  {'phase':>10}  {'J':>10}  active")
    print("  " + "─" * 50)
    for i, s in enumerate(result.scales[::4]):
        idx = result.scales.index(s)
        r = result.outputs[idx]
        active = result.regime[idx]
        print(
            f"  {s:6.3f}  {r.modulus_sq:10.6f}  "
            f"{r.phase:10.6f}  {r.phase_current:10.6f}  {active}"
        )

    print()
    print(f"  Transitions detected: {len(result.transitions)}")
    for t in result.transitions:
        print(f"    s ≈ {t.midpoint:.4f}  ({t.state_left} → {t.state_right})")

    print()
    active_intervals = result.active_intervals()
    print(f"  Active intervals: {len(active_intervals)}")
    for lo, hi in active_intervals:
        L_lo = length_from_scale(lo, reference_length=1.0)
        L_hi = length_from_scale(hi, reference_length=1.0)
        print(
            f"    {lo:.3f} ≤ s ≤ {hi:.3f} nats  "
            f"({L_lo:.3f} ≤ L ≤ {L_hi:.3f}  [L_ref=1])"
        )


# ── Part B: ScaleParameter path (AI1 design, no CNRS-H) ──────────────────────

def demo_parameter_sweep():
    print()
    print("=" * 60)
    print("Part B: ScaleParameter + ScaleSweep (AI1 design)")
    print("=" * 60)
    print()

    # Same Turing window computed via scale-dependent diffusion parameters
    # (polynomial expansion of D_u and D_v as functions of s)
    parameters = {
        "D_u": ScaleParameter(
            base=1.0,
            coefficients=[0.05],
            name="D_u",
            enforce_positive=True,
        ),
        "D_v": ScaleParameter(
            base=100.0,
            coefficients=[-0.30],
            name="D_v",
            enforce_positive=True,
        ),
    }

    def turing_model(s, params):
        d_u = params["D_u"]
        d_v = params["D_v"]
        return {"s": s, "D_u": d_u, "D_v": d_v, "ratio": d_v / d_u}

    def is_patterning(output):
        return output["ratio"] > 50.0

    sweep = ScaleSweep(
        model=turing_model,
        parameters=parameters,
        s_min=-1.0,
        s_max=2.0,
        n=31,
        classifier=is_patterning,
        label="turing_window_params",
    )

    result = sweep.run()

    print(f"  {'s':>6}  {'D_u':>8}  {'D_v':>8}  {'ratio':>8}  active")
    print("  " + "─" * 46)
    for i, (s, output, active) in enumerate(
        zip(result.scales, result.outputs, result.regime)
    ):
        if i % 5 == 0:
            print(
                f"  {s:6.2f}  {output['D_u']:8.4f}  "
                f"{output['D_v']:8.4f}  {output['ratio']:8.4f}  {active}"
            )

    print()
    print(f"  Transitions detected: {len(result.transitions)}")
    for t in result.transitions:
        print(f"    s ≈ {t.midpoint:.4f}  ({t.state_left} → {t.state_right})")

    print()
    active_intervals = result.active_intervals()
    print(f"  Active intervals: {len(active_intervals)}")
    for lo, hi in active_intervals:
        print(f"    {lo:.3f} ≤ s ≤ {hi:.3f} nats")


# ── Part C: Coordinate utilities ──────────────────────────────────────────────

def demo_coordinates():
    print()
    print("=" * 60)
    print("Part C: logarithmic_scale / length_from_scale")
    print("=" * 60)
    print()
    L_ref = 1.0
    print(f"  {'L':>10}  {'s = log(L/L_ref)':>18}  {'L recovered':>12}")
    print("  " + "─" * 44)
    for L in [0.1, 0.5, 1.0, math.e, 5.0, 10.0]:
        s = logarithmic_scale(L, L_ref)
        L_back = length_from_scale(s, L_ref)
        print(f"  {L:10.4f}  {s:18.6f}  {L_back:12.4f}")


if __name__ == "__main__":
    demo_ladder_sweep()
    demo_parameter_sweep()
    demo_coordinates()
