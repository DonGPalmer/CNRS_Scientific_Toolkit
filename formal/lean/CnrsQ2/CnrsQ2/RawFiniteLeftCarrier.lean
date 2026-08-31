/-
CNRS Q2 formalization — Phase 5D (August 30, 2026): raw finite-left carrier.

Phase 4 already proved `partialSum_tail_bound` for every digit stream
`d : ℕ → Fin 5`.  Completeness of ℤ_[5] therefore gives convergence for
arbitrary streams; the Phase-4 uniqueness theorem then identifies each stream
with the canonical digit sequence of its limit.

This removes the convergence/normalization proof fields used by the certified
Phase-5C carrier.  A nonzero raw finite-left string now consists only of an
integer starting exponent, a digit stream, and the condition that its leading
digit is nonzero.  Evaluation is obtained by taking the automatically existing
ℤ_[5] limit and shifting it by the corresponding integer power of π in ℚ_[5].

The capstones prove that raw evaluation is a bijection onto ℚ_[5], that the
norm of a nonzero string is determined exactly by its starting exponent, and
that the manuscript first-difference formula holds both within a fixed shift
and across unequal shifts.

The finite-support = R_A converse remains separate: it requires a formal finite
CNS expansion theorem for every Gaussian integer, not merely completion-level
stream convergence.
-/
import CnrsQ2.DigitIsometry
import Mathlib.Topology.MetricSpace.Cauchy

namespace CnrsQ2

/-! ### Step 1: every raw valuation-ring digit stream converges -/

/-- Pairwise Cauchy control for arbitrary digit-stream partial sums. -/
theorem dist_partialSum_le (d : ℕ → Fin 5) (N m n : ℕ)
    (hm : N ≤ m) (hn : N ≤ n) :
    dist (partialSum d m) (partialSum d n) ≤ (5 : ℝ)⁻¹ ^ N := by
  rcases le_total m n with hmn | hnm
  · rw [dist_eq_norm, norm_sub_rev]
    calc
      ‖partialSum d n - partialSum d m‖ ≤ (5 : ℝ)⁻¹ ^ m :=
        partialSum_tail_bound d m n hmn
      _ ≤ (5 : ℝ)⁻¹ ^ N := by
        exact pow_le_pow_of_le_one (by norm_num) (by norm_num) hm
  · rw [dist_eq_norm]
    calc
      ‖partialSum d m - partialSum d n‖ ≤ (5 : ℝ)⁻¹ ^ n :=
        partialSum_tail_bound d n m hnm
      _ ≤ (5 : ℝ)⁻¹ ^ N := by
        exact pow_le_pow_of_le_one (by norm_num) (by norm_num) hn

/-- Partial sums of every raw digit stream form a Cauchy sequence in ℤ_[5]. -/
theorem partialSum_cauchySeq (d : ℕ → Fin 5) : CauchySeq (partialSum d) := by
  rw [cauchySeq_iff_le_tendsto_0]
  refine ⟨(fun N : ℕ => (5 : ℝ)⁻¹ ^ N), ?_, ?_, ?_⟩
  · intro N
    positivity
  · intro n m N hn hm
    exact dist_partialSum_le d N n m hn hm
  · exact tendsto_pow_atTop_nhds_zero_of_lt_one
      (by norm_num) (by norm_num : (5 : ℝ)⁻¹ < 1)

/-- The automatically existing ℤ_[5] limit of an arbitrary raw digit stream. -/
noncomputable def rawDigitLimit (d : ℕ → Fin 5) : ℤ_[5] :=
  Filter.atTop.limUnder (partialSum d)

/-- Every arbitrary raw digit stream converges to `rawDigitLimit d`. -/
theorem tendsto_partialSum_rawDigitLimit (d : ℕ → Fin 5) :
    Filter.Tendsto (partialSum d) Filter.atTop (nhds (rawDigitLimit d)) :=
  (partialSum_cauchySeq d).tendsto_limUnder

/-- **Raw-stream uniqueness.** Every digit stream is the canonical digit stream
    of its automatically constructed limit. -/
theorem rawDigits_eq_digitSeq_limit (d : ℕ → Fin 5) :
    d = digitSeq (rawDigitLimit d) :=
  digitSeq_unique (rawDigitLimit d) d (tendsto_partialSum_rawDigitLimit d)

/-- Taking the raw limit of the canonical digit stream recovers the element. -/
theorem rawDigitLimit_digitSeq (x : ℤ_[5]) :
    rawDigitLimit (digitSeq x) = x := by
  exact tendsto_nhds_unique
    (tendsto_partialSum_rawDigitLimit (digitSeq x))
    (tendsto_partialSum_digitSeq x)

