# CNRS Scientific Toolkit v0.16.0 release-activation record

Intended release date: 2026-09-18

Status: RELEASE-ACTIVATION CANDIDATE; EXACT-HEAD CI PENDING

## Certified implementation

- implementation pull request: #8;
- audited head: `ba1f5eda0e359f10926587ced89e6dececb5e87d`;
- audited and merged tree: `884b23bc0e775efe4330823d954ad05dca12658c`;
- governed merge commit: `b382209899e97a64249d74291ce1b3268f84c64b`;
- post-merge workflow: `35275828314` — SUCCESS;
- formal subtree: `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`.

## Activation scope

This candidate changes release-facing version, citation, documentation,
release notes, tests, build tooling, publication automation, source index, and
checksum evidence from v0.15.0 to v0.16.0. It does not alter the certified
exact-multiplication implementation, frozen architecture/API/acceptance packet,
validation oracles, or governed Lean source.

`CITATION.cff` records the intended release date and Toolkit concept DOI.
The v0.16.0 version DOI does not exist before publication and will be installed
additively after Zenodo processes a separately authorized GitHub release.

## Remaining gates

1. Verify regression, acceptance, static guards, source index, activation
   checksums, reproducible builds, clean wheel/sdist installs, and release-asset
   guards.
2. Obtain exact-head Python/distribution and Lean CI.
3. Independently audit the exact activation head, tree, and artifacts.
4. Obtain separate authorization to mark ready and merge.
5. Obtain separate authorization to tag and publish; then verify Zenodo and
   install additive public-release closeout evidence.
