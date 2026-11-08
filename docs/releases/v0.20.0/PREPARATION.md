# CNRS Scientific Toolkit v0.20.0 — governed preparation status

**Status:** Source integrations complete (PRs #25–#28). v0.20.0 is NOT TAGGED, NOT PUBLISHED, and NOT AUTHOR-APPROVED for publication. Further pre-publication maintenance is separately reviewed and cannot be treated as a release authorization.

## Source integration history

- PR #25 introduced qualified experimental exact finite CNRS-H coefficient/Hurwitz modules, bounded operations and interop; merge `475a6b4d58068479e816450ea4b1506017473bcf`.
- PR #26 synchronized version 0.20.0 and candidate distribution checks; merge `e35085147e9eee1fdeda882b904db79f4737ce03`.
- PR #27 installed dormant v0.20 publication controls, author-approval verifier, negative tests, and the **v0.20.0 candidate section in the consolidated `RELEASE_NOTES.md`**; merge `af03014274d0d742da58376713cab8c8fb86ee3d`.
- PR #28 corrected the publication-control document's pre-merge wording; merge `e88087673705feaa9348acbeddcb8357ae93f97a`.
- Previous published v0.19.0 remains at tag commit `c4ce26efed4051a111e036fca8720aa1441cf5f7`; wheel and sdist must never be changed under that version identity.

## Scientific and API boundaries

The exact coefficient carrier is `R_A = Z[i][(-2+i)^(-1)]`, not unrestricted `Q(i)`. The finite Hurwitz arithmetic and `cnrs.cnrs_h_limits.BoundedFiniteOps` are opt-in, qualified experimental APIs; raw research classes remain unbounded. No new root-level exports or changes to established `CnrsHNative` or `CnrsHJet`. Existing Lean six-project builds do not prove or extract the new Python backend. No infinite-series convergence, trusted-input sandbox, universal resource guarantees, physical prediction, or performance superiority is claimed.

## Release engineering and current work

GitHub CI at the PR #28 merge reported 1,575 passing Python tests and 4 skipped, the historical arithmetic acceptance contracts, double-build reproducibility and isolated wheel/sdist installations. The independent 2026-11-08 review repeated the full suite across Python 3.9–3.13 and found different compressed archive bytes on distinct zlib hosts even though archive members matched. The current bounded maintenance candidate addresses that build-portability concern, pins build backend versions, updates the source inventory, and provides an **offline, non-publishing** approval-gate rehearsal. Its final source and distribution hashes must be taken after the eventual maintenance merge.

Consolidated `RELEASE_NOTES.md` now has a v0.20.0 **candidate** section above the preserved v0.19.0 published history. `CITATION.cff` identifies version 0.20.0 without inventing a release date. The distinct `.github/workflows/v020-release-assets.yml` triggers only on publication of the v0.20.0 GitHub Release; it must not be triggered until separately authorized.

The pre-publication approval procedure and invalid example manifest are in `docs/releases/v0.20.0/PUBLICATION_APPROVAL.md`. Neither the document nor any CI rehearsal confers approval.

## Remaining gates

1. Complete the bounded maintenance PR, review its exact diff, full CI, cross-compression portability evidence and non-publishing rehearsal. Obtain separate author approval before merging it.
2. Reverify the **actual final** main commit and Git tree and rebuild wheel/sdist twice after the last source commit; compare actual bytes across the intended build environments, inspect installed package, and independently record both SHA-256 values.
3. Inspect actual `cnrs-v020-publication` GitHub environment protection and variable scope, and tag-protection policy. Do not inherit the v0.19.0 sole-author reviewer exception without an explicit v0.20 decision.
4. Present the exact final commit/tree, two distribution bytes/hashes, release description, environment choices and durable approval record for separate **author publication approval**. A synthetic CI rehearsal manifest is explicitly invalid as approval.
5. Only after publication authorization and manifest configuration may the v0.20.0 tag and GitHub Release be created and the fail-closed upload checks executed. No release should be created as a test of the workflow.

**Excluded now:** no GitHub release/tag/publication, no Zenodo metadata work, no Zenodo deposit or DOI-index mutation. The previous release and all author-governed records remain unchanged.
