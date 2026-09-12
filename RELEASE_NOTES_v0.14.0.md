# v0.14.0 — Streaming Division and Formal–Runtime Witness Alignment

**Status:** implementation candidate — local gates GREEN; GitHub CI and audit pending
**Architecture freeze:** 2026-09-12  
**Baseline:** v0.13.1, commit `e7f8424a967292a36643bb5fa8206ccb1d3f8fcd`

## Purpose

v0.14.0 is the first Toolkit candidate with lazy, replayable division
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

## Local candidate validation

- historical Python regression suite: `1214 passed, 4 skipped, 0 failed`,
  with 922 retained warnings;
- dedicated v0.14.0 acceptance suite: `19 passed`;
- Lean source-alignment and proof-hygiene guard: PASS, six projects and exactly
  79 Lean files;
- wheel and source distribution builds: PASS;
- clean wheel and source installation smoke tests: PASS;
- equal-output benchmark: PASS over 30 deterministic cases.

Local distribution candidates:

| Artifact | Size | SHA-256 |
|---|---:|---|
| `cnrs-0.14.0-py3-none-any.whl` | 255,333 bytes | `6de8e4c4b2a4e19d8a0d01186e99ef87f6846602b538671d50a2bb9c9a9d3b92` |
| `cnrs-0.14.0.tar.gz` | 324,857 bytes | `4a527835e2eaee89ca90274bbb6b97db2ebb24359858ac9fb7b24569d6bf6d7c` |

These artifacts are local candidate builds. Release assets must be rebuilt or
identity-checked from the audited public candidate before publication.

The local benchmark found lower median time ratios for 1- and 10-digit prefixes
(0.645 and 0.936), higher ratios for 100 and 1,000 digits (3.073 and 10.736),
and a full-resolution median ratio of 0.973. Median peak-memory ratios fall to
0.721 at 1,000 digits. These are measurements from the recorded environment,
not universal performance guarantees. See `docs/V014_PERFORMANCE_RESULTS.md`.

## Release gates still pending

- GREEN GitHub Python CI and six-project Lean matrix on the uploaded candidate;
- independent audit of the exact candidate commit and artifacts;
- governed merge, tag, GitHub Release, and Zenodo publication.

Release date, public DOI, GitHub run identities, and final public commit remain
unset until those events exist.
