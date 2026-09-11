# P2-L3 Frozen Theorem Boundary

**Layer:** P2-L3 — Lossless Branch Serialization  
**Project:** `CNRSProblem2`  
**Frozen:** 2026-09-06

## Purpose

P2-L3 formalizes the branch-control part of the two serializations in
*Branch-Index Incorporation v8* and proves that serialization preserves the
complete P2-L2 canonical branch coordinate.

## Required results

1. The paper's zigzag equivalence `ℤ ≃ ℕ`, including the stated formulas for
   nonnegative and negative integers and both inverse laws.
2. Canonical little-endian base-4 payloads, with zero represented by `[0]`.
3. The self-delimiting branch block `payload ++ [4]`.
4. A decoder that accepts exactly canonical branch blocks.
5. Encoder validity, decoder/encoder round trip, encoder injectivity, exact
   decoder success, and uniqueness of canonical encoding.
6. An abstract lossless value codec, so this independent project can state the
   composition theorem without redefining CNRS-A.
7. Marker-delimited encode/decode round trips, parametrically over lossless
   value and integer codecs.
8. Self-delimiting encode/decode round trips for P2-L2 canonical coordinates,
   including exact recovery of the represented `BranchPoint`.

## Required endpoint examples

- branch `0` serializes as `[0, 4]`;
- branch `1` serializes as `[2, 4]`;
- branch `-1` serializes as `[1, 4]`.

## Locked interpretation

The token `4` is branch-control syntax, not a value digit. Base-4 payload
digits are stored least-significant first, matching the parser's scan from the
radix point outward.

## Explicit exclusions

P2-L3 does not prove a concrete CNRS-A digit-string codec or coverage theorem;
direct arithmetic on serialized strings; a new arithmetic alphabet; topology,
holomorphicity, or analytic continuation; inclusion of zero in the P2 branch
carrier; practical efficiency; or online/streaming arithmetic. The governed
baseline operation is decode–operate–encode.

