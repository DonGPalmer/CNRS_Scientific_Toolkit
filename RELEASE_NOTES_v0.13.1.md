# v0.13.1 — Public Lean Release and Provenance Synchronization

**Status:** release candidate preparation  
**Date:** 2026-09-12

v0.13.1 is a documentation and provenance patch. It connects the six-project
CNRS-LEAN-CAPSTONE snapshot vendored in Toolkit v0.13.0 with its governed
public publication as CNRS Lean v1.0.3.

## Public CNRS Lean identity

- repository: \`DonGPalmer/CNRS_Lean\`;
- release/tag: \`v1.0.3\`;
- commit: \`ce56a7359f494d29bab8e9bea6c3ea596f8fd62f\`;
- Zenodo version DOI: \`10.5281/zenodo.22727725\`;
- Zenodo concept DOI: \`10.5281/zenodo.22726349\`;
- formal inventory: six projects and 79 Lean source files;
- toolchain: Lean 4.33.0.

## Certification provenance retained

The authoritative source certification remains the private
CNRS-LEAN-CAPSTONE record:

- repository: \`DonGPalmer/SSC_Formal_Methods_CI\`;
- branch: \`cnrs-lean-consolidated-release-candidate\`;
- commit: \`07e776b4e1d7d09513394a4b676516eb51e4c597\`;
- tree: \`fd61bac37369f8e3020d70141c565a4fba414a98\`;
- workflow run/job: \`34534566879\` / \`103063055916\`;
- artifact: \`10175389923\`;
- artifact SHA-256:
  \`840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21\`.

The public repository provides the governed publication of this certified
formal package; it does not replace the private certification authority.

## Terminology correction

The programme name is standardized as **Complex Numeric Representation System
(CNRS)**. The former wording “Complex Numeric Representational System” was not
the authoritative expansion.

## Runtime and theorem impact

No Python arithmetic behavior, scientific workflow behavior, vendored Lean
source, or mathematical claim is changed. The Python Toolkit remains an
independently implemented, theorem-aligned computational layer; it is not
Lean-extracted or end-to-end formally verified by the included Lean projects.

## Validation

Final Python counts, GitHub Actions run identities, distribution checksums,
release commit, and the v0.13.1 Zenodo version DOI are intentionally pending
until the exact candidate has passed independent verification.

Required gates include the full Python suite, all six Lean matrix builds,
\`python tools/check_lean_alignment.py\`, version synchronization, JSON/CFF
validation, exact 79-file Lean inventory, source-index verification,
distribution builds, and an installed-wheel smoke test.
