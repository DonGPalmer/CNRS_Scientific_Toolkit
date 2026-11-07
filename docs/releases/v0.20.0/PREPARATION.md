# CNRS Scientific Toolkit v0.20.0 — governed candidate preparation

**Status:** CANDIDATE ONLY — no author approval of a public release, tag, DOI deposit, or immutable artifact hashes. The v0.20.0 version identity is *proposed for review*; merging this candidate is a separate decision. Publication is separately gated again after merging.

## Frozen baseline and intended content
- Published baseline: v0.19.0, tag commit `c4ce26efed4051a111e036fca8720aa1441cf5f7`; GitHub wheel SHA-256 `29ceba4684c68df02f64b43b0d6af2d84ff0e6070d56898426f7ed6d1f575bb5`; sdist SHA-256 `b0bf00ddbd7a9834f18b9a94b001293638db957ad173fd2d82c073e1fa2eb617`; Zenodo version DOI `10.5281/zenodo.23747938`. Preserve unchanged.
- New exact finite CNRS-H source integrated on `main` by PR #25, merge commit `475a6b4d58068479e816450ea4b1506017473bcf`.
- Qualified modules: `cnrs.cnrs_h_finite_exact` (coefficient ring `R_A=Z[i][(-2+i)^-1]` and finite divided-power/Hurwitz jet operations), `cnrs.cnrs_h_toolkit_interop` (bounded injected native-digit comparison), `cnrs.cnrs_h_limits` (opt-in checked `BoundedFiniteOps`). No new root-level public exports; existing `CnrsHNative` and `CnrsHJet` unchanged.
- Existing `gaussian_types.py` and `streaming_division.py` use `typing.Tuple`/`Union` for Python 3.9 compatibility; no numerical formula changes.
- Formal 6-project Lean subtree unchanged; no proof of the new Python backend, end-to-end extracted implementation, analytical convergence, infinite streams, untrusted-input safety or speed advantage is asserted.

## Candidate configuration
The candidate branch synchronizes `pyproject.toml` version, `cnrs.__version__`, and `tools/build_reproducible_distributions.py` to **0.20.0**. CI smoke-tests the exact finite modules from installed wheel and sdist and labels its artifacts `cnrs-v0.20.0`. Artifact names and checksums are **provisional** until an exact approved final commit/tree is frozen.

The existing `release-assets.yml` has dedicated handlers only for v0.18.0 and v0.19.0. **Do not create a v0.20.0 GitHub release or tag based on this preparation.** Publication requires a new, independently reviewed, fail-closed v0.20.0 approval-manifest workflow, including explicit author approval and exact source/asset SHA-256 gates. `tools/check_v019_release_approval.py` continues to apply to v0.19.0 only; it must not be reused as if it certified v0.20.0.

`CITATION.cff` and consolidated `RELEASE_NOTES.md` intentionally continue to describe the last **published** release until the separate release transaction. On release approval, update them in the candidate-to-final packaging transaction and rerun checks; do not insert a fictional release date or DOI.

## Required verification and approval gates
1. Verify all candidate source changes against **live** current `main` and resolve any base drift.
2. Full GitHub tests and historical v0.14–v0.18 acceptance, reproducible **two-pass** wheel/sdist build, isolated installed-package imports (including CNRS-H), Python 3.9–3.13 matrix, and all six Lean project builds plus source identity.
3. Independent release-delta audit: confirm no unintended source or API changes, no `R_A\rightarrow Q(i)` overclaim, and explicit resource budgets. Confirm publication notes remain experimentally qualified.
4. Obtain explicit **author approval** for candidate adoption/merge, then verify final commit and tree. Merge **does not** approve publication.
5. Prepare new v0.20.0 release-approval verifier, publication workflow/environment, approval manifest with SHA-256 of final commit/tree and **final** wheel/sdist; audit missing-manifest and changed-byte negative controls, non-clobbering upload. Reproducible source timestamp uses final commit, so pre-merge hashes are not authoritative.
6. Author separately approves **publication** and exact manifest; only then create/tag the approved release and verify public asset identity and a new Zenodo deposit. Update live programme history/DOI index under their own standards, not from a placeholder.

## Scope exclusions
No wheel/sdist upload to GitHub Releases, no PyPI deployment, no Zenodo deposit, no version DOI assignment, no new public release, no amendment of old Git tags. The existing concept DOI is the citation identity across versions; a new Zenodo *version DOI* must only be reported after deposit verification.

## Post-merge source-only gate
If `v0.20.0` becomes the next approved version, the release candidate must be rebased and independently verified against live final hashes; pre-merge `main` at `475a6b4d...` is a baseline pin, not a permanent authorization.
