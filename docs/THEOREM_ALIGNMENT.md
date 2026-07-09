# CNRS Theorem-to-Implementation Alignment

## Purpose

The CNRS Scientific Toolkit separates:

1. Mathematical theorem
2. Constructive algorithm
3. Software implementation
4. Verification tests

## CNRS-A

| Area | Mathematical status | Software |
|---|---|---|
| Addition | closure result | arithmetic module |
| Subtraction | derived closure | arithmetic module |
| Multiplication | closure theorem | multiplication module |
| Division | classified cases | division modules |

## CNRS-H

CNRS-H provides formal-series and calculus workflows.

Current implementation areas:
- differentiation
- integration
- composition
- continuation
- inversion workflows

## Open research items

The Toolkit does not claim completion of:
- metric completeness
- e-base CNS theorem
- full analytic closure
- physical interpretation of CNRS states


## Status vocabulary

See `STATUS_VOCABULARY_MAPPING.md` for the explicit mapping between Toolkit provenance labels and the five programme-level epistemic categories.


## Branch-index multiplication and logarithm algebra

Implementation: `cnrs/branch_algebra.py`. The branch-wrap cocycle restores exact lifted-argument addition and makes the lifted logarithm a group isomorphism from the universal cover of `C*` to `(C,+)`. Zero is excluded.

## Formal CNRS-H algebra

Implementation: `cnrs/formal_h_algebra.py` and the existing `CnrsH`/`CnrsHNative` classes. CNRS-H is treated as a Hurwitz-series algebra with binomial convolution and differentiation by shift. Formal identities are distinct from analytic convergence claims.


## v0.11.0 topology and hybrid additions

- Symbolic prefix space and beta-adic valuation-ring completeness: **established within current model**.
- Finite-Laurent completion as the local field at `beta=-2+i`: **established within current model**.
- Identification with ordinary complex topology: **disproved**; the topologies are incompatible.
- CNRS-H coefficientwise completeness over a complete coefficient ring: **established within current model**.
- Hybrid CNRS-A/CNRS-H differential-algebra representation theorem: **established within current model**, conditional on a canonical coefficient codec for the selected ring.
- Ordinary complex analytic convergence: separate and dependent on coefficient embedding and growth bounds.
