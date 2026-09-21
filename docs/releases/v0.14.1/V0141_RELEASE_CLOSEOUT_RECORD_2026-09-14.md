# CNRS Scientific Toolkit v0.14.1 release closeout record

**Status:** GitHub and Zenodo publication complete; independent post-release
closeout audit pending

**Release date:** 2026-09-14

## Published identity

- repository: `DonGPalmer/CNRS_Scientific_Toolkit`;
- tag: `v0.14.1`;
- commit: `a1ac3e1273ef9492c7b4a1aaeba08f078ce1d56a`;
- tree: `b7b258537aacbbf0ef8bac807c4f8fcd68d7ca38`;
- GitHub release ID: `388415806`;
- GitHub publication time: `2026-09-14T13:23:55Z`.

The published tag remains fixed. This additive closeout synchronization on
`main` does not move or recreate the tag and does not replace either published
distribution.

## CI and retained artifact

- Python/distribution workflow `34770774063`: SUCCESS;
- Lean workflow `34770773970`: SUCCESS;
- Lean jobs: source identity plus six project builds, 7/7 SUCCESS;
- retained candidate artifact `10321763058`;
- retained artifact name:
  `cnrs-v0.14.1-distributions-a1ac3e1273ef9492c7b4a1aaeba08f078ce1d56a`;
- retained artifact size: 568,385 bytes;
- retained artifact digest:
  `sha256:199badc1216afd76cad667c0ed80e2c825a8f9a189ff2268f27b223ac8405271`.

## Published distributions

Release-assets workflow `34848995514` completed successfully and attached:

- `cnrs-0.14.1-py3-none-any.whl`
  - size: 255,646 bytes;
  - SHA-256:
    `159db0051472f9b1c09f38786ea40b274661b674ac00de71ebcb61f140f1c377`;
- `cnrs-0.14.1.tar.gz`
  - size: 319,137 bytes;
  - SHA-256:
    `f5ca8b7f5b1849787a9c3cd8b4a6b3136d1196c70bfeaf1a936a641f2f67f520`.

## Zenodo identity

- version DOI: `10.5281/zenodo.22750622`;
- concept DOI: `10.5281/zenodo.20574852`.

The version DOI was supplied from the live v0.14.1 Zenodo record. Independent
verification of Zenodo metadata and deposited file identity remains part of
the post-release closeout audit.

## Scope and claim boundary

Version 0.14.1 changes release engineering and governance only. It changes no
arithmetic algorithm, public Python API, vendored Lean source, or mathematical
claim boundary. Python remains independently implemented and theorem-aligned;
it is not Lean-extracted or end-to-end formally verified.

## Historical evidence treatment

`V0141_PREPARATION_MANIFEST.json` and its original candidate-state fields are
historical preparation evidence. The synchronized manifest and checksum
inventory at the closeout commit record the additive post-publication state.
No claim is made that the post-release closeout commit is the published tag.

## Remaining gate

An independent read-only post-release audit must confirm the published tag,
GitHub release, two assets, Zenodo record, DOI metadata, and this additive
closeout synchronization before the v0.14.1 governance transaction is marked
fully closed and GREEN.
