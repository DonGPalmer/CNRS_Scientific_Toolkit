/-
CNRS Q2 formalization — Phase 5 (August 30, 2026): field-level digit carrier.

This module extends the valuation-ring expansion theorem from `DigitExpansion`
to nonzero elements of ℚ_[5].  For x ≠ 0 we normalize by the exact p-adic
valuation v(x), obtain a norm-one element of ℤ_[5], expand that element uniquely
in powers of π = image(β), and scale back by π^v(x).  The result is the concrete
form of thm:q2_digit_carrier(iii): finitely many negative-index digits, with the
first occupied digit at the valuation index and nonzero.

This Phase-5A increment deliberately stops at the field-carrier
existence/uniqueness theorem.  The first-differing-digit isometry theorem for
thm:q2_digit_carrier(iv) is a separate follow-on increment after this module
has passed the pinned GitHub Lean build.

The final paper statement that finite-support strings correspond exactly to
R_A = ℤ[i][β⁻¹] is deliberately not asserted here: the current Lean project
has proved the residue digit system, but not yet the separate finite CNS
expansion theorem for every Gaussian integer needed for the converse.
-/
import CnrsQ2.DigitExpansion
import CnrsQ2.FieldLevel
import Mathlib.Topology.Maps.Basic

namespace CnrsQ2

/-! ### Step 1: the uniformizer in the field and valuation normalization -/

/-- The chosen β-uniformizer, viewed in the p-adic field. -/
noncomputable def pi5Q : ℚ_[5] := (pi5 : ℚ_[5])

/-- The field norm of the chosen β-uniformizer is exactly 1/5. -/
theorem norm_pi5Q : ‖pi5Q‖ = (5 : ℝ)⁻¹ := by
  calc
    ‖pi5Q‖ = ‖(pi5 : ℚ_[5])‖ := by rfl
    _ = ‖pi5‖ := (PadicInt.norm_def (z := pi5)).symm
    _ = (5 : ℝ)⁻¹ := norm_pi5

/-- The chosen field uniformizer is nonzero. -/
theorem pi5Q_ne_zero : pi5Q ≠ 0 := by
  intro h
  have hn : ‖pi5Q‖ = 0 := by rw [h, norm_zero]
  rw [norm_pi5Q] at hn
  norm_num at hn

/-- Integer powers of the chosen β-uniformizer have the expected norm. -/
theorem norm_pi5Q_zpow (n : ℤ) :
    ‖pi5Q ^ n‖ = (5 : ℝ) ^ (-n) := by
  rw [norm_zpow, norm_pi5Q]
  exact inv_zpow' (5 : ℝ) n

/-- The raw normalized representative π^{-v(x)}x in the field. -/
noncomputable def rawFieldUnit (x : ℚ_[5]) : ℚ_[5] :=
  pi5Q ^ (-Padic.valuation x) * x

/-- For nonzero x, the raw normalized representative has norm exactly one. -/
theorem norm_rawFieldUnit (x : ℚ_[5]) (hx : x ≠ 0) :
    ‖rawFieldUnit x‖ = 1 := by
  rw [rawFieldUnit, _root_.norm_mul, norm_pi5Q_zpow,
      Padic.norm_eq_zpow_neg_valuation hx]
  simp only [neg_neg]
  change (5 : ℝ) ^ (Padic.valuation x) * (5 : ℝ) ^ (-Padic.valuation x) = 1
  rw [mul_comm]
  exact zpow_neg_mul_zpow_self (Padic.valuation x) (by norm_num : (5 : ℝ) ≠ 0)

/-- The normalized valuation-ring representative of a nonzero p-adic field
    element: π^{-v(x)}x has norm 1, hence lies in ℤ_[5]. -/
noncomputable def fieldUnit (x : ℚ_[5]) (hx : x ≠ 0) : ℤ_[5] :=
  ⟨rawFieldUnit x, by rw [norm_rawFieldUnit x hx]⟩

