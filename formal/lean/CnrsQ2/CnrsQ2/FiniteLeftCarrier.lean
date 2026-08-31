/-
CNRS Q2 formalization — Phase 5C (August 30, 2026): certified finite-left
field carrier and evaluation map.

Phase 5A proved the unique normalized field expansion for each nonzero
x : ℚ_[5]. Phase 5B proved the exact first-differing-digit norm formula.
This module packages those verified ingredients into an explicit certified
finite-left digit carrier.

A nonzero carrier stores an integer start index, a digit stream, its nonzero
field value, convergence of the shifted partial sums to that value, and the
normalization certificate that the start index is exactly the p-adic valuation
of the value. The leading digit is required to be nonzero. Zero is represented
separately.

This is deliberately a *certified* syntax: arbitrary raw digit streams are not
yet admitted without a convergence/normalization proof. Removing those proof
fields by proving convergence for every finite-left stream is a later cleanup
target. The finite-support = R_A converse also remains separate because it
requires a formal finite CNS expansion theorem for Gaussian integers.
-/
import CnrsQ2.DigitIsometry

namespace CnrsQ2

/-- A normalized nonzero finite-left β-adic digit string together with its
    certified field value. -/
structure NonzeroFiniteLeftDigits where
  shift : ℤ
  digits : ℕ → Fin 5
  leading_ne_zero : digits 0 ≠ 0
  value : ℚ_[5]
  value_ne_zero : value ≠ 0
  converges : Filter.Tendsto (fieldPartialSum shift digits)
    Filter.atTop (nhds value)
  normalized : shift = Padic.valuation value

/-- The canonical digits stored in a certified carrier are necessarily the
    canonical digits of the normalized valuation-ring unit of its value. -/
theorem NonzeroFiniteLeftDigits.digits_eq_canonical (s : NonzeroFiniteLeftDigits) :
    s.digits = digitSeq (fieldUnit s.value s.value_ne_zero) := by
  have hconv := s.converges
  rw [s.normalized] at hconv
  exact fieldDigitSeq_unique s.value s.value_ne_zero s.digits hconv

/-- Two certified nonzero carriers with the same field value are equal. -/
theorem NonzeroFiniteLeftDigits.ext_value {s t : NonzeroFiniteLeftDigits}
    (h : s.value = t.value) : s = t := by
  have hshift : s.shift = t.shift := by
    calc
      s.shift = Padic.valuation s.value := s.normalized
      _ = Padic.valuation t.value := congrArg Padic.valuation h
      _ = t.shift := t.normalized.symm
  have hs := s.digits_eq_canonical
  have ht := t.digits_eq_canonical
  have hdigits : s.digits = t.digits := by
    calc
      s.digits = digitSeq (fieldUnit s.value s.value_ne_zero) := hs
      _ = digitSeq (fieldUnit t.value t.value_ne_zero) := by
        cases h
        rfl
      _ = t.digits := ht.symm
  cases s with
  | mk sshift sdigits slead svalue sne sconv snorm =>
    cases t with
    | mk tshift tdigits tlead tvalue tne tconv tnorm =>
      simp only at hshift hdigits h
      subst tshift
      subst tdigits
      subst tvalue
      rfl

/-- The canonical certified nonzero carrier attached to x ≠ 0. -/
noncomputable def canonicalNonzeroFiniteLeftDigits (x : ℚ_[5]) (hx : x ≠ 0) :
    NonzeroFiniteLeftDigits where
  shift := Padic.valuation x
  digits := digitSeq (fieldUnit x hx)
  leading_ne_zero := fieldUnit_first_digit_ne_zero x hx
  value := x
  value_ne_zero := hx
  converges := tendsto_fieldPartialSum_digitSeq x hx
  normalized := rfl

/-- Full finite-left carrier, with zero represented separately. -/
inductive FiniteLeftDigitCarrier where
  | zero : FiniteLeftDigitCarrier
  | nonzero : NonzeroFiniteLeftDigits → FiniteLeftDigitCarrier

/-- Evaluation of the certified digit carrier in ℚ_[5]. -/
def finiteLeftEval : FiniteLeftDigitCarrier → ℚ_[5]
  | .zero => 0
  | .nonzero s => s.value

/-- Canonical carrier attached to any p-adic field element. -/
noncomputable def canonicalFiniteLeftCarrier (x : ℚ_[5]) : FiniteLeftDigitCarrier :=
  if hx : x = 0 then .zero else .nonzero (canonicalNonzeroFiniteLeftDigits x hx)

