# v0.14.0 — Streaming Division and Formal–Runtime Witness Alignment

**Status:** preimplementation candidate  
**Architecture freeze:** 2026-09-12  
**Baseline:** v0.13.1, commit `e7f8424a967292a36643bb5fa8206ccb1d3f8fcd`

## Purpose

v0.14.0 is planned as the first Toolkit release with lazy, replayable division
streams for exact Gaussian-rational values. It also introduces explicit bounded
resolution records and deterministic witnesses connecting runtime recurrence
states to the established canonical eventually-periodic representation.

## Frozen additions

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

## Performance evidence

No speed or memory advantage is presently claimed. The frozen benchmark must
measure construction, prefixes of 1/10/100/1,000 digits, complete resolution,
witness creation and validation, and peak memory on at least 30 deterministic
inputs. Results must retain raw timing data and environment metadata.

## Release gates still pending

- implementation of the frozen modules;
- GREEN v0.14.0 acceptance suite;
- GREEN existing Python regression suite with truthful counts;
- GREEN six-project Lean matrix and source-alignment guard;
- benchmark JSON and CSV with parity evidence;
- clean wheel and source-distribution installation;
- synchronized version, citation, source index, API, claim, test, and provenance records;
- independent audit of the exact candidate commit and artifacts;
- governed merge, tag, GitHub Release, and Zenodo publication.

This file must be updated from “preimplementation candidate” to “released” only
after those gates pass. No release date, DOI, test count, or performance result
is asserted in advance.

