# v0.13.0 — CNRS Lean Capstone Alignment

**Status:** release candidate preparation  
**Date:** 2026-09-11

v0.13.0 vendors the exact CNRS-LEAN-CAPSTONE source snapshot and synchronizes
the Toolkit's theorem inventory, provenance, claim crosswalk and independent
Lean CI with the closed six-project formal-methods campaign.

## Added

- all six certified Lean projects under `formal/lean/`;
- capstone checksum inventory, audit and final verdict;
- machine-readable consolidated identity in `formal/PROVENANCE.json`;
- six-project matrix build in the independent Lean workflow;
- repository guards for exact source identity and proof hygiene;
- P2-L9 branch-point attachment and P2-L10 finite-antiderivative crosswalks.

## Certified upstream identity

Commit `07e776b4e1d7d09513394a4b676516eb51e4c597`, tree
`fd61bac37369f8e3020d70141c565a4fba414a98`, run `34534566879`, job
`103063055916`, artifact `10175389923`, SHA-256
`840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21`.

The upstream certification records 79 Lean files, 14,341 lines, six normal and
six clean network-disabled builds, 3,042 jobs per project build, byte-stable
source and clean proof-hygiene gates.

## Runtime impact

No Python arithmetic behavior is changed solely by this synchronization.
Python remains independently implemented and theorem-aligned, not
Lean-extracted.

Candidate Python validation: `1218 passed, 0 failed`. The 921 warnings
comprise the retained reliable-domain diagnostics plus four pytest
deprecation warnings.

## Scope boundary

This release does not enlarge finite results to infinite series, analytic
continuation, path reconstruction, unequal branches, unrestricted streaming
arithmetic, or all complex numbers.
