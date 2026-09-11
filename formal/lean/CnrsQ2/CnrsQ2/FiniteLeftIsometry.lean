/-
CNRS Q2 formalization — Phase 5C' (August 30, 2026), Part B:
minimal finite-left carrier, bijective evaluation, and global isometry.

This module packages the verified Phase-5A field expansion and Phase-5B
first-differing-digit norm theorem using the stream-completion theorem proved
in `StreamCompletion`.

A nonzero finite-left string stores only:
  * its first occupied integer exponent `shift`,
  * its tail digit stream `digits : ℕ → Fin 5`, and
  * the normalization condition `digits 0 ≠ 0`.

It stores no field value, convergence certificate, valuation proof, or
normalization equation.  Evaluation derives those facts from the theorems.
This removes the dependent-record failure mode of the withdrawn Toolkit
Phase-5C experiment.

The explicit digit ultrametric below is the normalized-coordinate version of
Problem 4 v15's
  δβ(d,e) = 5^{-k(d,e)},
where k(d,e) is the first differing integer digit index.  If two nonzero
strings have different starting exponents, their first differing index is the
smaller shift.  If their shifts agree, it is the common shift plus the first
differing tail position.

The finite-support = R_A converse is intentionally not included here; it needs
the separate finite Gaussian CNS theorem and belongs to the next campaign.
-/
import CnrsQ2.StreamCompletion
import Mathlib.Data.Nat.Find
import Mathlib.Topology.MetricSpace.Isometry

namespace CnrsQ2

/-! ### 1. Minimal normalized finite-left syntax -/

/-- A normalized nonzero finite-left β-adic digit string. -/
structure NonzeroFiniteLeftDigits where
  shift : ℤ
  digits : ℕ → Fin 5
  leading_ne_zero : digits 0 ≠ 0

/-- Extensionality ignores the proof-valued normalization field. -/
@[ext]
theorem NonzeroFiniteLeftDigits.ext {s t : NonzeroFiniteLeftDigits}
    (hshift : s.shift = t.shift) (hdigits : s.digits = t.digits) : s = t := by
  cases s with
  | mk ss sd sh =>
      cases t with
      | mk ts td th =>
          simp only at hshift hdigits
          subst ts
          subst td
          rfl

/-- The full finite-left carrier; zero is represented separately. -/
inductive FiniteLeftDigitCarrier where
  | zero : FiniteLeftDigitCarrier
  | nonzero : NonzeroFiniteLeftDigits → FiniteLeftDigitCarrier

/-! ### 2. Evaluation and valuation normalization -/

/-- Evaluate finite-left syntax in ℚ_[5]. -/
noncomputable def finiteLeftEval : FiniteLeftDigitCarrier → ℚ_[5]
  | .zero => 0
  | .nonzero s => pi5Q ^ s.shift * (digitStreamLimit s.digits : ℚ_[5])

/-- The norm of a nonzero finite-left string is exactly determined by its
    starting exponent. -/
theorem norm_finiteLeftEval_nonzero (s : NonzeroFiniteLeftDigits) :
    ‖finiteLeftEval (.nonzero s)‖ = (5 : ℝ) ^ (-s.shift) := by
  have hu : ‖digitStreamLimit s.digits‖ = 1 :=
    norm_digitStreamLimit_eq_one_of_first_ne_zero s.digits s.leading_ne_zero
  have hcoe : ‖(digitStreamLimit s.digits : ℚ_[5])‖ = 1 := by
    calc
      ‖(digitStreamLimit s.digits : ℚ_[5])‖ = ‖digitStreamLimit s.digits‖ :=
        (PadicInt.norm_def (z := digitStreamLimit s.digits)).symm
      _ = 1 := hu
  rw [finiteLeftEval, _root_.norm_mul, norm_pi5Q_zpow, hcoe, mul_one]

