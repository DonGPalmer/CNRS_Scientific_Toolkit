# CNRS Lean Capstone Audit — P2-L1 through P2-L10

Date: 2026-09-10

## Final certification

**MATHEMATICS PASS / BOUNDARIES PASS / CONSOLIDATED RELEASE GREEN**

The subsequent consolidated workflow completed successfully as run
`34534566879`, job `103063055916`, artifact `10175389923`, SHA-256
`840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21`.

This capstone audit covers the complete governed CNRS Lean portfolio and the ten-layer CNRS Problem 2 chain. It does not extend any theorem boundary or add new mathematical claims.

## Frozen authoritative inputs

| Component | Authoritative identity |
|---|---|
| CNRSCore + CnrsQ2 | artifact `9830923099`; source commit `85007b340ab669dab8b9915e4f6a6064ff72b8f7` |
| CNRSArithmetic Phase F | commit `df064adff8266899880b15a9c2125826810eb083`; artifact `9976733222` |
| CNRSIntegration Phase E1 | commit `464d687f5c210b6d2eed34cbccbe54475259d0a9`; artifact `9831678250` |
| CNRSProblem1 P1-L7 | commit `8a770684f6cfc91cbf7363ca3848c802d9cc4548`; artifact `9971398183` |
| CNRSProblem2 P2-L10 | commit `38e38ceae3b9847c5fa4753145eabadec544e8fe`; artifact `10158719731` |

Every artifact ZIP digest is pinned in the consolidated workflow. The workflow reconstructs a single release tree from those exact evidence packages.

## P2-L1–P2-L10 audit findings

| Layer | Audited boundary | Capstone result |
|---|---|---|
| P2-L1 | Branch-cover carrier and quotient-compatible operations | PASS |
| P2-L2 | Canonical branch coordinate and lifted logarithm/exponential | PASS |
| P2-L3 | Lossless, self-delimiting branch serialization | PASS |
| P2-L4 | Finite Laurent value codec and fail-closed arithmetic | PASS |
| P2-L5 | Finite Hurwitz algebra, derivative, and sparse codec | PASS |
| P2-L6 | Branch-labelled finite Hurwitz values and equal-branch arithmetic | PASS |
| P2-L7 | Integer branch transport and operation equivariance | PASS |
| P2-L8 | Pair orbits, relative normal form, and zero-relative-branch domain | PASS |
| P2-L9 | Canonical branch-point attachment and integration bridge | PASS |
| P2-L10 | Finite antiderivative, derivative inverse law, and serialized bridge | PASS |

The two earlier audit defects remain closed: P2-L4 operations decode before operating, and P2-L8 explicitly proves raw-value preservation under pair normalization.

## Portfolio-level findings

- Inventory: 79 Lean source files and 14,341 source lines.
- Toolchain: all six projects pin Lean `v4.33.0` (commit `d8b18978322de05a8f3dba51ef03cf5461676c17`).
- Proof hygiene: no `sorry`, `sorryAx`, `admit`, added `axiom`, or `unsafe` declaration.
- Dependency policy: CNRSCore is foundational; CnrsQ2 and CNRSArithmetic depend only downstream on CNRSCore; CNRSIntegration bridges CNRSArithmetic and CnrsQ2; CNRSProblem1 is standalone; CNRSProblem2 depends on CNRSCore/CnrsQ2 and not on CNRSArithmetic, the separate CNRSIntegration project, or CNRSProblem1.
- Serialization policy: public serialized operations remain fail-closed at the governed codec boundaries.
- Branch policy: branch metadata is explicit; unequal-branch arithmetic remains rejected; common integer transport preserves the operation domain.
- Scope discipline: the release makes no claim of arbitrary infinite-series serialization, analytic continuation, path reconstruction, unequal-branch arithmetic, streaming multiplication/division, or general complex-number representation.

## Certification rule

The capstone becomes release-certified only if the consolidated workflow verifies every pinned artifact, verifies its internal inventories, compiles a cross-layer P2 declaration gate, completes all six normal builds, completes all six clean network-disabled rebuilds, detects no new project warnings, and proves pre-/post-build byte stability.