/-- Evaluation of the canonical carrier recovers the original field element. -/
theorem finiteLeftEval_canonical (x : ℚ_[5]) :
    finiteLeftEval (canonicalFiniteLeftCarrier x) = x := by
  by_cases hx : x = 0
  · simp [canonicalFiniteLeftCarrier, finiteLeftEval, hx]
  · simp [canonicalFiniteLeftCarrier, finiteLeftEval, hx,
      canonicalNonzeroFiniteLeftDigits]

/-- The certified finite-left evaluation map is surjective onto ℚ_[5]. -/
theorem finiteLeftEval_surjective : Function.Surjective finiteLeftEval := by
  intro x
  exact ⟨canonicalFiniteLeftCarrier x, finiteLeftEval_canonical x⟩

/-- The certified finite-left evaluation map is injective. The normalization
    certificate forces equal values to have the same start index, while the
    field-level uniqueness theorem forces their digit streams to agree. -/
theorem finiteLeftEval_injective : Function.Injective finiteLeftEval := by
  intro a b h
  cases a with
  | zero =>
      cases b with
      | zero => rfl
      | nonzero t =>
          change (0 : ℚ_[5]) = t.value at h
          exfalso
          exact t.value_ne_zero h.symm
  | nonzero s =>
      cases b with
      | zero =>
          change s.value = (0 : ℚ_[5]) at h
          exfalso
          exact s.value_ne_zero h
      | nonzero t =>
          have hst : s = t := NonzeroFiniteLeftDigits.ext_value h
          cases hst
          rfl

/-- **Certified carrier capstone.** Evaluation is a bijection between the
    normalized certified finite-left carrier and ℚ_[5]. -/
theorem finiteLeftEval_bijective : Function.Bijective finiteLeftEval :=
  ⟨finiteLeftEval_injective, finiteLeftEval_surjective⟩

/-- Every nonzero certified carrier explicitly reconstructs its value by
    scaling its canonical valuation-ring unit from its integer start index. -/
theorem NonzeroFiniteLeftDigits.value_eq_shifted_unit (s : NonzeroFiniteLeftDigits) :
    s.value = pi5Q ^ s.shift * (fieldUnit s.value s.value_ne_zero : ℚ_[5]) := by
  rw [s.normalized]
  exact (fieldUnit_reconstruct s.value s.value_ne_zero).symm

/-- **Evaluation-map isometry on a fixed valuation stratum.** If two certified
    nonzero carriers have the same start index and first differ k digits into
    their streams, then the norm of the difference of their evaluated values is
    exactly 5^(-shift) * (1/5)^k. This is the manuscript's first-difference
    metric formula on each fixed finite-left stratum. -/
theorem finiteLeftEval_norm_sub_eq_of_same_shift_first_diff
    (s t : NonzeroFiniteLeftDigits) (hshift : s.shift = t.shift) (k : ℕ)
    (hagree : ∀ j < k, s.digits j = t.digits j)
    (hne : s.digits k ≠ t.digits k) :
    ‖s.value - t.value‖ = (5 : ℝ) ^ (-s.shift) * (5 : ℝ)⁻¹ ^ k := by
  have hs := s.digits_eq_canonical
  have ht := t.digits_eq_canonical
  have hagree' : ∀ j < k,
      digitSeq (fieldUnit s.value s.value_ne_zero) j =
        digitSeq (fieldUnit t.value t.value_ne_zero) j := by
    intro j hj
    rw [← hs, ← ht]
    exact hagree j hj
  have hne' :
      digitSeq (fieldUnit s.value s.value_ne_zero) k ≠
        digitSeq (fieldUnit t.value t.value_ne_zero) k := by
    rw [← hs, ← ht]
    exact hne
  have hsvalue := s.value_eq_shifted_unit
  have htvalue :
      t.value = pi5Q ^ s.shift * (fieldUnit t.value t.value_ne_zero : ℚ_[5]) := by
    calc
      t.value = pi5Q ^ t.shift * (fieldUnit t.value t.value_ne_zero : ℚ_[5]) :=
        t.value_eq_shifted_unit
      _ = pi5Q ^ s.shift * (fieldUnit t.value t.value_ne_zero : ℚ_[5]) := by
        rw [hshift]
  rw [hsvalue, htvalue]
  exact norm_shifted_sub_eq_of_first_digit_diff s.shift
    (fieldUnit s.value s.value_ne_zero)
    (fieldUnit t.value t.value_ne_zero) k hagree' hne'

end CnrsQ2
