# CNRS Toolkit v0.20.0 publication approval and activation controls

**Status:** Prepared candidate, NOT APPROVED for merge, tag creation, GitHub publication, Zenodo deposit or version-history updates.
**Prior source merge:** PR #26, main commit e35085147e9eee1fdeda882b904db79f4737ce03. This is a baseline, NOT a final publication pin.
**Previous published release:** v0.19.0; DO NOT reuse its variables, manifest, tag, artifacts, release, or DOI.

## Publication authorization is a separate decision

An author decision to merge this candidate merely installs dormant publication controls. Publishing a GitHub release is a separate operation requiring explicit author approval of the final commit/tree, release files and manifest digest. Do not publish an empty GitHub Release to trigger this workflow before that authorization: an unapproved release event can still create a public release page even though the asset gate fails.

The candidate workflow is .github/workflows/v020-release-assets.yml. It matches only the published v0.20.0 release event, references the dedicated environment cnrs-v020-publication and never falls back to the v0.19.0 approval variables. It verifies source identity, build reproducibility, installed packages, exact wheel/sdist digests, release asset absence and public downloaded assets before reporting success. Uploads do NOT use --clobber. Existing v0.18/v0.19 jobs remain untouched.

## Publication environment and sole-author control

Create/verify GitHub Actions environment cnrs-v020-publication under explicit publication authorization. Inspect its actual protection settings and verify configuration variable scope. No reviewer-protection exception from v0.19.0 automatically carries over to v0.20.0. If GitHub cannot use a separate required reviewer for a sole-author repository, record a new explicit v0.20.0 author decision about reviewer protection, not an inferred exception.

The environment-specific variables are:
- CNRS_V020_APPROVED_MANIFEST_JSON: exact UTF-8 JSON bytes, including any trailing newline.
- CNRS_V020_APPROVED_MANIFEST_SHA256: SHA-256 of that exact raw JSON string independently approved out of band.

Do not define them at repository or organization level or inherit same-named values from those scopes. Do not compute/approve the trusted digest inside the release job or from a code-generated sidecar. A manifest or digest mismatch must block release asset publication. The digest is an identity gate, not cryptographic proof of human consent; environment administration remains trusted.

## Required immutable manifest structure — example is INVALID

All strings below in upper-case are placeholders; they are not hashes, approval or authorization.

    {
      "schema": 1,
      "version": "0.20.0",
      "tag": "v0.20.0",
      "commit": "FINAL_AUTHOR_APPROVED_FULL_40_HEX_COMMIT",
      "tree": "FINAL_AUTHOR_APPROVED_FULL_40_HEX_TREE",
      "assets": {
        "cnrs-0.20.0-py3-none-any.whl": "INDEPENDENTLY_VERIFIED_64_HEX_SHA256",
        "cnrs-0.20.0.tar.gz": "INDEPENDENTLY_VERIFIED_64_HEX_SHA256"
      },
      "approval_record": "DURABLE_AUTHOR_PUBLICATION_AUTHORIZATION_RECORD"
    }

The verifier tools/check_v020_release_approval.py rejects absent/mutated/duplicate-key manifests, incorrect version/tag, incomplete asset identity and wrong source/tag/tree or distribution bytes. The separate Python negative-test suite tests these controls.

## Order of governed work

1. Review and author-approve the publication-control PR for merging only. Record authorization in an immutable SSC journal event.
2. Recheck base/head immediately before merge. Merge with an expected-head guard. Verify the ACTUAL final main commit and Git tree, branch identity, published release baseline and post-merge CI.
3. Rebuild wheel/sdist twice from the final immutable commit, using SOURCE_DATE_EPOCH derived from that commit, and independently verify SHA-256, exact files, package version and isolated installs. The SHA-256 of pre-merge builds cannot be approved as if final.
4. Independently audit all release-facing text, CFF, source inventory, formal source identity and release artifacts. If source/build differs, stop; do not modify the approved manifest to force acceptance.
5. Obtain explicit author PUBLICATION approval for final commit/tree, two exact assets, GitHub release description, and chosen environment/reviewer settings. Create immutable approval record and out-of-band approved manifest SHA256.
6. Configure and verify the exact environment-scoped variables; check no conflicting same-named repository/organization variables exist. Only then create the v0.20.0 tag at the approved commit and publish its GitHub release. GitHub workflow verifies and uploads exact approved assets without replacement.
7. Independently retrieve the public assets and compare SHA256 and sizes. Confirm the actual published date and release URL. Never substitute a developer CI artifact for public release evidence.
8. Prepare a new VERSION of the existing Zenodo concept record (10.5281/zenodo.20574852), using separately reviewed metadata and exact deposited files. Verify publication and obtain the new version DOI; do not invent or pre-record it.
9. Follow Programme Register and Zenodo DOI register standards for exact new publication history rows; do not change registers from a draft or anticipated DOI. Journal the transaction and its closeout.

## Scientific boundaries retained

The finite exact carrier is R_A = Z[i][(-2+i)^(-1)], not unrestricted Q(i).
The CNRS-H modules remain qualified experimental APIs. BoundedFiniteOps imposes input/result budgets but does not make raw unbounded research classes safe for untrusted inputs. The six Lean project builds do not establish extraction or end-to-end proof of the new Python backend. No infinite-series convergence, universal time/memory bound, experimental physical result or performance advantage is claimed.

## Remains held

No release tag or GitHub Release, no published/modified wheel/sdist, no new Zenodo version DOI, no production version register update and no release environment changes are authorized by preparing this document.
