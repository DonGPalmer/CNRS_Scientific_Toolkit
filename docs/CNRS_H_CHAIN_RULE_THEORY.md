# CNRS-H Chain Rule Theory Note — v0.5.2

This note records the current mathematical status of the CNRS-H chain-rule layer.

## Finite local object

A `CnrsHJet` represents a finite local expansion around an explicit center `s0`:

```text
f(s) ~= sum_n d_n * (s - s0)^n / n!
```

The stored coefficients are the local derivative data `d_n = f^(n)(s0)` when the jet is built from a supported symbolic expression.

## Structural operations

Within a finite jet, the CNRS-H calculus operations are structural:

- differentiation is coefficient shift;
- integration is reverse coefficient shift with an integration constant;
- multiplication is EGF binomial convolution;
- composition is finite EGF composition of local coefficient data.

For supported jets, the finite-order chain rule is checked as:

```text
D(f o g) = (Df o g) * Dg
```

through the selected truncation order.

## Scope

This is a computational local result. It does not yet prove global analytic continuation, convergence on a full domain, or branch-cut transport. It is intended as a more explicit foundation for later convergence, branch-state, and path/winding layers.

## Next theoretical steps

1. Add radius/convergence hints for supported elementary functions.
2. Add Taylor-model-style remainder metadata.
3. Propagate branch state into jets.
4. Add path and winding tracking for continuation around singularities.
5. State an equivalence proposition connecting finite CNRS-H jets to ordinary analytic derivatives where the infinite series converges and a branch is fixed.