/-- A nonzero finite-left string never evaluates to zero. -/
theorem finiteLeftEval_nonzero_ne_zero (s : NonzeroFiniteLeftDigits) :
    finiteLeftEval (.nonzero s) ≠ 0 := by
  intro hzero
  have hn := norm_finiteLeftEval_nonzero s
  rw [hzero, norm_zero] at hn
  have hp : 0 < (5 : ℝ) ^ (-s.shift) :=
    zpow_pos (by norm_num : (0 : ℝ) < 5) _
  linarith

/-- Canonical normalized syntax attached to a nonzero p-adic field element. -/
noncomputable def canonicalNonzeroFiniteLeftDigits (x : ℚ_[5]) (hx : x ≠ 0) :
    NonzeroFiniteLeftDigits where
  shift := Padic.valuation x
  digits := digitSeq (fieldUnit x hx)
  leading_ne_zero := fieldUnit_first_digit_ne_zero x hx

/-- Evaluation is surjective: Phase 5A supplies the canonical field expansion. -/
theorem finiteLeftEval_surjective : Function.Surjective finiteLeftEval := by
  intro x
  by_cases hx : x = 0
  · refine ⟨.zero, ?_⟩
    simpa [finiteLeftEval] using hx.symm
  · refine ⟨.nonzero (canonicalNonzeroFiniteLeftDigits x hx), ?_⟩
    simp only [finiteLeftEval, canonicalNonzeroFiniteLeftDigits]
    rw [digitStreamLimit_digitSeq]
    exact fieldUnit_reconstruct x hx

/-! ### 3. Injectivity and bijectivity -/

/-- Equal evaluated nonzero strings have equal starting exponents, because
    their norms are distinct integer powers of 5. -/
theorem NonzeroFiniteLeftDigits.shift_eq_of_eval_eq
    {s t : NonzeroFiniteLeftDigits}
    (h : finiteLeftEval (.nonzero s) = finiteLeftEval (.nonzero t)) :
    s.shift = t.shift := by
  have hpow : (5 : ℝ) ^ (-s.shift) = (5 : ℝ) ^ (-t.shift) := by
    calc
      (5 : ℝ) ^ (-s.shift) = ‖finiteLeftEval (.nonzero s)‖ :=
        (norm_finiteLeftEval_nonzero s).symm
      _ = ‖finiteLeftEval (.nonzero t)‖ := congrArg norm h
      _ = (5 : ℝ) ^ (-t.shift) := norm_finiteLeftEval_nonzero t
  have hneg : -s.shift = -t.shift :=
    (zpow_right_inj₀ (by norm_num : (0 : ℝ) < 5)
      (by norm_num : (5 : ℝ) ≠ 1)).mp hpow
  exact neg_inj.mp hneg

/-- Equal evaluated nonzero strings have equal tail digit streams. -/
theorem NonzeroFiniteLeftDigits.digits_eq_of_eval_eq
    {s t : NonzeroFiniteLeftDigits}
    (h : finiteLeftEval (.nonzero s) = finiteLeftEval (.nonzero t)) :
    s.digits = t.digits := by
  have hshift := s.shift_eq_of_eval_eq h
  have hunitQ : (digitStreamLimit s.digits : ℚ_[5]) =
      (digitStreamLimit t.digits : ℚ_[5]) := by
    calc
      (digitStreamLimit s.digits : ℚ_[5]) =
          pi5Q ^ (-s.shift) * finiteLeftEval (.nonzero s) := by
            rw [finiteLeftEval, ← mul_assoc,
              zpow_neg_mul_zpow_self s.shift pi5Q_ne_zero, one_mul]
      _ = pi5Q ^ (-s.shift) * finiteLeftEval (.nonzero t) := by rw [h]
      _ = (digitStreamLimit t.digits : ℚ_[5]) := by
            rw [finiteLeftEval, hshift, ← mul_assoc,
              zpow_neg_mul_zpow_self t.shift pi5Q_ne_zero, one_mul]
  have hunit : digitStreamLimit s.digits = digitStreamLimit t.digits :=
    PadicInt.isOpenEmbedding_coe.injective hunitQ
  calc
    s.digits = digitSeq (digitStreamLimit s.digits) :=
      digits_eq_digitSeq_digitStreamLimit s.digits
    _ = digitSeq (digitStreamLimit t.digits) := by rw [hunit]
    _ = t.digits := (digits_eq_digitSeq_digitStreamLimit t.digits).symm

