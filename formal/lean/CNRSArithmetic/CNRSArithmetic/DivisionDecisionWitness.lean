/-
CNRSArithmetic Phase E8 candidate: certified division decision and witness
extraction.

This module combines the frozen E3--E7 results. It gives the complete orbit
carrier an executable presentation, derives a finite repetition horizon for
an arbitrary numerator, and turns the E5 divisibility theorem and E7 cycle
classifier into executable lists of termination and nonzero-cycle witnesses.

The phase does not claim universal termination, a closed-form cycle catalogue,
a minimal-period algorithm, or an online division transducer.
-/
import CNRSArithmetic.DivisionCycleEnumeration
import Mathlib.Data.Fintype.Pigeonhole
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

private theorem exists_mem_of_ne_nil
    {α : Type} {xs : List α} (hxs : xs ≠ []) :
    ∃ x, x ∈ xs := by
  cases xs with
  | nil => contradiction
  | cons x xs => exact ⟨x, by simp⟩

private theorem ne_nil_of_mem
    {α : Type} {xs : List α} {x : α} (hx : x ∈ xs) :
    xs ≠ [] := by
  cases xs with
  | nil => simp at hx
  | cons y ys => simp

/-- Executable presentation of E3's complete orbit carrier for an arbitrary
    initial numerator. -/
def divisionOrbitCarrierExec (Q N : GaussianInt) : Finset GaussianInt :=
  gaussianHeightCarrierExec (divisionOrbitBound Q N)

/-- Exact membership characterization of the executable complete-orbit
    carrier. -/
theorem mem_divisionOrbitCarrierExec_iff
    (Q N M : GaussianInt) :
    M ∈ divisionOrbitCarrierExec Q N ↔
      CNRSCore.gaussianHeight M ≤ divisionOrbitBound Q N := by
  exact mem_gaussianHeightCarrierExec_iff (divisionOrbitBound Q N) M

/-- Every state of the complete orbit belongs to its executable carrier. -/
theorem divisionIterate_mem_orbitCarrierExec
    (Q N : GaussianInt) (n : ℕ) :
    divisionIterate Q N n ∈ divisionOrbitCarrierExec Q N := by
  rw [mem_divisionOrbitCarrierExec_iff]
  exact divisionIterate_height_global_bound Q N n

/-- Coarse but computable upper bound on the number of steps needed to enter
    E7's divisor-dependent invariant carrier. -/
def divisionEntryHorizon (N : GaussianInt) : ℕ :=
  CNRSCore.gaussianHeight N

/-- Every orbit enters E7's invariant carrier within its initial height. -/
theorem divisionIterate_enters_stateCarrier_within_entryHorizon
    (Q N : GaussianInt) :
    ∃ entry : ℕ, entry ≤ divisionEntryHorizon N ∧
      divisionIterate Q N entry ∈ divisionStateCarrierExec Q := by
  generalize hheight : CNRSCore.gaussianHeight N = h
  induction h using Nat.strong_induction_on generalizing N with
  | h height ih =>
      by_cases hin : height ≤ divisionStateBound Q
      · refine ⟨0, by simp [divisionEntryHorizon], ?_⟩
        rw [mem_divisionStateCarrierExec_iff, divisionIterate_zero, hheight]
        exact hin
      · have hout :
            divisionStateBound Q < CNRSCore.gaussianHeight N := by
          rw [hheight]
          omega
        have hnext :
            CNRSCore.gaussianHeight (divisionNext Q N) < height := by
          rw [← hheight]
          exact divisionNext_height_lt_of_stateBound_lt Q N hout
        obtain ⟨entry, hentry, hmem⟩ :=
          ih (CNRSCore.gaussianHeight (divisionNext Q N)) hnext
            (divisionNext Q N) rfl
        refine ⟨entry + 1, ?_, ?_⟩
        · simp only [divisionEntryHorizon]
          have hentry' :
              entry ≤ CNRSCore.gaussianHeight (divisionNext Q N) := by
            simpa [divisionEntryHorizon] using hentry
          omega
        · have hshift :
              divisionIterate Q N (entry + 1) =
                divisionIterate Q (divisionNext Q N) entry := by
            simpa [Nat.one_add] using divisionIterate_add Q N 1 entry
          rw [hshift]
          exact hmem

