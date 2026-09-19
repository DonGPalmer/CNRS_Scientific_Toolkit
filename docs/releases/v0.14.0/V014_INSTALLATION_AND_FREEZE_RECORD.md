# v0.14.0 installation and freeze record

Freeze date: 2026-09-12  
Target repository: DonGPalmer/CNRS_Scientific_Toolkit  
Target release: v0.14.0  
Baseline release: v0.13.1  
Baseline commit: e7f8424a967292a36643bb5fa8206ccb1d3f8fcd  
Baseline tree: c2364123aef02514bc242c8ea0796dc7d7c1cdde

## Purpose

This record originated with the copy-into-existing-folder-structure
preimplementation freeze. The candidate now implements that frozen scope.
V014_FREEZE_AMENDMENT_2026-09-12.md records the two technical clarifications
made during implementation.

## Placement

Copy docs, acceptance, and benchmarks into the corresponding repository-root folders. Preserve v0.13.1 files unchanged. V014_FREEZE_MANIFEST.json and V014_SHA256SUMS.txt are governance records and may be kept at the repository root or in the release evidence directory.

The synchronized documents now describe an implementation candidate with local
gates GREEN. They do not authorize release. GitHub CI and independent audit
remain required as stated in V014_RELEASE_ACTIVATION_CHECKLIST.md.

## Frozen decision

The implementation target is exact Gaussian-rational streaming division with bounded, honest resolution states and deterministic witnesses. Existing materialized APIs remain supported. LIMIT_REACHED is not a mathematical conclusion.

## Preimplementation gate

After placement, syntax compilation of the acceptance file must pass, while pytest collection must fail because the new modules are absent. Record that as EXPECTED RED, not as a v0.13.1 regression.

## Release title

CNRS Scientific Toolkit v0.14.0 — Streaming Division and Formal–Runtime Witness Alignment