@[simp]
theorem coe_fieldUnit (x : ℚ_[5]) (hx : x ≠ 0) :
    (fieldUnit x hx : ℚ_[5]) = pi5Q ^ (-Padic.valuation x) * x := rfl

/-- The normalized field representative is a unit of the valuation ring in
    the metric sense: its norm is exactly 1. -/
theorem norm_fieldUnit (x : ℚ_[5]) (hx : x ≠ 0) :
    ‖fieldUnit x hx‖ = 1 := by
  rw [PadicInt.norm_def, coe_fieldUnit]
  exact norm_rawFieldUnit x hx

/-- Scaling the normalized valuation-ring representative back by π^{v(x)}
    recovers x exactly. -/
theorem fieldUnit_reconstruct (x : ℚ_[5]) (hx : x ≠ 0) :
    pi5Q ^ (Padic.valuation x) * (fieldUnit x hx : ℚ_[5]) = x := by
  rw [coe_fieldUnit, ← mul_assoc]
  have hpow :
      pi5Q ^ (Padic.valuation x) * pi5Q ^ (-Padic.valuation x) = 1 := by
    rw [mul_comm]
    exact zpow_neg_mul_zpow_self (Padic.valuation x) pi5Q_ne_zero
  rw [hpow, one_mul]

/-! ### Step 2: the leading digit of a normalized nonzero field element -/

/-- A valuation-ring element of norm one cannot have zero as its first
    canonical digit. -/
theorem digitSeq_zero_ne_of_norm_one (u : ℤ_[5]) (hu : ‖u‖ = 1) :
    digitSeq u 0 ≠ 0 := by
  intro h0
  have hs := remSeq_spec u 0
  have heq : u = pi5 * remSeq u 1 := by
    simpa [remSeq, digitP, h0] using hs
  have hle : ‖u‖ ≤ (5 : ℝ)⁻¹ := by
    rw [heq, _root_.norm_mul, norm_pi5]
    calc
      (5 : ℝ)⁻¹ * ‖remSeq u 1‖
          ≤ (5 : ℝ)⁻¹ * 1 := by
            apply mul_le_mul_of_nonneg_left (PadicInt.norm_le_one _) (by positivity)
      _ = (5 : ℝ)⁻¹ := by ring
  rw [hu] at hle
  norm_num at hle

/-- The first occupied digit in the normalized expansion of a nonzero field
    element is nonzero. -/
theorem fieldUnit_first_digit_ne_zero (x : ℚ_[5]) (hx : x ≠ 0) :
    digitSeq (fieldUnit x hx) 0 ≠ 0 :=
  digitSeq_zero_ne_of_norm_one (fieldUnit x hx) (norm_fieldUnit x hx)

/-! ### Step 3: field-level partial sums and the Q2b(iii) capstone -/

/-- A finite β-adic partial sum in the field with arbitrary integer starting
    index `n`.  The inner digit sum starts at exponent zero and is then scaled
    by π^n, so negative `n` represents the finite left tail. -/
noncomputable def fieldPartialSum (n : ℤ) (d : ℕ → Fin 5) (N : ℕ) : ℚ_[5] :=
  pi5Q ^ n * (partialSum d N : ℚ_[5])

/-- Multiplying a field partial sum by π^{-n} removes its integer shift. -/
theorem unscale_fieldPartialSum (n : ℤ) (d : ℕ → Fin 5) (N : ℕ) :
    pi5Q ^ (-n) * fieldPartialSum n d N = (partialSum d N : ℚ_[5]) := by
  rw [fieldPartialSum, ← mul_assoc,
      zpow_neg_mul_zpow_self n pi5Q_ne_zero, one_mul]

/-- Coercing the canonical ℤ_[5] partial sums into ℚ_[5] preserves their
    convergence. -/
