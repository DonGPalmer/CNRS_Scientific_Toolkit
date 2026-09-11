# CNRS Toolkit–Lean Claim Crosswalk

Status date: 2026-09-11  
Formal boundary: CNRS-LEAN-CAPSTONE

| Toolkit claim or capability | Toolkit area | Lean evidence | Alignment status |
|---|---|---|---|
| Base `-2+i`, norm 5 and five residue digits | core/digits | CNRSCore; CnrsQ2 | Lean-verified contract; Python separately tested |
| Natural beta-adic completion and unique digits | topology | CnrsQ2 | Lean-verified in `Z_5/Q_5`; not ordinary-complex convergence |
| Finite addition and exact division recurrence | arithmetic | CNRSArithmetic E1–E2; CNRSIntegration | Lean-verified model; Python not extracted |
| Bounded-state periodicity and classified outcomes | rational/periodic | CNRSArithmetic E3–E11; CNRSProblem1 | Lean-verified under frozen hypotheses |
| Frozen finite-state model cannot supply unrestricted online multiplication | transducer diagnostics | CNRSArithmetic Phase F | Verified obstruction for that model, not for every method |
| Problem 1 negative-base and quadratic cases | representation modules | CNRSProblem1 P1-L1–L7 | Lean-verified within explicit bases/hypotheses |
| Finite Laurent carrier and canonical codec | rational/value codec | CNRSProblem2 P2-L4 | Lean-verified, fail-closed operations |
| Finite Hurwitz product, derivative and Leibniz law | CNRS-H | CNRSProblem2 P2-L5 | Lean-verified for finite support |
| Explicit branch labels and equal-branch arithmetic | branch state | CNRSProblem2 P2-L6–L8 | Lean-verified partial-operation policy |
| Canonical branch-point attachment | branch integration | CNRSProblem2 P2-L9 | Lean-verified metadata bridge; no path reconstruction |
| Finite antiderivative/derivative reversal | CNRS-H calculus | CNRSProblem2 P2-L10 | Lean-verified finite coefficient law |
| Python scientific examples | workflows | no end-to-end refinement | Computationally verified within documented domains |
| Scale Space physical interpretation | applications | no current Lean derivation | Conditional/open research |

## Required wording

Use **Lean-verified mathematical theorem**, **theorem-aligned
implementation**, **computationally verified**, and **open** as distinct
evidence levels. Do not call the entire Python Toolkit formally verified.

## Deliberate exclusions

The crosswalk does not infer infinite-series serialization, analytic continuation,
winding-path recovery, unequal-branch arithmetic, unrestricted
streaming multiplication/division, or a universal complex representation.
