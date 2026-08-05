"""Node-specific multiple-branch continuation demo."""

from cnrs.symbolic import Var, sqrt
from cnrs.cnrs_h_path import circle_path
from cnrs.generalized_branch import BranchObject, BranchRegistry, continue_symbolic_with_registry

z = Var("z")
direct = sqrt(z * (z - 1), branch_key="whole")
factorized = sqrt(z, branch_key="at0") * sqrt(z - 1, branch_key="at1")

direct_registry = BranchRegistry([
    BranchObject("whole", "sqrt", [0, 1]),
])
factor_registry = BranchRegistry([
    BranchObject("at0", "sqrt", [0]),
    BranchObject("at1", "sqrt", [1]),
])

path = circle_path(center=0, radius=0.25, turns=1, label="once around 0")

direct_result = continue_symbolic_with_registry(direct, path, direct_registry)
factor_result = continue_symbolic_with_registry(factorized, path, factor_registry)

print(direct_result.summary())
print("direct:    ", direct_result.continued_expr)
print(factor_result.summary())
print("factorized:", factor_result.continued_expr)
