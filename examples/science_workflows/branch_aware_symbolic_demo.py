"""
Branch-aware symbolic calculus demo.

This example shows the v0.5.0 branch-state scaffold for logarithms, square
roots, and powers.  It demonstrates explicit branch choices, conservative
simplification, symbolic differentiation, and agreement with the autodiff layer
for local derivatives.
"""

from __future__ import annotations

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cnrs.autodiff import CnrsDual
from cnrs.symbolic import BranchState, Var, diff, exp, log, pow_branch, sqrt


def main() -> None:
    z = Var("z")

    print("Branch-aware symbolic calculus demo")
    print("====================================")

    state = BranchState(log_branch=2, sqrt_branch=1, pow_branch=3)
    print("Branch state:", state)

    log0 = log(z, branch=0)
    log2 = log(z, branch=2, branch_state=state)
    print("\nLog branches at z=-1:")
    print("  ", log0, "=", log0.eval({"z": -1}, L=20))
    print("  ", log2, "=", log2.eval({"z": -1}, L=20))
    print("  d/dz", log2, "=", diff(log2, z))

    sqrt0 = sqrt(z, branch=0)
    sqrt1 = sqrt(z, branch=1, branch_state=state)
    print("\nSqrt branches at z=-1:")
    print("  ", sqrt0, "=", sqrt0.eval({"z": -1}, L=20))
    print("  ", sqrt1, "=", sqrt1.eval({"z": -1}, L=20))

    p = pow_branch(z, 0.5, branch=1, branch_state=state)
    print("\nBranch-aware power:")
    print("  expr:", p)
    print("  value at z=-1:", p.eval({"z": -1}, L=20))

    unsafe = exp(log(z, branch=1)).simplify()
    print("\nConservative simplification:")
    print("  exp(log_1(z)) stays as:", unsafe)
    print("  sqrt(z*z) stays as:", sqrt(z * z).simplify())

    expr = log(z * z + 2, branch=1)
    dexpr = diff(expr, z).simplify()
    dual = expr.eval({"z": CnrsDual.variable(1.2, L=20)}, L=20)
    print("\nSymbolic/autodiff derivative check:")
    print("  expr:", expr)
    print("  diff:", dexpr)
    print("  symbolic at z=1.2:", dexpr.eval({"z": 1.2}, L=20))
    print("  autodiff derivative:", dual.deriv)


if __name__ == "__main__":
    main()
