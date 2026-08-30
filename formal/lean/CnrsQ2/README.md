# CnrsQ2 — Lean 4 formalization of the CNRS Q2 metric-completion theorem

**Status: ALL PHASES COMPLETE, zero sorries.**

## What is proven (machine-checked, Lean 4 v4.33.0 + Mathlib v4.33.0)

| File | Content | Sorries |
|---|---|---|
| `CnrsQ2/Basic.lean` | β = −2+i on Mathlib's `GaussianInt`; N(β)=5; prime-norm ⇒ irreducible (general lemma); **β prime in ℤ[i]** | 0 |
| `CnrsQ2/DigitAlphabet.lean` | Residue map φ(A+Bi)=(A+2B) mod 5, additive + multiplicative, φ(β)=0, **digit alphabet {0..4} bijective onto F₅** (thm:q2_digit_carrier(i)) | 0 |
| `CnrsQ2/HenselRoot.lean` | **√(−1) ∈ ℤ₅** via `hensels_lemma` on X²+1 at a=2 (‖F(2)‖=1/5 < 1=‖F′(2)‖²), with c ≡ 2 mod 5 | 0 |
| `CnrsQ2/Embedding.lean` | **φ : ℤ[i] →+* ℤ₅** via `Zsqrtd.lift`; **injective**; **‖φ(β)‖ = 1/5 exactly** (via (c−2)(c+2)=−5 + ultrametric unit argument) | 0 |
| `CnrsQ2/Density.lean` | **φ has dense range** (from `PadicInt.denseRange_intCast`); capstone `padicInt_is_beta_adic_completion` | 0 |
| `CnrsQ2/FieldLevel.lean` | **ψ : Frac(ℤ[i]) →+* ℚ₅** via `IsFractionRing.lift`; injective; dense (from `Padic.denseRange_ratCast`, rationals reached as num/den through ℤ[i]); capstone `padic_is_beta_adic_completion_field` | 0 |
| `CnrsQ2/DigitExpansion.lean` | **Phase 4, COMPLETE.** See below. | **0** |

**Capstone theorems (Q2a, zero sorries):**
```
theorem padicInt_is_beta_adic_completion :
    ∃ φ : GaussianInt →+* ℤ_[5],
      Function.Injective φ ∧ DenseRange φ ∧ ‖φ beta‖ = (5 : ℝ)⁻¹

theorem padic_is_beta_adic_completion_field :
    ∃ ψ : FractionRing GaussianInt →+* ℚ_[5],
      Function.Injective ψ ∧ DenseRange ψ ∧
      ‖ψ (algebraMap GaussianInt (FractionRing GaussianInt) beta)‖ = (5 : ℝ)⁻¹
```
An injective ring homomorphism with dense range carrying β to a uniformizer **is**
the statement that ℚ₅ (resp. ℤ₅) is the β-adic completion of ℚ(i) (resp. ℤ[i]) —
i.e. K_β ≅ ℚ₅, the headline Q2a claim of
`CNRS_problem4_partial_completeness` — stated concretely, without the abstract
`adicCompletion` machinery whose missing bridge lemma blocked the original attempt.

## Phase 4 (Q2b): now fully complete

`DigitExpansion.lean` proves thm:q2_digit_carrier(ii)/(iii) against ℤ_[5]
directly, using the uniformizer `pi5 := toPadic beta`. All zero-sorry:

- `span_pi5_eq_maximalIdeal`: π and 5 generate the same ideal of ℤ_[5].
- `exists_unique_digitP` (Milestone 4a): every y : ℤ_[5] has a unique digit
  k ∈ Fin 5 with y ≡ digitP k (mod maximal ideal).
- `exists_unique_reduction` (Milestone 4b): every y factors uniquely as
  y = digitP k + π·y′ — the one-step recursive digit-extraction step.
- `remSeq` / `digitSeq`: the recursive digit/remainder sequences built from
  Milestone 4b.
