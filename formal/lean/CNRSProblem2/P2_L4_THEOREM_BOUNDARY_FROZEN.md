# CNRSProblem2 P2-L4 theorem-boundary specification

Status: **FROZEN FOR AMBER AUDIT REPAIR**  
Layer: **P2-L4 — Finite-Laurent CNRS-A Value Codec**  
Freeze date: **2026-09-06**
Repair clarification date: **2026-09-07**

## Purpose

P2-L4 supplies the concrete finite-support value layer deliberately left
abstract in P2-L3. Its coefficient ring is exactly

\[
R_A=\mathbb Z[i][(-2+i)^{-1}].
\]

The implementation reuses the governed CnrsQ2 characterization of `R_A` and
the governed CNRSCore constructive Gaussian expansion. It does not duplicate
either theorem.

## Required theorem family

The candidate must provide:

- `finiteLaurentSubring` and `RAValue`;
- `FiniteLaurentCode`, exact evaluation, and membership in `R_A`;
- existence of a finite code for every `RAValue`;
- least-shift canonical encoding with a greedy canonical numerator;
- fail-closed decoding accepting exactly canonical encodings;
- both codec compositions, injectivity, validity, and normalization
  idempotence;
- the actual ring homomorphism from `RAValue` into the Gaussian fraction
  field;
- fail-closed `Option`-valued decode–operate–encode addition,
  multiplication, and negation;
- canonical-input success for all three operations;
- complete successful-result characterizations and exact evaluated results
  whenever an operation succeeds;
- rejection of addition or multiplication exactly when either input is
  noncanonical, and rejection of negation exactly when its input is
  noncanonical; and
- concrete composition of the value codec with the P2-L3 branch-index codec.

## Dependency boundary

P2-L4 may import governed `CnrsQ2`, and thereby governed `CNRSCore`, using
local path dependencies. Neither upstream project may import `CNRSProblem2`.
No dependency on `CNRSArithmetic`, `CNRSIntegration`, or `CNRSProblem1`
is permitted.

## Explicit exclusions

P2-L4 does not claim:

- an executable or efficient normalizer—the canonical choice is
  noncomputable at this boundary because the reused carrier theorem is
  existential;
- direct digit-by-digit or finite-state arithmetic on serialized strings;
- coverage of arbitrary infinite fractional streams or all complex numbers;
- a fixed-radix exponential or `e`-base representation;
- CNRS-H, divided-power differentiation, analytic convergence, or
  realization of formal Hurwitz streams;
- topology, holomorphicity, analytic continuation, complex powers, roots, or
  Scale Space dynamics.

## Acceptance gates

Audit eligibility requires exact P2-L3 baseline identity, exact governed
CnrsQ2/CNRSCore input identity, pinned Lean 4.33.0 and Mathlib 4.33.0, normal
and clean network-disabled builds, declaration and exclusion gates, no
`sorry`, `sorryAx`, `admit`, added axiom, or `unsafe`, stable
pre/post-build source bytes, and a complete evidence artifact.

Promotion is excluded until a separate independent audit returns GREEN and
the user explicitly authorizes governed promotion.
