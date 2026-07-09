# CNRS topology and hybrid representation

## Topology separation

The Toolkit distinguishes:

1. symbolic prefix topology on CNRS-A digit strings;
2. the `beta=-2+i`-adic topology;
3. finite Laurent shifts in the local field;
4. coefficientwise topology for CNRS-H;
5. ordinary complex analytic convergence.

The first-difference metric on right-infinite digit strings is isometric to the beta-adic metric under the digit value map. The resulting completion is the valuation ring at `(beta)`, topologically `Z_5`. Allowing finite negative offsets gives the local field, topologically `Q_5`. Neither topology is the ordinary complex topology.

## Hybrid theorem

A `CoefficientCodec` supplies a canonical encode/decode bijection between a coefficient ring and its CNRS-A representations. `HybridSeries` stores those canonical coefficients in the EGF/Hurwitz basis. Addition, Hurwitz multiplication, differentiation, integration, and exponential eigenfunctions are transported through the codec.

This implements the architecture:

`CNRS-A coefficient carrier + CNRS-H analytic-order carrier`.

Formal completeness does not by itself imply ordinary complex analytic convergence.
