# v0.11.2 — Generalized Node-Specific Branch Objects

v0.11.2 is a backward-compatible research extension of v0.11.1. It repairs the
multiple-branch identity loss found by the initial CNRS comparison study.

## Added

- `cnrs.generalized_branch` with:
  - `BranchObject`;
  - `BranchRegistry`;
  - `BranchTransition`;
  - `GeneralizedContinuationResult`;
  - `apply_branch_registry`;
  - `continue_symbolic_with_registry`.
- Optional `branch_key` on symbolic `Log`, `Sqrt`, and `Pow` nodes and their
  public constructors.
- `continued_jet_from_branch_registry` for node-specific CNRS-H jet rebuilding.
- Multiple-branch demonstration and eight new tests.
- Documentation in `docs/GENERALIZED_BRANCH_OBJECTS.md`.

## Corrected behavior

The v0.11.1 aggregate continuation layer applied a square-root branch delta to
every square-root node. For `sqrt(z) * sqrt(z-1)`, a loop around only `0` could
therefore flip both factors. The generalized registry binds each branch locus
to the intended node and restores agreement with `sqrt(z(z-1))` when the local
germs are matched.

## Validation

```text
1190 passed, 0 failed
```

The existing 917 warnings are unchanged reliable-domain diagnostics from other
scientific workflow tests.

## Scope boundary

The new object supports independent integer and finite-cyclic monodromy around
isolated branch points. Noncommuting permutation monodromy and full Riemann-
surface continuation remain future work.
