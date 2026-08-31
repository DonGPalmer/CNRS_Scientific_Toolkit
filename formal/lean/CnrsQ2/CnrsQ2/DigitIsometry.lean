/-
CNRS Q2 formalization — Phase 5B (August 30, 2026): first-differing-digit norm.

This module proves the metric core of thm:q2_digit_carrier(iv).  For two
canonical valuation-ring expansions, agreement below index k and a mismatch at
index k force the p-adic norm of the represented difference to be exactly
(1/5)^k.  Scaling both values by an arbitrary integer power pi^n then gives the
corresponding field-level norm formula.

This deliberately stops short of packaging all finite-left digit strings into a
single Sigma_beta carrier.  The theorem proved here is the exact first-difference
metric statement needed for that later packaging, without introducing a new
representation type merely for presentation.
-/
import CnrsQ2.FieldDigitExpansion

namespace CnrsQ2

/-! ### Step 1: residue and remainder facts -/

/-- The chosen uniformizer reduces to zero modulo the maximal ideal. -/
theorem toZMod_pi5 : PadicInt.toZMod pi5 = 0 := by
  have hlt : ‖pi5‖ < 1 := by
    rw [norm_pi5]
    norm_num
  have hmem : pi5 ∈ IsLocalRing.maximalIdeal ℤ_[5] := by
    rw [PadicInt.maximalIdeal_eq_span_p, Ideal.mem_span_singleton,
        ← PadicInt.norm_lt_one_iff_dvd]
    exact hlt
  rwa [← PadicInt.ker_toZMod, RingHom.mem_ker] at hmem

/-- The remainder at stage n has residue exactly the nth canonical digit. -/
theorem toZMod_remSeq (x : ℤ_[5]) (n : ℕ) :
    PadicInt.toZMod (remSeq x n) = (digitSeq x n : ZMod 5) := by
  have h := congrArg PadicInt.toZMod (remSeq_spec x n)
  rw [map_sub, map_mul, toZMod_digitP, toZMod_pi5, zero_mul] at h
  exact sub_eq_zero.mp h

/-- If the nth canonical digits differ, the corresponding nth remainders differ
    by a unit of ℤ_[5], hence their difference has norm one. -/
theorem norm_remSeq_sub_eq_one_of_digit_ne (x y : ℤ_[5]) (n : ℕ)
    (hne : digitSeq x n ≠ digitSeq y n) :
    ‖remSeq x n - remSeq y n‖ = 1 := by
  have hz : PadicInt.toZMod (remSeq x n - remSeq y n) ≠ 0 := by
    rw [map_sub, toZMod_remSeq, toZMod_remSeq]
    intro h
    apply hne
    exact natCast_fin5_bijective.1 (sub_eq_zero.mp h)
  have hnotlt : ¬ ‖remSeq x n - remSeq y n‖ < 1 := by
    intro hlt
    apply hz
    have hmem : remSeq x n - remSeq y n ∈ IsLocalRing.maximalIdeal ℤ_[5] := by
      rw [PadicInt.maximalIdeal_eq_span_p, Ideal.mem_span_singleton,
          ← PadicInt.norm_lt_one_iff_dvd]
      exact hlt
    rwa [← PadicInt.ker_toZMod, RingHom.mem_ker] at hmem
  exact le_antisymm (PadicInt.norm_le_one _) (not_lt.mp hnotlt)

/-! ### Step 2: exact norm at the first differing digit -/

/-- Equal canonical digits below n give equal nth partial sums. -/
theorem partialSum_digitSeq_eq_of_prefix (x y : ℤ_[5]) (n : ℕ)
    (hagree : ∀ k < n, digitSeq x k = digitSeq y k) :
    partialSum (digitSeq x) n = partialSum (digitSeq y) n := by
  unfold partialSum
  exact Finset.sum_congr rfl (fun k hk => by
    rw [hagree k (Finset.mem_range.mp hk)])

/-- **First-differing-digit theorem in the valuation ring.**
    If the canonical digit expansions of x and y agree below n and differ at
    n, then the p-adic norm of x-y is exactly (1/5)^n. -/
theorem norm_sub_eq_pow_of_first_digit_diff (x y : ℤ_[5]) (n : ℕ)
    (hagree : ∀ k < n, digitSeq x k = digitSeq y k)
    (hne : digitSeq x n ≠ digitSeq y n) :
    ‖x - y‖ = (5 : ℝ)⁻¹ ^ n := by
  have hsum := partialSum_digitSeq_eq_of_prefix x y n hagree
  have hx := partialSum_digitSeq_spec x n
  have hy := partialSum_digitSeq_spec y n
  have hdiff :
      x - y = pi5 ^ n * (remSeq x n - remSeq y n) := by
    calc
      x - y = (x - partialSum (digitSeq x) n) -
          (y - partialSum (digitSeq y) n) := by rw [hsum]; ring
      _ = pi5 ^ n * remSeq x n - pi5 ^ n * remSeq y n := by rw [hx, hy]
      _ = pi5 ^ n * (remSeq x n - remSeq y n) := by ring
  rw [hdiff, _root_.norm_mul, norm_pow, norm_pi5,
      norm_remSeq_sub_eq_one_of_digit_ne x y n hne, mul_one]

/-! ### Step 3: field-level shifted metric formula -/

/-- Coercion of a valuation-ring difference into ℚ_[5] preserves its norm. -/
theorem norm_coe_sub_padicInt (x y : ℤ_[5]) :
    ‖((x - y : ℤ_[5]) : ℚ_[5])‖ = ‖x - y‖ := by
  exact (PadicInt.norm_def (z := x - y)).symm

/-- **Field-shifted first-difference theorem.**
    After shifting both valuation-ring digit streams by the same integer n,
    a first mismatch k places into the stream gives norm
    5^(-n) * (1/5)^k.  This is exactly 5^(-(n+k)) after identifying k with
    an integer exponent. -/
theorem norm_shifted_sub_eq_of_first_digit_diff (n : ℤ) (x y : ℤ_[5]) (k : ℕ)
    (hagree : ∀ j < k, digitSeq x j = digitSeq y j)
    (hne : digitSeq x k ≠ digitSeq y k) :
    ‖pi5Q ^ n * (x : ℚ_[5]) - pi5Q ^ n * (y : ℚ_[5])‖
      = (5 : ℝ) ^ (-n) * (5 : ℝ)⁻¹ ^ k := by
  rw [← mul_sub, _root_.norm_mul, norm_pi5Q_zpow]
  have hcoe : ‖((x - y : ℤ_[5]) : ℚ_[5])‖ = (5 : ℝ)⁻¹ ^ k := by
    rw [norm_coe_sub_padicInt]
    exact norm_sub_eq_pow_of_first_digit_diff x y k hagree hne
  rw [← PadicInt.coe_sub, hcoe]

end CnrsQ2
