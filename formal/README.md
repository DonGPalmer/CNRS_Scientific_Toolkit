# CNRS Scientific Toolkit — Formal Verification

Status date: 2026-09-09  
Coverage boundary: governed Lean work through CNRSProblem2 P2-L8

## Purpose

This documentation connects the CNRS Scientific Toolkit to the separately governed Lean 4 formalization programme. It distinguishes mathematical proof, executable software, tests, and research hypotheses.

The evidence chain is:

`CNRS claim → Lean statement → machine-checked proof → software contract → Python implementation → tests`

A Lean theorem verifies the mathematical statement encoded in Lean. It does not automatically verify an independently written Python routine. Unless a refinement theorem is provided, the accurate status is **Lean-verified mathematical theorem with a separately tested, theorem-aligned implementation**.

## Current verified foundation

The governed programme currently includes:

- `CNRSCore`: shared Gaussian-base, digit, normalization, finiteness, and transducer foundations;
- `CnrsQ2`: beta-adic completion and unique digit expansions;
- `CNRSArithmetic`: exact arithmetic, state bounds, periodicity and finite-state multiplication boundaries through Phase F;
- `CNRSProblem1`: finite representation, termination, periodicity, and negabinary specialisation through P1-L7;
- `CNRSProblem2`: lifted logarithmic coordinates, branch serialization, finite Laurent values, finite Hurwitz algebra, branch-labelled operations, transport, and orbit normal forms through P2-L8.

All four governed endpoints listed in `PROVENANCE.json` passed their authoritative GitHub Actions certification. The P2-L8 endpoint includes three successful builds of 3,050 jobs, including a clean network-disabled rebuild.

## Currently vendored Lean project

`formal/lean/CnrsQ2/` remains the Toolkit's directly buildable Lean source snapshot. It formalizes the Q2 beta-adic metric-completion and digit-expansion results for `β = -2+i`, with `N(β)=5` and digit alphabet `{0,1,2,3,4}`. The project is pinned to Lean 4.33.0 and its resolved Mathlib version.

From `formal/lean/CnrsQ2/` run:

```bash
lake build
```

The workflow `.github/workflows/lean.yml` builds this project independently of the Python test suite. The newer governed `CNRSCore`, `CNRSArithmetic`, `CNRSProblem1`, and `CNRSProblem2` projects are documented here but are not yet vendored into this Toolkit branch.

## Evidence vocabulary

| Label | Meaning |
|---|---|
| Lean-verified | A theorem is present in the governed source and compiles under the pinned toolchain. |
| Theorem-aligned | Software is designed or tested against the theorem's contract, without an end-to-end refinement proof. |
| Computationally verified | Tests or independent calculations support the implementation within a stated domain. |
| Conditional | A conclusion is proved or implemented under explicit hypotheses. |
| Open | The current governed theory does not establish the claim. |

Do not describe the whole Toolkit as “formally verified.” Selected mathematical claims are Lean-verified; Python components remain separately tested unless explicitly linked by a refinement proof.

## Documents

- `docs/GOVERNED_THEOREM_INVENTORY.md` — governed projects, milestones, and principal theorem families;
- `docs/TOOLKIT_LEAN_CROSSWALK.md` — Toolkit claims and modules mapped to formal evidence;
- `docs/FORMAL_SCOPE_AND_OPEN_PROBLEMS.md` — proved scope, exclusions, and research frontier;
- `docs/GOVERNANCE_AND_REPRODUCIBILITY.md` — authority model and reproduction procedure;
- `PROVENANCE.json` — machine-readable authoritative identities.

## Release status

These are documentation-stage records through P2-L8. They do not vendor the current Lean projects into a new Toolkit release. The exact consolidated Lean source snapshot should be added only after the compatibility bridge, capstone interface, cross-problem certification, and consolidated release certification are complete.
