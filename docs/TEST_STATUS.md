# Test Status — v0.12.1

## Release validation

Validation run on 2026-08-04:

```text
1206 passed, 0 failed
```

The suite reports 917 retained reliable-domain warnings from selected biological, oscillator, and scale-law tests. Warnings are not silently suppressed because they identify evaluations outside estimated local reliability ranges.

## Principal validation groups

- finite CNRS-A encoding, normalization, arithmetic, and transducer behavior;
- exact Gaussian-rational reconstruction across finite, periodic, and Laurent-periodic classes;
- numerator-aware denominator ideals, valuations, termination, and minimal Laurent offsets;
- canonical periodic normalization, idempotence, semantic equality, and serialization;
- branch-wrap algebra and formal CNRS-H identities;
- symbolic/beta-adic distance, first-difference isometry, and hybrid coefficient transport;
- finite-sheet permutation, path-word, monodromy, transport, connectivity, and atlas checks;
- algebraic-curve parsing, resultant/discriminant construction, finite branch detection, numerical fallback, unbranched cases, and repeated-component rejection;
- ODE, scale-law, biological, oscillator, and interoperability cross-validation.

## Scope of test evidence

A passing test establishes agreement between the implementation and the encoded theorem, algorithm, or reference equation over the tested domain. It does not by itself prove:

- ordinary complex analytic convergence for arbitrary infinite series;
- certified global numerical continuation;
- correctness outside documented reliable domains;
- physical or biological applicability of exploratory workflows.

## Reproduction

From the package root:

```bash
python -m pytest -q
```

See `CNRS_P4_REFERENCE_STATUS.md`, `CLAIM_STATUS.md`, and `EXAMPLE_SMOKE_STATUS.md` for the surrounding claim and workflow boundaries.
