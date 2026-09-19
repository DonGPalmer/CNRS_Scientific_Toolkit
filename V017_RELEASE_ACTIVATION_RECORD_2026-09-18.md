# CNRS Scientific Toolkit v0.17.0 release-activation record

Intended release date: 2026-09-18

Status: RELEASE-ACTIVATION CANDIDATE; EXACT-HEAD CI PENDING

## Certified implementation

- implementation pull request: #10;
- audited head: `7840b51db1b7a3b9955aa20bd2b67fb99344335f`;
- audited and merged tree: `924b8af717e17183e8bf9375adcb9fb35ca4093f`;
- governed merge commit: `9965eb3bb2a1389469a4a99b90a03f6671fe76c8`;
- post-merge workflow: `35392851176` — SUCCESS;
- formal subtree: `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`.

## Activation scope

This candidate changes release-facing version, citation, documentation,
release notes, tests, build tooling, publication automation, source index, and
checksum evidence from v0.16.0 to v0.17.0. It does not alter the certified
exact-division implementation, frozen architecture/API/acceptance packet,
validation oracles, or governed Lean source.

`CITATION.cff` records the intended release date and Toolkit concept DOI.
The v0.17.0 version DOI does not exist before publication and will be installed
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
