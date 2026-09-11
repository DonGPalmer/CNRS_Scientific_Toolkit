/-
CNRSArithmetic Phase E6 candidate: finite division graph and cycle classification.

This module builds on the frozen E3--E5 results.  It packages the invariant
E3 carrier as a deterministic finite graph, identifies its periodic vertices,
derives the exact arithmetic reconstruction equation for a cycle, and proves
that an admissible division orbit is nondivisible exactly when it reaches a
nonzero periodic state.

The classifier is structural and exact.  It does not claim a closed-form
enumeration of cycles for every Gaussian divisor, a minimal period theorem,
or an online division transducer.
-/
import CNRSArithmetic.DivisionTermination
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- Iterating first for `m` steps and then for `n` steps is the same as
    iterating for `m + n` steps. -/
theorem divisionIterate_add (Q N : GaussianInt) (m n : ℕ) :
    divisionIterate Q N (m + n) =
      divisionIterate Q (divisionIterate Q N m) n := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Nat.add_succ, divisionIterate_succ, divisionIterate_succ, ih]

/-- Zero is a fixed state for every admissible divisor. -/
theorem divisionNext_zero
    (Q : GaussianInt) (hQ : DivisionAdmissible Q) :
    divisionNext Q 0 = 0 := by
  have h :=
    (divisionStep_unique Q 0 hQ (d := 0) (N' := 0) (by simp)).2
  exact h.symm

/-- Once an admissible exact-division orbit reaches zero, it stays zero. -/
theorem divisionIterate_zero_state
    (Q : GaussianInt) (hQ : DivisionAdmissible Q) (n : ℕ) :
    divisionIterate Q 0 n = 0 := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [divisionIterate_succ, ih, divisionNext_zero Q hQ]

/-- A zero state persists at every later index. -/
theorem divisionIterate_eq_zero_of_le
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    {n m : ℕ} (hn : divisionIterate Q N n = 0) (hnm : n ≤ m) :
    divisionIterate Q N m = 0 := by
  obtain ⟨k, rfl⟩ := Nat.exists_eq_add_of_le hnm
  rw [divisionIterate_add, hn, divisionIterate_zero_state Q hQ]

/-- A state is periodic when it returns to itself after a positive number of
    deterministic division steps. -/
def DivisionPeriodicState (Q N : GaussianInt) : Prop :=
  ∃ period : ℕ, 0 < period ∧ divisionIterate Q N period = N

/-- Every positive multiple of a period returns a periodic state to itself. -/
theorem divisionIterate_mul_period_eq_of_periodic
    (Q N : GaussianInt) {period : ℕ}
    (hperiod : divisionIterate Q N period = N) (k : ℕ) :
    divisionIterate Q N (k * period) = N := by
  induction k with
  | zero => simp
  | succ k ih =>
      rw [Nat.succ_mul, divisionIterate_add, ih, hperiod]

/-- A periodic admissible orbit that ever reaches zero began at zero. -/
theorem eq_zero_of_periodic_of_terminates
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    (hperiodic : DivisionPeriodicState Q N)
    (hterminates : ∃ n : ℕ, divisionIterate Q N n = 0) :
    N = 0 := by
  rcases hperiodic with ⟨period, hp, hperiod⟩
  rcases hterminates with ⟨n, hn⟩
  have hp1 : 1 ≤ period := hp
  have hle : n ≤ n * period := by
    simpa using Nat.mul_le_mul_left n hp1
  have hz := divisionIterate_eq_zero_of_le Q N hQ hn hle
  have hreturn :=
    divisionIterate_mul_period_eq_of_periodic Q N hperiod n
  exact hreturn.symm.trans hz

/-- Membership in the explicit E3 square implies the corresponding height
    bound.  Together with E3's converse theorem, this identifies the carrier
    exactly with the divisor-dependent height ball. -/
theorem gaussianHeight_le_of_mem_gaussianHeightCarrier
    (B : ℕ) (x : GaussianInt)
    (hx : x ∈ gaussianHeightCarrier B) :
    CNRSCore.gaussianHeight x ≤ B := by
  classical
  rw [gaussianHeightCarrier] at hx
  rcases Finset.mem_image.mp hx with ⟨p, hp, hpx⟩
  rcases Finset.mem_product.mp hp with ⟨hre, him⟩
  rw [Finset.mem_Icc] at hre him
  subst x
  change max p.1.natAbs p.2.natAbs ≤ B
  apply max_le
  · have hB : 0 ≤ (B : ℤ) := by positivity
    have hsquare : p.1 * p.1 ≤ (B : ℤ) * (B : ℤ) := by
      nlinarith [hre.1, hre.2]
    have habs : p.1.natAbs ≤ ((B : ℤ).natAbs) :=
      Int.natAbs_le_iff_mul_self_le.mpr hsquare
    simpa using habs
  · have hB : 0 ≤ (B : ℤ) := by positivity
    have hsquare : p.2 * p.2 ≤ (B : ℤ) * (B : ℤ) := by
      nlinarith [him.1, him.2]
    have habs : p.2.natAbs ≤ ((B : ℤ).natAbs) :=
      Int.natAbs_le_iff_mul_self_le.mpr hsquare
    simpa using habs

/-- Every periodic state lies in the invariant E3 divisor ball. -/
theorem divisionPeriodicState_height_le_stateBound
    (Q N : GaussianInt) (hperiodic : DivisionPeriodicState Q N) :
    CNRSCore.gaussianHeight N ≤ divisionStateBound Q := by
  by_contra hnot
  have houtside :
      divisionStateBound Q < CNRSCore.gaussianHeight N :=
    Nat.lt_of_not_ge hnot
  have hnext := divisionNext_height_lt_of_stateBound_lt Q N houtside
  rcases hperiodic with ⟨period, hp, hperiod⟩
  obtain ⟨k, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hp)
  have htail :=
    divisionIterate_height_global_bound Q (divisionNext Q N) k
  have hshift :
      divisionIterate Q N (k + 1) =
        divisionIterate Q (divisionNext Q N) k := by
    simpa [Nat.one_add] using divisionIterate_add Q N 1 k
  have hNle :
      CNRSCore.gaussianHeight N ≤
        max (CNRSCore.gaussianHeight (divisionNext Q N))
          (divisionStateBound Q) := by
    calc
      CNRSCore.gaussianHeight N =
          CNRSCore.gaussianHeight
            (divisionIterate Q (divisionNext Q N) k) :=
        congrArg CNRSCore.gaussianHeight (hperiod.symm.trans hshift)
      _ ≤ max (CNRSCore.gaussianHeight (divisionNext Q N))
          (divisionStateBound Q) := htail
  have hmaxlt :
      max (CNRSCore.gaussianHeight (divisionNext Q N))
          (divisionStateBound Q) < CNRSCore.gaussianHeight N :=
    max_lt hnext houtside
  omega

/-- Therefore every periodic state is a vertex of the explicit E3 carrier. -/
theorem divisionPeriodicState_mem_stateCarrier
    (Q N : GaussianInt) (hperiodic : DivisionPeriodicState Q N) :
    N ∈ divisionStateCarrier Q := by
  apply mem_gaussianHeightCarrier_of_height_le
  exact divisionPeriodicState_height_le_stateBound Q N hperiodic

/-- Vertices of the finite E6 division graph. -/
noncomputable def divisionStateGraphVertices (Q : GaussianInt) :
    Finset GaussianInt :=
  divisionStateCarrier Q

/-- The edge relation of the deterministic E6 division graph. -/
noncomputable def divisionStateGraphEdge
    (Q N N' : GaussianInt) : Prop :=
  N ∈ divisionStateGraphVertices Q ∧ N' = divisionNext Q N

/-- The E3 invariant bound makes the E6 graph closed under its successor. -/
theorem divisionStateGraph_successor_mem
    (Q N : GaussianInt) (hN : N ∈ divisionStateGraphVertices Q) :
    divisionNext Q N ∈ divisionStateGraphVertices Q := by
  apply mem_gaussianHeightCarrier_of_height_le
  apply divisionNext_height_le_stateBound
  exact gaussianHeight_le_of_mem_gaussianHeightCarrier
    (divisionStateBound Q) N hN

/-- Every graph vertex has exactly one successor vertex. -/
theorem divisionStateGraph_successor_unique
    (Q N : GaussianInt) (hN : N ∈ divisionStateGraphVertices Q) :
    ∃! N' : GaussianInt,
      N' ∈ divisionStateGraphVertices Q ∧
        divisionStateGraphEdge Q N N' := by
  refine ⟨divisionNext Q N, ?_, ?_⟩
  · exact ⟨divisionStateGraph_successor_mem Q N hN, hN, rfl⟩
  · intro N' hN'
    exact hN'.2.2

/-- Executable test for a return within a specified positive-period horizon. -/
def divisionReturnsWithin
    (Q N : GaussianInt) (limit : ℕ) : Bool :=
  (List.range (limit + 1)).any
    (fun period =>
      decide (0 < period ∧ divisionIterate Q N period = N))

/-- The executable return test is true exactly when a positive return period
    no larger than the requested horizon exists. -/
theorem divisionReturnsWithin_eq_true_iff
    (Q N : GaussianInt) (limit : ℕ) :
    divisionReturnsWithin Q N limit = true ↔
      ∃ period : ℕ, 0 < period ∧ period ≤ limit ∧
        divisionIterate Q N period = N := by
  simp [divisionReturnsWithin]
  constructor
  · rintro ⟨period, hlimit, hpositive, hreturn⟩
    exact ⟨period, hpositive, hlimit, hreturn⟩
  · rintro ⟨period, hpositive, hlimit, hreturn⟩
    exact ⟨period, hlimit, hpositive, hreturn⟩

/-- Exact finite theorem-level classifier containing precisely the periodic
    vertices of the divisor graph.  Unlike `divisionReturnsWithin`, this
    unbounded existential classifier is intentionally noncomputable. -/
noncomputable def divisionCycleStates (Q : GaussianInt) :
    Finset GaussianInt := by
  classical
  exact (divisionStateGraphVertices Q).filter
    (fun N => DivisionPeriodicState Q N)

/-- Membership in the finite classifier is exactly periodicity. -/
theorem mem_divisionCycleStates_iff
    (Q N : GaussianInt) :
    N ∈ divisionCycleStates Q ↔ DivisionPeriodicState Q N := by
  classical
  constructor
  · intro h
    exact (Finset.mem_filter.mp h).2
  · intro h
    exact Finset.mem_filter.mpr
      ⟨divisionPeriodicState_mem_stateCarrier Q N h, h⟩

/-- A period gives an exact arithmetic cycle equation. -/
theorem divisionCycle_reconstruction
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    {period : ℕ} (hperiod : divisionIterate Q N period = N) :
    Q * divisionPrefixValue Q N period =
      (1 - beta ^ period) * N := by
  have h := divisionIterate_reconstruct Q N hQ period
  rw [hperiod] at h
  calc
    Q * divisionPrefixValue Q N period =
        Q * divisionPrefixValue Q N period + beta ^ period * N -
          beta ^ period * N := by ring
    _ = N - beta ^ period * N := by rw [h]
    _ = (1 - beta ^ period) * N := by ring

/-- A nonzero periodic state for an admissible divisor cannot be divisible by
    that divisor. -/
theorem nonzero_periodic_not_dvd
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    (hN : N ≠ 0) (hperiodic : DivisionPeriodicState Q N) :
    ¬ Q ∣ N := by
  intro hdiv
  have hterm := divisionIterate_terminates_of_dvd Q N hQ hdiv
  exact hN (eq_zero_of_periodic_of_terminates Q N hQ hperiodic hterm)

/-- Exact E6 orbit classification: for an admissible divisor, a numerator is
    nondivisible exactly when its deterministic orbit reaches a nonzero
    periodic vertex of the finite E6 graph. -/
theorem not_dvd_iff_reaches_nonzero_periodic
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    (¬ Q ∣ N) ↔
      ∃ start : ℕ,
        divisionIterate Q N start ≠ 0 ∧
          DivisionPeriodicState Q (divisionIterate Q N start) := by
  constructor
  · intro hndiv
    obtain ⟨start, period, hp, hperiod, hnonzero⟩ :=
      not_dvd_implies_eventually_periodic_nonzero Q N hQ hndiv
    refine ⟨start, ?_, period, hp, ?_⟩
    · simpa using hnonzero 0
    · rw [← divisionIterate_add Q N start period]
      simpa using hperiod 0
  · rintro ⟨start, hnonzero, hperiodic⟩ hdiv
    obtain ⟨n, hn⟩ := divisionIterate_terminates_of_dvd Q N hQ hdiv
    have hlate : divisionIterate Q N (start + n) = 0 := by
      apply divisionIterate_eq_zero_of_le Q N hQ hn
      omega
    have htailTerminates :
        ∃ k : ℕ,
          divisionIterate Q (divisionIterate Q N start) k = 0 := by
      refine ⟨n, ?_⟩
      rw [← divisionIterate_add Q N start n]
      exact hlate
    exact hnonzero
      (eq_zero_of_periodic_of_terminates Q
        (divisionIterate Q N start) hQ hperiodic htailTerminates)

end CNRSArithmetic
