/-
CNRSArithmetic Phase E11 candidate: direct representative integrity for the
certified E10 cycle-outcome payload.

E9 proves that every primitive cycle has exactly one canonical catalogue
representative.  E10 stores that representative together with the complete
primitive-cycle state set in each executable cycle outcome.  This module
connects those two interfaces directly: the stored representative belongs to
its stored state set, every rotation canonicalizes to it, and it is the unique
fixed/catalogue state in that set.

This is a theorem-only strengthening of the bounded E10 outcome API.  It does
not claim universal termination, streaming-input online division, a closed-form
cycle classification, or practical efficiency.
-/
import CNRSArithmetic.DivisionOutcomeMachine
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- The representative stored in every certified cycle outcome belongs to the
    primitive-cycle state set stored in that same outcome. -/
theorem divisionCycleOutcome_representative_mem_states
    (Q N : GaussianInt) {outcome : DivisionCycleOutcome}
    (houtcome : outcome ∈ divisionCycleOutcomes Q N) :
    outcome.representative ∈ outcome.states := by
  rcases divisionCycleOutcome_spec Q N houtcome with
    ⟨_, _, _, hperiodic, _, _, _, hstates, _, hrepresentative, _⟩
  rw [hstates, hrepresentative]
  exact divisionCanonicalCycleRepresentative_mem Q outcome.state hperiodic

/-- Every state in an outcome's primitive cycle canonicalizes to the
    representative stored in that outcome. -/
theorem divisionCycleOutcome_canonical_eq_representative_of_mem_states
    (Q N : GaussianInt) {outcome : DivisionCycleOutcome}
    (houtcome : outcome ∈ divisionCycleOutcomes Q N)
    (T : GaussianInt) (hT : T ∈ outcome.states) :
    divisionCanonicalCycleRepresentative Q T = outcome.representative := by
  rcases divisionCycleOutcome_spec Q N houtcome with
    ⟨_, _, _, hperiodic, _, _, _, hstates, _, hrepresentative, _⟩
  have hTcycle : T ∈ divisionMinimalCycleStates Q outcome.state := by
    rw [← hstates]
    exact hT
  calc
    divisionCanonicalCycleRepresentative Q T =
        divisionCanonicalCycleRepresentative Q outcome.state :=
      divisionCanonicalCycleRepresentative_eq_of_mem_cycle
        Q outcome.state T hperiodic hTcycle
    _ = outcome.representative := hrepresentative.symm

/-- Within an outcome's state set, a state is fixed by canonicalization exactly
    when it is the representative stored in the outcome. -/
theorem divisionCycleOutcome_canonical_fixed_iff_eq_representative
    (Q N : GaussianInt) {outcome : DivisionCycleOutcome}
    (houtcome : outcome ∈ divisionCycleOutcomes Q N)
    (T : GaussianInt) (hT : T ∈ outcome.states) :
    divisionCanonicalCycleRepresentative Q T = T ↔
      T = outcome.representative := by
  constructor
  · intro hfixed
    calc
      T = divisionCanonicalCycleRepresentative Q T := hfixed.symm
      _ = outcome.representative :=
        divisionCycleOutcome_canonical_eq_representative_of_mem_states
          Q N houtcome T hT
  · intro hTrep
    rw [hTrep]
    exact divisionCycleOutcome_canonical_eq_representative_of_mem_states
      Q N houtcome outcome.representative
        (divisionCycleOutcome_representative_mem_states Q N houtcome)

/-- The representative is the unique state in the stored primitive cycle that
    is fixed by canonical representative selection. -/
theorem divisionCycleOutcome_unique_canonical_fixed_state
    (Q N : GaussianInt) {outcome : DivisionCycleOutcome}
    (houtcome : outcome ∈ divisionCycleOutcomes Q N) :
    ∃! R : GaussianInt,
      R ∈ outcome.states ∧
        divisionCanonicalCycleRepresentative Q R = R := by
  refine ⟨outcome.representative, ?_, ?_⟩
  · refine ⟨divisionCycleOutcome_representative_mem_states Q N houtcome, ?_⟩
    exact divisionCycleOutcome_canonical_eq_representative_of_mem_states
      Q N houtcome outcome.representative
        (divisionCycleOutcome_representative_mem_states Q N houtcome)
  · intro R hR
    exact (divisionCycleOutcome_canonical_fixed_iff_eq_representative
      Q N houtcome R hR.1).mp hR.2

/-- Within an outcome's state set, catalogue membership is equivalent to being
    the representative stored in the outcome. -/
theorem divisionCycleOutcome_mem_catalogue_iff_eq_representative
    (Q N : GaussianInt) {outcome : DivisionCycleOutcome}
    (houtcome : outcome ∈ divisionCycleOutcomes Q N)
    (T : GaussianInt) (hT : T ∈ outcome.states) :
    T ∈ divisionCycleCatalogueExec Q ↔ T = outcome.representative := by
  constructor
  · intro hcatalogue
    have hfixed : divisionCanonicalCycleRepresentative Q T = T :=
      ((mem_divisionCycleCatalogueExec_iff_periodic_fixed Q T).mp
        hcatalogue).2
    exact (divisionCycleOutcome_canonical_fixed_iff_eq_representative
      Q N houtcome T hT).mp hfixed
  · intro hTrep
    subst T
    exact (divisionCycleOutcome_spec Q N houtcome).2.2.2.2.2.2.2.2.2.2

/-- The representative stored in a certified cycle outcome is exactly the
    unique catalogue state lying in that outcome's primitive cycle. -/
theorem divisionCycleOutcome_unique_catalogue_representative
    (Q N : GaussianInt) {outcome : DivisionCycleOutcome}
    (houtcome : outcome ∈ divisionCycleOutcomes Q N) :
    ∃! R : GaussianInt,
      R ∈ outcome.states ∧ R ∈ divisionCycleCatalogueExec Q := by
  refine ⟨outcome.representative, ?_, ?_⟩
  · exact ⟨divisionCycleOutcome_representative_mem_states Q N houtcome,
      (divisionCycleOutcome_spec Q N houtcome).2.2.2.2.2.2.2.2.2.2⟩
  · intro R hR
    exact (divisionCycleOutcome_mem_catalogue_iff_eq_representative
      Q N houtcome R hR.1).mp hR.2

end CNRSArithmetic
