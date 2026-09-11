/-
CNRSArithmetic Phase E9 candidate: executable minimal return periods and
primitive cycle representatives.

This module builds only on the frozen E8 decision-and-witness layer.  It
repackages the bounded return-period witnesses as a finite set, extracts its
least element by computation, proves that element is the exact least positive
return period, and enumerates the distinct states in one primitive cycle.

The phase does not claim universal termination, a closed-form classification
of cycles for every divisor, or an online division transducer.
-/
import CNRSArithmetic.DivisionDecisionWitness
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- Executable finite set of all positive return periods within E7's complete
    return horizon. -/
def divisionReturnPeriodWitnessFinset
    (Q S : GaussianInt) : Finset ℕ :=
  (Finset.range (divisionSearchHorizon Q + 1)).filter
    (fun period => decide
      (0 < period ∧ divisionIterate Q S period = S))

/-- Exact membership theorem for the finite return-period set. -/
theorem mem_divisionReturnPeriodWitnessFinset_iff
    (Q S : GaussianInt) (period : ℕ) :
    period ∈ divisionReturnPeriodWitnessFinset Q S ↔
      0 < period ∧ period ≤ divisionSearchHorizon Q ∧
        divisionIterate Q S period = S := by
  simp [divisionReturnPeriodWitnessFinset, and_left_comm]

/-- The finite return-period set is nonempty exactly for periodic states. -/
theorem divisionReturnPeriodWitnessFinset_nonempty_iff_periodic
    (Q S : GaussianInt) :
    (divisionReturnPeriodWitnessFinset Q S).Nonempty ↔
      DivisionPeriodicState Q S := by
  constructor
  · rintro ⟨period, hperiod⟩
    have hw :=
      (mem_divisionReturnPeriodWitnessFinset_iff Q S period).mp hperiod
    exact ⟨period, hw.1, hw.2.2⟩
  · intro hperiodic
    rcases divisionPeriodicState_has_period_le_searchHorizon Q S hperiodic with
      ⟨period, hpositive, hbound, hreturn⟩
    exact ⟨period,
      (mem_divisionReturnPeriodWitnessFinset_iff Q S period).mpr
        ⟨hpositive, hbound, hreturn⟩⟩

/-- Executable least positive return period, with value zero for a
    nonperiodic state. -/
def divisionMinimalReturnPeriod (Q S : GaussianInt) : ℕ :=
  let periods := divisionReturnPeriodWitnessFinset Q S
  if h : periods.Nonempty then periods.min' h else 0

/-- For a periodic state, the executable value is positive, returns the
    state, and is no larger than any other positive return period. -/
theorem divisionMinimalReturnPeriod_spec
    (Q S : GaussianInt) (hperiodic : DivisionPeriodicState Q S) :
    0 < divisionMinimalReturnPeriod Q S ∧
      divisionMinimalReturnPeriod Q S ≤ divisionSearchHorizon Q ∧
      divisionIterate Q S (divisionMinimalReturnPeriod Q S) = S ∧
      ∀ period : ℕ,
        0 < period → divisionIterate Q S period = S →
          divisionMinimalReturnPeriod Q S ≤ period := by
  let periods := divisionReturnPeriodWitnessFinset Q S
  have hnonempty : periods.Nonempty := by
    exact (divisionReturnPeriodWitnessFinset_nonempty_iff_periodic Q S).mpr
      hperiodic
  have hvalue :
      divisionMinimalReturnPeriod Q S = periods.min' hnonempty := by
    simp [divisionMinimalReturnPeriod, periods, hnonempty]
  have hmember : divisionMinimalReturnPeriod Q S ∈ periods := by
    rw [hvalue]
    exact Finset.min'_mem periods hnonempty
  have hspec :=
    (mem_divisionReturnPeriodWitnessFinset_iff Q S
      (divisionMinimalReturnPeriod Q S)).mp hmember
  refine ⟨hspec.1, hspec.2.1, hspec.2.2, ?_⟩
  intro period hpositive hreturn
  by_cases hbound : period ≤ divisionSearchHorizon Q
  · have hperiodmem : period ∈ periods := by
      exact (mem_divisionReturnPeriodWitnessFinset_iff Q S period).mpr
        ⟨hpositive, hbound, hreturn⟩
    rw [hvalue]
    exact Finset.min'_le periods period hperiodmem
  · omega

/-- The executable least-period value is positive exactly for periodic
    states. -/
theorem divisionMinimalReturnPeriod_pos_iff_periodic
    (Q S : GaussianInt) :
    0 < divisionMinimalReturnPeriod Q S ↔ DivisionPeriodicState Q S := by
  constructor
  · intro hpositive
    let periods := divisionReturnPeriodWitnessFinset Q S
    by_cases hnonempty : periods.Nonempty
    · exact
        (divisionReturnPeriodWitnessFinset_nonempty_iff_periodic Q S).mp
          hnonempty
    · have hzero : divisionMinimalReturnPeriod Q S = 0 := by
        simp [divisionMinimalReturnPeriod, periods, hnonempty]
      omega
  · intro hperiodic
    exact (divisionMinimalReturnPeriod_spec Q S hperiodic).1

