# Test Status — v0.16.0 Release Activation

The repaired implementation candidate passed 29 dedicated v0.16 tests, five
executable acceptance tests, 61 preserved v0.15 tests, 19 preserved v0.14
tests, and the full regression suite at 1,310 passed, 4 skipped, 922 warnings.
Acceptance covered 4,490 valid strings, 425 canonical operands, 180,625
operand pairs, 5,000 randomized long round trips, 5,000 randomized
exact-value/parity products, and the 300-digit all-`4` stress case.

Exact-head push and pull-request CI passed before merge. PR #8 merged as
`b382209899e97a64249d74291ce1b3268f84c64b`, tree
`884b23bc0e775efe4330823d954ad05dca12658c`; post-merge workflow
`35275828314` passed both Python and distribution jobs. The six-project,
79-file Lean identity remained unchanged.

# Test Status — v0.15.0 Release Finalization

The independently audited implementation recorded 61 dedicated v0.15 passes,
19 unchanged v0.14 acceptance passes, 1,278 standard-suite passes with 4
optional-dependency skips and 922 warnings, and 1,282 passes with optional
pandas and 921 warnings. The 16-file candidate checksum inventory passed 16/16
and the implementation source index passed 472/472. Exact-head Python,
distribution, claim/oracle, benchmark, and seven-job Lean gates succeeded.

Release-finalization CI rebuilds and clean-installs both v0.15.0 distributions
and re-runs the complete Python and Lean lanes at the final tagged tree.

# Test Status — v0.14.1 Release

The v0.14.1 preparation tree adds three release-engineering tests and
reproducible distribution gates. Local validation passed with `1221 passed`
and 921 warnings in an optional-dependency-rich environment; the unchanged
v0.14.0 acceptance suite contributed 19 passes. Two successive builds produced
byte-identical wheel and source distributions, and both installed cleanly as
version `0.14.1`. Final public-candidate counts, workflow identities, artifact
identities, and distribution SHA-256 values were subsequently confirmed by
GitHub Actions. Python/distribution run `34770774063` and seven-job Lean run
`34770773970` succeeded at commit
`a1ac3e1273ef9492c7b4a1aaeba08f078ce1d56a`. Release-assets run
`34848995514` successfully attached and verified both distributions.
Independent post-release closeout audit remains pending. The required gates
are frozen in `V0141_ACCEPTANCE_TEST_PLAN.md`.

The v0.14.0 release baseline follows unchanged.

## v0.14.0 release validation

Release validation on 2026-09-12:

- regression suite: `1214 passed, 4 skipped, 0 failed`, 922 warnings;
- v0.14.0 acceptance suite: `19 passed`;
- source-alignment guard: PASS, six Lean projects and 79 Lean files;
- wheel and source distribution build: PASS;
- clean installation smoke tests for both distributions: PASS;
- 30-case equal-output timing/memory benchmark: PASS.

The independently audited head `cd0d590818de3f2db615f2269276ede53527827d`
is GREEN. Post-merge Python/distribution run `34734237160` and seven-job Lean
run `34734237144` are SUCCESS.
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
