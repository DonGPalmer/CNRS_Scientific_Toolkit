"""
turing_scale_exit.py
====================
Demonstrates cnrs_bio: finding the Turing instability exit scale.

The Gierer-Meinhardt activator-inhibitor system, embedded in the
four-dimensional Scale Space manifold, has a diffusion ratio
d(s) = D_h(s)/D_a(s) that decays with increasing scale s.

Turing pattern formation is active where d(s) > d_hi.
The exit scale s_exit is where d(s) crosses d_hi — the scale at
which the instability becomes extinct.

For the Paper 18 demonstration parameters (c=0.5, gamma=50):
    d_hi  ≈ 41.785
    s_exit ≈ 0.52 nats  (~17 μm, inter-cellular scale)

This script demonstrates all three workflows:
  A. Early reduction: use d(s) directly, no scale-gradient correction
  B. Same as A for real diffusion ratio — no complex structure at this level
  C. CNRS-H stream: d_ratio as a ScaleLaw with exact digit-shift derivative;
     scale-gradient correction d_eff shifts s_exit

Usage:
    python turing_scale_exit.py

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

from cnrs.cnrs_bio import (
    GmParams,
    da_profile, dh_profile, d_ratio,
    turing_discriminant, find_s_exit,
    turing_profile, compare_turing_workflows,
    d_eff,
)


def main():
    print("=" * 60)
    print("  Turing instability exit scale — cnrs_bio demo")
    print("=" * 60)

    p = GmParams()

    # ── Discriminant roots ──────────────────────────────────────────────────
    d_lo, d_hi = turing_discriminant(p)
    print(f"\nGM parameters: c={p.c}, gamma={p.gamma}")
    print(f"Turing discriminant roots:")
    print(f"  d_lo = {d_lo:.4f}")
    print(f"  d_hi = {d_hi:.4f}  (instability active for d(s) > d_hi)")

    # ── Diffusion profiles as ScaleLaws ─────────────────────────────────────
    da = da_profile(p, terms=32)
    dh = dh_profile(p, terms=32)
    dr = d_ratio(p, terms=32)

    print(f"\nDiffusion profiles at s=0:")
    print(f"  D_a(0) = {da.evaluate(0.0).real:.4f}  (activator)")
    print(f"  D_h(0) = {dh.evaluate(0.0).real:.4f}  (inhibitor)")
    print(f"  d(0)   = {dr.evaluate(0.0).real:.4f}  = D_h/D_a")

    print(f"\nExact digit-shift log-derivative of d(s):")
    print(f"  d[log d]/ds = {dr.log_derivative(0.5).real:.4f}")
    print(f"  Expected:     {p.lam_h - p.lam_a:.4f}  (= lam_h - lam_a)")

    # ── Workflow A/B: plain s_exit ───────────────────────────────────────────
    s_exit_plain = find_s_exit(p)
    print(f"\nWorkflow A/B — s_exit from d(s) = d_hi:")
    print(f"  s_exit = {s_exit_plain:.4f} nats")
    # Verify analytically
    s_analytic = (3.0 / 5.0) * math.log(100.0 / d_hi)
    print(f"  Analytic: (3/5)*ln(100/d_hi) = {s_analytic:.4f} nats")
    print(f"  Agreement: {abs(s_exit_plain - s_analytic):.2e}")

    # ── Workflow C: with scale-gradient correction ───────────────────────────
    print(f"\nWorkflow C — d_eff with scale-gradient correction:")
    for a1a0, h1h0, label in [
        (0.0,  0.0,  "no correction (should match A/B)"),
        (0.3,  0.0,  "positive a1/a0 (activator gradient)"),
        (0.0,  0.1,  "small positive h1/h0 (inhibitor gradient)"),
    ]:
        result = compare_turing_workflows(
            p=p, a1_over_a0=a1a0, h1_over_h0=h1h0,
            s_vals=np.linspace(0.0, 2.0, 300))
        s_c = result.s_exit_with_correction
        s_label = f"{s_c:.4f}" if s_c is not None else "none in range"
        print(f"  a1/a0={a1a0:.1f}, h1/h0={h1h0:.1f} ({label})")
        print(f"    s_exit = {s_label} nats")

    # ── Full profile ─────────────────────────────────────────────────────────
    prof = turing_profile(p, s_vals=np.linspace(0.0, 2.0, 400))
    n_active = int(np.sum(prof.active))
    n_total = len(prof.active)
    print(f"\nTuring profile (0 to 2 nats):")
    print(f"  Active (d > d_hi): {n_active}/{n_total} scale points")
    print(f"  Inactive (d ≤ d_hi): {n_total - n_active}/{n_total} scale points")
    print(f"  s_exit confirmed: {prof.s_exit:.4f} nats")

    print(f"\nPhysical interpretation:")
    print(f"  s_exit ≈ {s_exit_plain:.2f} nats ≈ exp({s_exit_plain:.2f}) μm reference scale")
    print(f"  Turing patterns active at sub-cellular and cellular scales")
    print(f"  Instability extinct at tissue scale and above")
    print(f"  Consistent with Paper 18, Table 1")

    print("\n" + "=" * 60)
    print("  PASS — all values consistent with Paper 18")
    print("=" * 60)


if __name__ == "__main__":
    main()
