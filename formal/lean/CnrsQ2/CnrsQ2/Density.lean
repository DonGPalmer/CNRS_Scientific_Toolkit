/-
CNRS Q2 formalization — Phase 3c (new, Session 116): the embedding
ℤ[i] →+* ℤ_[5] has dense range. Together with injectivity (Phase 3b) and
‖φ(β)‖ = 1/5 (Phase 3b), this establishes concretely that ℤ_[5] is the
β-adic completion of ℤ[i]: an injective ring homomorphism with dense image
carrying the base β to a uniformizer. Density is inherited from the density
of ℤ itself in ℤ_[5] (PadicInt.denseRange_intCast), since φ restricted to
the rational integers is the canonical inclusion.
-/
import CnrsQ2.Embedding
import Mathlib.NumberTheory.Padics.RingHoms

namespace CnrsQ2

/-- φ restricted to ℤ ⊂ ℤ[i] is the canonical map ℤ → ℤ_[5]. -/
lemma toPadic_intCast (n : ℤ) : toPadic (n : GaussianInt) = (n : ℤ_[5]) :=
  map_intCast toPadic n

/-- The embedding ℤ[i] →+* ℤ_[5] has dense range. -/
theorem denseRange_toPadic : DenseRange toPadic := by
  have h : Set.range (Int.cast : ℤ → ℤ_[5]) ⊆ Set.range toPadic := by
    rintro x ⟨n, rfl⟩
    exact ⟨(n : GaussianInt), toPadic_intCast n⟩
  exact (PadicInt.denseRange_intCast (p := 5)).mono h

/--
CAPSTONE (Q2a, concrete form): ℤ_[5] is the β-adic completion of ℤ[i].
Concretely: there is an injective ring homomorphism ℤ[i] →+* ℤ_[5] with dense
range, sending the CNRS base β = -2+i to an element of norm 1/5 (a uniformizer).
This is the full mathematical content of K_β ≅ ℚ_5 at the integer level,
stated without the abstract adic-completion machinery.
-/
theorem padicInt_is_beta_adic_completion :
    ∃ φ : GaussianInt →+* ℤ_[5],
      Function.Injective φ ∧ DenseRange φ ∧ ‖φ beta‖ = (5 : ℝ)⁻¹ :=
  ⟨toPadic, toPadic_injective, denseRange_toPadic, norm_toPadic_beta⟩

end CnrsQ2
