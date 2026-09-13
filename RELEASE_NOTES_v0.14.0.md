# v0.14.0 — Streaming Division and Formal–Runtime Witness Alignment

**Status:** governed merge complete; post-merge CI GREEN; tag and publication pending
**Release date:** 2026-09-12
**Architecture freeze:** 2026-09-12  
**Baseline:** v0.13.1, commit `e7f8424a967292a36643bb5fa8206ccb1d3f8fcd`

## Purpose

v0.14.0 is the first Toolkit release with lazy, replayable division
streams for exact Gaussian-rational values. It also introduces explicit bounded
resolution records and deterministic witnesses connecting runtime recurrence
states to the established canonical eventually-periodic representation.

## Implemented additions

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

## Compatibility

The existing `cnrs.division`, `CnrsRational`, `expand_division`, and
`canonical_expansion` interfaces remain supported. v0.14.0 must not alter
their signatures or reinterpret existing result classes.

## Claim boundary

The intended claim is exact Gaussian-rational streaming division. This does not
establish arbitrary-real or arbitrary-complex stream arithmetic, unrestricted
infinite-stream field closure, streaming multiplication, analytic convergence,
or a universal cycle-discovery bound.

Lean verifies the mathematical statements encoded in the governed formal
projects. The Python implementation is independently written and must be
described as theorem-aligned and computationally tested, not Lean-extracted or
formally verified.

## Release validation

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

## Governance and publication status

- independently audited candidate `cd0d590818de3f2db615f2269276ede53527827d`: GREEN;
- governed merge commit `511526fdd60cfa2967d0307fe16ba4131785c0b3`;
- post-merge Python/distribution run `34734237160`: SUCCESS;
- post-merge seven-job Lean run `34734237144`: SUCCESS;
- tag, GitHub Release, release-asset publication, and Zenodo verification pending.

The release uses the Toolkit concept DOI `10.5281/zenodo.20574852`. The Zenodo
version DOI will be recorded after publication.
