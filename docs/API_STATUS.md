# API Status — v0.12.1

## Stable research interfaces

- finite CNRS-A representation and normalization;
- addition, subtraction, and multiplication;
- structured Gaussian-rational division and exact value reconstruction;
- `CnrsRational.evaluate()` and `partial_sum()`;
- `analyze_termination`, denominator-ideal utilities, and canonical periodic normalization;
- symbolic-prefix and beta-adic distance utilities;
- canonical coefficient codecs and finite `HybridSeries` operations.

## Research interfaces with explicit scope

- CNRS-H coefficient calculus, composition, inversion, local jets, and domain diagnostics;
- branch-aware symbolic and formal-state workflows;
- `RiemannSurface` finite-cover transport with explicitly represented sheets and monodromy;
- `AlgebraicCurve` and `finite_branch_points` for finite polynomial critical-value detection;
- ODE, scale-law, biological, oscillator, and interoperability modules.

## Gaussian-rational theorem APIs

| API | Status | Meaning |
|---|---|---|
| `analyze_termination` | theorem-backed | Reduced denominator ideal, valuations, obstruction, termination, minimal Laurent offset |
| `denominator_ideal_generator` | theorem-backed | Unit-normalized generator of the reduced principal denominator ideal |
| `CanonicalPeriodicExpansion.from_gaussian_fraction` | theorem-backed | Canonical finite/eventually-periodic Laurent expansion |
| `canonicalize_periodic` | theorem-backed | Exact value recovery followed by deterministic re-expansion |
| `primitive_period` | theorem-backed utility | Primitive block extraction after exact cycle identification |

## Topology and hybrid APIs

- `symbolic_distance`, `beta_adic_distance`, and `first_difference_isometry`: theorem-aligned finite witnesses for the natural CNRS-A ultrametric structure. The underlying Q2 completion theorem is Lean-verified; these Python utilities remain independently implemented finite witnesses.
- `CoefficientCodec` and `HybridSeries`: exact transport of finite Hurwitz-series operations through a caller-supplied canonical coefficient codec.

These APIs do not identify beta-adic convergence with ordinary complex convergence.

## Surface and algebraic-curve APIs

- `SheetPermutation`, `BranchGenerator`, `PathWord`, `SurfacePoint`, `RiemannSurface`, `SurfaceChart`, and `SurfaceAtlas`: implemented finite-cover research interfaces.
- `AlgebraicCurve`, `BranchAnalysis`, `finite_branch_points`: implemented finite-plane branch detector, exact where symbolic roots are available and numerical otherwise.

## Compatibility

The legacy module `cnrs.cnrs_division_status` remains a deprecated compatibility wrapper. New code should use `cnrs.division`.

## Open API areas

- certified arbitrary infinite-stream arithmetic;
- unrestricted analytic closure and rigorous global remainder bounds;
- automatic monodromy discovery in v0.12.1;
- singular-curve normalization, infinity analysis, Puiseux charts, and certified continuation;
- a canonical global representation API for all ordinary complex values.

See `CNRS_P4_REFERENCE_STATUS.md` for the current Problem 4 citation and theorem map.
