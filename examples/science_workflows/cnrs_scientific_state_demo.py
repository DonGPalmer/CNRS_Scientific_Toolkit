"""CNRS-native scientific state demo.

This example shows the v0.7.0 integration object: a single state carries a
CNRS-H local jet, source expression, scale unit, branch metadata, local-domain
metadata, path history, and observation maps.
"""

from cnrs.symbolic import Var, exp, log
from cnrs.cnrs_scientific_state import CnrsScientificState
from cnrs.cnrs_h_path import BranchPoint, circle_path


def main() -> None:
    s = Var("s")

    scale_state = CnrsScientificState.from_symbolic(exp(0.08 * s), s, center=-12, order=8)
    print("Scale-law state:")
    print(" ", scale_state.summary())
    print("  value at center:", scale_state.evaluate(-12))
    print("  derivative at center:", scale_state.diff(order=7).evaluate(-12))

    branch_state = CnrsScientificState.from_symbolic(log(1 + s), s, center=0, order=6)
    path = circle_path(center=0, radius=1, turns=1, label="unit loop")
    continued = branch_state.continue_along(path, branch_points=[BranchPoint(0, kind="log")])
    print("\nBranch continuation state:")
    print(" ", continued.summary())
    print("  original value at 0:", branch_state.evaluate(0))
    print("  continued value at 0:", continued.evaluate(0))
    print("  path history:", continued.path_history)

    oscillatory = CnrsScientificState.from_symbolic(exp(1j * s), s, center=0, order=12)
    points = [0, 0.2, 0.4]
    print("\nObservation maps:")
    print("  complex:", oscillatory.observe(points, "complex"))
    print("  abs2:", oscillatory.observe(points, "abs2"))
    print("  phase:", oscillatory.observe(points, "phase"))


if __name__ == "__main__":
    main()