/-- Finite-left evaluation is injective. -/
theorem finiteLeftEval_injective : Function.Injective finiteLeftEval := by
  intro a b h
  cases a with
  | zero =>
      cases b with
      | zero => rfl
      | nonzero t =>
          exfalso
          exact finiteLeftEval_nonzero_ne_zero t h.symm
  | nonzero s =>
      cases b with
      | zero =>
          exfalso
          exact finiteLeftEval_nonzero_ne_zero s h
      | nonzero t =>
          have hshift := s.shift_eq_of_eval_eq h
          have hdigits := s.digits_eq_of_eval_eq h
          have hst : s = t := NonzeroFiniteLeftDigits.ext hshift hdigits
          exact congrArg FiniteLeftDigitCarrier.nonzero hst

/-- **Phase-5C' representation capstone.** Evaluation is a bijection between
    normalized finite-left digit syntax and ℚ_[5]. -/
theorem finiteLeftEval_bijective : Function.Bijective finiteLeftEval :=
  ⟨finiteLeftEval_injective, finiteLeftEval_surjective⟩

/-! ### 4. First differing tail position -/

/-- Different digit functions differ at some natural index. -/
theorem exists_digit_ne_of_ne {d e : ℕ → Fin 5} (h : d ≠ e) :
    ∃ k, d k ≠ e k := by
  by_contra hnone
  apply h
  funext k
  by_contra hk
  exact hnone ⟨k, hk⟩

/-- First natural index at which two tail streams differ; it is only
    semantically used when the streams are unequal. -/
noncomputable def firstDigitDiff (d e : ℕ → Fin 5) : ℕ := by
  classical
  exact if h : d = e then 0 else Nat.find (exists_digit_ne_of_ne h)

/-- The first-difference index really is a mismatch. -/
theorem firstDigitDiff_spec {d e : ℕ → Fin 5} (h : d ≠ e) :
    d (firstDigitDiff d e) ≠ e (firstDigitDiff d e) := by
  classical
  unfold firstDigitDiff
  rw [dif_neg h]
  exact Nat.find_spec (exists_digit_ne_of_ne h)

