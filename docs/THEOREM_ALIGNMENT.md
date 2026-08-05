# CNRS Theorem-to-Implementation Alignment — v0.12.1

## Purpose

The CNRS Scientific Toolkit separates:

1. mathematical theorem;
2. constructive algorithm;
3. software implementation;
4. verification tests;
5. release and citation record.

## CNRS-A and Problem 4 alignment

| Area | Mathematical status | Principal software |
|---|---|---|
| Gaussian-integer representation | Established external CNS foundation and programme formalization | `cnrs.core`, `cnrs.cnrs_value` |
| Addition and subtraction | Closure result / derived closure | arithmetic and normalization modules |
| Multiplication | Closure theorem with constructive normalization | multiplication modules |
| Gaussian-rational eventual periodicity | Established within current model | `cnrs.cnrs_rational`, `cnrs.division` |
| Denominator-ideal termination and minimal offset | Established within current model | `cnrs.gaussian_valuation` |
| Canonical periodic normalization | Established within current model | `cnrs.canonical_periodic` |
| Natural symbolic/beta-adic completeness | Established within current model; completion is local (`Z_5`/`Q_5` topologically), not `C` | `cnrs.topology` |

## CNRS-H and hybrid alignment

| Area | Mathematical status | Principal software |
|---|---|---|
| Hurwitz-series algebra | Established within current model | `cnrs.formal_h_algebra`, `cnrs.h` |
| Shift differentiation and right-shift integration | Established within current model | CNRS-H calculus modules |
| Composition, chain rule, inversion | Formal theorem / finite-order implementation | CNRS-H compose and chain modules |
| Coefficientwise completeness | Established when the coefficient ring is complete | `cnrs.topology` |
| Hybrid CNRS-A/CNRS-H representation | Established conditionally on a canonical coefficient codec | `cnrs.hybrid` |
| Ordinary analytic convergence | Separate open analytic problem | domain/Taylor-model diagnostics only |

## Branch and surface alignment

- `cnrs.branch_algebra`: theorem-aligned lifted multiplication/logarithm algebra on the universal cover of nonzero complex values.
- `cnrs.riemann_surface`: finite global cover model with explicit monodromy supplied or constructed by the caller.
- `cnrs.algebraic_curve`: finite critical-value detector from `P=P_w=0`; not a complete compact Riemann-surface constructor.

## Open research items

The Toolkit does not claim completion of:

- the e-base CNS theorem;
- a single canonical CNRS-A representation for every ordinary complex value;
- unrestricted ordinary complex analytic convergence;
- certified global continuation and automatic compact algebraic-surface construction;
- physical interpretation or empirical necessity of CNRS states.

## Reference map

See `CNRS_P4_REFERENCE_STATUS.md` for the canonical Problem 4 Version 12 citation and the bundled theorem records. See `STATUS_VOCABULARY_MAPPING.md` for provenance and epistemic-status terminology.