/-! ### Step 2: a nonzero leading digit gives a norm-one unit -/

/-- A raw stream with nonzero leading digit has a norm-one limit in ℤ_[5]. -/
theorem norm_rawDigitLimit_eq_one_of_first_ne_zero (d : ℕ → Fin 5)
    (h0 : d 0 ≠ 0) : ‖rawDigitLimit d‖ = 1 := by
  have hcanon := rawDigits_eq_digitSeq_limit d
  have hfirst : digitSeq (rawDigitLimit d) 0 ≠ 0 := by
    rw [← hcanon]
    exact h0
  have hres := toZMod_remSeq (rawDigitLimit d) 0
  have hres0 : PadicInt.toZMod (rawDigitLimit d) =
      (digitSeq (rawDigitLimit d) 0 : ZMod 5) := by
    simpa [remSeq] using hres
  have hdigit : (digitSeq (rawDigitLimit d) 0 : ZMod 5) ≠ 0 := by
    intro hz
    apply hfirst
    apply natCast_fin5_bijective.1
    simpa using hz
  have hzmod : PadicInt.toZMod (rawDigitLimit d) ≠ 0 := by
    rw [hres0]
    exact hdigit
  have hnotlt : ¬ ‖rawDigitLimit d‖ < 1 := by
    intro hlt
    apply hzmod
    have hmem : rawDigitLimit d ∈ IsLocalRing.maximalIdeal ℤ_[5] := by
      rw [PadicInt.maximalIdeal_eq_span_p, Ideal.mem_span_singleton,
          ← PadicInt.norm_lt_one_iff_dvd]
      exact hlt
    rwa [← PadicInt.ker_toZMod, RingHom.mem_ker] at hmem
  exact le_antisymm (PadicInt.norm_le_one _) (not_lt.mp hnotlt)

/-- A raw stream with nonzero leading digit has nonzero limit. -/
theorem rawDigitLimit_ne_zero_of_first_ne_zero (d : ℕ → Fin 5)
    (h0 : d 0 ≠ 0) : rawDigitLimit d ≠ 0 := by
  intro hz
  have hn := norm_rawDigitLimit_eq_one_of_first_ne_zero d h0
  rw [hz, norm_zero] at hn
  norm_num at hn

/-! ### Step 3: raw finite-left syntax and evaluation -/

/-- A raw normalized nonzero finite-left digit string: only syntax plus the
    necessary nonzero leading-digit condition. -/
structure RawNonzeroFiniteLeftDigits where
  shift : ℤ
  digits : ℕ → Fin 5
  leading_ne_zero : digits 0 ≠ 0

/-- Raw finite-left carrier, with zero represented separately. -/
inductive RawFiniteLeftDigitCarrier where
  | zero : RawFiniteLeftDigitCarrier
  | nonzero : RawNonzeroFiniteLeftDigits → RawFiniteLeftDigitCarrier

/-- Evaluation of raw finite-left syntax in ℚ_[5]. -/
noncomputable def rawFiniteLeftEval : RawFiniteLeftDigitCarrier → ℚ_[5]
  | .zero => 0
  | .nonzero s => pi5Q ^ s.shift * (rawDigitLimit s.digits : ℚ_[5])

/-- The norm of a raw nonzero finite-left string is exactly determined by its
    starting exponent. -/
theorem norm_rawFiniteLeftEval_nonzero (s : RawNonzeroFiniteLeftDigits) :
    ‖rawFiniteLeftEval (.nonzero s)‖ = (5 : ℝ) ^ (-s.shift) := by
  have hu : ‖rawDigitLimit s.digits‖ = 1 :=
    norm_rawDigitLimit_eq_one_of_first_ne_zero s.digits s.leading_ne_zero
  have hcoe : ‖(rawDigitLimit s.digits : ℚ_[5])‖ = 1 := by
    calc
      ‖(rawDigitLimit s.digits : ℚ_[5])‖ = ‖rawDigitLimit s.digits‖ :=
        (PadicInt.norm_def (z := rawDigitLimit s.digits)).symm
      _ = 1 := hu
  rw [rawFiniteLeftEval, _root_.norm_mul, norm_pi5Q_zpow, hcoe, mul_one]

