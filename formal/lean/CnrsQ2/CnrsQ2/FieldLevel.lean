/-
CNRS Q2 formalization — Phase 3d (Session 116): the field-level statement.
The embedding ℤ[i] →+* ℤ_[5] extends to the fraction field:
Frac(ℤ[i]) →+* ℚ_[5], injective (automatic: any ring hom from a field),
with dense range, sending β to an element of norm 1/5.
This is the concrete form of K_β ≅ ℚ_5 (Q2a at field level).
-/
import CnrsQ2.Density

namespace CnrsQ2

/-- The composite ℤ[i] →+* ℚ_[5]. -/
noncomputable def toPadicField : GaussianInt →+* ℚ_[5] :=
  (PadicInt.Coe.ringHom).comp toPadic

lemma toPadicField_injective : Function.Injective toPadicField :=
  Subtype.coe_injective.comp toPadic_injective

/-- The field-level map Frac(ℤ[i]) →+* ℚ_[5]. -/
noncomputable def fracToPadic : FractionRing GaussianInt →+* ℚ_[5] :=
  IsFractionRing.lift toPadicField_injective

lemma fracToPadic_algebraMap (z : GaussianInt) :
    fracToPadic (algebraMap GaussianInt (FractionRing GaussianInt) z) = toPadicField z :=
  IsFractionRing.lift_algebraMap toPadicField_injective z

/-- Any ring hom from a field into a nontrivial ring is injective. -/
lemma fracToPadic_injective : Function.Injective fracToPadic :=
  fracToPadic.injective

/-- Norm of the image of β at field level is 1/5. -/
theorem norm_fracToPadic_beta :
    ‖fracToPadic (algebraMap GaussianInt (FractionRing GaussianInt) beta)‖ = (5 : ℝ)⁻¹ := by
  rw [fracToPadic_algebraMap]
  have : ‖toPadicField beta‖ = ‖toPadic beta‖ := rfl
  rw [this, norm_toPadic_beta]

/-- The rationals land in the range of fracToPadic: q = num/den with both
integers, and integer casts factor through ℤ[i]. -/
lemma ratCast_mem_range (q : ℚ) : (q : ℚ_[5]) ∈ Set.range fracToPadic := by
  refine ⟨(algebraMap GaussianInt (FractionRing GaussianInt) (q.num : GaussianInt)) /
          (algebraMap GaussianInt (FractionRing GaussianInt) ((q.den : ℤ) : GaussianInt)), ?_⟩
  rw [map_div₀, fracToPadic_algebraMap, fracToPadic_algebraMap]
  have hnum : toPadicField ((q.num : ℤ) : GaussianInt) = ((q.num : ℤ) : ℚ_[5]) :=
    map_intCast toPadicField q.num
  have hden : toPadicField (((q.den : ℤ) : ℤ) : GaussianInt) = (((q.den : ℤ) : ℤ) : ℚ_[5]) :=
    map_intCast toPadicField (q.den : ℤ)
  rw [hnum, hden]
  rw [Rat.cast_def]
  push_cast
  rfl

/-- The field-level map has dense range: ℚ is dense in ℚ_[5] and lies in the range. -/
theorem denseRange_fracToPadic : DenseRange fracToPadic := by
  have h : Set.range ((↑) : ℚ → ℚ_[5]) ⊆ Set.range fracToPadic := by
    rintro x ⟨q, rfl⟩
    exact ratCast_mem_range q
  exact (Padic.denseRange_ratCast (p := 5)).mono h

/--
CAPSTONE (Q2a, field level): ℚ_[5] is the β-adic completion of ℚ(i) = Frac(ℤ[i]).
There is an injective ring homomorphism Frac(ℤ[i]) →+* ℚ_[5] with dense range
sending β to an element of norm 1/5. This is K_β ≅ ℚ_5 in concrete form.
-/
theorem padic_is_beta_adic_completion_field :
    ∃ ψ : FractionRing GaussianInt →+* ℚ_[5],
      Function.Injective ψ ∧ DenseRange ψ ∧
      ‖ψ (algebraMap GaussianInt (FractionRing GaussianInt) beta)‖ = (5 : ℝ)⁻¹ :=
  ⟨fracToPadic, fracToPadic_injective, denseRange_fracToPadic, norm_fracToPadic_beta⟩

end CnrsQ2
