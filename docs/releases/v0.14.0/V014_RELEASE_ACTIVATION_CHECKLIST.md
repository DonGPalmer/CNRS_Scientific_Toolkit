# v0.14.0 release activation checklist

Status: GOVERNED MERGE AND POST-MERGE CI GREEN; FINALIZATION CI PENDING

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

The synchronized candidate at commit
`cd0d590818de3f2db615f2269276ede53527827d`, tree
`18e171d6a8e5a3a0b5a69614d05950fe0144f2ac`, passed independent re-audit with
artifact `10310278319`. Governed merge commit
`511526fdd60cfa2967d0307fe16ba4131785c0b3` is on `main`. Post-merge
Python/distribution run `34734237160` and seven-job Lean run `34734237144`
both succeeded. Release date `2026-09-12` is authorized.

Finalization CI, tag, GitHub Release, attached release assets, and Zenodo
version DOI verification remain pending.

## Release sequence

1. Run Python/distribution and seven-job Lean CI on the release-finalization commit.
2. Verify the finalization commit/tree, workflow runs, and exact distribution artifact.
3. Create tag `v0.14.0` at the verified finalization commit.
4. Publish the GitHub Release using the approved release notes.
5. Attach the exact finalization wheel and source distribution.
6. Verify Zenodo publication and record the version DOI.
