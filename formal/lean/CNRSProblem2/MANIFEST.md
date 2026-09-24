# CNRSProblem2 P2-L10 authoritative manifest

Status: **AUTHORITATIVE CERTIFICATION PASS / CONSOLIDATED RELEASE GREEN**

## Layer

P2-L10 — Finite Hurwitz Antiderivative and Exact Reversal.

## Certification outcome

- Authoritative P2-L10 branch: `cnrsproblem2-p2-l10-authoritative-live`
- Authoritative P2-L10 head:
  `38e38ceae3b9847c5fa4753145eabadec544e8fe`
- Authoritative P2-L10 artifact: `10158719731`
- Consolidated release-candidate head:
  `07e776b4e1d7d09513394a4b676516eb51e4c597`
- Consolidated workflow run/job: `34534566879` / `103063055916` — **SUCCESS**
- Consolidated artifact: `10175389923`
- Consolidated artifact SHA-256:
  `840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21`

P2-L10 passed exact-byte certification, independent audit, separate promotion,
and consolidated capstone certification.

## Exact governed predecessor baseline

- Authoritative P2-L9 branch: `cnrsproblem2-p2-l9-authoritative-live`
- Authoritative P2-L9 head:
  `be9f20f49e3878d639ec09b742c2c88e8afe66a9`
- Exact complete baseline tree:
  `4484945f2a46cca87e1eeab185d3b69fbbed201e`
- Authoritative P2-L9 workflow run: `34395065351` — **SUCCESS**
- Authoritative P2-L9 artifact: `10121389343`
- Artifact SHA-256:
  `78dd41f4515095d35cc108ef39a32504e1f09691fdcca23556eb121184eef0a3`

This exact P2-L9 state was the frozen input during P2-L10 candidate
development and audit. It is retained as historical provenance and is not the
current P2 certification endpoint.

## Declared P2-L10 project delta

- modified `CNRSProblem2.lean`;
- added `CNRSProblem2/FiniteHurwitzAntiderivative.lean`;
- added `P2_L10_THEOREM_BOUNDARY_FROZEN.md`;
- modified `README.md`; and
- modified `MANIFEST.md`.

The P2-L10 candidate certification workflow was the only repository-level
addition during this layer.

## Implemented boundary

P2-L10 defines finite-support Hurwitz antiderivation with a supplied constant,
proves both exact inverse laws with the governed derivative, exposes
fail-closed sparse and branch-aware code operations, and proves compatibility
with branch transport, P2-L9 attachment, and relative-branch invariance.

## Exclusions

No theorem introduces analytic or contour integration, convergence, infinite
series or streams, an inferred integration constant, factorial division,
unequal-branch arithmetic, streaming arithmetic, CNRSArithmetic,
CNRSProblem1, the separate CNRSIntegration project, or Scale Space semantics.

## Certification result

The final workflow enforced the exact P2-L9 baseline and five-file project
delta, source identities, frozen declarations, proof-marker and prohibited
dependency gates, three pinned builds including a clean network-disabled
rebuild, warning checks, byte stability, and complete evidence packaging.
All requirements passed before authoritative promotion.
