# CNRS Scientific Toolkit v0.14.1 — Release Governance and Reproducible Packaging

**Status:** published; GitHub and Zenodo release complete
**Release date:** 2026-09-14

CNRS means **Complex Numeric Representation System**.

## Purpose

Version 0.14.1 is a release-engineering and governance maintenance update. It
does not change the exact Gaussian-rational streaming-division algorithm,
division witnesses, public Python APIs, vendored Lean sources, or mathematical
claim boundaries released in v0.14.0.

## Changes

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

## Required validation

- complete Python regression suite;
- unchanged v0.14.0 acceptance suite;
- reproducible double-build comparison;
- clean installation from the wheel and source distribution;
- Lean source-identity gate and all six project builds;
- release-guard tests;
- independent audit of the immutable candidate and retained distributions.

## Publication identity

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

## Claim boundary

No new arithmetic, convergence, physical, biological, or formal-verification
claim is introduced. Python remains independently implemented and
theorem-aligned, not Lean-extracted or end-to-end formally verified.
