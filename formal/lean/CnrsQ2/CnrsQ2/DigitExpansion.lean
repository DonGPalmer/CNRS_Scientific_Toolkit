/-
CNRS Q2 formalization — Phase 4, COMPLETE (Session, August 2026).
Restated against the concrete types this project actually uses (ℤ_[5] via
`toPadic`, not the abstract Obeta/Kbeta of the superseded Phase3_AdicCompletion
branch). The old archived Phase4_DigitExpansion.lean was written against that
superseded abstract branch and does not type-check against this project; this
file is a full restatement, not a port.

thm:q2_digit_carrier(ii)/(iii) in full: every x : ℤ_[5] has a UNIQUE digit
sequence d : ℕ → Fin 5 whose partial sums Σ digitP(d n) · π^n converge to x.
Milestones 4a (exists_unique_digitP) and 4b (exists_unique_reduction) give the
one-step residue/reduction machinery; this file assembles them into the full
infinite expansion via a recursive digit/remainder construction, an exact
partial-sum identity, an ultrametric tail bound, and separate existence and
uniqueness arguments (uniqueness by strong induction, extracting each digit
from a norm-contradiction: a genuine mismatch would force norm exactly 1
against a derived bound of ≤ 1/5). Zero sorries — verified via `#print axioms`
on every theorem in this file, and via a full clean rebuild of the entire
project from scratch (not an incremental/cached build).
-/
import CnrsQ2.Density
import CnrsQ2.DigitAlphabet
import Mathlib.Analysis.Normed.Group.Ultra

namespace CnrsQ2

open Zsqrtd

/-! ### Step 0: the uniformizer π and its ideal -/

/-- The image of β under the embedding: our chosen uniformizer of ℤ_[5]. -/
noncomputable def pi5 : ℤ_[5] := toPadic beta

theorem norm_pi5 : ‖pi5‖ = (5 : ℝ)⁻¹ := norm_toPadic_beta

/-- π and 5 generate the same ideal: π is a uniformizer, not just any
    norm-1/5 element. Proof: ‖π‖ = ‖5‖ gives 5 ∣ π (norm_lt_one_iff_dvd),
    write π = 5*w; multiplicativity of the norm then forces ‖w‖ = 1, i.e. w
    is a unit (`PadicInt.isUnit_iff`), so π and 5 are associates. -/
theorem span_pi5_eq_maximalIdeal :
    Ideal.span ({pi5} : Set ℤ_[5]) = IsLocalRing.maximalIdeal ℤ_[5] := by
  rw [PadicInt.maximalIdeal_eq_span_p]
  have hnorm5 : ‖(5 : ℤ_[5])‖ = (5 : ℝ)⁻¹ := by
    have h := PadicInt.norm_p (p := 5)
    simpa using h
  have hlt1 : ‖pi5‖ < 1 := by rw [norm_pi5]; norm_num
  obtain ⟨w, hw⟩ := (PadicInt.norm_lt_one_iff_dvd pi5).mp hlt1
  have hnw : ‖pi5‖ = ‖((5 : ℕ) : ℤ_[5])‖ * ‖w‖ := by rw [hw, _root_.norm_mul]
  have h5cast : ((5 : ℕ) : ℤ_[5]) = (5 : ℤ_[5]) := by norm_cast
  rw [h5cast, norm_pi5, hnorm5] at hnw
  have hwunit : ‖w‖ = 1 := by
    have h5ne : (5 : ℝ)⁻¹ ≠ 0 := by norm_num
    field_simp at hnw
    linarith [hnw]
  have hu : IsUnit w := PadicInt.isUnit_iff.mpr hwunit
  obtain ⟨u, hu⟩ := hu
  rw [Ideal.span_singleton_eq_span_singleton]
  refine ⟨u⁻¹, ?_⟩
  rw [hw, ← hu]
  rw [mul_assoc]
  norm_cast
  simp

/-! ### Step 1: the digit alphabet directly on ℤ_[5], and the one-step
    residue-extraction lemma (the ℤ_[5]-side analogue of Milestone 4a). -/