/-- Raw nonzero finite-left syntax never evaluates to zero. -/
theorem rawFiniteLeftEval_nonzero_ne_zero (s : RawNonzeroFiniteLeftDigits) :
    rawFiniteLeftEval (.nonzero s) ≠ 0 := by
  intro hzero
  have hn := norm_rawFiniteLeftEval_nonzero s
  rw [hzero, norm_zero] at hn
  have hp : 0 < (5 : ℝ) ^ (-s.shift) := by positivity
  linarith

/-- Canonical raw nonzero syntax attached to a nonzero field element. -/
noncomputable def canonicalRawNonzeroFiniteLeftDigits (x : ℚ_[5]) (hx : x ≠ 0) :
    RawNonzeroFiniteLeftDigits where
  shift := Padic.valuation x
  digits := digitSeq (fieldUnit x hx)
  leading_ne_zero := fieldUnit_first_digit_ne_zero x hx

/-- Canonical raw carrier attached to any p-adic field element. -/
noncomputable def canonicalRawFiniteLeftCarrier (x : ℚ_[5]) :
    RawFiniteLeftDigitCarrier :=
  if hx : x = 0 then .zero else .nonzero (canonicalRawNonzeroFiniteLeftDigits x hx)

/-- Evaluation of canonical raw syntax recovers the original field element. -/
theorem rawFiniteLeftEval_canonical (x : ℚ_[5]) :
    rawFiniteLeftEval (canonicalRawFiniteLeftCarrier x) = x := by
  by_cases hx : x = 0
  · simp [canonicalRawFiniteLeftCarrier, rawFiniteLeftEval, hx]
  · simp only [canonicalRawFiniteLeftCarrier, hx, ↓reduceDIte,
      rawFiniteLeftEval, canonicalRawNonzeroFiniteLeftDigits]
    rw [rawDigitLimit_digitSeq]
    exact fieldUnit_reconstruct x hx

/-- Raw finite-left evaluation is surjective onto ℚ_[5]. -/
theorem rawFiniteLeftEval_surjective : Function.Surjective rawFiniteLeftEval := by
  intro x
  exact ⟨canonicalRawFiniteLeftCarrier x, rawFiniteLeftEval_canonical x⟩

/-! ### Step 4: injectivity and bijectivity of raw evaluation -/

/-- Equal evaluated values force equal starting exponents for nonzero raw
    strings, because their norms are distinct integer powers of 5. -/
theorem RawNonzeroFiniteLeftDigits.shift_eq_of_eval_eq
    {s t : RawNonzeroFiniteLeftDigits}
    (h : rawFiniteLeftEval (.nonzero s) = rawFiniteLeftEval (.nonzero t)) :
    s.shift = t.shift := by
  have hpow : (5 : ℝ) ^ (-s.shift) = (5 : ℝ) ^ (-t.shift) := by
    calc
      (5 : ℝ) ^ (-s.shift) = ‖rawFiniteLeftEval (.nonzero s)‖ :=
        (norm_rawFiniteLeftEval_nonzero s).symm
      _ = ‖rawFiniteLeftEval (.nonzero t)‖ := congrArg norm h
      _ = (5 : ℝ) ^ (-t.shift) := norm_rawFiniteLeftEval_nonzero t
  have hneg : -s.shift = -t.shift :=
    (zpow_right_inj₀ (by norm_num : (0 : ℝ) < 5)
      (by norm_num : (5 : ℝ) ≠ 1)).mp hpow
  exact neg_inj.mp hneg

/-- Equal evaluated values force equal raw digit streams for nonzero strings. -/
theorem RawNonzeroFiniteLeftDigits.digits_eq_of_eval_eq
    {s t : RawNonzeroFiniteLeftDigits}
    (h : rawFiniteLeftEval (.nonzero s) = rawFiniteLeftEval (.nonzero t)) :
    s.digits = t.digits := by
  have hshift := s.shift_eq_of_eval_eq h
  have hunitQ : (rawDigitLimit s.digits : ℚ_[5]) =
      (rawDigitLimit t.digits : ℚ_[5]) := by
    have hp : pi5Q ^ s.shift ≠ 0 := zpow_ne_zero s.shift pi5Q_ne_zero
    apply mul_left_cancel₀ hp
    simpa [rawFiniteLeftEval, hshift] using h
  have hunit : rawDigitLimit s.digits = rawDigitLimit t.digits :=
    PadicInt.isOpenEmbedding_coe.injective hunitQ
  calc
    s.digits = digitSeq (rawDigitLimit s.digits) := rawDigits_eq_digitSeq_limit s.digits
    _ = digitSeq (rawDigitLimit t.digits) := by rw [hunit]
    _ = t.digits := (rawDigits_eq_digitSeq_limit t.digits).symm

