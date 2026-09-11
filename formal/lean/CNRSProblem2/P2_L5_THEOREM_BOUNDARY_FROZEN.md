# CNRSProblem2 P2-L5 theorem-boundary specification

Status: **FROZEN FOR INDEPENDENT AUDIT**  
Layer: **P2-L5 — Finite-Support CNRS-H Algebra and Sparse Codec**  
Freeze date: **2026-09-07**

## Purpose

P2-L5 formalizes the finite-support subalgebra of Hurwitz coefficient
families over the governed P2-L4 ring

\[
R_A=\mathbb Z[i][(-2+i)^{-1}].
\]

Multiplication is binomial convolution. The outer left shift is the formal
Hurwitz derivative.

## Required theorem family

The candidate must provide:

- `FiniteHurwitz R` as natural-indexed finitely supported coefficients;
- `FiniteHurwitz.single` and exact basis multiplication;
- exact coefficient-level finite-support binomial-convolution semantics;
- a `CommRing (FiniteHurwitz R)` instance whenever `R` is a commutative ring;
- `FiniteHurwitz.deriv`, exact coefficient shifting, additivity, and the
  Leibniz rule;
- `FiniteHurwitzValue := FiniteHurwitz RAValue`;
- `FiniteHurwitzCode` and exact raw-code value semantics;
- canonical sparse encoding using ordered supported indices and canonical
  P2-L4 coefficient encodings;
- fail-closed decoding accepting exactly canonical encodings;
- encoder value recovery, injectivity, validity, normalization preservation,
  and normalization idempotence;
- the `finiteHurwitzCodec` lossless-codec packaging;
- fail-closed `Option`-valued decode–operate–encode addition,
  multiplication, negation, and differentiation;
- canonical-input success and complete successful-result characterization
  for all four operations;
- exact result value whenever an operation succeeds; and
- rejection of binary operations exactly when either operand is rejected,
  and rejection of unary operations exactly when their operand is rejected.

## Dependency boundary

P2-L5 may import the governed P2-L4 finite-Laurent value codec and Mathlib.
The governed P2-L4, CnrsQ2, and CNRSCore sources remain unchanged. No
dependency on `CNRSArithmetic`, `CNRSIntegration`, or `CNRSProblem1` is
permitted.

## Explicit exclusions

P2-L5 does not claim:

- the full infinite Hurwitz-series ring `H(R_A)` or serialization of
  arbitrary infinite streams;
- analytic convergence, analytic realization, topology, holomorphicity, or
  analytic continuation;
- division by factorials or a rational-algebra structure on `R_A`;
- efficient, executable, finite-state, or digit-by-digit convolution;
- coupling between the Hurwitz carrier and P2-L3 branch state;
- a third-coordinate construction or a general complex-number
  representation; or
- complex powers, roots, CNRSIntegration, or Scale Space dynamics.

## Acceptance gates

Audit eligibility requires exact P2-L4 authoritative baseline identity,
exact governed CnrsQ2/CNRSCore input identity, pinned Lean 4.33.0 and Mathlib
4.33.0, normal and clean network-disabled builds, a compiled frozen
declaration gate, proof-marker and prohibited-dependency gates, stable
pre/post-build source bytes, and a complete exact-byte evidence artifact.

Promotion is excluded until a separate independent audit returns GREEN and
the user explicitly authorizes governed promotion.
