# CNRS-H Path and Winding Tracking

v0.6.2 adds conservative continuation-path and winding-number scaffolding to the CNRS-H branch-aware layer.

The goal is limited but important: a CNRS-H local jet can now carry not only a static branch label, but also branch-state changes induced by a supplied path in the complex plane.

## What is implemented

- `ContinuationPath`: piecewise-linear paths in the complex plane.
- `winding_number(path, point)`: integer winding around an isolated point.
- `BranchPoint`: branch-point metadata for log, sqrt, power, or all branch families.
- `update_branch_state_along_path`: conservative branch-state updates.
- `continue_log` and `continue_sqrt`: small reference evaluators showing the effect of path winding.
- `CnrsHJet.continue_along(...)`: records path-induced branch-state changes and path history on local jets.

## What is not claimed

This is not full analytic continuation. It does not lift arbitrary functions to Riemann surfaces, recompute jet coefficients after continuation, or prove global equivalence of branches. It is a local path/winding bookkeeping layer for finite CNRS-H jets.

## Example

```python
from cnrs.cnrs_h_path import BranchPoint, circle_path, winding_number
from cnrs.cnrs_h_jet import jet_from_symbolic
from cnrs.symbolic import Var, log

s = Var("s")
path = circle_path(turns=1, label="unit loop")

print(winding_number(path, 0))  # 1

jet = jet_from_symbolic(log(1+s, branch=0), s, center=0, order=6)
continued = jet.continue_along(path, branch_points=[BranchPoint(0, kind="log")])
print(continued.branch_state.log_branch)  # 1
print(continued.branch_state.winding)     # 1
```

## Status

The path layer is CNRS-native branch scaffolding. It is a step beyond static branch tags, but remains local and finite-order. A later release should connect path continuation more deeply to coefficient re-expansion and analytic domains.
