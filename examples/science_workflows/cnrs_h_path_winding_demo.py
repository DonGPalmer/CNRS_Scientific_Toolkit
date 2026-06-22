"""CNRS-H path/winding demonstration for v0.6.2."""

from cnrs.cnrs_h_path import BranchPoint, circle_path, continue_log, continue_sqrt, winding_number
from cnrs.cnrs_h_jet import jet_from_symbolic
from cnrs.symbolic import Var, log


def main() -> None:
    s = Var("s")
    path = circle_path(center=0, radius=1, turns=1, samples_per_turn=64, label="one loop around zero")

    print("Path:", path.summary())
    print("Winding around 0:", winding_number(path, 0))
    print("log(1) after path:", continue_log(1, path))
    print("sqrt(1) after path:", continue_sqrt(1, path))

    jet = jet_from_symbolic(log(1 + s, branch=0), s, center=0, order=6)
    continued = jet.continue_along(path, branch_points=[BranchPoint(0, kind="log", label="0")])

    print("Original jet branch:", jet.branch_summary())
    print("Continued jet branch:", continued.branch_summary())
    print("Path history:", continued.path_history)


if __name__ == "__main__":
    main()