/-- The digit alphabet, embedded directly in ℤ_[5] via the natural inclusion. -/
noncomputable def digitP (k : Fin 5) : ℤ_[5] := ((k : ℕ) : ℤ_[5])

/-- `digitP` agrees with the programme's own digit embedding, composed with
    the canonical map to ℤ_[5]: this connects the ℤ_[5]-side construction
    back to the actual CNRS-A digit alphabet used throughout the rest of the
    programme, rather than an ad hoc restatement. -/
theorem toPadic_digit (k : Fin 5) : toPadic (CnrsQ2.digit k) = digitP k := by
  have hd : CnrsQ2.digit k = (((k : ℕ) : ℤ) : GaussianInt) := by
    rw [Zsqrtd.intCast_val]; rfl
  rw [hd, digitP, map_intCast]
  push_cast
  ring

theorem toZMod_digitP (k : Fin 5) : PadicInt.toZMod (digitP k) = (k : ZMod 5) := by
  rw [digitP]
  have h := map_natCast (PadicInt.toZMod (p := 5)) (k : ℕ)
  rw [h]
  exact ZMod.natCast_rightInverse (n := 5) (k : ZMod 5)

/-- `Fin 5 → ZMod 5` by the natural inclusion is a bijection. -/
theorem natCast_fin5_bijective : Function.Bijective (fun k : Fin 5 => (k : ZMod 5)) := by
  decide

