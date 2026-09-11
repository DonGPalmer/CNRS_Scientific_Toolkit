/-
CNRS Q2 formalization — Phase 5C' (August 30, 2026), Part A:
arbitrary digit-stream completion.

The already verified Phase-4 theorem `partialSum_tail_bound` applies to every
stream `d : ℕ → Fin 5`, not only to canonical streams.  This module turns that
uniform tail estimate into a Cauchy theorem, uses completeness of ℤ_[5] to
construct the stream limit, and then invokes the verified Phase-4 uniqueness
theorem to show that every raw stream is exactly the canonical digit stream of
its own limit.

This is the key simplification relative to the withdrawn Phase-5C/5D Toolkit
experiment: convergence is a theorem of the digit syntax, not a certificate
stored inside the carrier.
-/
import CnrsQ2.DigitIsometry
import Mathlib.Topology.MetricSpace.Cauchy

namespace CnrsQ2

/-! ### 1. Every digit stream is Cauchy -/

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

/-- Partial sums of every digit stream form a Cauchy sequence in ℤ_[5]. -/
theorem partialSum_cauchySeq (d : ℕ → Fin 5) : CauchySeq (partialSum d) := by
  refine cauchySeq_of_le_tendsto_0 (fun N : ℕ => (5 : ℝ)⁻¹ ^ N) ?_ ?_
  · intro n m N hn hm
    exact dist_partialSum_le d N n m hn hm
  · exact tendsto_pow_atTop_nhds_zero_of_lt_one
      (by norm_num) (by norm_num : (5 : ℝ)⁻¹ < 1)

/-! ### 2. The canonical limit of an arbitrary stream -/

/-- The automatically existing ℤ_[5] limit of an arbitrary digit stream. -/
noncomputable def digitStreamLimit (d : ℕ → Fin 5) : ℤ_[5] :=
  Filter.atTop.limUnder (partialSum d)

/-- Every arbitrary digit stream converges to `digitStreamLimit d`. -/
theorem tendsto_partialSum_digitStreamLimit (d : ℕ → Fin 5) :
    Filter.Tendsto (partialSum d) Filter.atTop (nhds (digitStreamLimit d)) :=
  (partialSum_cauchySeq d).tendsto_limUnder

/-- Every raw digit stream is the canonical digit stream of its own limit. -/
theorem digits_eq_digitSeq_digitStreamLimit (d : ℕ → Fin 5) :
    d = digitSeq (digitStreamLimit d) :=
  digitSeq_unique (digitStreamLimit d) d (tendsto_partialSum_digitStreamLimit d)

/-- Taking the stream limit of the canonical digit sequence recovers the
    original valuation-ring element. -/
theorem digitStreamLimit_digitSeq (x : ℤ_[5]) :
    digitStreamLimit (digitSeq x) = x := by
  exact tendsto_nhds_unique
    (tendsto_partialSum_digitStreamLimit (digitSeq x))
    (tendsto_partialSum_digitSeq x)

/-! ### 3. A nonzero leading digit is exactly the norm-one stratum -/

/-- A raw stream with nonzero leading digit has a norm-one limit in ℤ_[5]. -/
theorem norm_digitStreamLimit_eq_one_of_first_ne_zero (d : ℕ → Fin 5)
    (h0 : d 0 ≠ 0) : ‖digitStreamLimit d‖ = 1 := by
  have hcanon := digits_eq_digitSeq_digitStreamLimit d
  have hfirst : digitSeq (digitStreamLimit d) 0 ≠ 0 := by
    rw [← hcanon]
    exact h0
  have hres := toZMod_remSeq (digitStreamLimit d) 0
  have hres0 : PadicInt.toZMod (digitStreamLimit d) =
      (digitSeq (digitStreamLimit d) 0 : ZMod 5) := by
    simpa [remSeq] using hres
  have hdigit : (digitSeq (digitStreamLimit d) 0 : ZMod 5) ≠ 0 := by
    intro hz
    apply hfirst
    apply natCast_fin5_bijective.1
    simpa using hz
  have hzmod : PadicInt.toZMod (digitStreamLimit d) ≠ 0 := by
    rw [hres0]
    exact hdigit
  have hnotlt : ¬ ‖digitStreamLimit d‖ < 1 := by
    intro hlt
    apply hzmod
    have hmem : digitStreamLimit d ∈ IsLocalRing.maximalIdeal ℤ_[5] := by
      rw [PadicInt.maximalIdeal_eq_span_p, Ideal.mem_span_singleton,
          ← PadicInt.norm_lt_one_iff_dvd]
      exact hlt
    rwa [← PadicInt.ker_toZMod, RingHom.mem_ker] at hmem
  exact le_antisymm (PadicInt.norm_le_one _) (not_lt.mp hnotlt)

/-- A stream with nonzero leading digit has nonzero limit. -/
theorem digitStreamLimit_ne_zero_of_first_ne_zero (d : ℕ → Fin 5)
    (h0 : d 0 ≠ 0) : digitStreamLimit d ≠ 0 := by
  intro hz
  have hn := norm_digitStreamLimit_eq_one_of_first_ne_zero d h0
  rw [hz, norm_zero] at hn
  norm_num at hn

end CnrsQ2
