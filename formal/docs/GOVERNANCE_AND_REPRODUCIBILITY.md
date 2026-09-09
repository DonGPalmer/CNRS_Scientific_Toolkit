# Lean Governance and Reproducibility

Status date: 2026-09-09

## Authority model

| Layer | Role |
|---|---|
| SSC Formal Methods GitHub repository | Active Lean development, exact-byte CI, and auditable candidate/authoritative branches |
| `/_SSC/25_Formal Methods/30_Lean4/` | Governed programme copy and rollback snapshots |
| CNRS Scientific Toolkit working tree | Documentation and future release integration |
| Toolkit GitHub repository | Public software development and independent Python/Lean workflows |
| Zenodo | Immutable, citable release archive |

No Lean source should be edited independently inside the Toolkit. A Toolkit release must vendor an exact snapshot from a certified authoritative formal-methods endpoint and record the identity in `PROVENANCE.json`.

## Candidate-to-authoritative process

1. Freeze a theorem boundary and exact baseline.
2. Develop on a candidate branch without changing the governed Dropbox project.
3. Run pinned, normal offline, and clean network-disabled builds.
4. Gate source identities, dependencies, proof markers, declarations, warnings, and byte stability.
5. Obtain an independent mathematical and evidence audit.
6. Repair and re-certify if required.
7. Create a complete pre-promotion rollback snapshot.
8. Promote exact audited bytes to Dropbox.
9. Rebuild on an authoritative GitHub branch.
10. Independently verify the final artifact ZIP and checksum inventory.

## Reproduction requirements

Every formal release record should include:

- repository and branch;
- commit and tree SHA;
- Lean and Mathlib pins;
- authoritative workflow run and job;
- artifact ID, size, and SHA-256 digest;
- source-file SHA-256 inventory;
- frozen declaration inventory;
- proof-marker and prohibited-dependency results;
- normal and clean offline build logs;
- pre/post-build byte comparison;
- exact baseline-to-release delta.

## Toolkit integration rules

- Keep Python tests and Lean verification in separate workflows.
- Do not alter Python algorithms solely to accommodate source integration.
- Do not use a Git submodule as the only archived source because ordinary release ZIPs may omit submodule contents.
- Prefer a vendored, hash-verified Lean snapshot for public Toolkit and Zenodo releases.
- Preserve the active SSC Formal Methods history as the development provenance.
- Update the crosswalk whenever a theorem, Python contract, or status classification changes.

## Present state

The documents in this directory describe the governed state through P2-L8. Full Lean source vendoring and consolidated Toolkit release certification are intentionally deferred until the bounded completion programme is finished.
