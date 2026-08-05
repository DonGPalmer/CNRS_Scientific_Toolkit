# CNRS Topology and Hybrid Representation — v0.12.1

## Topology separation

The Toolkit distinguishes:

1. symbolic prefix topology on CNRS-A digit strings;
2. the `beta=-2+i`-adic topology;
3. finite Laurent shifts in the associated local field;
4. coefficientwise topology for CNRS-H;
5. ordinary complex analytic convergence.

The first-difference metric on right-infinite digit strings is isometric to the beta-adic metric under the digit value map. The resulting completion is the valuation ring at `(beta)`, topologically `Z_5`. Allowing finite negative offsets gives the local field, topologically `Q_5`. Neither topology is the ordinary complex topology.

This resolves the natural CNRS-A metric-completeness question. It does not establish that the completion is `C`, and it does not settle ordinary analytic convergence for arbitrary CNRS-H objects.

## Hybrid theorem

A `CoefficientCodec` supplies a canonical encode/decode bijection between a selected coefficient ring and its CNRS-A representations. `HybridSeries` stores those canonical coefficients in the EGF/Hurwitz basis. Addition, Hurwitz multiplication, differentiation, integration, and exponential eigenfunctions are transported through the codec.

This implements the architecture:

```text
CNRS-A coefficient carrier + CNRS-H analytic-order carrier
```

Formal coefficientwise completeness transfers when the coefficient ring is complete. Analytic function realization remains dependent on an embedding and growth/convergence conditions.

## References

See `theory/METRIC_TOPOLOGICAL_COMPLETENESS_V1.*`, `theory/HYBRID_CNRS_A_CNRS_H_REPRESENTATION_THEOREM_V1.*`, and `CNRS_P4_REFERENCE_STATUS.md`.
