# Governed Lean Theorem Inventory

Status date: 2026-09-11  
Authority: CNRS-LEAN-CAPSTONE

| Project | Governed boundary | Principal verified content |
|---|---|---|
| CNRSCore | v1 | Gaussian base/digits, quotient steps, finite words and finiteness |
| CnrsQ2 | v5 | beta-adic completion, unique digits, finite-support carrier and stream completion |
| CNRSArithmetic | E1–E11; Phase F | addition, exact division, finite-state outcomes, representatives and online-multiplication obstruction |
| CNRSIntegration | E1 | exact bridge between CNRSArithmetic and CnrsQ2 |
| CNRSProblem1 | P1-L1–L7 | alternating order, admissibility, cylinders, orbit language, quadratic periodicity and negabinary normalization |
| CNRSProblem2 | P2-L1–L10 | branch cover, canonical lift, serialization, finite Laurent/Hurwitz algebra, transport, relative normalization, branch attachment and antiderivative reversal |

## Problem 2 layers

| Layer | Source | Boundary |
|---|---|---|
| P2-L1 | `BranchCover.lean` | branch carrier and quotient-compatible operations |
| P2-L2 | `CanonicalLiftedLog.lean` | canonical lifted logarithm/exponential |
| P2-L3 | `BranchSerialization.lean` | canonical lossless branch serialization |
| P2-L4 | `FiniteLaurentValueCodec.lean` | finite Laurent carrier and fail-closed codec arithmetic |
| P2-L5 | `FiniteHurwitz.lean` | finite Hurwitz ring, derivative and Leibniz law |
| P2-L6 | `BranchedFiniteHurwitz.lean` | branch-labelled values and equal-branch arithmetic |
| P2-L7 | `BranchTransport.lean` | integer branch transport and equivariance |
| P2-L8 | `BranchOrbit.lean` | pair orbits, relative branch and canonical normal form |
| P2-L9 | `CNRSIntegration.lean` | branch-point attachment and compatibility bridge |
| P2-L10 | `FiniteHurwitzAntiderivative.lean` | finite antiderivative, inverse laws and serialized bridge |

## Evidence boundary

The exhaustive source inventory is `formal/capstone/SHA256SUMS.txt`; the
reader-facing audit is `formal/capstone/CNRS_LEAN_CAPSTONE_AUDIT.md`.
The release certifies the finite kernel only and does not extend any theorem
to arbitrary infinite streams, analytic continuation, unequal branches,
unrestricted streaming arithmetic, or all complex numbers.

