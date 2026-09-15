# CNRS Scientific Toolkit v0.15.0 architecture freeze

Status: SECOND HOLD REPAIRED; INDEPENDENT RE-AUDIT REQUIRED

Baseline: `main` commit `f0f674be654a2d9a82f8ec8b77ca732a04af218a`.
Controlling amendments: `V015_FREEZE_AMENDMENT_2026-09-14.md` and `V015_FREEZE_AMENDMENT_2026-09-15.md`; the later amendment controls conflicts.

## Release objective

v0.15.0 will add exact finite-support convolution and convolution-backed multiplication for finite Gaussian-integer coefficient sequences, including Laurent offsets.

## Components

- `cnrs.gaussian_types`: canonical Gaussian integers, public coercion, reduced Gaussian rationals.
- `cnrs.finite_sequence`: immutable trimmed carrier and exact Laurent evaluation.
- `cnrs.convolution`: exact production convolution and deterministic product-count progress.
- `cnrs.convolution_witnesses`: complete-witness schema and canonical serialization.
- `cnrs.validation.convolution_oracle`: independent nested-loop verification; never imports production convolution.
- `cnrs.gaussian_normalization`: new exact Gaussian/Laurent carry normalization.
- `benchmarks/benchmark_finite_convolution.py`: public-API comparisons.

The legacy `cnrs.normalization` integer/string route remains unchanged and is not authoritative for the new carrier.

## Exact representation rules

Stored coefficients are exact `tuple[int,int]` pairs. Laurent evaluation returns canonical reduced Gaussian rationals. For a nonzero finite sequence, construction trims boundary zeros; every trimmed low-exponent zero increments the stored offset. Therefore exact value and exponent placement are preserved before trimming, but canonical stored offset is allowed to increase.

Raw convolution is first positioned at `left.offset + right.offset`. Its coefficient array is then passed through the same canonical trimming rule.

## Exact normalization

Starting at the input offset, process every stored position in increasing exponent order using exact Gaussian carry division by `beta=(-2,1)`. After the final input position, each additional carry-drain recurrence counts as one `max_carry_steps` unit. Input-position processing is not counted by that limit. Output boundary zeros are trimmed canonically, so output offset may increase. Exact value is invariant; no floating-point arithmetic or rounding is permitted.

## State and independence

Nonterminal progress uses `IN_PROGRESS`; terminal states are `COMPLETE` and `LIMIT_REACHED`. Only a complete terminal exposes a result. Witnesses exist only for complete multiplication. The independent verifier imports scalar/carrier/normalization primitives as specified but may not import or call production convolution.

## Resource boundary

Limits bound stored-position product count, and normalization has a separate post-input carry-drain count. Neither bounds coefficient bit length, Python-integer work, output allocation, elapsed time, or total memory.

## Compatibility and non-goals

Existing v0.14.1 signatures remain unchanged. Arbitrary infinite streams, approximate/FFT convolution, universal performance claims, bounded total resources, Lean extraction, unrestricted analytic convergence, and branch-state changes are excluded.
