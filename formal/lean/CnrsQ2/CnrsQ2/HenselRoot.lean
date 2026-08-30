/-
CNRS Q2 formalization — Phase 3a (new, Session 116): √(-1) exists in ℤ_[5],
via Mathlib's Hensel lemma applied to F = X² + 1 at the approximate root a = 2.
‖F(2)‖ = ‖5‖ = 1/5 < 1 = ‖F'(2)‖² since F'(2) = 4 is a 5-adic unit.
-/
import Mathlib.NumberTheory.Padics.Hensel
import Mathlib.NumberTheory.Padics.PadicIntegers

open Polynomial

namespace CnrsQ2

instance fact_prime_five : Fact (Nat.Prime 5) := ⟨Nat.prime_five⟩

/-- The polynomial X² + 1 over ℤ_[5]. -/
noncomputable def F : Polynomial ℤ_[5] := X ^ 2 + 1

lemma F_aeval_two : F.aeval (2 : ℤ_[5]) = 5 := by
  simp only [F, map_add, map_pow, map_one, aeval_X]
  norm_num

lemma F_deriv_aeval_two : F.derivative.aeval (2 : ℤ_[5]) = 4 := by
  simp only [F, derivative_add, derivative_one, derivative_pow, derivative_X]
  simp
  norm_num

lemma norm_F_aeval_two : ‖F.aeval (2 : ℤ_[5])‖ = (5 : ℝ)⁻¹ := by
  rw [F_aeval_two]
  have := PadicInt.norm_p (p := 5)
  simpa using this

lemma norm_F_deriv_aeval_two : ‖F.derivative.aeval (2 : ℤ_[5])‖ = 1 := by
  rw [F_deriv_aeval_two]
  have h4 : ((4 : ℕ) : ℤ_[5]) = (4 : ℤ_[5]) := by norm_num
  rw [← h4, PadicInt.norm_natCast_eq_one_iff]
  decide

/-- Hensel hypothesis: ‖F(2)‖ < ‖F'(2)‖². -/
lemma hensel_hyp : ‖F.aeval (2 : ℤ_[5])‖ < ‖F.derivative.aeval (2 : ℤ_[5])‖ ^ 2 := by
  rw [norm_F_aeval_two, norm_F_deriv_aeval_two]
  norm_num

/-- There is a square root of -1 in ℤ_[5], congruent to 2 mod 5. -/
theorem exists_sqrt_neg_one : ∃ c : ℤ_[5], c * c = -1 ∧ ‖c - 2‖ < 1 := by
  obtain ⟨z, hz, hdist, -, -⟩ := hensels_lemma hensel_hyp
  refine ⟨z, ?_, ?_⟩
  · have h : z ^ 2 + 1 = 0 := by
      simpa only [F, map_add, map_pow, map_one, aeval_X] using hz
    linear_combination h
  · rw [norm_F_deriv_aeval_two] at hdist
    exact hdist

end CnrsQ2
