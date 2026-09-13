# Lean formalization alignment — v0.14.1 note

v0.14.1 does not modify the vendored Lean source or enlarge the formal proof
boundary. The six-project CNRS-LEAN-CAPSTONE alignment remains unchanged.
The v0.14.0 streaming-division implementation does not enlarge the governed
Lean proof boundary. Python recurrence and witness fields are aligned with
existing Gaussian-rational periodicity and canonical-normalization concepts
where available. Lazy iteration, JSON serialization, benchmark behavior, and
Python witness validation are computationally verified runtime properties, not
Lean theorems. The released capstone alignment record follows.

# Lean Formalization Alignment — CNRS-LEAN-CAPSTONE

CNRS means **Complex Numeric Representation System**.

## Purpose

This record connects the six-project governed Lean release to the CNRS
Scientific Toolkit without collapsing mathematical proof, Python
implementation, testing, and scientific interpretation into one evidence
level.

The detailed reader-facing crosswalk is
[`formal/docs/TOOLKIT_LEAN_CROSSWALK.md`](../formal/docs/TOOLKIT_LEAN_CROSSWALK.md).

## Formal identity

- source repository: `DonGPalmer/SSC_Formal_Methods_CI`;
- consolidated commit: `07e776b4e1d7d09513394a4b676516eb51e4c597`;
- tree: `fd61bac37369f8e3020d70141c565a4fba414a98`;
- workflow run/job: `34534566879` / `103063055916`;
- artifact: `10175389923`;
- artifact SHA-256: `840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21`;
- Lean: `v4.33.0`;
- source: 79 Lean files, 14,341 lines.

## Governed public release

The certified formal package is publicly released as:

- repository: `DonGPalmer/CNRS_Lean`;
- tag: `v1.0.3`;
- commit: `ce56a7359f494d29bab8e9bea6c3ea596f8fd62f`;
- Zenodo version DOI: `10.5281/zenodo.22727725`;
- Zenodo concept DOI: `10.5281/zenodo.22726349`.

The public release is the governed publication of the certified source. It
does not replace the private capstone record as certification authority.

## Verified projects

| Project | Boundary |
|---|---|
| CNRSCore | finite Gaussian foundation |
| CnrsQ2 | beta-adic completion and digit expansion |
| CNRSArithmetic | E1–E11 and Phase F |
| CNRSIntegration | E1 Addition Bridge |
| CNRSProblem1 | P1-L1 through P1-L7 |
| CNRSProblem2 | P2-L1 through P2-L10 |

The exact source is vendored under `formal/lean/`; source identity is checked
against `formal/capstone/SHA256SUMS.txt`.

## Evidence vocabulary

- **Lean-verified mathematical theorem** — present in the certified project.
- **Theorem-aligned implementation** — Python follows the contract but is not
  extracted from Lean.
- **Computationally verified** — supported by tests within stated domains.
- **Open or conditional** — outside the certified boundary.

Do not describe the entire Toolkit as formally verified.

## Boundary

The capstone does not prove arbitrary infinite serialization, ordinary-complex
analytic convergence, analytic continuation or path recovery, unequal-branch
arithmetic, unrestricted streaming multiplication/division, or a universal
complex-representation theorem.
