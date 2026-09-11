# CNRSProblem2 P2-L6 theorem-boundary specification

Status: **FROZEN FOR INDEPENDENT AUDIT**
Layer: **P2-L6 — Branch-Aware Finite CNRS-H State and Lossless Codec**
Freeze date: **2026-09-08**

## Purpose

P2-L6 composes the governed P2-L3 branch-index codec with the governed P2-L5
finite-Hurwitz codec. It makes branch metadata explicit and prevents operations
from silently discarding or changing it.

## Required theorem family

The candidate must provide:

- `BranchedFiniteHurwitzValue` and `BranchedFiniteHurwitzCode`;
- canonical componentwise encoding and fail-closed decoding;
- codec round-trip, encoder injectivity, validity, and exact
  `decode = some` and `isSome` characterizations;
- total raw-code interpretation for normalization only;
- raw-value-preserving, valid, idempotent normalization;
- `branchedFiniteHurwitzCodec` lossless-codec packaging;
- fail-closed `Option`-valued addition, multiplication, negation, and
  differentiation;
- binary operations succeeding only after both codes decode and their branch
  indices are equal;
- unary operations preserving the decoded branch;
- exact canonical-input success and unequal-branch rejection;
- complete successful-result and rejection characterizations; and
- exact finite-Hurwitz value and branch semantics whenever an operation
  succeeds.

## Branch policy

The branch index is explicit metadata. P2-L6 defines no cross-branch coercion.
Addition and multiplication reject unequal decoded branches. Negation and the
Hurwitz derivative preserve the decoded branch exactly.

## Dependency boundary

P2-L6 may import governed P2-L3 through P2-L5 and Mathlib. The governed P2-L5,
CnrsQ2, and CNRSCore sources remain unchanged. No dependency on
`CNRSArithmetic`, `CNRSIntegration`, or `CNRSProblem1` is permitted.

## Explicit exclusions

P2-L6 does not claim:

- analytic branch continuation or path/winding reconstruction;
- a mathematical law for combining unequal branch states;
- the full infinite Hurwitz-series ring or arbitrary stream serialization;
- efficient, digit-level, online, or finite-state Hurwitz arithmetic;
- a third coordinate or general complex-number representation;
- compatibility with CNRSArithmetic Phase D or Phase F;
- streaming division or division–multiplication duality; or
- CNRSIntegration or Scale Space dynamics.

## Acceptance gates

Audit eligibility requires exact P2-L5 authoritative baseline identity, exact
governed CnrsQ2/CNRSCore input identity, pinned Lean 4.33.0 and Mathlib 4.33.0,
three successful builds including a clean network-disabled rebuild, a compiled
frozen declaration gate, proof-marker and prohibited-dependency gates, stable
pre/post-build source bytes, and a complete exact-byte evidence artifact.

Promotion is excluded until a separate independent audit returns GREEN and the
user explicitly authorizes governed promotion.

## Freeze rule

Changing the branch-equality policy, adding cross-branch semantics, expanding
to infinite series, or introducing a prohibited project dependency requires a
documented unfreeze decision before implementation changes.