/-- Raw finite-left evaluation is injective. -/
theorem rawFiniteLeftEval_injective : Function.Injective rawFiniteLeftEval := by
  intro a b h
  cases a with
  | zero =>
      cases b with
      | zero => rfl
      | nonzero t =>
          exfalso
          exact rawFiniteLeftEval_nonzero_ne_zero t h.symm
  | nonzero s =>
      cases b with
      | zero =>
          exfalso
          exact rawFiniteLeftEval_nonzero_ne_zero s h
      | nonzero t =>
          have hshift := s.shift_eq_of_eval_eq h
          have hdigits := s.digits_eq_of_eval_eq h
          cases s with
          | mk ss sd sh =>
              cases t with
              | mk ts td th =>
                  simp only at hshift hdigits
                  subst ts
                  subst td
                  rfl

/-- **Phase-5D raw-carrier capstone.** Raw finite-left evaluation is a
    bijection onto ℚ_[5], with no convergence or normalization certificate
    stored in the syntax. -/
theorem rawFiniteLeftEval_bijective : Function.Bijective rawFiniteLeftEval :=
  ⟨rawFiniteLeftEval_injective, rawFiniteLeftEval_surjective⟩

/-! ### Step 5: full first-difference metric formulas -/

/-- Same-shift first-difference formula directly on raw syntax. -/
theorem rawFiniteLeftEval_norm_sub_eq_of_same_shift_first_diff
    (s t : RawNonzeroFiniteLeftDigits) (hshift : s.shift = t.shift) (k : ℕ)
    (hagree : ∀ j < k, s.digits j = t.digits j)
    (hne : s.digits k ≠ t.digits k) :
    ‖rawFiniteLeftEval (.nonzero s) - rawFiniteLeftEval (.nonzero t)‖
      = (5 : ℝ) ^ (-s.shift) * (5 : ℝ)⁻¹ ^ k := by
  have hs := rawDigits_eq_digitSeq_limit s.digits
  have ht := rawDigits_eq_digitSeq_limit t.digits
  have hagree' : ∀ j < k,
      digitSeq (rawDigitLimit s.digits) j =
        digitSeq (rawDigitLimit t.digits) j := by
    intro j hj
    rw [← hs, ← ht]
    exact hagree j hj
  have hne' : digitSeq (rawDigitLimit s.digits) k ≠
      digitSeq (rawDigitLimit t.digits) k := by
    rw [← hs, ← ht]
    exact hne
  rw [rawFiniteLeftEval]
  rw [hshift]
  exact norm_shifted_sub_eq_of_first_digit_diff t.shift
    (rawDigitLimit s.digits) (rawDigitLimit t.digits) k hagree' hne'

/-- Across unequal starting exponents, the larger p-adic norm dominates the
    difference.  This is the cross-stratum part of the finite-left isometry. -/
theorem rawFiniteLeftEval_norm_sub_eq_max_of_shift_ne
    (s t : RawNonzeroFiniteLeftDigits) (hshift : s.shift ≠ t.shift) :
    ‖rawFiniteLeftEval (.nonzero s) - rawFiniteLeftEval (.nonzero t)‖
      = max ((5 : ℝ) ^ (-s.shift)) ((5 : ℝ) ^ (-t.shift)) := by
  have hnorm : ‖rawFiniteLeftEval (.nonzero s)‖ ≠
      ‖rawFiniteLeftEval (.nonzero t)‖ := by
    rw [norm_rawFiniteLeftEval_nonzero, norm_rawFiniteLeftEval_nonzero]
    intro hpow
    have hneg : -s.shift = -t.shift :=
      (zpow_right_inj₀ (by norm_num : (0 : ℝ) < 5)
      (by norm_num : (5 : ℝ) ≠ 1)).mp hpow
    exact hshift (neg_inj.mp hneg)
  have hadd := IsUltrametricDist.norm_add_eq_max_of_norm_ne_norm
    (x := rawFiniteLeftEval (.nonzero s))
    (y := -rawFiniteLeftEval (.nonzero t)) (by simpa using hnorm)
  simpa [sub_eq_add_neg, norm_neg,
    norm_rawFiniteLeftEval_nonzero] using hadd

/-- Distance from zero to a raw nonzero string is exactly its shift norm. -/
theorem rawFiniteLeftEval_norm_sub_zero (s : RawNonzeroFiniteLeftDigits) :
    ‖rawFiniteLeftEval (.nonzero s) - 0‖ = (5 : ℝ) ^ (-s.shift) := by
  simpa using norm_rawFiniteLeftEval_nonzero s

end CnrsQ2
