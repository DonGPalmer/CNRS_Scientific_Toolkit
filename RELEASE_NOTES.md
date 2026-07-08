# v0.10.3 — Independent Validation and Metadata Synchronization

## Summary

v0.10.3 incorporates the July 7, 2026 independent Toolkit audit into the repository. The release does not introduce a new completeness claim or alter the core CNRS-A arithmetic algorithms. It strengthens independent verification, metadata accuracy, API clarity, and release hygiene.

## Added

- `docs/audits/toolkit_audit_2026-07-07_v1.md`: permanent audit record.
- `tools/toolkit_audit_crossval.py`: standalone exact cross-validation harness with nonzero exit status on failure.
- `tests/test_independent_cross_validation_v0103.py`: deterministic independent arithmetic and CNRS-H regression checks.
- `CnrsH.eigen_exponential(alpha, terms)` and `CnrsHNative.eigen_exponential(alpha, terms)` for the EGF eigenfunction with coefficients `alpha**n`.
- `docs/STATUS_VOCABULARY_MAPPING.md`: mapping between Toolkit provenance labels and the five programme-level epistemic labels.
- `.gitattributes`: normalized LF text files.

## Changed

- Synchronized README and test-status metadata with the independently observed baseline of `1126 passed, 6 xfailed` before the v0.10.3 test additions.
- Reorganized `docs/CLAIM_STATUS.md` so the current release status appears before historical records.
- Clarified that `CnrsH.exponential(d, terms)` represents `d*exp(rho)`, while `eigen_exponential(alpha, terms)` represents `exp(alpha*rho)`.
- Normalized Python and documentation line endings to LF.
- Added SymPy to the development dependency set for independent CNRS-H reference checks.

## Independent audit result

- Core arithmetic reference checks: passed.
- CNRS-H calculus and composition spot-checks: passed.
- Contamination sweep for recently corrected/refuted claims: clean.
- Six expected failures remain documented in `tests/test_evaluate_limitations.py`; they are limitation markers, not hidden regressions.

## Validation policy

Release validation: `1128 passed, 6 xfailed`. Future main-branch status should be taken from CI rather than from a permanently hand-maintained count.

## Open research boundaries

- Metric completeness remains open.
- The e-base CNS theorem remains open.
- General analytic closure remains open.
- The research-layer scientific workflows require a separate per-module audit.
