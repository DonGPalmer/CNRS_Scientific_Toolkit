# v0.14.0 release activation checklist

Status: AMBER REPAIR COMPLETE; EVIDENCE-SYNCHRONIZED CI/RE-AUDIT HOLD

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

The premature `date-released` field has been removed. Exact-head repair commit
`b4382510d724bf92bc26aedb4fb52da31b627af3`, tree
`c4fde4738adc20a8f46d121bb81fa6ed93859bbd`, Python/distribution run
`34733222919`, and seven-job Lean run `34733222954` are GREEN. Retained artifact
`10309848481` contains the exact wheel, source distribution, SHA-256 inventory,
candidate commit, and candidate tree. Its archive digest is
`sha256:dff8c3306e2350ddbd7f40cfa7262616c07c8e08cfe99a58510ed3b0fccf238c`.

Evidence-synchronized-head CI, final audit, GitHub Release URL, actual release
date, and Zenodo version DOI remain pending.

## Release sequence

1. Run Python/distribution and seven-job Lean CI on the repair commit.
2. Synchronize the repair commit/tree, workflow runs, and artifact identity.
3. Run CI on the evidence-synchronized immutable candidate.
4. Obtain a GREEN independent re-audit of that candidate and artifact.
5. Governed merge and post-merge verification.
6. Add the actual release date, verify, tag, publish the GitHub Release assets,
   and verify Zenodo publication.
