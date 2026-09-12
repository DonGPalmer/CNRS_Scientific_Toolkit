# v0.14.0 release activation checklist

Status: IMPLEMENTATION AND LOCAL ACCEPTANCE COMPLETE; CI/AUDIT HOLD

## Documents supplied in this package

- README.md
- RELEASE_NOTES.md
- RELEASE_NOTES_v0.14.0.md
- CITATION.cff
- SOURCE_INDEX.txt
- synchronized architecture, API, division, claim, test, theorem-alignment,
  Lean-alignment, acceptance, and performance documents under docs/

## Completed non-document release updates

- pyproject.toml identifies 0.14.0;
- cnrs/__init__.py identifies 0.14.0 and exports the approved APIs;
- version-regression tests identify 0.14.0;
- wheel and source distributions build and install successfully;
- SOURCE_INDEX.txt is regenerated from the candidate tree.

## Evidence completed locally

- regression: 1214 passed, 4 skipped, 922 warnings;
- dedicated acceptance: 19 passed;
- measured source commit/tree recorded in performance evidence;
- wheel and source-distribution names, sizes, and SHA-256 values recorded;
- both clean installation smoke tests pass;
- performance JSON/CSV and summary are retained.

GitHub Actions run/job identities, audited public candidate commit/tree,
GitHub Release URL, release date, and Zenodo version DOI remain pending.

## Release sequence

1. Upload the implementation candidate branch and open a draft pull request.
2. Confirm Python CI and all six Lean jobs are GREEN.
3. Obtain an independent audit of the immutable candidate.
4. Synchronize final public commit, run identities, date, and release assets.
5. Governed merge, tag, GitHub Release, and Zenodo publication.
