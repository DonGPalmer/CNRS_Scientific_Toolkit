# P2-L10 theorem boundary — frozen before certification

Status: **FROZEN FOR P2-L10 CANDIDATE**

P2-L10 may add only finite-support Hurwitz antiderivation with an explicit
constant coefficient, its exact inverse laws with the governed derivative,
fail-closed serialized operations, and compatibility with the governed branch
transport and P2-L9 attachment bridge.

## Required declaration families

- `FiniteHurwitz.antideriv`, inserting a chosen coefficient at index zero and
  shifting every existing coefficient upward;
- exact coefficient-zero and successor-coefficient semantics;
- `FiniteHurwitz.deriv_antideriv` and
  `FiniteHurwitz.antideriv_coeff_zero_deriv`;
- injectivity for a fixed constant and equality classification by derivative
  plus constant coefficient;
- fail-closed `antiderivFiniteHurwitzCode`, with canonical success, complete
  success and rejection characterizations, and exact value semantics;
- both serialized differentiation–antiderivation compositions on canonical
  inputs;
- `antiderivBranchedFiniteHurwitz`, preserving the value construction and
  exact branch metadata, with both inverse laws;
- fail-closed `antiderivBranchedFiniteHurwitzCode`, with complete success and
  rejection characterizations and exact raw-value semantics; and
- compatibility with branch transport, P2-L9 attachment and attached coding,
  and P2-L8 relative-branch invariance for pairs.

## Frozen policy

P2-L10 concerns finite coefficient families only. It does not introduce
analytic, path, or contour integration; convergence; infinite Hurwitz series
or arbitrary streams; inferred constants of integration; factorial division;
unequal-branch arithmetic; the separate `CNRSIntegration` project;
`CNRSArithmetic`; `CNRSProblem1`; or Scale Space semantics.