/-- Every earlier tail position agrees. -/
theorem firstDigitDiff_prefix {d e : ℕ → Fin 5} (h : d ≠ e) :
    ∀ j < firstDigitDiff d e, d j = e j := by
  classical
  intro j hj
  have hj' : j < Nat.find (exists_digit_ne_of_ne h) := by
    simpa [firstDigitDiff, h] using hj
  by_contra hne
  exact (Nat.find_min (exists_digit_ne_of_ne h) hj') hne

/-! ### 5. Same-shift and cross-shift norm formulas -/

/-- Same-shift first-difference formula directly on finite-left syntax. -/
theorem finiteLeftEval_norm_sub_eq_of_same_shift_first_diff
    (s t : NonzeroFiniteLeftDigits) (hshift : s.shift = t.shift) (k : ℕ)
    (hagree : ∀ j < k, s.digits j = t.digits j)
    (hne : s.digits k ≠ t.digits k) :
    ‖finiteLeftEval (.nonzero s) - finiteLeftEval (.nonzero t)‖
      = (5 : ℝ) ^ (-s.shift) * (5 : ℝ)⁻¹ ^ k := by
  have hs := digits_eq_digitSeq_digitStreamLimit s.digits
  have ht := digits_eq_digitSeq_digitStreamLimit t.digits
  have hagree' : ∀ j < k,
      digitSeq (digitStreamLimit s.digits) j =
        digitSeq (digitStreamLimit t.digits) j := by
    intro j hj
    rw [← hs, ← ht]
    exact hagree j hj
  have hne' : digitSeq (digitStreamLimit s.digits) k ≠
      digitSeq (digitStreamLimit t.digits) k := by
    rw [← hs, ← ht]
    exact hne
  rw [finiteLeftEval]
  rw [hshift]
  exact norm_shifted_sub_eq_of_first_digit_diff t.shift
    (digitStreamLimit s.digits) (digitStreamLimit t.digits) k hagree' hne'

/-- Across unequal starting exponents, the larger p-adic norm dominates the
    difference.  This is the cross-stratum part of the digit isometry. -/
theorem finiteLeftEval_norm_sub_eq_max_of_shift_ne
    (s t : NonzeroFiniteLeftDigits) (hshift : s.shift ≠ t.shift) :
    ‖finiteLeftEval (.nonzero s) - finiteLeftEval (.nonzero t)‖
      = max ((5 : ℝ) ^ (-s.shift)) ((5 : ℝ) ^ (-t.shift)) := by
  have hnorm : ‖finiteLeftEval (.nonzero s)‖ ≠
      ‖finiteLeftEval (.nonzero t)‖ := by
    rw [norm_finiteLeftEval_nonzero, norm_finiteLeftEval_nonzero]
    intro hpow
    have hneg : -s.shift = -t.shift :=
      (zpow_right_inj₀ (by norm_num : (0 : ℝ) < 5)
        (by norm_num : (5 : ℝ) ≠ 1)).mp hpow
    exact hshift (neg_inj.mp hneg)
  have hadd := IsUltrametricDist.norm_add_eq_max_of_norm_ne_norm
    (x := finiteLeftEval (.nonzero s))
    (y := -finiteLeftEval (.nonzero t)) (by simpa using hnorm)
  simpa [sub_eq_add_neg, norm_neg,
    norm_finiteLeftEval_nonzero] using hadd

/-- For base 5, the maximum of two shift norms is exactly the norm attached
    to the smaller starting exponent.  This is the manuscript first-index form
    of the cross-stratum distance. -/
theorem max_five_zpow_neg_eq_min (a b : ℤ) :
    max ((5 : ℝ) ^ (-a)) ((5 : ℝ) ^ (-b)) =
      (5 : ℝ) ^ (-min a b) := by
  rcases le_total a b with hab | hba
  · rw [min_eq_left hab, max_eq_left]
    exact (zpow_le_zpow_iff_right₀ (by norm_num : (1 : ℝ) < 5)).2
      (neg_le_neg hab)
  · rw [min_eq_right hba, max_eq_right]
    exact (zpow_le_zpow_iff_right₀ (by norm_num : (1 : ℝ) < 5)).2
      (neg_le_neg hba)

/-- Across unequal shifts, the first differing absolute digit index is the
    smaller shift, so the norm is exactly `5 ^ (-min shift₁ shift₂)`. -/
theorem finiteLeftEval_norm_sub_eq_min_shift_of_shift_ne
    (s t : NonzeroFiniteLeftDigits) (hshift : s.shift ≠ t.shift) :
    ‖finiteLeftEval (.nonzero s) - finiteLeftEval (.nonzero t)‖
      = (5 : ℝ) ^ (-min s.shift t.shift) := by
  rw [finiteLeftEval_norm_sub_eq_max_of_shift_ne s t hshift,
    max_five_zpow_neg_eq_min]

/-- Distance from a nonzero string to zero is determined by its starting
    exponent. -/
theorem finiteLeftEval_norm_sub_zero (s : NonzeroFiniteLeftDigits) :
    ‖finiteLeftEval (.nonzero s) - 0‖ = (5 : ℝ) ^ (-s.shift) := by
  simpa using norm_finiteLeftEval_nonzero s

/-! ### 6. Explicit digit ultrametric and global evaluation formula -/

/-- The explicit normalized finite-left digit ultrametric.

For equal common shifts it uses the first differing tail digit. For unequal
shifts, the smaller absolute digit index is the first difference, so the
larger of the two p-adic norms is the distance. -/
noncomputable def finiteLeftDigitDist
    (a b : FiniteLeftDigitCarrier) : ℝ := by
  classical
  cases a with
  | zero =>
      cases b with
      | zero => exact 0
      | nonzero t => exact (5 : ℝ) ^ (-t.shift)
  | nonzero s =>
      cases b with
      | zero => exact (5 : ℝ) ^ (-s.shift)
      | nonzero t =>
          exact if hshift : s.shift = t.shift then
            if hdigits : s.digits = t.digits then 0
            else (5 : ℝ) ^ (-s.shift) * (5 : ℝ)⁻¹ ^
              firstDigitDiff s.digits t.digits
          else (5 : ℝ) ^ (-min s.shift t.shift)

/-- **Global first-difference formula.** Field distance after evaluation is
    exactly the explicit digit ultrametric on the complete finite-left carrier. -/
theorem dist_finiteLeftEval_eq_digitDist (a b : FiniteLeftDigitCarrier) :
    dist (finiteLeftEval a) (finiteLeftEval b) = finiteLeftDigitDist a b := by
  classical
  cases a with
  | zero =>
      cases b with
      | zero => simp [finiteLeftEval, finiteLeftDigitDist]
      | nonzero t =>
          change dist 0 (finiteLeftEval (.nonzero t)) = (5 : ℝ) ^ (-t.shift)
          rw [dist_eq_norm, zero_sub, norm_neg]
          exact norm_finiteLeftEval_nonzero t
  | nonzero s =>
      cases b with
      | zero =>
          change dist (finiteLeftEval (.nonzero s)) 0 = (5 : ℝ) ^ (-s.shift)
          rw [dist_eq_norm, sub_zero]
          exact norm_finiteLeftEval_nonzero s
      | nonzero t =>
          by_cases hshift : s.shift = t.shift
          · by_cases hdigits : s.digits = t.digits
            · have hst : s = t := NonzeroFiniteLeftDigits.ext hshift hdigits
              subst t
              simp [finiteLeftDigitDist]
            · have hformula :=
                finiteLeftEval_norm_sub_eq_of_same_shift_first_diff s t hshift
                  (firstDigitDiff s.digits t.digits)
                  (firstDigitDiff_prefix hdigits)
                  (firstDigitDiff_spec hdigits)
              rw [dist_eq_norm]
              simpa [finiteLeftDigitDist, hshift, hdigits] using hformula
          · have hformula :=
                finiteLeftEval_norm_sub_eq_min_shift_of_shift_ne s t hshift
            rw [dist_eq_norm]
            simpa [finiteLeftDigitDist, hshift] using hformula

/-! ### 7. Actual metric/isometry packaging -/

/-- Pull back the p-adic metric through the injective evaluation map. -/
noncomputable instance finiteLeftMetricSpace : MetricSpace FiniteLeftDigitCarrier :=
  MetricSpace.induced finiteLeftEval finiteLeftEval_injective inferInstance

/-- Under the induced metric, evaluation is an actual Lean `Isometry`. -/
theorem finiteLeftEval_isometry : Isometry finiteLeftEval :=
  MetricSpace.isometry_induced finiteLeftEval finiteLeftEval_injective

/-- The induced metric on finite-left syntax is definitionally the field metric,
    and substantively equals the explicit first-difference digit formula above. -/
theorem finiteLeft_dist_eq_digitDist (a b : FiniteLeftDigitCarrier) :
    dist a b = finiteLeftDigitDist a b := by
  change dist (finiteLeftEval a) (finiteLeftEval b) = finiteLeftDigitDist a b
  exact dist_finiteLeftEval_eq_digitDist a b

/-- **Phase-5C' isometric-bijection capstone.** The normalized finite-left digit
    carrier is isometrically equivalent to ℚ_[5]. -/
noncomputable def finiteLeftIsometryEquiv : FiniteLeftDigitCarrier ≃ᵢ ℚ_[5] where
  toEquiv := Equiv.ofBijective finiteLeftEval finiteLeftEval_bijective
  isometry_toFun := finiteLeftEval_isometry

/-- The isometric equivalence automatically gives the manuscript's topological
    identification of the normalized finite-left carrier with the p-adic field. -/
noncomputable def finiteLeftHomeomorph : FiniteLeftDigitCarrier ≃ₜ ℚ_[5] :=
  finiteLeftIsometryEquiv.toHomeomorph

end CnrsQ2
