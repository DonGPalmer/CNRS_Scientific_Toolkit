# CNRS Scientific Toolkit v0.15.0 release finalization record

Release date: 2026-09-16

Status: RELEASE-FINALIZATION CANDIDATE; EXACT-HEAD CI PENDING

## Certified implementation

- implementation pull request: #5;
- audited head: `0740c1e8ace7af98ac3ed4c76d6ba74610bada56`;
- audited and merged tree: `88a545bbf359e2e5fe2b0d29111b915e08963e08`;
- governed merge commit: `fa93a8307905961808321e19d7020dc7806e4e5f`;
- post-merge Python/distribution run: `35146390315` — SUCCESS;
- exact-tree Lean run: `35133435901` — SUCCESS, source identity plus six builds;
- retained post-merge artifact: `10467418615`;
- artifact digest: `sha256:78541253771825f09d6d8c8a414564f914418145c8db60b9598cf0ca625a1e76`.

## Finalization scope

This finalization changes release-facing version, citation, documentation,
tests, build tooling, and publication automation from v0.14.1 to v0.15.0. It
does not alter the certified convolution implementation, benchmark results,
frozen API, acceptance contract, or governed Lean source.

`CITATION.cff` records the actual release date and Toolkit concept DOI. The
v0.15.0 version DOI does not exist before publication and will be installed
additively after Zenodo processes the GitHub release.

## Remaining gates

1. Verify local tests, candidate checksums, source index, reproducible builds,
   clean wheel/source installs, and release-asset guards.
2. Obtain exact-head Python/distribution and seven-job Lean CI.
3. Verify the exact finalization commit/tree and distribution artifact.
4. Merge the certified finalization head, tag the exact merge commit
   `v0.15.0`, and publish the GitHub Release with both certified assets.
5. Verify the Zenodo record and version DOI, then install an additive closeout
   and synchronize the DOI register.
