# CNRS Scientific Toolkit v0.14.1 — Release Governance and Reproducible Packaging

**Status:** maintenance candidate; governed release pending
**Release date:** to be supplied immediately before tagging

CNRS means **Complex Numeric Representation System**.

## Purpose

Version 0.14.1 is a release-engineering and governance maintenance update. It
does not change the exact Gaussian-rational streaming-division algorithm,
division witnesses, public Python APIs, vendored Lean sources, or mathematical
claim boundaries released in v0.14.0.

## Changes

- Closes the v0.14.0 release record and removes stale candidate/publication
  language.
- Records Toolkit Zenodo version DOI `10.5281/zenodo.22731846` and concept DOI
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

## Claim boundary

No new arithmetic, convergence, physical, biological, or formal-verification
claim is introduced. Python remains independently implemented and
theorem-aligned, not Lean-extracted or end-to-end formally verified.
