# CNRS Scientific Toolkit v0.18.0 release-activation record

Intended release date: 2026-09-23

Status: RELEASE-ACTIVATION CANDIDATE; EXACT-HEAD CI PENDING

## Certified implementation

- implementation pull request: #15;
- audited head: `fe3c27795085b13b402272de9a91b7a42d9ddda0`;
- audited and merged tree: `0a2fbba6151fd893231fe7f4bed459c0a7e0a853`;
- governed merge commit: `ac03e2925ce754d84cceedf548fd2060ffe33736`;
- post-merge workflow: `35877214047` — SUCCESS;
- formal subtree: `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`;
- merge-closeout audit SHA-256:
  `d4905efbf9a4f50ff2922b97ffc7ae51efcce606e0b448520e9508117d43dea1`.

## Activation scope

This candidate changes release-facing version, citation, documentation,
consolidated release notes, tests, build tooling, publication automation,
source index, and checksum evidence from v0.17.0 to v0.18.0. It does not alter
the certified exact addition/subtraction implementation, validation oracles,
frozen architecture/API/acceptance packet, or governed Lean source.

`CITATION.cff` records the intended release date and Toolkit concept DOI.
The v0.18.0 version DOI does not exist before publication and will be installed
additively after Zenodo processes a separately authorized GitHub release.

## Certified behavior and boundary

Addition preserves the released 14-state relation and v0.17 bytes throughout
the accepted finite grammar while using exact integer-pair construction.
Negation is exact multiplication by `"144"`; subtraction is exact negation
followed by exact addition. The release corrects only the independently
demonstrated fractional v0.17 negation/subtraction defect.

The release does not claim arbitrary infinite-stream arithmetic, unrestricted
analytic convergence, universal resource bounds, Lean extraction, or
end-to-end formal verification of the independently implemented Python
runtime.

## Remaining gates

1. Verify regression, all v0.14–v0.18 acceptance and claim guards, source
   inventory, activation checksums, reproducible builds, clean wheel/sdist
   installs, and release-asset guards.
2. Obtain exact-head push and pull-request Python/distribution CI.
3. Independently audit the exact activation head, tree, and artifacts.
4. Obtain separate authorization to mark ready and merge.
5. Obtain separate authorization to tag and publish; then verify GitHub assets
   and Zenodo and install additive public-release closeout evidence.
