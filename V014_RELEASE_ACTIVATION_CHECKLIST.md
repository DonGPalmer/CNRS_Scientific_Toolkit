# v0.14.0 release activation checklist

Status: INITIAL CI GREEN; AMBER EVIDENCE REPAIR IN PROGRESS; RELEASE HOLD

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

## Initial public-candidate evidence

- candidate commit: `a65c5834e56ed2bd28a8683c4a9e2017bb64157e`;
- candidate tree: `9eb4ed67891405fa8824d933c883e51205f152a8`;
- Python workflow run `34722404539`: SUCCESS;
- Lean workflow run `34722404541`: SUCCESS;
- Lean jobs: source identity, CNRSCore, CnrsQ2, CNRSArithmetic,
  CNRSIntegration, CNRSProblem1, and CNRSProblem2 all succeeded;
- independent audit disposition: AMBER on 2026-09-13;
- functional implementation: GREEN;
- blockers: premature citation release date, pre-CI evidence records, and
  distributions not independently available.

The premature `date-released` field has been removed. The Python workflow now
builds, smoke-tests, checksums, and uploads the wheel and source distribution as
a retained artifact. Repair-candidate commit/tree, workflow runs, artifact
identity, final audit, GitHub Release URL, actual release date, and Zenodo
version DOI remain pending.

## Release sequence

1. Run Python/distribution and seven-job Lean CI on the repair commit.
2. Synchronize the repair commit/tree, workflow runs, and artifact identity.
3. Run CI on the evidence-synchronized immutable candidate.
4. Obtain a GREEN independent re-audit of that candidate and artifact.
5. Governed merge and post-merge verification.
6. Add the actual release date, verify, tag, publish the GitHub Release assets,
   and verify Zenodo publication.
