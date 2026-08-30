/-
CNRS Q2 formalization — Phase 3b (new, Session 116): the canonical embedding
ℤ[i] →+* ℤ_[5] sending i to the Hensel square root of -1, its injectivity,
and the exact valuation ‖φ(β)‖ = 1/5 of the image of the base β = -2+i.
This is the concrete realization of the β-adic ↔ 5-adic correspondence.
-/
import CnrsQ2.Basic
import CnrsQ2.HenselRoot

open Zsqrtd

namespace CnrsQ2

/-- A fixed square root of -1 in ℤ_[5] with c ≡ 2 (mod 5). -/
noncomputable def sqrtNegOne : ℤ_[5] := exists_sqrt_neg_one.choose

lemma sqrtNegOne_sq : sqrtNegOne * sqrtNegOne = -1 :=
  exists_sqrt_neg_one.choose_spec.1

lemma norm_sqrtNegOne_sub_two : ‖sqrtNegOne - 2‖ < 1 :=
  exists_sqrt_neg_one.choose_spec.2

/-- The root packaged for `Zsqrtd.lift` (needs `r * r = ((-1 : ℤ) : ℤ_[5])`). -/
noncomputable def rootPack : { r : ℤ_[5] // r * r = ((-1 : ℤ) : ℤ_[5]) } :=
  ⟨sqrtNegOne, by push_cast; exact sqrtNegOne_sq⟩

/-- The canonical ring embedding ℤ[i] →+* ℤ_[5], sending i ↦ sqrtNegOne. -/
noncomputable def toPadic : GaussianInt →+* ℤ_[5] := Zsqrtd.lift rootPack

/-- -1 is not a perfect square in ℤ. -/
lemma neg_one_ne_sq : ∀ n : ℤ, (-1 : ℤ) ≠ n * n := by
  intro n h
  nlinarith [mul_self_nonneg n]

/-- The embedding is injective. -/
theorem toPadic_injective : Function.Injective toPadic :=
  Zsqrtd.lift_injective rootPack neg_one_ne_sq

/-- The image of β under the embedding. -/
lemma toPadic_beta : toPadic beta = sqrtNegOne - 2 := by
  simp only [toPadic, beta, Zsqrtd.lift_apply_apply, rootPack]
  push_cast
  ring

/-- ‖c + 2‖ = 1: since c ≡ 2 mod 5, c + 2 ≡ 4 mod 5 is a unit. -/
lemma norm_sqrtNegOne_add_two : ‖sqrtNegOne + 2‖ = 1 := by
  have h4 : ‖((4 : ℕ) : ℤ_[5])‖ = 1 := by
    rw [PadicInt.norm_natCast_eq_one_iff]; decide
  have hrw : sqrtNegOne + 2 = (sqrtNegOne - 2) + ((4 : ℕ) : ℤ_[5]) := by
    push_cast; ring
  rw [hrw]
  have hne : ‖sqrtNegOne - 2‖ ≠ ‖((4 : ℕ) : ℤ_[5])‖ := by
    rw [h4]; exact ne_of_lt norm_sqrtNegOne_sub_two
  rw [PadicInt.norm_add_eq_max_of_ne hne, h4]
  exact max_eq_right (le_of_lt (h4 ▸ norm_sqrtNegOne_sub_two))

/-- (c - 2)(c + 2) = -5. -/
lemma sub_mul_add : (sqrtNegOne - 2) * (sqrtNegOne + 2) = -5 := by
  have := sqrtNegOne_sq
  linear_combination this

/-- The exact valuation: ‖φ(β)‖ = 1/5, i.e. β maps to a uniformizer of ℤ_[5]. -/
theorem norm_toPadic_beta : ‖toPadic beta‖ = (5 : ℝ)⁻¹ := by
  rw [toPadic_beta]
  have hmul : ‖(sqrtNegOne - 2) * (sqrtNegOne + 2)‖ = ‖(-5 : ℤ_[5])‖ := by
    rw [sub_mul_add]
  rw [_root_.norm_mul, norm_sqrtNegOne_add_two, mul_one] at hmul
  rw [hmul, _root_.norm_neg]
  have := PadicInt.norm_p (p := 5)
  simpa using this

end CnrsQ2
