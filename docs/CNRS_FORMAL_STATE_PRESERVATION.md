# CNRS* Formal State Preservation

v0.8.1 expands `CnrsFormalState` from a passive tuple into a small preservation
object for theorem-aligned workflows.

A formal state carries:

```text
(value, coefficients, branch_state, center, order, domain, status, metadata)
```

where `value` is a `CVal` and `coefficients` is a `CnrsHNative` coefficient
object.

Supported preservation operations:

- differentiation: coefficient drop;
- integration: coefficient prepend;
- addition: CVal addition plus CNRS-H coefficient addition;
- multiplication: CVal multiplication plus CNRS-H EGF product.

The preservation layer does not settle full branch-composition semantics. If
branch states differ, the operation records both branch states rather than
pretending there is a single resolved global branch.
