"""
Reaction-diffusion scale-exit demonstration.

This example uses the CNRS toolkit as a scale-aware wrapper around a standard
linear Turing analysis.  It does not solve the full PDE.  It asks a focused
multi-scale question:

    as diffusion coefficients vary with logarithmic scale s, where does a
    Turing instability enter or exit?

For the default Gierer-Meinhardt parameters used in the CNRS biology paper,
D_u(s) = 0.01 exp(-s/3), D_v(s) = exp(-2s), so the diffusion ratio decreases
with scale.  The model begins inside the Turing-active window and exits near
s = 0.52 nats.
"""
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cnrs.cnrs_rd_scale_exit import exponential_gm_scale_exit, gm_default_kinetics, turing_thresholds


def main():
    kinetics = gm_default_kinetics()
    thresholds = turing_thresholds(kinetics)

    result = exponential_gm_scale_exit(
        kinetics,
        d_u0=0.01,
        d_v0=1.0,
        lambda_u=-1.0 / 3.0,
        lambda_v=-2.0,
        s_min=0.0,
        s_max=2.0,
        n=81,
    )

    print("Reaction-diffusion scale-exit demonstration")
    print("--------------------------------------------")
    print(f"Kinetics: {kinetics.name}")
    print(f"Stable homogeneous kinetics: {kinetics.homogeneous_stable()}")
    print(f"Turing ratio thresholds: d_low={thresholds.d_low:.4f}, d_high={thresholds.d_high:.4f}")
    print()

    print("Selected scale samples:")
    for idx in [0, 10, 20, 30, 40, 60, 80]:
        point = result.points[idx]
        print(
            f"s={point.s: .3f}  "
            f"D_u={point.d_u: .6f}  "
            f"D_v={point.d_v: .6f}  "
            f"ratio={point.ratio: .3f}  "
            f"active={point.active}"
        )

    print()
    print("Transitions:")
    if not result.transitions:
        print("  none")
    for transition in result.transitions:
        print(f"  {transition.kind} at s ≈ {transition.s_mid:.4f}")

    print()
    print("Active intervals:")
    for left, right in result.active_intervals():
        print(f"  {left:.4f} <= s <= {right:.4f}")


if __name__ == "__main__":
    main()
