# Lean formalization alignment — CNRS Q2

## Purpose

This record connects the machine-checked Lean 4 Q2 formalization to the current CNRS Scientific Toolkit implementation without collapsing distinct evidence levels.

The evidence chain is:

`paper/programme theorem -> Lean theorem -> software contract -> Python implementation -> regression/cross-validation tests`

A Lean proof establishes the mathematical statement encoded in Lean. It does not automatically certify that an independently written Python routine implements that theorem. Where a direct software refinement has not yet been proved, the status below is **formal theorem + tested implementation**, not end-to-end formally verified software.

## Formal project identity

- Repository path: `formal/lean/CnrsQ2/`
- Lean: `v4.33.0`
- Mathlib: `v4.33.0`
- Formal source snapshot: CNRS Q2 v3, 2026-08-30
- Formal source status: zero `sorry` in the maintained project source

## Theorem-to-implementation crosswalk

| Lean source / theorem | Mathematical content | Toolkit target | Alignment status |
|---|---|---|---|
| `Basic.lean` (`norm_beta`, `prime_beta`) | `beta=-2+i`, norm 5, Gaussian primality foundation | `cnrs.core.base`, `cnrs.gaussian_valuation` | Direct mathematical contract; implementation independently tested |
| `DigitAlphabet.lean` (`digit_bijective` and residue map results) | `{0,...,4}` is the residue digit system modulo beta | `cnrs.core.digits`, normalization code | Direct mathematical contract; implementation independently tested |
| `HenselRoot.lean` | Hensel construction of a square root of `-1` in `Z_5` with required residue | `cnrs.topology` theory layer | Formal foundation/context; no runtime Hensel dependency required |
| `Embedding.lean` | Injective ring embedding `Z[i] -> Z_5`, beta has norm `1/5` | `cnrs.topology`, `cnrs.gaussian_valuation` | Formal foundation for beta-adic interpretation |
| `Density.lean` (`padicInt_is_beta_adic_completion`) | Dense image and integer-level Q2 capstone | `cnrs.topology` | Formal foundation for natural beta-adic completion claim |
| `FieldLevel.lean` (`padic_is_beta_adic_completion_field`) | Field-level embedding into `Q_5`, dense image, beta valuation | rational/local-field interpretation | Formal foundation; Python field representation is not claimed to be Lean-extracted |
| `DigitExpansion.lean` (`exists_unique_digitP`) | unique next digit modulo maximal ideal in `Z_5` | finite digit/residue logic and `cnrs.topology` | Completion-level mathematical contract; current Python code supplies related finite witnesses, not a runtime `Z_5` refinement |
| `DigitExpansion.lean` (`exists_unique_reduction`) | unique `y = digit + pi*y'` step in `Z_5` | finite/exact reduction and topology layers | Completion-level formal reduction theorem; Python reduction/classification code is independently tested and is not Lean-extracted |
| `DigitExpansion.lean` (`partialSum_digitSeq_spec`) | exact completion-level reconstruction remainder identity | `cnrs.topology`; expansion verification concepts | Formal invariant suitable for future property tests; general floating-point `InfiniteExpansion` is not identified with this `Z_5` construction |
| `DigitExpansion.lean` (`tendsto_partialSum_digitSeq`) | canonical partial sums converge in the beta-adic completion | `cnrs.topology` | Formal convergence theorem in the beta-adic domain; no ordinary-complex convergence claim |
| `DigitExpansion.lean` (`digitSeq_unique`) | uniqueness of the convergent digit sequence | canonical beta-adic expansion semantics | Formal uniqueness theorem; runtime finite/rational canonicalizers remain independently tested |
| `DigitExpansion.lean` (`exists_unique_digit_expansion`) | full existence-and-uniqueness Q2b theorem | topology/completion theorem layer | Formal capstone; the Toolkit does not yet expose a general executable `Z_5` infinite-stream object, and this is not an ordinary complex analytic convergence claim |

## Claim-status wording

Use the following vocabulary in Toolkit documentation:

- **Lean-verified mathematical theorem** — the theorem is present in the maintained Lean project and builds under the pinned toolchain.
- **Theorem-aligned implementation** — Python is designed/tested against the theorem's contract, but no extraction/refinement proof connects executable Python to Lean.
- **Computationally verified** — tests/cross-validation support the implementation within stated domains.
- **Open** — neither the Lean project nor the current theorem records establish the claim.

Do not use “formally verified Toolkit” as a blanket description. The accurate statement is that selected CNRS Q2 mathematical claims are Lean-verified and linked to theorem-aligned Python implementations.

## Scope boundary

The Q2 formalization concerns the natural beta-adic completion and its digit expansion. It does not identify that completion with the ordinary complex plane, prove unrestricted ordinary complex analytic convergence, settle the e-base CNS question, or certify the physical interpretation of CNRS/Scale Space applications.
