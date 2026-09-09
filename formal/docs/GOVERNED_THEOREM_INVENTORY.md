# Governed Lean Theorem Inventory

Status date: 2026-09-09  
Inventory type: principal theorem families, not a generated declaration dump

## CNRSCore and CnrsQ2

| Area | Principal verified content | Governed status |
|---|---|---|
| Gaussian base | `β = -2 + i`, norm 5, primality and divisibility foundations | Governed |
| Digit alphabet | digits `0,…,4` form the required residue system modulo `β` | Governed |
| Reduction | unique digit/remainder reduction | Governed |
| Completion | embeddings into `ℤ₅` and `ℚ₅`, density, and beta-adic interpretation | Governed |
| Infinite beta-adic digits | existence and uniqueness of the canonical `Fin 5` expansion and convergence of partial sums | Governed |
| Shared infrastructure | normalization, finite-state, finiteness, and fixed-multiplier foundations used by later projects | Governed |

Representative Q2 declarations include `norm_beta`, `prime_beta`, `digit_bijective`, `exists_unique_digitP`, `exists_unique_reduction`, `partialSum_digitSeq_spec`, `tendsto_partialSum_digitSeq`, `digitSeq_unique`, and `exists_unique_digit_expansion`.

## CNRSArithmetic through E11 and Phase F

| Milestone family | Principal verified content |
|---|---|
| E1–E2 | addition bridge and exact-division recurrence |
| E3–E4 | finite carriers, state bounds, and eventual periodicity |
| E5–E7 | termination, cycle classification, and constructive cycle enumeration |
| E8–E9 | decision witnesses and minimal-period results |
| E10–E11 | outcome machine and representative-integrity results |
| Phase F | finite-state/online multiplication impossibility boundary under the frozen model |

This track formalizes exact algebraic and finite-state claims. It does not establish an efficient general arithmetic engine for arbitrary infinite streams.

## CNRSProblem1 through P1-L7

| Layer | Principal verified content |
|---|---|
| P1-L1–L4 | finite-representation foundation, evaluation, termination, and canonical structural results |
| P1-L5 | strengthened finite/periodic representation results |
| P1-L6 | quadratic-lattice boundedness and eventual periodicity, including the stated quadratic specialisations |
| P1-L7 | exact negabinary (`β = -2`) specialisation and repaired theorem boundary |

The quadratic results are specialised statements with explicit hypotheses; they are not blanket periodicity theorems for every algebraic base.

## CNRSProblem2 through P2-L8

| Layer | Source | Principal verified content |
|---|---|---|
| P2-L1 | `BranchCover.lean` | lifted logarithmic branch coordinates and coordinate equivalence, including the converse classification |
| P2-L2 | `CanonicalLiftedLog.lean` | canonical lifted-coordinate representative and exact recovery |
| P2-L3 | `BranchSerialization.lean` | canonical self-delimiting integer branch codec, fail-closed decoding, and lossless compositions |
| P2-L4 | `FiniteLaurentValueCodec.lean` | `R_A = ℤ[i][(-2+i)⁻¹]`, canonical finite Laurent codec, normalization, and fail-closed code operations |
| P2-L5 | `FiniteHurwitz.lean` | finite-support Hurwitz convolution, commutative ring structure, derivative, and Leibniz rule |
| P2-L6 | `BranchedFiniteHurwitz.lean` | branch-labelled finite-Hurwitz codec and equal-branch fail-closed arithmetic |
| P2-L7 | `BranchTransport.lean` | integer branch transport, composition, invariants, serialized transport, and arithmetic equivariance |
| P2-L8 | `BranchOrbit.lean` | diagonal pair transport, relative-branch invariant, orbit classification, canonical relative normal form, and arithmetic-domain classification |

### P2-L4 operation contract

`addFiniteLaurentCode`, `mulFiniteLaurentCode`, and `negFiniteLaurentCode` decode every required input, return `Option`, reject noncanonical codes, and canonically encode successful results.

### P2-L5 Hurwitz algebra

For finite-support sequences over a commutative coefficient ring,

`(a*b)ₙ = Σ_{i+j=n} binomial(n,i) aᵢ bⱼ`,

and the shift derivative `(Da)ₙ = aₙ₊₁` satisfies `D(xy) = D(x)y + xD(y)`.

### P2-L6 branch policy

Addition and multiplication are partial on branch-labelled states and succeed only after both canonical inputs decode and their branch indices agree. Negation and differentiation preserve the decoded branch. No unequal-branch arithmetic law is inferred.

### P2-L7–L8 branch geometry

Transport is `Tₘ(x,k) = (x,k+m)`. Diagonal transport preserves the relative branch `Δ = l-k`. Ordered pairs are classified by their two finite-Hurwitz values and `Δ`, with canonical representative branches `(0,Δ)`. Equal-branch arithmetic is exactly the `Δ = 0` sector.

## Inventory maintenance

The final consolidated release should generate an exhaustive declaration inventory directly from the certified Lean environment. This document should remain the reader-facing thematic inventory.
