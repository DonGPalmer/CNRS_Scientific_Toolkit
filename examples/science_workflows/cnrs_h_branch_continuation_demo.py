"""CNRS-H branch-aware local continuation demo (v0.6.3)."""

from cnrs.symbolic import Var, log, sqrt
from cnrs.cnrs_h_path import BranchPoint, circle_path
from cnrs.cnrs_h_continuation import continued_jet_from_symbolic

s = Var("s")
path = circle_path(center=0, radius=1, turns=1, label="one loop around zero")

print("CNRS-H branch-aware local continuation demo")
print("Path:", path.summary())

log_result = continued_jet_from_symbolic(
    log(1 + s),
    s,
    center=0,
    order=5,
    path=path,
    branch_points=[BranchPoint(0, kind="log", label="log branch point")],
)
print("\nlog(1+s):")
print("  original:", log_result.original_expr)
print("  continued:", log_result.continued_expr)
print("  branch state:", log_result.continued_jet.branch_state)
print("  c0 original:", log_result.original_jet.coeff(0))
print("  c0 continued:", log_result.continued_jet.coeff(0))
print("  summary:", log_result.summary())

sqrt_result = continued_jet_from_symbolic(
    sqrt(1 + s),
    s,
    center=0,
    order=5,
    path=path,
    branch_points=[BranchPoint(0, kind="sqrt", label="sqrt branch point")],
)
print("\nsqrt(1+s):")
print("  original:", sqrt_result.original_expr)
print("  continued:", sqrt_result.continued_expr)
print("  branch state:", sqrt_result.continued_jet.branch_state)
print("  first original coeffs:", [sqrt_result.original_jet.coeff(i) for i in range(3)])
print("  first continued coeffs:", [sqrt_result.continued_jet.coeff(i) for i in range(3)])
print("  summary:", sqrt_result.summary())