theorem tendsto_coe_partialSum_digitSeq (u : ℤ_[5]) :
    Filter.Tendsto
      (fun N => (partialSum (digitSeq u) N : ℚ_[5]))
      Filter.atTop (nhds (u : ℚ_[5])) := by
  change Filter.Tendsto
    (Subtype.val ∘ partialSum (digitSeq u))
    Filter.atTop (nhds (Subtype.val u))
  exact
    (PadicInt.isOpenEmbedding_coe.continuous.tendsto u).comp
      (tendsto_partialSum_digitSeq u)

/-- Existence: after scaling the canonical expansion of the normalized unit by
    π^{v(x)}, the field partial sums converge to x. -/
theorem tendsto_fieldPartialSum_digitSeq (x : ℚ_[5]) (hx : x ≠ 0) :
    Filter.Tendsto
      (fieldPartialSum (Padic.valuation x) (digitSeq (fieldUnit x hx)))
      Filter.atTop (nhds x) := by
  change Filter.Tendsto
    (fun N =>
      pi5Q ^ (Padic.valuation x) *
        (partialSum (digitSeq (fieldUnit x hx)) N : ℚ_[5]))
    Filter.atTop (nhds x)
  have hcoe := tendsto_coe_partialSum_digitSeq (fieldUnit x hx)
  have hscaled := Filter.Tendsto.const_mul (pi5Q ^ (Padic.valuation x)) hcoe
  rw [fieldUnit_reconstruct x hx] at hscaled
  exact hscaled

/-- Uniqueness: any digit stream converging to x with the canonical valuation
    shift is the canonical digit stream of the normalized valuation-ring unit. -/
theorem fieldDigitSeq_unique (x : ℚ_[5]) (hx : x ≠ 0) (f : ℕ → Fin 5)
    (hf : Filter.Tendsto
      (fieldPartialSum (Padic.valuation x) f)
      Filter.atTop (nhds x)) :
    f = digitSeq (fieldUnit x hx) := by
  have hunscaledRaw :=
    Filter.Tendsto.const_mul (pi5Q ^ (-Padic.valuation x)) hf
  have hfun :
      (fun N =>
        pi5Q ^ (-Padic.valuation x) *
          fieldPartialSum (Padic.valuation x) f N)
        = (fun N => (partialSum f N : ℚ_[5])) := by
    funext N
    exact unscale_fieldPartialSum (Padic.valuation x) f N
  rw [hfun] at hunscaledRaw
  have hlim :
      pi5Q ^ (-Padic.valuation x) * x = (fieldUnit x hx : ℚ_[5]) :=
    (coe_fieldUnit x hx).symm
  rw [hlim] at hunscaledRaw
  have hz5 : Filter.Tendsto (partialSum f) Filter.atTop
      (nhds (fieldUnit x hx)) := by
    apply (PadicInt.isOpenEmbedding_coe.tendsto_nhds_iff).mpr
    change Filter.Tendsto
      (fun N => (partialSum f N : ℚ_[5]))
      Filter.atTop (nhds (fieldUnit x hx : ℚ_[5]))
    exact hunscaledRaw
  exact digitSeq_unique (fieldUnit x hx) f hz5

/-- **Q2b(iii), field-level capstone.** Every nonzero x : ℚ_[5] has a unique
    β-adic digit expansion whose first occupied exponent is exactly
    `Padic.valuation x`.  The digit at that exponent is nonzero, and the
    shifted finite partial sums converge to x.  Consequently only finitely
    many negative-index digits occur. -/
theorem exists_unique_field_digit_expansion (x : ℚ_[5]) (hx : x ≠ 0) :
    ∃! d : ℕ → Fin 5,
      Filter.Tendsto
        (fieldPartialSum (Padic.valuation x) d)
        Filter.atTop (nhds x) ∧ d 0 ≠ 0 :=
  ⟨digitSeq (fieldUnit x hx),
    ⟨tendsto_fieldPartialSum_digitSeq x hx,
      fieldUnit_first_digit_ne_zero x hx⟩,
    fun f hf => fieldDigitSeq_unique x hx f hf.1⟩

end CnrsQ2
