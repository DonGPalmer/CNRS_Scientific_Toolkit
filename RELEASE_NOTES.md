# CNRS Scientific Toolkit Release Notes

This is the consolidated, reverse-chronological record of notable Toolkit
changes. The version-specific `RELEASE_NOTES_vX.Y.Z.md` files are retained
unchanged as historical release artifacts, while this file is the current
reader-facing release history.

For future releases, add the complete release record directly here. Create a
separate version-specific release-note file only when a governed release
procedure explicitly requires one.

## Contents

- [v0.17.0](#v0-17-0)
- [v0.16.0](#v0-16-0)
- [v0.15.0](#v0-15-0)
- [v0.14.1](#v0-14-1)
- [v0.14.0](#v0-14-0)
- [v0.13.1](#v0-13-1)
- [v0.13.0](#v0-13-0)
- [Post-v0.12.1 Q2 integration](#post-v0-12-1-q2-integration)
- [v0.12.1](#v0-12-1)
- [v0.12.0](#v0-12-0)
- [v0.11.2](#v0-11-2)
- [v0.11.1](#v0-11-1)
- [v0.11.0](#v0-11-0)

<a id="v0-17-0"></a>

## CNRS Scientific Toolkit v0.17.0

### Exact CNRS-A string division

Version 0.17.0 connects finite CNRS-A strings to the exact streaming-division
engine released in v0.14.0. The public exact API returns a structured result
that explicitly distinguishes terminating, eventually-periodic, and
limit-reached outcomes.

#### Added

- `divide_cnrs_exact` for exact division of two finite CNRS-A strings;
- `ExactDivisionResult` and `DivisionStreamStatus` outcomes for terminating,
  eventually-periodic, and limit-reached computations;
- exact Gaussian-rational value reconstruction for resolved results;
- deterministic division witnesses and independent witness revalidation;
- strict finite-string parsing and zero-divisor rejection;
- explicit counted-step limits whose exhaustion returns `LIMIT_REACHED`;
- static route, dependency, and legacy-complex-arithmetic isolation guards;
- clean wheel and source-distribution exact-division smoke tests.

#### Compatibility

The historical `div_cnrs(a, b) -> str` API remains available for compatibility
and emits `DeprecationWarning` on call. It retains legacy Python-complex
behavior and is not part of the v0.17 exactness claim. Existing v0.16 exact
multiplication, v0.15 finite convolution, v0.14 streaming division, and earlier
compatible APIs remain unchanged.

#### Outcome semantics

- `TERMINATING` identifies a finite exact quotient.
- `EVENTUALLY_PERIODIC` identifies an exact quotient represented by a
  deterministic preperiod and primitive cycle.
- `LIMIT_REACHED` is a reproducible operational outcome. It is not evidence
  that the quotient is aperiodic and does not expose a resolved witness.

The step limit bounds counted streaming recurrence steps only. It does not
bound wall-clock time, total memory, integer bit length, input or output size,
or witness-serialization cost.

#### Claim boundary

Production exact division uses integer, Gaussian-integer, and rational-pair
arithmetic. Validation oracles are not production dependencies. The release
makes no universal elapsed-time, whole-memory, integer-bit-length,
arbitrary-infinite-stream, unrestricted analytic, or end-to-end Lean-
verification claim.

#### Validation

- dedicated v0.17 tests: 65 passed;
- executable v0.17 acceptance: 6 passed;
- preserved v0.16 tests: 29 passed;
- preserved v0.16 acceptance: 5 passed;
- preserved v0.15 tests: 61 passed;
- preserved v0.14 acceptance: 19 passed;
- full regression: 1,378 passed, 4 skipped, 922 warnings;
- exact-head push and pull-request CI: SUCCESS;
- post-merge Python/distribution CI: SUCCESS;
- six-project, 79-file Lean identity: unchanged;
- independent implementation audit and two-file repair delta audit: PASS.

The audited implementation head was
`7840b51db1b7a3b9955aa20bd2b67fb99344335f`, tree
`924b8af717e17183e8bf9375adcb9fb35ca4093f`. PR #10 merged it normally as
`9965eb3bb2a1389469a4a99b90a03f6671fe76c8` with the identical tree.

#### Publication closeout

GitHub release v0.17.0 was published on 2026-09-19 from release commit
`3125503d49c7956103f68ad6aa8edb1e808537f3`. The Zenodo version DOI is
`10.5281/zenodo.22846854`; the Toolkit concept DOI remains
`10.5281/zenodo.20574852`.

---

<a id="v0-16-0"></a>

## CNRS Scientific Toolkit v0.16.0

### Exact CNRS-A string multiplication

Version 0.16.0 connects finite CNRS-A strings to the exact Gaussian/Laurent
carrier released in v0.15.0 and routes public string multiplication through
that exact arithmetic spine.

#### Added

- exact parsing from the frozen finite CNRS-A grammar into
  `CNRSFiniteSequence`;
- canonical formatting from digit-valued finite carriers back to CNRS-A text;
- public exports `cnrs_string_to_finite_sequence` and
  `finite_sequence_to_cnrs_string`;
- exact `mul_cnrs` routing through `convolve_exact` and
  `normalize_gaussian_laurent`;
- independent rational-pair and historical-parity validation oracles;
- static route and anti-regression guards, including division and duplicate
  arithmetic-loop rejection;
- clean wheel and source-distribution bridge/fractional-product smoke tests.

#### Compatibility

The public `mul_cnrs(a, b) -> str` signature is unchanged. Existing valid
finite-input outputs, v0.15.0 convolution and witness interfaces, v0.14.0
streaming-division contracts, and earlier compatible APIs remain unchanged.

#### Claim boundary

Production parsing, convolution, carry normalization, and formatting use
integer or Gaussian-integer arithmetic. Validation oracles are not production
dependencies. The release makes no universal elapsed-time, whole-memory,
integer-bit-length, arbitrary-infinite-stream, unrestricted analytic, or
end-to-end Lean-verification claim.

#### Validation

- dedicated v0.16 tests: 29 passed;
- executable v0.16 acceptance: 5 passed;
- exhaustive valid strings: 4,490;
- canonical operands: 425;
- exhaustive operand pairs: 180,625;
- randomized long round trips: 5,000;
- randomized exact-value/parity products: 5,000;
- 300-digit all-`4` stress: exact parity and value PASS;
- preserved v0.15 tests: 61 passed;
- preserved v0.14 acceptance: 19 passed;
- full regression: 1,310 passed, 4 skipped, 922 warnings;
- exact-head push and pull-request CI: SUCCESS;
- six-project, 79-file Lean identity: unchanged;
- independent audit: PASS after additive administrative reconciliation.

The audited implementation head was
`ba1f5eda0e359f10926587ced89e6dececb5e87d`, tree
`884b23bc0e775efe4330823d954ad05dca12658c`. PR #8 merged it normally as
`b382209899e97a64249d74291ce1b3268f84c64b` with the identical tree.

The Toolkit concept DOI remains `10.5281/zenodo.20574852`. The v0.16.0
version DOI will be recorded after separately authorized GitHub release
publication and Zenodo processing.

---

<a id="v0-15-0"></a>

## CNRS Scientific Toolkit v0.15.0

### Exact finite convolution and canonical witnesses

Version 0.15.0 implements the independently audited 42-gate finite-convolution
contract for exact Gaussian-coefficient Laurent sequences.

#### Added

- strict Gaussian-integer coercion and canonical Gaussian-rational values;
- immutable finite Laurent sequences with exact evaluation;
- deterministic raw and chunked finite convolution;
- product-count limit states and deterministic progress records;
- exact canonical base-`(-2+i)` normalization;
- canonical JSON convolution witnesses with SHA-256 identities;
- independent nested-loop convolution and witness verification;
- equality-gated timing and peak-memory benchmark evidence;
- public exports, acceptance tests, claim guards, and CI integration.

#### Compatibility

Existing v0.14 streaming-division and witness interfaces remain unchanged. No
existing public arithmetic signature was removed or modified.

#### Claim boundary

The release covers exact finite arithmetic over the frozen carrier.
`max_products` bounds the counted coefficient products only.
`max_carry_steps` bounds post-input carry-drain steps only. These controls do
not bound coefficient bit length, Python-integer work, total allocation,
elapsed time, or total memory. No universal performance superiority,
arbitrary-infinite-stream multiplication, unrestricted analytic convergence,
or end-to-end Lean verification of the Python runtime is claimed.

#### Validation

- dedicated v0.15 contract suite: 61 passed;
- unchanged v0.14 acceptance suite: 19 passed;
- standard full suite: 1,278 passed, 4 skipped, 922 warnings;
- full suite with optional pandas: 1,282 passed, 921 warnings;
- candidate checksum inventory: 16/16 PASS;
- implementation source index: 472/472 exact;
- exact-head Python/distribution runs: SUCCESS;
- exact-head Lean source identity plus six project builds: 7/7 SUCCESS;
- independent audit: PASS after one PR-body-only administrative correction.

The audited implementation head was
`0740c1e8ace7af98ac3ed4c76d6ba74610bada56`, tree
`88a545bbf359e2e5fe2b0d29111b915e08963e08`. PR #5 merged it normally as
`fa93a8307905961808321e19d7020dc7806e4e5f` with the identical tree.

The published v0.15.0 Zenodo version DOI is
`10.5281/zenodo.22812232`. The Toolkit concept DOI remains
`10.5281/zenodo.20574852`.

---

<a id="v0-14-1"></a>

## CNRS Scientific Toolkit v0.14.1 — Release Governance and Reproducible Packaging

**Status:** published; GitHub and Zenodo release complete
**Release date:** 2026-09-14

CNRS means **Complex Numeric Representation System**.

### Purpose

Version 0.14.1 is a release-engineering and governance maintenance update. It
does not change the exact Gaussian-rational streaming-division algorithm,
division witnesses, public Python APIs, vendored Lean sources, or mathematical
claim boundaries released in v0.14.0.

### Changes

- Closes the v0.14.0 release record and removes stale candidate/publication
  language.
- Records the prior v0.14.0 Zenodo version DOI `10.5281/zenodo.22731846`, the
  v0.14.1 version DOI `10.5281/zenodo.22750622`, and concept DOI
  `10.5281/zenodo.20574852`.
- Derives `SOURCE_DATE_EPOCH` from the checked-out Git commit.
- Builds the wheel and source distribution twice in isolated directories and
  requires byte-identical outputs.
- Produces a SHA-256 inventory and records the exact commit and tree.
- Updates GitHub artifact upload from `actions/upload-artifact@v4` to the
  Node-24-compatible `actions/upload-artifact@v7`.
- Adds an exact-tag release workflow that validates `v0.14.1`, builds the
  distributions reproducibly, attaches both files to the GitHub Release, and
  verifies their presence through the GitHub API.

### Required validation

- complete Python regression suite;
- unchanged v0.14.0 acceptance suite;
- reproducible double-build comparison;
- clean installation from the wheel and source distribution;
- Lean source-identity gate and all six project builds;
- release-guard tests;
- independent audit of the immutable candidate and retained distributions.

### Publication identity

- tag and commit: `v0.14.1` at
  `a1ac3e1273ef9492c7b4a1aaeba08f078ce1d56a`;
- Git tree: `b7b258537aacbbf0ef8bac807c4f8fcd68d7ca38`;
- Python/distribution workflow: `34770774063` — SUCCESS;
- Lean workflow: `34770773970` — seven jobs SUCCESS;
- retained candidate artifact: `10321763058`;
- release-assets workflow: `34848995514` — SUCCESS;
- wheel SHA-256:
  `159db0051472f9b1c09f38786ea40b274661b674ac00de71ebcb61f140f1c377`;
- source-distribution SHA-256:
  `f5ca8b7f5b1849787a9c3cd8b4a6b3136d1196c70bfeaf1a936a641f2f67f520`;
- Zenodo version DOI: `10.5281/zenodo.22750622`;
- Zenodo concept DOI: `10.5281/zenodo.20574852`.

Independent post-release closeout audit remains pending.

### Claim boundary

No new arithmetic, convergence, physical, biological, or formal-verification
claim is introduced. Python remains independently implemented and
theorem-aligned, not Lean-extracted or end-to-end formally verified.

---

<a id="v0-14-0"></a>

## v0.14.0 — Streaming Division and Formal–Runtime Witness Alignment

**Status:** governed merge complete; post-merge CI GREEN; tag and publication pending
**Release date:** 2026-09-12
**Architecture freeze:** 2026-09-12
**Baseline:** v0.13.1, commit `e7f8424a967292a36643bb5fa8206ccb1d3f8fcd`

### Purpose

v0.14.0 is the first Toolkit release with lazy, replayable division
streams for exact Gaussian-rational values. It also introduces explicit bounded
resolution records and deterministic witnesses connecting runtime recurrence
states to the established canonical eventually-periodic representation.

### Implemented additions

- `cnrs.streaming_division` for lazy digit generation and bounded resolution;
- `cnrs.witnesses` for versioned JSON-safe witness creation and validation;
- `DivisionStreamStatus` values `TERMINATING`,
  `EVENTUALLY_PERIODIC`, and `LIMIT_REACHED`;
- exact parity with `CanonicalPeriodicExpansion`;
- acceptance coverage for input discipline, replay, digit bounds, termination,
  periodicity, Gaussian denominators, normalization, search limits, witness
  tamper detection, determinism, and at least 100 parity cases;
- a reproducible benchmark comparing prefix latency, full resolution, witness
  overhead, and peak memory with traditional processing.

### Compatibility

The existing `cnrs.division`, `CnrsRational`, `expand_division`, and
`canonical_expansion` interfaces remain supported. v0.14.0 must not alter
their signatures or reinterpret existing result classes.

### Claim boundary

The intended claim is exact Gaussian-rational streaming division. This does not
establish arbitrary-real or arbitrary-complex stream arithmetic, unrestricted
infinite-stream field closure, streaming multiplication, analytic convergence,
or a universal cycle-discovery bound.

Lean verifies the mathematical statements encoded in the governed formal
projects. The Python implementation is independently written and must be
described as theorem-aligned and computationally tested, not Lean-extracted or
formally verified.

### Release validation

- historical Python regression suite: `1214 passed, 4 skipped, 0 failed`,
  with 922 retained warnings;
- dedicated v0.14.0 acceptance suite: `19 passed`;
- Lean source-alignment and proof-hygiene guard: PASS, six projects and exactly
  79 Lean files;
- wheel and source distribution builds: PASS;
- clean wheel and source installation smoke tests: PASS;
- equal-output benchmark: PASS over 30 deterministic cases.

Initial local distribution candidates:

| Artifact | Size | SHA-256 |
|---|---:|---|
| `cnrs-0.14.0-py3-none-any.whl` | 255,333 bytes | `6de8e4c4b2a4e19d8a0d01186e99ef87f6846602b538671d50a2bb9c9a9d3b92` |
| `cnrs-0.14.0.tar.gz` | 324,857 bytes | `4a527835e2eaee89ca90274bbb6b97db2ebb24359858ac9fb7b24569d6bf6d7c` |

These artifacts are local candidate builds. Release assets must be rebuilt or
identity-checked from the audited public candidate before publication.

Exact-head GitHub Actions build evidence for commit
`b4382510d724bf92bc26aedb4fb52da31b627af3` is retained as artifact
`10309848481` (90-day retention; archive digest
`sha256:dff8c3306e2350ddbd7f40cfa7262616c07c8e08cfe99a58510ed3b0fccf238c`).
Its independently downloadable contents are:

| Artifact | Size | SHA-256 |
|---|---:|---|
| `cnrs-0.14.0-py3-none-any.whl` | 255,333 bytes | `f7bf8d4862e401c93437658f8a279a1340ea126e4aa707fbffb8a645fd259fde` |
| `cnrs-0.14.0.tar.gz` | 324,753 bytes | `bee726e4c05db1f1c05e864a254170a54aa6fecf199fe990e627488d4f64dd29` |

The artifact also contains `CANDIDATE_COMMIT.txt`, `CANDIDATE_TREE.txt`, and
`SHA256SUMS.txt`; they bind the files to the stated commit and tree.

The local benchmark found lower median time ratios for 1- and 10-digit prefixes
(0.645 and 0.936), higher ratios for 100 and 1,000 digits (3.073 and 10.736),
and a full-resolution median ratio of 0.973. Median peak-memory ratios fall to
0.721 at 1,000 digits. These are measurements from the recorded environment,
not universal performance guarantees. See `docs/V014_PERFORMANCE_RESULTS.md`.

### Governance and publication status

- independently audited candidate `cd0d590818de3f2db615f2269276ede53527827d`: GREEN;
- governed merge commit `511526fdd60cfa2967d0307fe16ba4131785c0b3`;
- post-merge Python/distribution run `34734237160`: SUCCESS;
- post-merge seven-job Lean run `34734237144`: SUCCESS;
- tag, GitHub Release, release-asset publication, and Zenodo verification pending.

The release uses the Toolkit concept DOI `10.5281/zenodo.20574852`. The Zenodo
version DOI will be recorded after publication.

---

<a id="v0-13-1"></a>

## v0.13.1 — Public Lean Release and Provenance Synchronization

**Status:** released
**Date:** 2026-09-12

v0.13.1 is a documentation and provenance patch. It connects the six-project
CNRS-LEAN-CAPSTONE snapshot vendored in Toolkit v0.13.0 with its governed
public publication as CNRS Lean v1.0.3.

### Public CNRS Lean identity

- repository: \`DonGPalmer/CNRS_Lean\`;
- release/tag: \`v1.0.3\`;
- commit: \`ce56a7359f494d29bab8e9bea6c3ea596f8fd62f\`;
- Zenodo version DOI: \`10.5281/zenodo.22727725\`;
- Zenodo concept DOI: \`10.5281/zenodo.22726349\`;
- formal inventory: six projects and 79 Lean source files;
- toolchain: Lean 4.33.0.

### Certification provenance retained

The authoritative source certification remains the private
CNRS-LEAN-CAPSTONE record:

- repository: \`DonGPalmer/SSC_Formal_Methods_CI\`;
- branch: \`cnrs-lean-consolidated-release-candidate\`;
- commit: \`07e776b4e1d7d09513394a4b676516eb51e4c597\`;
- tree: \`fd61bac37369f8e3020d70141c565a4fba414a98\`;
- workflow run/job: \`34534566879\` / \`103063055916\`;
- artifact: \`10175389923\`;
- artifact SHA-256:
  \`840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21\`.

The public repository provides the governed publication of this certified
formal package; it does not replace the private certification authority.

### Terminology correction

The programme name is standardized as **Complex Numeric Representation System
(CNRS)**. The former wording “Complex Numeric Representational System” was not
the authoritative expansion.

### Runtime and theorem impact

No Python arithmetic behavior, scientific workflow behavior, vendored Lean
source, or mathematical claim is changed. The Python Toolkit remains an
independently implemented, theorem-aligned computational layer; it is not
Lean-extracted or end-to-end formally verified by the included Lean projects.

### Validation

Final Python counts, GitHub Actions run identities, distribution checksums,
release commit, and the v0.13.1 Zenodo version DOI are intentionally pending
until the exact candidate has passed independent verification.

Required gates include the full Python suite, all six Lean matrix builds,
\`python tools/check_lean_alignment.py\`, version synchronization, JSON/CFF
validation, exact 79-file Lean inventory, source-index verification,
distribution builds, and an installed-wheel smoke test.

---

<a id="v0-13-0"></a>

## v0.13.0 — CNRS Lean Capstone Alignment

**Status:** release candidate preparation
**Date:** 2026-09-11

v0.13.0 vendors the exact CNRS-LEAN-CAPSTONE source snapshot and synchronizes
the Toolkit's theorem inventory, provenance, claim crosswalk and independent
Lean CI with the closed six-project formal-methods campaign.

### Added

- all six certified Lean projects under `formal/lean/`;
- capstone checksum inventory, audit and final verdict;
- machine-readable consolidated identity in `formal/PROVENANCE.json`;
- six-project matrix build in the independent Lean workflow;
- repository guards for exact source identity and proof hygiene;
- P2-L9 branch-point attachment and P2-L10 finite-antiderivative crosswalks.

### Certified upstream identity

Commit `07e776b4e1d7d09513394a4b676516eb51e4c597`, tree
`fd61bac37369f8e3020d70141c565a4fba414a98`, run `34534566879`, job
`103063055916`, artifact `10175389923`, SHA-256
`840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21`.

The upstream certification records 79 Lean files, 14,341 lines, six normal and
six clean network-disabled builds, byte-stable source and clean proof-hygiene
gates. The certified build counts are CNRSCore 3,015; CnrsQ2 3,037;
CNRSArithmetic 3,043; CNRSIntegration 3,046; CNRSProblem1 8,723; and
CNRSProblem2 3,052 jobs, totaling 23,916 across the six-project pass.

### Runtime impact

No Python arithmetic behavior is changed solely by this synchronization.
Python remains independently implemented and theorem-aligned, not
Lean-extracted.

Candidate Python validation: `1214 passed, 4 skipped, 0 failed`. The 922
warnings comprise retained reliable-domain diagnostics and pytest deprecation
warnings.

### Scope boundary

This release does not enlarge finite results to infinite series, analytic
continuation, path reconstruction, unequal branches, unrestricted streaming
arithmetic, or all complex numbers.

---

<a id="post-v0-12-1-q2-integration"></a>

## Historical post-v0.12.1 Q2 integration

- Added the governed CNRS Q2 Lean 4 project under `formal/lean/CnrsQ2/`, pinned to Lean 4 v4.33.0 and Mathlib v4.33.0.
- Added an independent `.github/workflows/lean.yml` build lane; Lean results remain separate from the v0.12.1 Python release baseline.
- Added `docs/LEAN_FORMALIZATION_ALIGNMENT.md` with the theorem-to-software crosswalk and explicit refinement boundary.
- Extended `cnrs.theorem_alignment.TheoremRecord` with optional formal-proof metadata and registered the Q2 beta-adic completion and unique digit-expansion theorems.
- Added repository guards for governed Lean source identity, theorem names, and formal metadata.
- No Python arithmetic algorithm was changed by this integration.
- Post-integration Python validation: `1211 passed, 0 failed`, with 917 retained reliable-domain warnings. The actual Lean `lake build` is assigned to the independent GitHub Actions lane; the governed Lean manifest records the previously clean-built unchanged proof code.

---

<a id="v0-12-1"></a>

## CNRS Scientific Toolkit v0.12.1

**Release date:** 2026-08-04 documentation-synchronized rebuild
**Theme:** Algebraic-curve intake, finite branch-point detection, and Problem 4 record synchronization.

### Added: algebraic-curve branch detection

- `cnrs.algebraic_curve.AlgebraicCurve` for accepting and validating polynomial relations `P(z,w)=0`.
- Exact construction of `P_w`, the resultant `Res_w(P,P_w)`, and the polynomial discriminant where available.
- Detection of candidate finite branch values from resultant roots.
- Recovery of ramification points satisfying `P=0` and `P_w=0` over each candidate value.
- Exact root handling when SymPy supplies complete roots, with explicit numerical fallback using `nroots`.
- Ramification multiplicity, exact/numerical status, residual, and warning metadata.
- Convenience functions `algebraic_curve(...)` and `finite_branch_points(...)`.
- Seven focused tests covering exact, numerical, unbranched, and repeated-component cases.

Install the optional algebraic dependency with:

```bash
pip install cnrs[algebraic]
```

### Problem 4 documentation synchronization

The full package now identifies the canonical Problem 4 record:

> Donald G. Palmer, *Partial Operational Completeness of a Positional Number System for Complex Numbers*, Version 12, Zenodo, 2026. DOI: `10.5281/zenodo.21791909`.

Updated current-status files:

- `README.md`
- `CITATION.cff`
- `RELEASE_NOTES.md`
- `docs/CLAIM_STATUS.md`
- `docs/THEOREM_ALIGNMENT.md`
- `docs/API_STATUS.md`
- `docs/TEST_STATUS.md`
- `docs/GAUSSIAN_RATIONAL_THEOREMS.md`
- `docs/CNRS_TOPOLOGY_AND_HYBRID.md`
- `docs/RESEARCH_STATUS.md`
- `docs/CNRS_P4_REFERENCE_STATUS.md` (new)

The documentation now distinguishes the resolved natural beta-adic completeness result from the separate open question of ordinary complex analytic convergence.

### Validation

```text
1206 passed, 0 failed
```

The suite reports 917 retained reliable-domain warnings from pre-existing scientific-workflow tests.

### Scope boundary

The algebraic-curve detector computes finite critical values of the projection `(z,w) -> z`. It does not yet:

- analyze branch behavior at infinity;
- normalize singular or reducible curves;
- infer monodromy permutations automatically;
- build Puiseux charts;
- certify numerical roots or continuation paths.

The bundled P4 records establish results only in their explicitly stated algebraic, beta-adic, coefficientwise, or formal domains. They do not identify the beta-adic completion with the ordinary complex plane and do not prove unrestricted analytic convergence of all CNRS-H series.

---

<a id="v0-12-0"></a>

## CNRS Scientific Toolkit v0.12.0

### Finite global Riemann-surface layer

This release adds `cnrs.riemann_surface`, an explicit finite-sheet branched-cover model with:

- finite sheet permutations;
- branch-locus loop generators;
- reduced ordered path words;
- noncommuting monodromy;
- lifted surface points and audited transport steps;
- connected-sheet orbit checks;
- local chart evaluators and overlap validation;
- cyclic root-surface constructors.

The earlier generalized node-specific branch registry remains supported. The new layer addresses cases where winding totals are insufficient because loop order matters.

### Validation

Nine new tests cover permutation algebra, path reduction, square- and cubic-root sheet transport, inverse words, noncommuting monodromy, atlas overlap checks, convenience construction, and invalid-data rejection.

### Boundaries

This is a finite monodromy and atlas scaffold. It does not automatically infer algebraic branch points, Puiseux expansions, monodromy, genus, compactification, or certified geometric path words.

---

<a id="v0-11-2"></a>

## v0.11.2 — Generalized Node-Specific Branch Objects

v0.11.2 is a backward-compatible research extension of v0.11.1. It repairs the
multiple-branch identity loss found by the initial CNRS comparison study.

### Added

- `cnrs.generalized_branch` with:
  - `BranchObject`;
  - `BranchRegistry`;
  - `BranchTransition`;
  - `GeneralizedContinuationResult`;
  - `apply_branch_registry`;
  - `continue_symbolic_with_registry`.
- Optional `branch_key` on symbolic `Log`, `Sqrt`, and `Pow` nodes and their
  public constructors.
- `continued_jet_from_branch_registry` for node-specific CNRS-H jet rebuilding.
- Multiple-branch demonstration and eight new tests.
- Documentation in `docs/GENERALIZED_BRANCH_OBJECTS.md`.

### Corrected behavior

The v0.11.1 aggregate continuation layer applied a square-root branch delta to
every square-root node. For `sqrt(z) * sqrt(z-1)`, a loop around only `0` could
therefore flip both factors. The generalized registry binds each branch locus
to the intended node and restores agreement with `sqrt(z(z-1))` when the local
germs are matched.

### Validation

```text
1190 passed, 0 failed
```

The existing 917 warnings are unchanged reliable-domain diagnostics from other
scientific workflow tests.

### Scope boundary

The new object supports independent integer and finite-cyclic monodromy around
isolated branch points. Noncommuting permutation monodromy and full Riemann-
surface continuation remain future work.

---

<a id="v0-11-1"></a>

## v0.11.1 — Division Classification Consistency Patch

v0.11.1 is a corrective patch to the v0.11.0 rational-expansion release. It aligns the retained v0.8.x compatibility classifier with the theorem-aligned public division API and adds cross-API regression protection.

### Fixed

- Added a corrected, deprecated compatibility module at `cnrs.cnrs_division_status`.
- Made `classify_division()` numerator-aware by delegating to `cnrs.division.classify_denominator()`.
- Ensured powers of five are not treated as automatically terminating.
- Added regression tests for `1/5`, `1/25`, `conjugate(beta)/5`, and `conjugate(beta)^2/25`.
- Added cross-API consistency tests covering Gaussian-integer, terminating, periodic, shifted-periodic, negative-denominator, and equivalent-fraction cases.
- Clarified that a finite Laurent offset does not by itself imply a terminating expansion.

### Mathematical correction retained

For `beta = -2+i`,

```text
5 = beta * conjugate(beta).
```

A reduced denominator `5**s` produces a terminating Laurent expansion only when the reduced numerator cancels `conjugate(beta)**s`. Therefore:

- `1/5` is shifted eventually periodic;
- `1/25` is shifted eventually periodic;
- `conjugate(beta)/5 = 1/beta` terminates;
- `conjugate(beta)**2/25 = 1/beta**2` terminates.

### Compatibility

`cnrs.cnrs_division_status` is retained only for compatibility and emits `DeprecationWarning`. New code should use:

```python
from cnrs.division import classify_denominator
```

### Validation

Final validation: `1182 passed`, `0 failed`. Build and distribution metadata checks completed successfully.

---

<a id="v0-11-0"></a>

## v0.11.0 — Rational Expansion and Scientific Workflow Validation

**Release date:** 2026-07-08

This release advances the Toolkit from the v0.10.x verification line to a substantive validation release. It introduces no claim of full CNRS completeness.

### Division and rational expansion

- Corrected `CnrsRational.evaluate()` so its default returns the exact represented value for finite, periodic, and Laurent-periodic classes.
- Added `CnrsRational.partial_sum(n_digits)` for diagnostic finite formal sums that respect `power_offset`.
- Removed six expected-failure markers associated with the former Laurent-periodic evaluation limitation.
- Added randomized exact reconstruction tests using `fractions.Fraction`.
- Added reduced-denominator classification checks, equivalent-fraction invariance, sampled period-minimality checks, long-period validation, and invalid-input tests.
- Integrated the Gaussian-rational eventual-periodicity theorem for base `z0=-2+i`.
- Corrected integer-denominator classification using Gaussian factorization: `5=z0*conjugate(z0)`. In particular, `1/5` is shifted-periodic, not terminating; a denominator `5**s` terminates only when the numerator cancels `conjugate(z0)**s`.
- Added `docs/theory/GAUSSIAN_RATIONAL_PERIODICITY_THEOREM_V1.md` and theorem-specific regression tests.

### Scientific workflow audit

- Cross-validated first- and second-order CNRS-H ODE solutions against closed forms.
- Cross-validated exponential scale laws.
- Rechecked biological diffusion profiles, steady state, Jacobian, and Turing prerequisites.
- Cross-validated linear complex oscillator behavior.
- Compared the interoperability workflow with closed-form and SciPy reference solutions.
- Added `docs/audits/SCIENTIFIC_WORKFLOW_AUDIT_V011.md`.

### Validation

- `1167 passed`
- `0 xfailed`
- `0 unexpected failures`

Warnings remain intentional domain diagnostics when existing tests deliberately evaluate truncated EGF models outside their estimated reliable range.

### Claim boundary

The release establishes implementation agreement with the equations represented in the Toolkit. It does not prove metric completeness, the e-base theorem, or the physical applicability of exploratory Scale Space and biological workflows.

### Final theorem-alignment additions

The final v0.11.0 package now includes the full Gaussian denominator-ideal and valuation API and canonical periodic normalization:

- arbitrary Gaussian numerator and denominator support;
- exact Gaussian gcd, divisibility, unit normalization, and beta valuation;
- intrinsic denominator-ideal generator;
- exact termination analysis and minimal Laurent offset;
- canonical eventually periodic Laurent expansion;
- least-preperiod cycle detection and primitive-period normalization;
- exact semantic equality and deterministic serialization;
- theorem papers and independent verification script.

The special `1/5` behavior is now a corollary of the general Gaussian-ideal implementation rather than a standalone special case.


### Branch-index and formal CNRS-H theorem alignment

- Added `LiftedComplex` with the exact branch-wrap cocycle for multiplication on the universal cover of `C*`.
- Added a single-valued lifted logarithm satisfying an exact product law.
- Added formal Hurwitz-series coefficient operations for CNRS-H and exact theorem tests for Leibniz, integration, inversion, and exponential eigenfunctions.
- Included both theorem papers and independent verification scripts under `docs/theory/` and `docs/audits/scripts/`.
### Metric/topological completeness and hybrid theorem integration

- Added `cnrs.topology` with exact symbolic-prefix and beta-adic distance utilities, finite-digit evaluation, the first-difference isometry check, and CNRS-H coefficientwise product distance.
- Recorded the theorem that right-infinite CNRS-A strings complete to the valuation ring at `beta=-2+i` (`Z_5` topologically), while finite Laurent shifts give the corresponding local field (`Q_5` topologically).
- Explicitly separated beta-adic convergence from ordinary complex convergence.
- Added `cnrs.hybrid` with `CoefficientCodec` and `HybridSeries`, transporting canonical CNRS-A coefficient representations into the CNRS-H Hurwitz-series carrier.
- Added theorem-aligned tests for ultrametricity, first-difference isometry, coefficientwise convergence, Hurwitz-product transport, Leibniz, integration, exponential eigenfunctions, and deterministic serialization.
- Included both theorem papers and independent verification scripts under `docs/theory/` and `docs/audits/scripts/`.
