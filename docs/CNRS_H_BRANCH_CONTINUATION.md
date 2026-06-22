# CNRS-H Branch-Aware Local Continuation

v0.6.3 adds a conservative branch-aware local continuation rebuild layer.

v0.6.2 recorded path-induced branch changes as metadata on `CnrsHJet`. v0.6.3
uses the same path/winding events to shift explicit symbolic branches in
`log`, `sqrt`, and `pow_branch` expressions, then rebuilds the finite CNRS-H jet
from the continued expression.

This means branch changes can affect the local coefficients when the symbolic
source expression is available. For example, a loop around the logarithm branch
point shifts the constant term of `log(1+s)` by `2*pi*i`; a loop around a square
root branch point flips the sign of the local `sqrt(1+s)` jet.

## Example

```python
from cnrs.symbolic import Var, log
from cnrs.cnrs_h_path import BranchPoint, circle_path
from cnrs.cnrs_h_continuation import continued_jet_from_symbolic

s = Var("s")
path = circle_path(center=0, radius=1, turns=1)

result = continued_jet_from_symbolic(
    log(1+s), s, center=0, order=6, path=path,
    branch_points=[BranchPoint(0, kind="log")],
)

print(result.continued_expr)
print(result.continued_jet.branch_state)
print(result.summary())
```

## Claim status

This is still local and finite-order. It is not a full global analytic
continuation theorem and does not perform Riemann-surface lifting. It is a
CNRS-H coefficient recalculation scaffold for supported symbolic expressions
with explicit branch nodes.