/-- An orbit already in E7's invariant carrier repeats within the E7 carrier
    cardinality. -/
theorem divisionStateCarrier_orbit_repeats_within_searchHorizon
    (Q N : GaussianInt) (hN : N ∈ divisionStateCarrierExec Q) :
    ∃ a b : ℕ, a < b ∧ b ≤ divisionSearchHorizon Q ∧
      divisionIterate Q N a = divisionIterate Q N b := by
  classical
  let C := divisionStateCarrierExec Q
  let H := divisionSearchHorizon Q
  let f : Fin (H + 1) → {M // M ∈ C} := fun n =>
    ⟨divisionIterate Q N n, by
      change divisionIterate Q N n ∈ divisionStateCarrierExec Q
      rw [mem_divisionStateCarrierExec_iff]
      apply divisionIterate_height_le_stateBound_of_le
      exact (mem_divisionStateCarrierExec_iff Q N).mp hN⟩
  have hcard : Fintype.card {M // M ∈ C} < Fintype.card (Fin (H + 1)) := by
    simp [C, H, divisionSearchHorizon]
  obtain ⟨a, b, hab, hEq⟩ :=
    Fintype.exists_ne_map_eq_of_card_lt f hcard
  have hstate :
      divisionIterate Q N a = divisionIterate Q N b := by
    exact congrArg Subtype.val hEq
  rcases lt_or_gt_of_ne hab with hablt | hbalt
  · refine ⟨a, b, hablt, ?_, hstate⟩
    exact Nat.le_of_lt_succ b.isLt
  · refine ⟨b, a, hbalt, ?_, hstate.symm⟩
    exact Nat.le_of_lt_succ a.isLt

/-- Executable decision horizon: enough steps to enter E7's invariant carrier,
    followed by one complete E7 carrier cardinality. -/
def divisionDecisionHorizon (Q N : GaussianInt) : ℕ :=
  divisionEntryHorizon N + divisionSearchHorizon Q

/-- By the E8 decision horizon, every deterministic orbit has repeated a
    state. -/
theorem divisionOrbit_repeats_within_decisionHorizon
    (Q N : GaussianInt) :
    ∃ a b : ℕ, a < b ∧ b ≤ divisionDecisionHorizon Q N ∧
      divisionIterate Q N a = divisionIterate Q N b := by
  obtain ⟨entry, hentry, hmem⟩ :=
    divisionIterate_enters_stateCarrier_within_entryHorizon Q N
  obtain ⟨a, b, hab, hb, hEq⟩ :=
    divisionStateCarrier_orbit_repeats_within_searchHorizon Q
      (divisionIterate Q N entry) hmem
  refine ⟨entry + a, entry + b, by omega, ?_, ?_⟩
  · rw [divisionDecisionHorizon]
    omega
  · calc
      divisionIterate Q N (entry + a) =
          divisionIterate Q (divisionIterate Q N entry) a :=
        divisionIterate_add Q N entry a
      _ = divisionIterate Q (divisionIterate Q N entry) b := hEq
      _ = divisionIterate Q N (entry + b) :=
        (divisionIterate_add Q N entry b).symm

/-- The earlier state in a bounded repeated pair is periodic. -/
theorem divisionPeriodicState_of_bounded_repeat
    (Q N : GaussianInt) {a b : ℕ} (hab : a < b)
    (hEq : divisionIterate Q N a = divisionIterate Q N b) :
    DivisionPeriodicState Q (divisionIterate Q N a) := by
  refine ⟨b - a, Nat.sub_pos_of_lt hab, ?_⟩
  have hadd := divisionIterate_add Q N a (b - a)
  have hindex : a + (b - a) = b := by omega
  rw [hindex] at hadd
  exact hadd.symm.trans hEq.symm

/-- Executable list of all zero-state indices up to a requested horizon. -/
def divisionZeroWitnesses
    (Q N : GaussianInt) (limit : ℕ) : List ℕ :=
  (List.range (limit + 1)).filter
    (fun n => decide (divisionIterate Q N n = 0))

/-- Exact membership theorem for the bounded termination-witness list. -/
theorem mem_divisionZeroWitnesses_iff
    (Q N : GaussianInt) (limit n : ℕ) :
    n ∈ divisionZeroWitnesses Q N limit ↔
      n ≤ limit ∧ divisionIterate Q N n = 0 := by
  simp [divisionZeroWitnesses]

/-- Executable list of all indices up to a requested horizon whose states are
    nonzero periodic vertices according to E7's exact classifier. -/
def divisionNonzeroCycleEntryWitnesses
    (Q N : GaussianInt) (limit : ℕ) : List ℕ :=
  (List.range (limit + 1)).filter
    (fun n => decide
      (divisionIterate Q N n ≠ 0 ∧
        divisionIterate Q N n ∈ divisionCycleStatesExec Q))

/-- Exact membership theorem for bounded nonzero-cycle entry witnesses. -/
theorem mem_divisionNonzeroCycleEntryWitnesses_iff
    (Q N : GaussianInt) (limit n : ℕ) :
    n ∈ divisionNonzeroCycleEntryWitnesses Q N limit ↔
      n ≤ limit ∧ divisionIterate Q N n ≠ 0 ∧
        DivisionPeriodicState Q (divisionIterate Q N n) := by
  simp [divisionNonzeroCycleEntryWitnesses,
    mem_divisionCycleStatesExec_iff]

/-- By the decision horizon, every admissible division orbit has exposed
    either a termination witness or a nonzero periodic-state witness. -/
theorem divisionDecisionWitnesses_exhaustive
    (Q N : GaussianInt) (_hQ : DivisionAdmissible Q) :
    divisionZeroWitnesses Q N (divisionDecisionHorizon Q N) ≠ [] ∨
      divisionNonzeroCycleEntryWitnesses Q N
        (divisionDecisionHorizon Q N) ≠ [] := by
  obtain ⟨a, b, hab, hb, hEq⟩ :=
    divisionOrbit_repeats_within_decisionHorizon Q N
  have hperiodic :=
    divisionPeriodicState_of_bounded_repeat Q N hab hEq
  by_cases hz : divisionIterate Q N a = 0
  · left
    apply ne_nil_of_mem
    exact (mem_divisionZeroWitnesses_iff Q N
      (divisionDecisionHorizon Q N) a).mpr
        ⟨le_trans (Nat.le_of_lt hab) hb, hz⟩
  · right
    apply ne_nil_of_mem
    exact (mem_divisionNonzeroCycleEntryWitnesses_iff Q N
      (divisionDecisionHorizon Q N) a).mpr
        ⟨le_trans (Nat.le_of_lt hab) hb, hz, hperiodic⟩

/-- Executable divisibility decision: search the certified finite horizon for
    a zero state. -/
def divisionDividesExec (Q N : GaussianInt) : Bool :=
  decide
    (divisionZeroWitnesses Q N (divisionDecisionHorizon Q N) ≠ [])

/-- The E8 executable decision is exact for every admissible divisor. -/
theorem divisionDividesExec_eq_true_iff
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    divisionDividesExec Q N = true ↔ Q ∣ N := by
  simp only [divisionDividesExec, decide_eq_true_eq]
  constructor
  · intro hnonempty
    rcases exists_mem_of_ne_nil hnonempty with ⟨n, hn⟩
    exact (divisionOrbit_terminates_iff_dvd Q N hQ).mp
      ⟨n, (mem_divisionZeroWitnesses_iff Q N
        (divisionDecisionHorizon Q N) n).mp hn |>.2⟩
  · intro hdiv
    by_contra hempty
    have hcycle :
        divisionNonzeroCycleEntryWitnesses Q N
          (divisionDecisionHorizon Q N) ≠ [] :=
      (divisionDecisionWitnesses_exhaustive Q N hQ).resolve_left
        (fun hne => hne hempty)
    rcases exists_mem_of_ne_nil hcycle with ⟨start, hstart⟩
    have hw :=
      (mem_divisionNonzeroCycleEntryWitnesses_iff Q N
        (divisionDecisionHorizon Q N) start).mp hstart
    have hndiv := (not_dvd_iff_reaches_nonzero_periodic Q N hQ).mpr
      ⟨start, hw.2.1, hw.2.2⟩
    exact hndiv hdiv

/-- At the certified horizon, the termination-witness list is nonempty
    exactly when the numerator is divisible by the admissible divisor. -/
theorem divisionZeroWitnesses_nonempty_iff_dvd
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    divisionZeroWitnesses Q N (divisionDecisionHorizon Q N) ≠ [] ↔
      Q ∣ N := by
  simpa [divisionDividesExec] using
    divisionDividesExec_eq_true_iff Q N hQ

/-- At the certified horizon, the nonzero-cycle entry list is nonempty exactly
    when the numerator is not divisible by the admissible divisor. -/
theorem divisionNonzeroCycleEntryWitnesses_nonempty_iff_not_dvd
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    divisionNonzeroCycleEntryWitnesses Q N
        (divisionDecisionHorizon Q N) ≠ [] ↔
      ¬ Q ∣ N := by
  constructor
  · intro hnonempty
    rcases exists_mem_of_ne_nil hnonempty with ⟨start, hstart⟩
    have hw :=
      (mem_divisionNonzeroCycleEntryWitnesses_iff Q N
        (divisionDecisionHorizon Q N) start).mp hstart
    exact (not_dvd_iff_reaches_nonzero_periodic Q N hQ).mpr
      ⟨start, hw.2.1, hw.2.2⟩
  · intro hndiv
    rcases divisionDecisionWitnesses_exhaustive Q N hQ with hzero | hcycle
    · exact False.elim
        (hndiv ((divisionZeroWitnesses_nonempty_iff_dvd Q N hQ).mp hzero))
    · exact hcycle

/-- Executable list of positive return periods up to E7's universal return
    horizon for a candidate periodic state. -/
def divisionReturnPeriodWitnesses
    (Q S : GaussianInt) : List ℕ :=
  (List.range (divisionSearchHorizon Q + 1)).filter
    (fun period => decide
      (0 < period ∧ divisionIterate Q S period = S))

/-- Exact membership theorem for the executable bounded return-period list. -/
theorem mem_divisionReturnPeriodWitnesses_iff
    (Q S : GaussianInt) (period : ℕ) :
    period ∈ divisionReturnPeriodWitnesses Q S ↔
      0 < period ∧ period ≤ divisionSearchHorizon Q ∧
        divisionIterate Q S period = S := by
  simp [divisionReturnPeriodWitnesses, and_left_comm]

/-- E7 completeness guarantees that the return-period witness list is
    nonempty exactly for periodic states. -/
theorem divisionReturnPeriodWitnesses_nonempty_iff_periodic
    (Q S : GaussianInt) :
    divisionReturnPeriodWitnesses Q S ≠ [] ↔
      DivisionPeriodicState Q S := by
  constructor
  · intro hnonempty
    rcases exists_mem_of_ne_nil hnonempty with ⟨period, hp⟩
    have hw := (mem_divisionReturnPeriodWitnesses_iff Q S period).mp hp
    exact ⟨period, hw.1, hw.2.2⟩
  · intro hperiodic
    rcases divisionPeriodicState_has_period_le_searchHorizon Q S hperiodic with
      ⟨period, hp, hbound, hreturn⟩
    apply ne_nil_of_mem
    exact (mem_divisionReturnPeriodWitnesses_iff Q S period).mpr
      ⟨hp, hbound, hreturn⟩

/-- Every extracted nonzero-cycle entry has at least one executable bounded
    positive return-period witness. -/
theorem cycleEntry_has_returnPeriodWitness
    (Q N : GaussianInt) {start limit : ℕ}
    (hstart : start ∈ divisionNonzeroCycleEntryWitnesses Q N limit) :
    divisionReturnPeriodWitnesses Q (divisionIterate Q N start) ≠ [] := by
  apply (divisionReturnPeriodWitnesses_nonempty_iff_periodic Q
    (divisionIterate Q N start)).mpr
  exact (mem_divisionNonzeroCycleEntryWitnesses_iff Q N limit start).mp
    hstart |>.2.2

/-- Any extracted zero index computes an exact Gaussian quotient witness. -/
theorem zeroWitness_gives_exact_quotient
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    {limit n : ℕ} (hn : n ∈ divisionZeroWitnesses Q N limit) :
    Q * divisionPrefixValue Q N n = N := by
  apply divisionIterate_eq_zero_implies_exact Q N hQ n
  exact (mem_divisionZeroWitnesses_iff Q N limit n).mp hn |>.2

end CNRSArithmetic
