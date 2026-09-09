# CNRS Toolkit–Lean Claim Crosswalk

Status date: 2026-09-09  
Formal boundary: governed Lean work through P2-L8

| Toolkit claim or capability | Toolkit area | Lean evidence | Alignment status |
|---|---|---|---|
| Gaussian base `-2+i` has norm 5 and supports the five residue digits | core/digit modules | `CNRSCore`, `CnrsQ2` | Lean-verified mathematical contract; Python separately tested |
| Natural beta-adic completion and unique digit sequences | topology layer | `CnrsQ2` completion and digit-expansion theorem families | Lean-verified in `ℤ₅`/`ℚ₅`; not ordinary-complex convergence |
| Exact finite addition and division recurrence | arithmetic/normalization modules | `CNRSArithmetic` E1–E2 | Lean-verified model; implementation not Lean-extracted |
| Bounded deterministic states imply eventual periodicity | rational/periodic modules | `CNRSArithmetic` E3–E9 and `CNRSProblem1` | Lean-verified under frozen hypotheses |
| Outcome classification and canonical representatives | arithmetic classification utilities | `CNRSArithmetic` E10–E11 | Lean-verified model; software alignment remains test-based |
| General online multiplication cannot be supplied by the frozen finite-state model | transducer diagnostics | `CNRSArithmetic` Phase F | Lean-verified impossibility boundary; not a claim that multiplication is impossible by all methods |
| Finite Laurent coefficients represent `ℤ[i][(-2+i)⁻¹]` | rational/value codec | `CNRSProblem2.FiniteLaurentValueCodec` | Lean-verified carrier, codec, normalization, and fail-closed operations |
| Formal CNRS-H finite-truncation multiplication uses binomial convolution | CNRS-H algebra modules | `CNRSProblem2.FiniteHurwitz` | Lean-verified for finite support |
| CNRS-H differentiation is coefficient shift and obeys Leibniz | CNRS-H calculus | `FiniteHurwitz` derivative theorems | Lean-verified for finite support; right-shift integration and infinite analytic realization are separate |
| Branch-labelled finite-Hurwitz states serialize canonically | branch/hybrid state modules | `BranchedFiniteHurwitz` plus P2-L3 codecs | Lean-verified representation contract |
| Invalid or noncanonical serialized operation inputs fail explicitly | codec-facing operations | P2-L4, P2-L5, and P2-L6 `Option` operation theorem families | Lean-verified fail-closed contract |
| Common branch transport preserves values and operation behavior | branch algebra | `BranchTransport` | Lean-verified common-shift equivariance |
| Relative branch classifies diagonal branch-pair orbits | branch/surface helpers | `BranchOrbit` | Lean-verified finite pair-state result; not a general Riemann-surface constructor |
| Python scientific examples reproduce stated equations | examples/workflows | no end-to-end Lean refinement | Computationally verified only within documented test domains |
| Scale Space physical interpretation | scientific applications | no current Lean derivation | Open/conditional research |

## Required wording

Use “Lean-verified mathematical theorem” for the formal statements. Use “theorem-aligned implementation” where Python realizes the same intended contract but is connected only by design review and tests.

Do not infer any of the following from this crosswalk:

- that Lean has verified the Python interpreter or runtime;
- that a finite-support result automatically applies to infinite series;
- that beta-adic convergence is ordinary complex analytic convergence;
- that branch metadata reconstructs an analytic continuation path;
- that a diagnostic or impossibility theorem supplies a new algorithm.

## Crosswalk gaps to close before consolidated release

1. Prove the P2 compatibility bridge to the earlier `BranchPoint` and canonical lifted-coordinate interfaces.
2. Provide one integrated P2 codec/API capstone.
3. Prove explicit overlap agreements among `CNRSCore`, `CNRSArithmetic`, `CNRSProblem1`, and `CNRSProblem2`.
4. Add property tests whose fixtures are generated from frozen Lean theorem examples where practical.
5. Decide which Python APIs are sufficiently aligned to be labelled theorem-aligned rather than merely computationally verified.
