"""CNRS-H branch-state propagation demo.

Run with:
    python examples/science_workflows/cnrs_h_branch_state_demo.py
"""

from cnrs.symbolic import Var, log, sqrt, pow_branch, BranchState
from cnrs.cnrs_h_jet import jet_from_symbolic, verify_jet_chain_rule


def main() -> None:
    s = Var("s")
    x = Var("x")

    log_jet = jet_from_symbolic(log(1 + s, branch=2), s, center=0, order=6)
    sqrt_jet = jet_from_symbolic(sqrt(1 + s, branch=1), s, center=0, order=6)
    pow_jet = jet_from_symbolic(pow_branch(1 + s, 0.5, branch=3), s, center=0, order=6)

    print("log jet branch:", log_jet.branch_summary())
    print("sqrt jet branch:", sqrt_jet.branch_summary())
    print("pow jet branch:", pow_jet.branch_summary())

    product = log_jet * sqrt_jet
    print("product merged branch:", product.branch_summary())

    outer = jet_from_symbolic(log(1 + x, branch=2), x, center=0, order=7)
    inner = jet_from_symbolic(sqrt(1 + s, branch=1) - 1, s, center=0, order=7)
    comparison = verify_jet_chain_rule(outer, inner, order=5, atol=1e-8)

    print("chain rule passed:", comparison.passed)
    print("lhs branch:", comparison.lhs.branch_summary())
    print("rhs branch:", comparison.rhs.branch_summary())

    manual = log_jet.with_branch_state(BranchState(log_branch=2, winding=1), note="manual winding scaffold")
    print("manual winding scaffold:", manual.branch_summary())


if __name__ == "__main__":
    main()
