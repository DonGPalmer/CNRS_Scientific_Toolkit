# CNRS Scientific Toolkit v0.14.0 — AMBER audit repair record

Date: 2026-09-13

Status: REPAIR AUTHORIZED; RELEASE HOLD

## Audited candidate

- pull request: #2;
- commit: `a65c5834e56ed2bd28a8683c4a9e2017bb64157e`;
- tree: `9eb4ed67891405fa8824d933c883e51205f152a8`;
- Python workflow run: `34722404539` — SUCCESS;
- Lean workflow run: `34722404541` — SUCCESS;
- Lean jobs: source identity and all six governed projects — SUCCESS.

## Audit disposition

The independent audit returned AMBER. It found no blocking functional defect in
streaming division or witness validation. Release remains blocked by a premature
`date-released` field, pre-CI evidence records, and distributions that were not
independently available from CI.

## Authorized repair

1. Remove `date-released` until governed publication.
2. Record the initial candidate, tree, workflow runs, seven Lean jobs, and AMBER
   disposition in repository evidence.
3. Build and smoke-test the wheel and source distribution in GitHub Actions.
4. Upload those exact bytes, checksums, commit, and tree as a retained workflow
   artifact.
5. Synchronize the resulting repair identities in a subsequent evidence commit.
6. Re-run CI and submit the immutable synchronized candidate and artifact for
   independent re-audit.

## Identity rule

A Git commit cannot contain its own hash or the identities of workflow runs that
do not yet exist. Accordingly, the evidence chain distinguishes the initial
implementation candidate, the repair/build commit, and the later evidence-
synchronization commit. Each transition must preserve the implementation bytes
or disclose any change.

No merge, tag, GitHub Release, package publication, or Zenodo deposition is
authorized by this record.
