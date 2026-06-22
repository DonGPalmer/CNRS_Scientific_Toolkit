"""CNRS-H local-domain diagnostics demo.

Run from the repository root:

    python examples/science_workflows/cnrs_h_domain_diagnostics_demo.py
"""

from cnrs.cnrs_h_jet import jet_from_symbolic
from cnrs.symbolic import Var, exp, log, sqrt


def show(label, jet, points):
    print(f"\n{label}")
    print("center:", jet.center)
    print("domain:", jet.domain)
    for p in points:
        print(
            f"  s={p}: valid={jet.valid_for(p)}, "
            f"boundary_margin={jet.distance_to_boundary(p)}, "
            f"last_term≈{jet.estimate_truncation_error(p)}"
        )


def main():
    s = Var("s")

    show(
        "log(1+s) around s0=0 has branch point at s=-1",
        jet_from_symbolic(log(1 + s), s, center=0, order=8),
        [0.25, 0.9, 1.25],
    )

    show(
        "sqrt(1+s) around s0=0.25 has nearest branch point at s=-1",
        jet_from_symbolic(sqrt(1 + s), s, center=0.25, order=8),
        [0.5, 1.0, 2.0],
    )

    show(
        "exp(0.08*s) around a biological scale is entire in this local model",
        jet_from_symbolic(exp(0.08 * s), s, center=-12, order=8),
        [-12, -11.5, 0],
    )


if __name__ == "__main__":
    main()
