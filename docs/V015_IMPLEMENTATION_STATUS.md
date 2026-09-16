# CNRS Scientific Toolkit v0.15.0 implementation status

Status: candidate implementation complete; public CI and independent audit pending.

The candidate implements the approved 42-gate finite-convolution contract without changing the released `0.14.1` version metadata.

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