/-- **Milestone 4a (ℤ_[5]-side): unique residue digit.**
    Every y : ℤ_[5] has a unique digit k with y ≡ digitP k (mod the maximal
    ideal), i.e. `toZMod (y - digitP k) = 0`. This is the direct analogue,
    inside the completion, of `exists_unique_digit` on ℤ[i] itself
    (`DigitAlphabet.lean`'s `digit_bijective`, one level down). -/
theorem exists_unique_digitP (y : ℤ_[5]) :
    ∃! k : Fin 5, PadicInt.toZMod (y - digitP k) = 0 := by
  obtain ⟨k, hk⟩ := natCast_fin5_bijective.2 (PadicInt.toZMod y)
  simp only at hk
  refine ⟨k, ?_, ?_⟩
  · show PadicInt.toZMod (y - digitP k) = 0
    rw [map_sub, toZMod_digitP, hk, sub_self]
  · intro k' hk'
    have hk' : PadicInt.toZMod (y - digitP k') = 0 := hk'
    apply natCast_fin5_bijective.1
    show (k' : ZMod 5) = (k : ZMod 5)
    have h2 : PadicInt.toZMod (digitP k') = PadicInt.toZMod y := by
      have := hk'
      rw [map_sub, sub_eq_zero] at this
      exact this.symm
    rw [← toZMod_digitP k', h2, hk]

/-! ### Step 2: the one-step quotient, y ↦ (y - digitP k) / π, well-defined
    in ℤ_[5] because the numerator lies in the maximal ideal = (π). -/

/-- **Milestone 4b (ℤ_[5]-side): the one-step reduction.** Every y : ℤ_[5]
    factors uniquely as `y = digitP k + π * y'` for some `y' : ℤ_[5]` — the
    single recursive step of the digit-extraction algorithm, now running
    inside the complete ring rather than terminating after finitely many
    steps on ℤ[i]. This is new: nothing in the project prior to this file
    reaches inside the completion at all. -/
theorem exists_unique_reduction (y : ℤ_[5]) :
    ∃! k : Fin 5, ∃ y' : ℤ_[5], y - digitP k = pi5 * y' := by
  obtain ⟨k, hk0, hkU⟩ := exists_unique_digitP y
  have hmem_iff : ∀ z : ℤ_[5], PadicInt.toZMod z = 0 ↔ ∃ y' : ℤ_[5], z = pi5 * y' := by
    intro z
    rw [← RingHom.mem_ker, PadicInt.ker_toZMod, ← span_pi5_eq_maximalIdeal,
        Ideal.mem_span_singleton']
    constructor
    · rintro ⟨a, ha⟩; exact ⟨a, by rw [← ha]; ring⟩
    · rintro ⟨a, ha⟩; exact ⟨a, by rw [ha]; ring⟩
  refine ⟨k, (hmem_iff _).mp hk0, ?_⟩
  rintro k' hk'
  exact hkU k' ((hmem_iff _).mpr hk')

/-! ### Step 4: the recursive digit/remainder construction, existence and
    uniqueness of the full convergent expansion. -/

/-- One step of the construction, packaging Milestone 4b's witness pair. -/
noncomputable def stepPair (y : ℤ_[5]) : Fin 5 × ℤ_[5] :=
  ⟨(exists_unique_reduction y).exists.choose,
   (exists_unique_reduction y).exists.choose_spec.choose⟩

noncomputable def stepDigit (y : ℤ_[5]) : Fin 5 := (stepPair y).1
noncomputable def stepRemainder (y : ℤ_[5]) : ℤ_[5] := (stepPair y).2

theorem stepPair_spec (y : ℤ_[5]) :
    y - digitP (stepDigit y) = pi5 * stepRemainder y :=
  (exists_unique_reduction y).exists.choose_spec.choose_spec

/-- The remainder sequence: `remSeq x 0 = x`, each subsequent term is the
    previous step's remainder. -/
noncomputable def remSeq (x : ℤ_[5]) : ℕ → ℤ_[5]
  | 0 => x
  | n + 1 => stepRemainder (remSeq x n)

/-- The digit sequence read off at each step of `remSeq`. -/
noncomputable def digitSeq (x : ℤ_[5]) (n : ℕ) : Fin 5 := stepDigit (remSeq x n)

theorem remSeq_spec (x : ℤ_[5]) (n : ℕ) :
    remSeq x n - digitP (digitSeq x n) = pi5 * remSeq x (n + 1) :=
  stepPair_spec (remSeq x n)

/-- The partial sums of a digit sequence. -/
noncomputable def partialSum (f : ℕ → Fin 5) (N : ℕ) : ℤ_[5] :=
  ∑ n ∈ Finset.range N, digitP (f n) * pi5 ^ n

/-- The defining recursive identity: `x` minus the `N`th partial sum of its
    own canonical digit sequence is exactly `π^N` times the `N`th
    remainder. -/
theorem partialSum_digitSeq_spec (x : ℤ_[5]) (N : ℕ) :
    x - partialSum (digitSeq x) N = pi5 ^ N * remSeq x N := by
  induction N with
  | zero => simp [partialSum, remSeq]
  | succ N ih =>
    rw [partialSum, Finset.sum_range_succ, ← partialSum]
    have h := remSeq_spec x N
    have : x - (partialSum (digitSeq x) N + digitP (digitSeq x N) * pi5 ^ N)
         = (x - partialSum (digitSeq x) N) - digitP (digitSeq x N) * pi5 ^ N := by ring
    rw [this, ih]
    have : pi5 ^ N * remSeq x N - digitP (digitSeq x N) * pi5 ^ N
         = pi5 ^ N * (remSeq x N - digitP (digitSeq x N)) := by ring
    rw [this, h]
    ring

/-- For **any** digit sequence (not necessarily the canonical one), the
    partial sums move by at most `‖π‖^m` past index `m` — the ultrametric
    tail bound underlying both existence and uniqueness below. -/
theorem partialSum_tail_bound (f : ℕ → Fin 5) (m N : ℕ) (hmN : m ≤ N) :
    ‖partialSum f N - partialSum f m‖ ≤ (5 : ℝ)⁻¹ ^ m := by
  have hrw : partialSum f N - partialSum f m
      = ∑ n ∈ Finset.Ico m N, digitP (f n) * pi5 ^ n := by
    rw [partialSum, partialSum, ← Finset.sum_Ico_eq_sub _ hmN]
  rw [hrw]
  rcases Finset.eq_empty_or_nonempty (Finset.Ico m N) with he | hne
  · simp [he]
  · apply IsUltrametricDist.norm_sum_le_of_forall_le_of_nonneg (by positivity)
    intro k hk
    rw [Finset.mem_Ico] at hk
    have h1 : ‖digitP (f k) * pi5 ^ k‖ = ‖digitP (f k)‖ * ‖pi5‖ ^ k := by
      rw [_root_.norm_mul, norm_pow]
    rw [h1]
    calc ‖digitP (f k)‖ * ‖pi5‖ ^ k
        ≤ 1 * ‖pi5‖ ^ k := by
          apply mul_le_mul_of_nonneg_right (PadicInt.norm_le_one _) (by positivity)
      _ = ((5:ℝ)⁻¹) ^ k := by rw [one_mul, norm_pi5]
      _ ≤ (5:ℝ)⁻¹ ^ m := by
          apply pow_le_pow_of_le_one (by norm_num) (by norm_num) hk.1

/-- **Existence** direction: the canonical construction's partial sums
    converge to `x`. -/
theorem tendsto_partialSum_digitSeq (x : ℤ_[5]) :
    Filter.Tendsto (partialSum (digitSeq x)) Filter.atTop (nhds x) := by
  rw [tendsto_iff_norm_sub_tendsto_zero]
  apply squeeze_zero (fun N => norm_nonneg _) (fun N => ?_)
    (tendsto_pow_atTop_nhds_zero_of_lt_one
      (by norm_num) (by norm_num : (5:ℝ)⁻¹ < 1))
  rw [norm_sub_rev, partialSum_digitSeq_spec]
  calc ‖pi5 ^ N * remSeq x N‖ = ‖pi5‖ ^ N * ‖remSeq x N‖ := by
        rw [_root_.norm_mul, norm_pow]
    _ ≤ ‖pi5‖ ^ N * 1 := by
        apply mul_le_mul_of_nonneg_left (PadicInt.norm_le_one _) (by positivity)
    _ = (5:ℝ)⁻¹ ^ N := by rw [mul_one, norm_pi5]

/-- Any digit sequence whose partial sums converge to `x` matches the
    canonical one at every index — the **uniqueness** direction. -/
theorem digitSeq_unique (x : ℤ_[5]) (f : ℕ → Fin 5)
    (hf : Filter.Tendsto (partialSum f) Filter.atTop (nhds x)) :
    f = digitSeq x := by
  funext n
  induction n using Nat.strong_induction_on with
  | _ n IH =>
  have hagree : ∀ k < n, f k = digitSeq x k := fun k hk => IH k hk
  have hpartial_eq : partialSum f n = partialSum (digitSeq x) n := by
    unfold partialSum
    exact Finset.sum_congr rfl (fun k hk => by rw [hagree k (Finset.mem_range.mp hk)])
  -- Tail bounds past index `n+1`, from the limit, for both sequences.
  have htail_f : ‖x - partialSum f (n+1)‖ ≤ (5:ℝ)⁻¹ ^ (n+1) := by
    have htendsto : Filter.Tendsto (fun N => ‖partialSum f N - partialSum f (n+1)‖)
        Filter.atTop (nhds ‖x - partialSum f (n+1)‖) := (hf.sub tendsto_const_nhds).norm
    exact le_of_tendsto htendsto (Filter.eventually_atTop.mpr
      ⟨n+1, fun N hN => partialSum_tail_bound f (n+1) N hN⟩)
  have htail_g : ‖x - partialSum (digitSeq x) (n+1)‖ ≤ (5:ℝ)⁻¹ ^ (n+1) := by
    have htendsto : Filter.Tendsto (fun N => ‖partialSum (digitSeq x) N - partialSum (digitSeq x) (n+1)‖)
        Filter.atTop (nhds ‖x - partialSum (digitSeq x) (n+1)‖) :=
      ((tendsto_partialSum_digitSeq x).sub tendsto_const_nhds).norm
    exact le_of_tendsto htendsto (Filter.eventually_atTop.mpr
      ⟨n+1, fun N hN => partialSum_tail_bound (digitSeq x) (n+1) N hN⟩)
  have hstep_f : partialSum f (n+1) = partialSum f n + digitP (f n) * pi5 ^ n := by
    rw [partialSum, Finset.sum_range_succ, ← partialSum]
  have hstep_g : partialSum (digitSeq x) (n+1)
      = partialSum (digitSeq x) n + digitP (digitSeq x n) * pi5 ^ n := by
    rw [partialSum, Finset.sum_range_succ, ← partialSum]
  have hkey : ‖digitP (f n) - digitP (digitSeq x n)‖ * (5:ℝ)⁻¹ ^ n ≤ (5:ℝ)⁻¹ ^ (n+1) := by
    have hdiff : partialSum f (n+1) - partialSum (digitSeq x) (n+1)
        = (digitP (f n) - digitP (digitSeq x n)) * pi5 ^ n := by
      rw [hstep_f, hstep_g, hpartial_eq]; ring
    have hbound : ‖partialSum f (n+1) - partialSum (digitSeq x) (n+1)‖ ≤ (5:ℝ)⁻¹ ^ (n+1) := by
      calc ‖partialSum f (n+1) - partialSum (digitSeq x) (n+1)‖
          = ‖(partialSum f (n+1) - x) + (x - partialSum (digitSeq x) (n+1))‖ := by
            congr 1; ring
        _ ≤ max ‖partialSum f (n+1) - x‖ ‖x - partialSum (digitSeq x) (n+1)‖ :=
            IsUltrametricDist.isNonarchimedean_norm _ _
        _ ≤ (5:ℝ)⁻¹ ^ (n+1) := by
            apply max_le
            · rw [norm_sub_rev]; exact htail_f
            · exact htail_g
    rw [hdiff, _root_.norm_mul, norm_pow, norm_pi5] at hbound
    exact hbound
  have hne1 : ‖digitP (f n) - digitP (digitSeq x n)‖ ≤ (5:ℝ)⁻¹ := by
    have h5n : (0:ℝ) < (5:ℝ)⁻¹ ^ n := by positivity
    have := (mul_le_mul_iff_of_pos_right h5n).mp
      (by rw [pow_succ] at hkey; linarith [hkey] : ‖digitP (f n) - digitP (digitSeq x n)‖ * (5:ℝ)⁻¹ ^ n
        ≤ (5:ℝ)⁻¹ * (5:ℝ)⁻¹ ^ n)
    exact this
  by_contra hne
  have hz : PadicInt.toZMod (digitP (f n) - digitP (digitSeq x n)) ≠ 0 := by
    rw [map_sub, toZMod_digitP, toZMod_digitP]
    intro h
    exact hne (natCast_fin5_bijective.1 (sub_eq_zero.mp h))
  have hnotlt : ¬ ‖digitP (f n) - digitP (digitSeq x n)‖ < 1 := by
    intro hlt
    apply hz
    have hmem : digitP (f n) - digitP (digitSeq x n) ∈ IsLocalRing.maximalIdeal ℤ_[5] := by
      rw [PadicInt.maximalIdeal_eq_span_p, Ideal.mem_span_singleton,
          ← PadicInt.norm_lt_one_iff_dvd]
      exact hlt
    rwa [← PadicInt.ker_toZMod, RingHom.mem_ker] at hmem
  have heq1 : ‖digitP (f n) - digitP (digitSeq x n)‖ = 1 :=
    le_antisymm (PadicInt.norm_le_one _) (not_lt.mp hnotlt)
  rw [heq1] at hne1
  norm_num at hne1

/-- **Milestone 4c, complete**: every `x : ℤ_[5]` has a unique digit
    sequence whose partial sums converge to it — the full statement of
    thm:q2_digit_carrier(ii)/(iii) in these concrete types. -/
theorem exists_unique_digit_expansion (x : ℤ_[5]) :
    ∃! d : ℕ → Fin 5,
      Filter.Tendsto
        (fun N => ∑ n ∈ Finset.range N, digitP (d n) * pi5 ^ n)
        Filter.atTop (nhds x) :=
  ⟨digitSeq x, tendsto_partialSum_digitSeq x,
    fun f hf => digitSeq_unique x f hf⟩

end CnrsQ2