- `partialSum_digitSeq_spec`: the exact identity x − sₙ = πᴺ · remSeqₙ.
- `partialSum_tail_bound`: an ultrametric tail bound for **any** digit
  sequence (not just the canonical one) — the key lemma reused by both
  directions below.
- `tendsto_partialSum_digitSeq` (**existence**): the canonical sequence's
  partial sums converge to x, via `squeeze_zero` against (1/5)^N → 0.
- `digitSeq_unique` (**uniqueness**): any digit sequence whose partial sums
  converge to x equals the canonical one, by strong induction — at each
  index, a genuine digit mismatch is shown to force
  ‖digitP(f n) − digitP(digitSeq n)‖ = 1 (via the toZMod/maximal-ideal
  connection), contradicting a derived bound of ≤ 1/5.
- `exists_unique_digit_expansion`: **the full theorem**, assembling the
  above two directions into the `∃!` statement.

Verified via `#print axioms` on every theorem above (all depend only on
`propext, Classical.choice, Quot.sound` — no `sorryAx`), and via a full
clean rebuild of the entire project from scratch (`rm -rf .lake/build`
then `lake build`), not merely an incremental/cached build.

## Rebuild instructions (proven multiple times now)
```
curl -sSfL https://elan.lean-lang.org/elan-init.sh | sh -s -- -y --default-toolchain none
# project dir with this lakefile.toml + lean-toolchain (both pinned v4.33.0)
git clone --depth 1 --branch v4.33.0 https://github.com/leanprover-community/mathlib4 .lake/packages/mathlib
lake exe cache get Mathlib.NumberTheory.Padics.PadicNumbers Mathlib.NumberTheory.Zsqrtd.GaussianInt \
  Mathlib.RingTheory.DedekindDomain.AdicValuation Mathlib.NumberTheory.Padics.Hensel \
  Mathlib.NumberTheory.Padics.RingHoms Mathlib.Data.ZMod.Basic Mathlib.Analysis.Normed.Group.Ultra
lake build   # ~2 min, everything from cache except the 7 project files
```
**Disk warnings (hit repeatedly across sessions):** (1) never run a blanket
`lake exe cache get` — full Mathlib exhausts the sandbox quota; targeted list
above is sufficient. (2) Do NOT delete `mathlib/.git` to save space — lake
then re-clones from scratch, destroying the unpacked oleans. Deleting the
OTHER packages' `.git` dirs is safe.

## Destination
The authoritative live project is:
`/_SSC/20_Program/80_Strategy/30_Lean4/CnrsQ2/`

This stable, unversioned folder is the working Lean project. Immutable dated/versioned
snapshots are stored in `/_SSC/20_Program/80_Strategy/30_Lean4/99_Archive/`.
The earlier live-folder name `CnrsQ2_lean_aug_18_2026_v2/` is superseded by this
stable project location.

## File naming & versioning convention (adopted Session 116)
Lean's build system fixes the internal names (`lakefile.toml`, `lean-toolchain`,
and module-path-matching `.lean` files), so programme conventions apply at the
**archive level only**:
- **Dropbox layout**: one project = one folder, tree stored verbatim.
- **Versioned snapshots**: zips named per programme convention —
  `CnrsQ2_lean_<mmm>_<dd>_<yyyy>_v<N>.zip` — stored in `30_Lean4/99_Archive/`.
  The zip name carries date+version; the files inside never do.
- **MANIFEST.md** inside each snapshot records toolchain, build state, and
  per-file sha256 prefixes, so any snapshot is self-describing without unpacking
  the corpus context.
- **In-file changelogs**: each `.lean` file's header comment carries its own
  session history (the same role %-comment changelogs play in the .tex corpus),
  since the filename cannot.
- If a second Lean project is ever started, it gets its own sibling folder
  (`30_Lean4/<ProjectName>/`) — internal names like `Basic.lean` may repeat
  across projects; the folder, not the filename, disambiguates.
