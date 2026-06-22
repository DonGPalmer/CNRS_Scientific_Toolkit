# CNRS Scientific State (v0.7.0)

`CnrsScientificState` is the first consolidated CNRS-native science object.  It
keeps the CNRS-H local jet as the primary representation and carries the
metadata needed for scientific use:

- source symbolic expression, when available;
- expansion variable and expansion center;
- scale unit, usually `nat`;
- CNRS-H branch state;
- path history;
- local domain metadata;
- finite-order claim status;
- observation maps that keep the complex state until a reduction is explicitly requested.

The object is intended to prevent the toolkit from looking like a collection of
wrappers around standard methods.  The native spine is:

```text
CNRS-H jet + branch state + path history + domain metadata + scientific observation policy
```

## Example

```python
from cnrs.symbolic import Var, exp, log
from cnrs.cnrs_scientific_state import CnrsScientificState
from cnrs.cnrs_h_path import BranchPoint, circle_path

s = Var("s")
state = CnrsScientificState.from_symbolic(exp(0.08*s), s, center=-12, order=8)
print(state.evaluate(-12))
print(state.diff().evaluate(-12))

log_state = CnrsScientificState.from_symbolic(log(1+s), s, center=0, order=6)
path = circle_path(center=0, radius=1, turns=1)
continued = log_state.continue_along(path, branch_points=[BranchPoint(0, kind="log")])
print(continued.branch_state)
```

## Claim status

`CnrsScientificState` is still a finite local object.  It does not claim global
analytic continuation or proof-grade interval bounds.  Its purpose is to unify
the existing CNRS-native pieces into one explicit scientific representation.
