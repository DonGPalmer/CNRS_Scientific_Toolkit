# CNRS Scientific Toolkit v0.15.0 architecture freeze

Status: FROZEN FOR IMPLEMENTATION

Baseline: `main` commit `f0f674be654a2d9a82f8ec8b77ca732a04af218a`.

## Release objective

v0.15.0 will add exact finite-support convolution and convolution-backed multiplication for CNRS coefficient sequences. The work joins the Toolkit's exact Gaussian-integer arithmetic, bounded execution controls, witness validation, and theorem-alignment discipline without changing the meaning of existing arithmetic APIs.

## Components

- `cnrs.finite_sequence`: immutable finite coefficient carrier, support bounds, trimming, evaluation, equality, and conversion.
- `cnrs.convolution`: exact schoolbook finite convolution and bounded/chunked iteration.
- `cnrs.convolution_witnesses`: stable witness schema and independent recomputation.
- `cnrs.normalization`: existing canonical normalization remains authoritative; the new layer delegates to it.
- `cnrs.validation`: reference Gaussian-integer and ordinary polynomial comparisons.
- `benchmarks/benchmark_finite_convolution.py`: reproducible comparison harness.

## Dependency boundary

```text
finite_sequence -> existing exact coefficient types
convolution -> finite_sequence + resource limits
convolution_witnesses -> finite_sequence + convolution
normalization adapter -> convolution + existing normalization
validation/benchmarks -> public APIs only
```

No application or validation module may become a dependency of the native convolution layer.

## Invariants

1. Inputs and outputs have finite support.
2. Coefficient arithmetic is exact; no floating-point arithmetic enters the native path.
3. Zero has one canonical empty-support representation.
4. Output support is contained in the Minkowski sum of input supports.
5. A successful result equals direct coefficient convolution.
6. Bounded operations never return a partial result as complete.
7. Witness validation recomputes decisive facts independently.
8. Existing v0.14.1 APIs and behavior remain backward compatible.
9. Streaming/chunking changes scheduling, not mathematical results.
10. Normalization is explicit and never silently changes the represented value.

## Non-goals

- arbitrary infinite-stream multiplication;
- FFT or floating-point convolution;
- asymptotic superiority claims;
- automatic proof transfer from Lean to Python;
- unrestricted analytic convergence;
- changes to branch-state semantics.

Implementation may begin only against the frozen API, claim, test, benchmark, and Lean-alignment documents. Contract changes require a dated freeze amendment.
