# CNRS Scientific Toolkit v0.15.0 architecture freeze

Status: HOLD REPAIRED; INDEPENDENT RE-AUDIT REQUIRED

Baseline: `main` commit `f0f674be654a2d9a82f8ec8b77ca732a04af218a`.
Controlling amendment: `V015_FREEZE_AMENDMENT_2026-09-14.md`.

## Release objective

v0.15.0 will add exact finite-support convolution and convolution-backed multiplication for finite Gaussian-integer coefficient sequences, including Laurent offsets.

## Components and ownership

- `cnrs.gaussian_types`: canonical `GaussianInteger`, `GaussianLike`, coercion, and reduced `GaussianRational`.
- `cnrs.finite_sequence`: immutable trimmed finite carrier and exact Laurent evaluation.
- `cnrs.convolution`: native convolution, product-count limits, and deterministic progress.
- `cnrs.convolution_witnesses`: witness/result schemas and canonical serialization only.
- `cnrs.validation.convolution_oracle`: independent verifier using its own nested-loop recomputation; it must not import `cnrs.convolution`.
- `cnrs.gaussian_normalization`: new exact carry normalization for Gaussian coefficients and Laurent offsets.
- `benchmarks/benchmark_finite_convolution.py`: comparisons through public APIs.

The legacy `cnrs.normalization` integer/string route remains unchanged for compatibility and is not authoritative for the new Gaussian/Laurent carrier.

## Dependency boundary

```text
gaussian_types <- finite_sequence <- convolution
       ^                ^              |
       |                |              v
gaussian_normalization  |     convolution_witnesses
                        |
validation.convolution_oracle (imports types/carrier only; never convolution)
benchmarks (public APIs and independent oracle)
```

Witness production may use convolution outputs. Witness verification must call the independent oracle and must not call or import the production convolution function.

## Exact normalization

For a coefficient at exponent `k`, combine it with the incoming Gaussian carry `a`; choose the unique CNRS digit `d in {0,1,2,3,4}` congruent to `a` modulo `beta=-2+i`; compute the next carry exactly as `(a-(d,0))/beta` using Gaussian divisibility. Processing begins at the sequence offset and drains carry toward increasing exponents. The result preserves the Laurent offset and exact value. No `complex`, floating-point division, or `round` is permitted.

## Invariants

1. Stored coefficients are canonical Gaussian pairs.
2. Inputs and outputs have finite support.
3. Laurent evaluation is exact in reduced Gaussian rationals.
4. Zero is `coefficients == ()`, `offset == 0`, `support is None`.
5. Required products equal the Cartesian product of stored coefficient positions, including stored internal zeros.
6. Traversal is lexicographic by left index then right index.
7. Limits bound product count only.
8. Partial work is never represented as a complete result or witness.
9. Witness verification independently recomputes decisive arithmetic.
10. Existing v0.14.1 APIs remain backward compatible.

## Non-goals

Arbitrary infinite streams, floating-point/FFT convolution, universal performance superiority, bounded coefficient bit complexity, Lean extraction, unrestricted convergence, and branch-state changes are excluded.
