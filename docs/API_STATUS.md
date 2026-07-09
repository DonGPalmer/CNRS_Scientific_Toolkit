# API Status — v0.11.1

## Stable research interfaces

- finite CNRS-A representation and normalization;
- addition, subtraction, multiplication;
- structured Gaussian-rational division and exact value reconstruction;
- `CnrsRational.evaluate()` for exact represented values;
- `CnrsRational.partial_sum()` for diagnostic formal sums.

## Research interfaces

- CNRS-H coefficient calculus and native paths;
- branch-aware and formal-state workflows;
- ODE, scale-law, biological, oscillator, and interoperability modules.

## Open mathematical areas

- completeness of infinite expansions;
- e-base theorem;
- full analytic closure.

## Gaussian-rational classification note

`classify_denominator()` is numerator-aware as of v0.11.0. It uses Gaussian-integer divisibility to distinguish true finite Laurent cases from shifted-periodic cases such as `1/5`.

## Gaussian-rational theorem APIs (v0.11.0)

| API | Status | Meaning |
|---|---|---|
| `analyze_termination` | theorem-backed | Denominator ideal, valuations, residual obstruction, minimal Laurent offset |
| `denominator_ideal_generator` | theorem-backed | Unit-normalized generator of the reduced principal denominator ideal |
| `CanonicalPeriodicExpansion.from_gaussian_fraction` | theorem-backed | Canonical finite/eventually-periodic Laurent expansion |
| `canonicalize_periodic` | theorem-backed | Exact value recovery followed by deterministic re-expansion |
| `primitive_period` | theorem-backed utility | Primitive block extraction after exact cycle identification |


### Exact branch algebra
`LiftedComplex`, `branch_wrap`, and `principal_arg` are theorem-aligned APIs over nonzero complex values.

### Formal CNRS-H algebra
`hurwitz_product`, `formal_h_derivative`, `formal_h_integral`, `formal_h_inverse`, and `exponential_eigenfunction` expose exact finite coefficient identities.


## v0.11.0 topology and hybrid additions

- Symbolic prefix space and beta-adic valuation-ring completeness: **established within current model**.
- Finite-Laurent completion as the local field at `beta=-2+i`: **established within current model**.
- Identification with ordinary complex topology: **disproved**; the topologies are incompatible.
- CNRS-H coefficientwise completeness over a complete coefficient ring: **established within current model**.
- Hybrid CNRS-A/CNRS-H differential-algebra representation theorem: **established within current model**, conditional on a canonical coefficient codec for the selected ring.
- Ordinary complex analytic convergence: separate and dependent on coefficient embedding and growth bounds.

## v0.11.1 compatibility correction

The optional legacy module `cnrs.cnrs_division_status` is retained as a deprecated compatibility wrapper. Its `classify_division()` function delegates to the numerator-aware `cnrs.division.classify_denominator()` implementation. New code should use `cnrs.division` directly.
