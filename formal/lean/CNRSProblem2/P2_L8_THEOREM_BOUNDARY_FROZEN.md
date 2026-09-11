# P2-L8 theorem boundary — frozen before certification

Status: **FROZEN FOR P2-L8 CANDIDATE**

P2-L8 may add only diagonal branch transport on pairs, classification by the
relative branch invariant, its canonical first-branch-zero representative, and
a fail-closed serialized pair interface.

## Required declaration families

- `diagonalBranchShift`, with identity and composition;
- `relativeBranch`, invariant under diagonal transport;
- `BranchPairOrbit`, with reflexivity, symmetry, and transitivity;
- `branchPairOrbit_iff`, classifying an orbit by the two values and relative
  branch difference;
- `canonicalRelativePair`, with exact coordinates, orbit membership,
  idempotence, and equality classification;
- the paired encoder and fail-closed decoder, exact round trip, decoder
  characterization, and encoder injectivity;
- explicit raw-value normalization preservation via
  `BranchedFiniteHurwitzPairCode.rawValue_normalize`, and normalization
  idempotence;
- `canonicalRelativePairCode`, with exact canonical success, complete success
  and rejection characterizations, raw-value semantics, and normalization
  compatibility;
- exact identification of the equal-branch arithmetic domain with relative
  branch zero for both addition and multiplication.

## Frozen policy

P2-L8 classifies simultaneous branch transports of ordered pairs. It does not
quotient an individual branch-labelled state, discard branch metadata, define
arithmetic for unequal branches, reconstruct paths or winding histories, or
add infinite-series, streaming, integration, or Scale Space semantics.
