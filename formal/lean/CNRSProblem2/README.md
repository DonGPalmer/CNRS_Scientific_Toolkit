# CNRSProblem2 — P2-L10 finite-Hurwitz antiderivative

P2-L10 extends the governed P2-L1–P2-L9 development with an exact
finite-support Hurwitz antiderivative. A caller supplies the constant
coefficient; all other coefficients are shifted upward by one index.

## Governed certification

P2-L10 is promoted and authoritatively certified at commit
`38e38ceae3b9847c5fa4753145eabadec544e8fe`, artifact `10158719731`.
The consolidated capstone workflow passed as run `34534566879`, job
`103063055916`, artifact `10175389923`, SHA-256
`840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21`.

## Governed P2-L9 predecessor

P2-L9 was promoted and authoritatively certified at commit
`be9f20f49e3878d639ec09b742c2c88e8afe66a9`, workflow run
`34395065351`. Its branch-carrier integration bridge remains unchanged.

## P2-L10 additions

- finite-support Hurwitz antiderivation with an explicit constant coefficient;
- exact coefficient-zero and successor-coefficient formulas;
- exact differentiation–antiderivation reversal in both directions;
- reconstruction and equality classification from derivative plus constant;
- fail-closed sparse-code antiderivation, with complete success and rejection
  characterizations and exact value semantics;
- exact serialized differentiation–antiderivation compositions;
- branch-aware antiderivation preserving explicit branch metadata;
- fail-closed branch-code antiderivation with exact raw-value semantics; and
- compatibility with P2-L7 transport, P2-L9 attachment and attached coding,
  and P2-L8 relative-branch invariance.

## Explicit exclusions

P2-L10 does not introduce analytic, path, or contour integration,
convergence, infinite Hurwitz series or arbitrary streams, inferred constants
of integration, factorial division, unequal-branch arithmetic, or streaming
arithmetic. It does not import `CNRSArithmetic`, `CNRSProblem1`, the separate
`CNRSIntegration` project, the Toolkit, or Scale Space code.

## Environment and dependencies

- Lean 4.33.0
- Mathlib 4.33.0
- exact governed P2-L9 authoritative predecessor baseline
- governed CnrsQ2 v5 and CNRSCore v1 inherited unchanged
- no dependency on CNRSArithmetic, the separate CNRSIntegration project,
  CNRSProblem1, the Toolkit, or Scale Space code

Status: **AUTHORITATIVELY CERTIFIED / CONSOLIDATED RELEASE GREEN**.

P2-L10 passed exact-byte certification, independent audit, separate promotion,
and consolidated capstone certification. The P2-L9 identity above is retained
as the historical predecessor baseline.
