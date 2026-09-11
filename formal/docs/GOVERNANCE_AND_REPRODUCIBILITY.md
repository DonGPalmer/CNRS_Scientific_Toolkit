# Lean Governance and Reproducibility

Status date: 2026-09-11

## Authority model

| Layer | Role |
|---|---|
| SSC Formal Methods GitHub | Lean development and exact-byte CI |
| SSC Dropbox Formal Methods | authoritative governed projects and immutable releases |
| CNRS Scientific Toolkit | public vendored snapshot and theorem-to-software alignment |
| Zenodo | immutable citable Toolkit releases |

The Toolkit source must not be edited independently. It is vendored from the
certified capstone artifact.

## Capstone identity

- branch: `cnrs-lean-consolidated-release-candidate`;
- commit: `07e776b4e1d7d09513394a4b676516eb51e4c597`;
- tree: `fd61bac37369f8e3020d70141c565a4fba414a98`;
- workflow run/job: `34534566879` / `103063055916`;
- artifact: `10175389923`;
- artifact SHA-256: `840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21`.

## Toolkit verification

1. Run `python tools/check_lean_alignment.py` from the repository root. This
   is the supported Toolkit-layout verification command: it remaps the
   upstream inventory's preserved `./release/...` paths to
   `formal/lean/...` and verifies every checksum.
2. Confirm the command reports the exact six-project, 79-file inventory and a
   clean proof-marker gate.
3. Run the Python suite independently.
4. Build all six Lean projects in the Lean workflow.
5. Confirm no forbidden proof markers and no source drift.
6. Record the Toolkit commit and release artifact checksum.

Python and Lean results remain separate. A Toolkit release may report both,
but it must not describe the independently written Python runtime as
Lean-extracted or end-to-end formally verified.
