# Generalized Branch Objects — v0.11.2

## Purpose

The original CNRS-H continuation API aggregates path-induced branch changes by
operation type (`log_delta`, `sqrt_delta`, and `pow_delta`). That remains useful
for one-puncture expressions, but it cannot distinguish which branch point acts
on which multivalued symbolic node.

v0.11.2 adds a backward-compatible node-specific branch layer.

## Symbolic branch keys

`log`, `sqrt`, and `pow_branch` accept an optional stable `branch_key`:

```python
z = Var("z")
expr = sqrt(z, branch_key="at0") * sqrt(z - 1, branch_key="at1")
```

The key identifies a symbolic multivalued component. It is not itself a sheet
number.

## BranchObject

```python
BranchObject(
    key="at0",
    kind="sqrt",
    loci=[0],
    state=0,
)
```

A branch object carries:

- a stable symbolic key;
- a kind: `log`, `sqrt`, or `pow`;
- one or more isolated branch-locus points;
- a current branch state;
- an optional cyclic modulus;
- a descriptive label.

Defaults:

- logarithm and power states live in `Z`;
- square-root states live in `Z/2Z`.

For a path `gamma`, the update is

```text
state_new = state_old + sum(wind(gamma, locus))
```

with reduction modulo the object's modulus when present.

## BranchRegistry

A `BranchRegistry` is an immutable collection of uniquely keyed branch objects.
It computes independent path transitions and then applies the resulting states
only to symbolic nodes carrying the corresponding keys.

```python
registry = BranchRegistry([
    BranchObject("at0", "sqrt", [0]),
    BranchObject("at1", "sqrt", [1]),
])

result = continue_symbolic_with_registry(expr, path, registry)
```

The result records the original and continued expressions, both registries,
and one before/after transition per branch object.

## Multiple-locus nodes

A single node may depend on multiple branch points:

```python
whole = sqrt(z * (z - 1), branch_key="whole")
registry = BranchRegistry([
    BranchObject("whole", "sqrt", [0, 1]),
])
```

A loop around either point toggles the square-root state. A loop around both
adds two windings and returns to the original parity.

## Representation-invariance test

The extension tests matched local germs for

```text
sqrt(z(z-1))
```

and

```text
sqrt(z) sqrt(z-1)
```

along loops around 0, around 1, and around both. The continued values and local
CNRS-H jet coefficients agree within the toolkit's finite CNRS-float tolerance.

This repairs the concrete failure found in the v0.11.1 aggregate branch model,
where one square-root event was applied to every square-root node.

## CNRS-H jet rebuilding

Use:

```python
continued_jet_from_branch_registry(
    expr,
    "z",
    center=z0,
    order=8,
    path=path,
    registry=registry,
)
```

The returned jet stores a continuation note and path-history entry while its
coefficients are rebuilt from the correctly keyed continued expression.

## Backward compatibility

The following existing API remains unchanged:

- `BranchDelta`;
- `branch_delta_from_events`;
- `shift_symbolic_branches`;
- `continued_jet_from_symbolic`.

Expressions without `branch_key` continue to use the aggregate behavior.

## Current boundary

This extension supports commuting integer or finite-cyclic branch updates around
isolated points. It does **not** yet implement:

- noncommuting permutation monodromy;
- a fundamental-groupoid path-word carrier;
- automatic inference of branch loci from arbitrary symbolic expressions;
- branch cuts as geometric objects;
- global Riemann-surface construction;
- certified continuation close to singular points.

The next generalized layer should replace scalar `state` with a typed monodromy
action capable of finite permutations and, eventually, path-groupoid transport.
