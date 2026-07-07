# v0.10.2 — Verification and Release Engineering Release

## Summary

v0.10.2 strengthens the reproducibility layer of the CNRS Scientific Toolkit.
It does not introduce new mathematical claims. It improves the connection
between CNRS mathematics, implementation, validation, and release packaging.

## Added

- Automated release-cleanup tooling (`tools/build_release.py`)
- Release archive verification
- Expanded reproducibility guidance

## Changed

- Improved theorem-to-implementation traceability.
- Clarified stable, research, and open capability boundaries.
- Improved release hygiene.
- Removed generated development artifacts from release packages.

## Validation

Regression suite:

- 1121 passed
- 6 expected failures
- 0 unexpected failures

## Current status

Stable implementation layer:
- CNRS-A representation
- normalization
- arithmetic workflows
- multiplication workflows
- structured division workflows

Research layers:
- CNRS-H extensions
- branch-aware workflows
- scientific applications

Open mathematical questions:
- metric completeness
- e-base CNS theorem
- full analytic closure
