# CNRS-H Branch-State Propagation

v0.6.1 moves branch-state metadata into the CNRS-H local analytic layer.

## Scope

A `CnrsHJet` now carries:

```python
branch_state: BranchState
branch_note: str
```

This records local choices used by symbolic complex functions before they are converted into finite CNRS-H coefficient jets:

- `log(..., branch=k)` updates `log_branch`;
- `sqrt(..., branch=k)` updates `sqrt_branch`;
- `pow_branch(..., ..., branch=k)` updates `pow_branch`;
- `winding` remains a scaffold for future path-dependent continuation.

The branch state is preserved by local coefficient operations including differentiation, integration, center shifting, multiplication, composition, and finite-order chain-rule verification.

## What this establishes

This release establishes local branch bookkeeping inside the CNRS-H representation.  It is no longer only a symbolic-layer annotation: the finite coefficient object itself carries the branch choices that shaped its values.

Example:

```python
from cnrs.symbolic import Var, log
from cnrs.cnrs_h_jet import jet_from_symbolic

s = Var("s")
jet = jet_from_symbolic(log(1 + s, branch=2), s, center=0, order=6)

assert jet.branch_state.log_branch == 2
print(jet.branch_summary())
```

## What this does not yet establish

This is not yet path-dependent analytic continuation.  The toolkit does not yet lift paths to Riemann surfaces, compute monodromy groups, or update branches by tracking loops around singularities.  Composition uses conservative metadata merging and reports that no path continuation was performed.

A later branch/path release should add explicit continuation paths and winding-number updates.
