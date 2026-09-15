# CNRS Scientific Toolkit v0.15.0 freeze amendment — 2026-09-14

Status: REPAIRS THE AUDITED HOLD; INDEPENDENT RE-AUDIT REQUIRED

Audited predecessor: commit `170694a675686da2c7c1cfcd4bc45c68877914d4`.

## Disposition of findings

1. The stored coefficient type is now exactly `tuple[int, int]`; public coercion from a non-Boolean `int` is specified.
2. Laurent evaluation returns a reduced exact `GaussianRational`, not a Gaussian integer.
3. v0.15.0 introduces a new exact Gaussian/Laurent normalization route. It does not delegate to the legacy integer/string normalizer.
4. Product counting, traversal, progress records, terminal states, result fields, and exceptions are fixed.
5. Witness JSON, UTF-8 byte encoding, SHA-256 digests, schema, and an implementation-independent verification module are fixed.
6. “Bounded” is narrowed to “product-count bounded”; coefficient bit length and output allocation remain unbounded unless separately limited.
7. The manifest covers every freeze document, this amendment, and the source index. Exact blob identities are recorded in a terminal binding record after content repair.
8. Acceptance gates now test every corrected contract.

## Supersession rule

Where the predecessor freeze conflicts with this amendment or the synchronized contract documents, this amendment controls. No runtime implementation is authorized until an independent re-audit returns GREEN.

## Self-reference rule

No manifest may truthfully contain its own final blob hash or the SHA of the commit that contains it. The terminal binding therefore records the repaired content blobs and predecessor commit; GitHub PR head and tree provide the terminal identity. A later audit must identify that immutable head and tree. This is an explicit evidence chain, not an omitted identity.
