# CNRS Scientific Toolkit v0.15.0 implementation status

Status: AMBER evidence/acceptance repair complete; terminal CI and independent re-audit pending.

The candidate implements the approved 42-gate finite-convolution contract without changing the released `0.14.1` version metadata.

The repaired executable identity is commit
`2adf691b3ad25dd2db9a7be6d9aae92175a71db8`, tree
`8e05246d477237bd96b6d3cb51c82a1f17404e9d`. It closes the first audit's
acceptance-coverage findings. The terminal descendant may change benchmark
outputs, governance records, and the test-only import needed for GitHub runner
collection, but not runtime bytes; PR #5 supplies its terminal commit/tree
binding.

## Public API components

- `cnrs.gaussian_types`: strict `GaussianInteger`, `GaussianLike`, and canonical `GaussianRational`.
- `cnrs.finite_sequence`: immutable canonical `CNRSFiniteSequence` with exact Laurent evaluation.
- `cnrs.convolution`: exact, chunked and product-count-limited convolution plus multiplication results.
- `cnrs.gaussian_normalization`: exact canonical base-`(-2+i)` carry recurrence.
- `cnrs.convolution_witnesses`: canonical JSON, SHA-256 sequence identities, parsing and verification.
- `cnrs.validation.convolution_oracle`: independent nested-loop oracle.

## Resource boundary

`max_products` is product-count bounded only. `max_carry_steps` is post-input carry-drain-count bounded only. Neither limits coefficient bit length, Python-integer work, output allocation, elapsed time or total memory.

## Formal boundary

The implementation is independent Python. Existing Lean projects remain checksum governed and independently built. A theorem-backed v0.15.0 claim requires an exact certified theorem mapping; otherwise the release posture remains computationally validated finite exact arithmetic.

`docs/V015_LEAN_ALIGNMENT_PLAN.md` now records the exact certified restricted
mapping for zero-offset canonical digit words and explicitly excludes the
general Gaussian/Laurent Python carrier from an end-to-end Lean claim.
