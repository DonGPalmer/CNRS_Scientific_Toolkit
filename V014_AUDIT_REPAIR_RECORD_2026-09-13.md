# CNRS Scientific Toolkit v0.14.0 — AMBER audit repair record

Date: 2026-09-13

Status: REPAIR EXECUTED; EVIDENCE-SYNCHRONIZED CI/RE-AUDIT HOLD

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

## Repair/build completion

- exact-head repair commit: `b4382510d724bf92bc26aedb4fb52da31b627af3`;
- exact-head repair tree: `c4fde4738adc20a8f46d121bb81fa6ed93859bbd`;
- Python, acceptance, and distribution run: `34733222919` — SUCCESS;
- Lean source identity and six-project run: `34733222954` — SUCCESS;
- retained distribution artifact: `10309848481`;
- artifact name: `cnrs-v0.14.0-distributions-b4382510d724bf92bc26aedb4fb52da31b627af3`;
- artifact size: 573,636 bytes;
- artifact archive digest:
  `sha256:dff8c3306e2350ddbd7f40cfa7262616c07c8e08cfe99a58510ed3b0fccf238c`;
- retention expiry: 2026-12-12.

The artifact records the same commit and tree internally. Its wheel is 255,333
bytes with SHA-256
`f7bf8d4862e401c93437658f8a279a1340ea126e4aa707fbffb8a645fd259fde`.
Its source distribution is 324,753 bytes with SHA-256
`bee726e4c05db1f1c05e864a254170a54aa6fecf199fe990e627488d4f64dd29`.

The streaming implementation module hashes are unchanged from the initial
candidate. The remaining candidate changes are governance records and workflow
binding needed to make exact artifacts auditable.

## Final re-audit and merge disposition

Independent re-audit returned GREEN for commit
`cd0d590818de3f2db615f2269276ede53527827d`, tree
`18e171d6a8e5a3a0b5a69614d05950fe0144f2ac`, and retained artifact
`10310278319`.

The authorized governed merge produced commit
`511526fdd60cfa2967d0307fe16ba4131785c0b3`. Post-merge
Python/distribution run `34734237160` and Lean run `34734237144` succeeded.
The release date `2026-09-12` was explicitly authorized for finalization.
