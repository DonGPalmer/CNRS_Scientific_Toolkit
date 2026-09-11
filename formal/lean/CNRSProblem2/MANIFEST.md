# CNRSProblem2 P2-L10 candidate manifest

Status: **IMPLEMENTATION COMPLETE / P2-L10 CANDIDATE CERTIFICATION PENDING**

## Layer

P2-L10 — Finite Hurwitz Antiderivative and Exact Reversal.

## Exact governed baseline

- Authoritative P2-L9 branch: `cnrsproblem2-p2-l9-authoritative-live`
- Authoritative P2-L9 head:
  `be9f20f49e3878d639ec09b742c2c88e8afe66a9`
- Exact complete baseline tree:
  `4484945f2a46cca87e1eeab185d3b69fbbed201e`
- Authoritative P2-L9 workflow run: `34395065351` — **SUCCESS**
- Authoritative P2-L9 artifact: `10121389343`
- Artifact SHA-256:
  `78dd41f4515095d35cc108ef39a32504e1f09691fdcca23556eb121184eef0a3`

The governed Dropbox project remains unchanged at P2-L9 during candidate
development and audit.

## Declared P2-L10 project delta

- modified `CNRSProblem2.lean`;
- added `CNRSProblem2/FiniteHurwitzAntiderivative.lean`;
- added `P2_L10_THEOREM_BOUNDARY_FROZEN.md`;
- modified `README.md`; and
- modified `MANIFEST.md`.

The candidate certification workflow is the only repository-level addition.

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

## Acceptance requirements

The final workflow must enforce the exact P2-L9 baseline and five-file project
delta, source identities, frozen declarations, proof-marker and prohibited
dependency gates, three pinned builds including a clean network-disabled
rebuild, candidate warning checks, byte stability, and complete evidence
packaging.

This candidate is not eligible for Dropbox promotion until an independent
audit returns GREEN and the user gives separate explicit authorization.