/-- A nonperiodic state receives the distinguished least-period value zero. -/
theorem divisionMinimalReturnPeriod_eq_zero_iff_not_periodic
    (Q S : GaussianInt) :
    divisionMinimalReturnPeriod Q S = 0 ↔
      ¬ DivisionPeriodicState Q S := by
  constructor
  · intro hzero hperiodic
    have hpositive :=
      (divisionMinimalReturnPeriod_pos_iff_periodic Q S).mpr hperiodic
    omega
  · intro hnotperiodic
    by_contra hnonzero
    have hpositive : 0 < divisionMinimalReturnPeriod Q S :=
      Nat.pos_of_ne_zero hnonzero
    exact hnotperiodic
      ((divisionMinimalReturnPeriod_pos_iff_periodic Q S).mp hpositive)

/-- Executable set of states visited before the least positive return.  For a
    periodic state this is exactly one traversal of its primitive cycle. -/
def divisionMinimalCycleStates
    (Q S : GaussianInt) : Finset GaussianInt :=
  (Finset.range (divisionMinimalReturnPeriod Q S)).image
    (divisionIterate Q S)

/-- Exact membership characterization of the primitive-cycle state set. -/
theorem mem_divisionMinimalCycleStates_iff
    (Q S T : GaussianInt) :
    T ∈ divisionMinimalCycleStates Q S ↔
      ∃ n : ℕ, n < divisionMinimalReturnPeriod Q S ∧
        divisionIterate Q S n = T := by
  simp [divisionMinimalCycleStates]

/-- No state is repeated during the first traversal of a primitive cycle. -/
theorem divisionMinimalCycleStates_card
    (Q S : GaussianInt) (hperiodic : DivisionPeriodicState Q S) :
    (divisionMinimalCycleStates Q S).card =
      divisionMinimalReturnPeriod Q S := by
  let period := divisionMinimalReturnPeriod Q S
  have hspec := divisionMinimalReturnPeriod_spec Q S hperiodic
  have hinjective :
      Set.InjOn (divisionIterate Q S) (Finset.range period : Set ℕ) := by
    intro i hi j hj hEq
    have hiLt : i < period := Finset.mem_range.mp hi
    have hjLt : j < period := Finset.mem_range.mp hj
    by_contra hne
    rcases lt_or_gt_of_ne hne with hij | hji
    · have hprop :=
        divisionIterate_eq_add_of_eq Q S hEq (period - j)
      have hjindex : j + (period - j) = period := by omega
      have hsmallPos : 0 < i + (period - j) := by omega
      have hsmallLt : i + (period - j) < period := by omega
      have hsmallReturn :
          divisionIterate Q S (i + (period - j)) = S := by
        rw [hjindex] at hprop
        exact hprop.trans hspec.2.2.1
      have hminimal : period ≤ i + (period - j) :=
        hspec.2.2.2 (i + (period - j)) hsmallPos hsmallReturn
      omega
    · have hprop :=
        divisionIterate_eq_add_of_eq Q S hEq.symm (period - i)
      have hiindex : i + (period - i) = period := by omega
      have hsmallPos : 0 < j + (period - i) := by omega
      have hsmallLt : j + (period - i) < period := by omega
      have hsmallReturn :
          divisionIterate Q S (j + (period - i)) = S := by
        rw [hiindex] at hprop
        exact hprop.trans hspec.2.2.1
      have hminimal : period ≤ j + (period - i) :=
        hspec.2.2.2 (j + (period - i)) hsmallPos hsmallReturn
      omega
  simpa [divisionMinimalCycleStates, period] using
    (Finset.card_image_iff.mpr hinjective)

/-- Every iterate of a periodic state is itself periodic. -/
theorem divisionIterate_periodicState
    (Q S : GaussianInt) (hperiodic : DivisionPeriodicState Q S) (n : ℕ) :
    DivisionPeriodicState Q (divisionIterate Q S n) := by
  rcases hperiodic with ⟨period, hpositive, hreturn⟩
  refine ⟨period, hpositive, ?_⟩
  calc
    divisionIterate Q (divisionIterate Q S n) period =
        divisionIterate Q S (n + period) :=
      (divisionIterate_add Q S n period).symm
    _ = divisionIterate Q S (period + n) := by rw [Nat.add_comm]
    _ = divisionIterate Q (divisionIterate Q S period) n :=
      divisionIterate_add Q S period n
    _ = divisionIterate Q S n := by rw [hreturn]

/-- Every state in the primitive-cycle enumeration is periodic. -/
theorem mem_divisionMinimalCycleStates_periodic
    (Q S T : GaussianInt) (hperiodic : DivisionPeriodicState Q S)
    (hT : T ∈ divisionMinimalCycleStates Q S) :
    DivisionPeriodicState Q T := by
  rcases (mem_divisionMinimalCycleStates_iff Q S T).mp hT with
    ⟨n, _hn, rfl⟩
  exact divisionIterate_periodicState Q S hperiodic n

end CNRSArithmetic
