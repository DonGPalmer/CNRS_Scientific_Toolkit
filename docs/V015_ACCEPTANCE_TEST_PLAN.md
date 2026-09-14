# CNRS Scientific Toolkit v0.15.0 acceptance test plan

Status: FROZEN BEFORE IMPLEMENTATION

## Carrier and exactness

| Gate | Requirement |
|---|---|
| A1 | Zero, trimming, offsets, support bounds, equality, and immutability behave canonically |
| A2 | Known examples and randomized finite cases match direct Gaussian-integer convolution exactly |
| A3 | Evaluation of convolution equals the product of evaluations for multiple exact bases |
| A4 | Empty, singleton, shifted, sparse, negative-coefficient, and cancellation cases pass |
| A5 | Output support and coefficient types satisfy the architecture invariants |

## Algebra and normalization

| Gate | Requirement |
|---|---|
| A6 | Commutativity, associativity, and distributivity pass for finite accepted cases |
| A7 | Additive and multiplicative zero/identity laws pass |
| A8 | Canonical normalization preserves exact represented value |
| A9 | Raw convolution and normalized multiplication remain separately inspectable |
| A10 | Existing multiplication parity cases remain unchanged |

## Limits, iteration, and witnesses

| Gate | Requirement |
|---|---|
| A11 | Product-count boundary tests cover below, equal to, and above the required count |
| A12 | `LIMIT_REACHED` never exposes a partial result as complete |
| A13 | Chunk size does not change terminal result or canonical witness |
| A14 | Iteration is deterministic and replayable |
| A15 | Witness serialization round-trips canonically |
| A16 | Independent validation accepts genuine witnesses and rejects every mutated decisive field |
| A17 | Invalid types, Boolean limits, negative limits, and malformed witnesses fail deterministically |

## Regression and comparison

| Gate | Requirement |
|---|---|
| A18 | Complete pre-v0.15 Python regression suite passes |
| A19 | Existing v0.14 streaming-division acceptance suite passes unchanged |
| A20 | Comparison oracle uses an independently written direct implementation |
| A21 | Benchmark harness produces machine-readable JSON and CSV with environment metadata |
| A22 | Timing reports warm-up, sample count, median, dispersion, and input family |
| A23 | Memory comparison uses one documented measurement method and does not overclaim |

## Formal alignment and release governance

| Gate | Requirement |
|---|---|
| A24 | Lean alignment names exact theorem, repository, commit, tree, toolchain, workflow, and artifact |
| A25 | Vendored Lean source identity and proof-hygiene guard pass |
| A26 | All six existing Lean projects build; any new formal project/build is separately identified |
| A27 | Claim-boundary guard rejects prohibited release language |
| A28 | Package/runtime/CFF versions synchronize only at release finalization |
| A29 | Reproducible wheel and sdist build twice identically and install cleanly |
| A30 | Independent audit certifies immutable candidate source, CI, distributions, benchmarks, and claims |

## Required test families

Use exhaustive small-support cases where feasible, fixed seeded randomized cases for wider coverage, metamorphic algebraic tests, corruption tests for witnesses, and explicit performance-regression thresholds that detect gross regressions without treating timing noise as correctness failure.

No gate may be waived silently. A waiver requires a dated record stating scope, justification, impact, and approval.
