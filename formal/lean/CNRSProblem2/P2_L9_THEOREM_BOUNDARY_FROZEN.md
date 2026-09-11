# P2-L9 theorem boundary — frozen before certification

Status: **FROZEN FOR P2-L9 CANDIDATE**

P2-L9 may add only the compatibility bridge between the canonical
`BranchPoint` sheet coordinate and the explicit branch metadata of the
finite CNRS-H carrier, together with exact transport, coding, normalization,
and P2-L8 relative-pair compatibility.

## Required declaration families

- `BranchPoint.branchIndex`, equal to the frozen principal-turn coordinate;
- `BranchPoint.shiftByTurns`, with radius and total-angle coordinates,
  identity, composition, canonical-angle invariance, and exact branch-index
  translation;
- `attachFiniteHurwitz`, preserving the finite-Hurwitz value and attaching
  exactly the branch point's canonical sheet, with injectivity;
- `CompatibleWithBranchPoint`, characterized by existence and uniqueness of
  an attached finite-Hurwitz value and invariant under simultaneous transport;
- `encodeAttachedFiniteHurwitz` and fail-closed
  `decodeAttachedFiniteHurwitz`, with exact round trip, complete decoder
  characterization, and encoder injectivity;
- `normalizeAttachedFiniteHurwitz`, with exact raw-value/branch semantics,
  idempotence, and compatibility with whole-turn code transport;
- `attachFiniteHurwitzPair` and
  `BranchPoint.relativeBranchIndex`, with exact agreement with P2-L8
  `relativeBranch` and invariance under simultaneous full-turn shifts; and
- exact compatibility of attached pairs with
  `canonicalRelativePair` and `canonicalRelativePairCode`.

## Frozen policy

P2-L9 relates already-governed branch-coordinate and finite-Hurwitz metadata.
It does not assert that a finite Hurwitz value determines a polar radius,
principal angle, branch point, analytic path, or winding history. It does not
introduce cross-branch arithmetic, quotient away branch metadata, add infinite
series or streams, import `CNRSArithmetic` or the separate
`CNRSIntegration` project, or introduce Scale Space semantics.
