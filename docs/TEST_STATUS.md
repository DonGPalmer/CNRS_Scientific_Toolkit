# Test Status — v0.14.0 candidate

Local candidate validation on 2026-09-12:

- regression suite: `1214 passed, 4 skipped, 0 failed`, 922 warnings;
- v0.14.0 acceptance suite: `19 passed`;
- source-alignment guard: PASS, six Lean projects and 79 Lean files;
- wheel and source distribution build: PASS;
- clean installation smoke tests for both distributions: PASS;
- 30-case equal-output timing/memory benchmark: PASS.

GitHub Actions run identities and independent audit identity remain pending.
The v0.13.1 release baseline follows unchanged.

# Test Status — v0.13.1 Release

## v0.13.1 release validation

`1214 passed, 4 skipped, 0 failed` on 2026-09-12. The run reported 922
warnings: retained reliable-domain diagnostics and pytest deprecation warnings.

All six Lean projects completed successfully in the matrix workflow. The
successful six-project candidate run is
[34706663684](https://github.com/DonGPalmer/CNRS_Scientific_Toolkit/actions/runs/34706663684).

The initial upload exposed two stale tests that still asserted package version
`0.13.0`; both were updated to `0.13.1` before final validation.

## Release validation

Validation run on 2026-08-04:

```text
1206 passed, 0 failed
```

The suite reports 917 retained reliable-domain warnings from selected biological, oscillator, and scale-law tests. Warnings are not silently suppressed because they identify evaluations outside estimated local reliability ranges.

## Independent Lean verification lane

The v0.13.1 release retains six projects under `formal/lean/` and a
six-project matrix in `.github/workflows/lean.yml`. Repository-level guards
verify the exact capstone checksum inventory, project identities, theorem
boundaries and proof-marker policy. GitHub Actions performs the actual
`lake build` for each project.

Merged-tree validation on 2026-08-30: `1211 passed, 0 failed`, with 917 retained warnings. The increase from 1206 to 1211 is exactly five repository-level Lean-integration guards. Lean itself was not re-run in the packaging environment; the pinned GitHub workflow performs `lake build`.

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
