/-
CNRSArithmetic Phase E10 candidate: certified bounded division outcomes.

This module combines E8's exact finite-horizon decision and witness layer
with E9's executable least periods and canonical primitive-cycle catalogue.
For each numerator and fixed divisor it returns one tagged executable
outcome: all bounded exact-quotient certificates, or all bounded nonzero
cycle-entry certificates enriched with their least period, primitive cycle,
and canonical catalogue representative.

Correctness is stated for admissible divisors.  This phase does not claim
universal termination, a streaming-input online division transducer, a
closed-form cycle classification, or practical efficiency.
-/
import CNRSArithmetic.DivisionCycleCatalogue
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- The first `n` quotient digits, in least-significant-first order. -/
def divisionQuotientDigits
    (Q N : GaussianInt) (n : ℕ) : List Digit :=
  List.ofFn (fun k : Fin n => divisionDigitAt Q N k)

/-- Executable data attached to a bounded zero-state witness. -/
structure DivisionExactOutcome where
  steps : ℕ
  digits : List Digit
  quotient : GaussianInt
deriving DecidableEq

/-- Build the exact-outcome data associated with a candidate step count. -/
def mkDivisionExactOutcome
    (Q N : GaussianInt) (n : ℕ) : DivisionExactOutcome where
  steps := n
  digits := divisionQuotientDigits Q N n
  quotient := divisionPrefixValue Q N n

/-- All exact-quotient outcomes exposed by the certified E8 horizon. -/
def divisionExactOutcomes
    (Q N : GaussianInt) : List DivisionExactOutcome :=
  (divisionZeroWitnesses Q N (divisionDecisionHorizon Q N)).map
    (mkDivisionExactOutcome Q N)

/-- Exact membership characterization of the bounded exact-outcome list. -/
theorem mem_divisionExactOutcomes_iff
    (Q N : GaussianInt) (outcome : DivisionExactOutcome) :
    outcome ∈ divisionExactOutcomes Q N ↔
      ∃ n : ℕ,
        n ≤ divisionDecisionHorizon Q N ∧
        divisionIterate Q N n = 0 ∧
        mkDivisionExactOutcome Q N n = outcome := by
  constructor
  · intro houtcome
    rcases List.mem_map.mp houtcome with ⟨n, hn, hmk⟩
    have hw :=
      (mem_divisionZeroWitnesses_iff Q N
        (divisionDecisionHorizon Q N) n).mp hn
    exact ⟨n, hw.1, hw.2, hmk⟩
  · rintro ⟨n, hbound, hzero, hmk⟩
    exact List.mem_map.mpr
      ⟨n, (mem_divisionZeroWitnesses_iff Q N
        (divisionDecisionHorizon Q N) n).mpr
          ⟨hbound, hzero⟩, hmk⟩

/-- Every exact-outcome entry is bounded, carries the emitted digit prefix,
    and reconstructs the original numerator. -/
theorem divisionExactOutcome_spec
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    {outcome : DivisionExactOutcome}
    (houtcome : outcome ∈ divisionExactOutcomes Q N) :
    outcome.steps ≤ divisionDecisionHorizon Q N ∧
      divisionIterate Q N outcome.steps = 0 ∧
      outcome.digits =
        divisionQuotientDigits Q N outcome.steps ∧
      outcome.quotient =
        divisionPrefixValue Q N outcome.steps ∧
      Q * outcome.quotient = N := by
  rcases (mem_divisionExactOutcomes_iff Q N outcome).mp houtcome with
    ⟨n, hbound, hzero, hmk⟩
  subst outcome
  refine ⟨hbound, hzero, rfl, rfl, ?_⟩
  exact divisionIterate_eq_zero_implies_exact Q N hQ n hzero

/-- For an admissible divisor, the exact-outcome payload is nonempty exactly
    when the divisor divides the numerator. -/
theorem divisionExactOutcomes_nonempty_iff_dvd
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    divisionExactOutcomes Q N ≠ [] ↔ Q ∣ N := by
  simpa [divisionExactOutcomes] using
    divisionZeroWitnesses_nonempty_iff_dvd Q N hQ

/-- Executable data attached to a bounded nonzero periodic-state witness. -/
structure DivisionCycleOutcome where
  entry : ℕ
  state : GaussianInt
  period : ℕ
  states : Finset GaussianInt
  representative : GaussianInt
deriving DecidableEq

/-- Enrich a candidate entry index with the complete E9 primitive-cycle
    information attached to its orbit state. -/
def mkDivisionCycleOutcome
    (Q N : GaussianInt) (entry : ℕ) : DivisionCycleOutcome :=
  let state := divisionIterate Q N entry
  {
    entry := entry
    state := state
    period := divisionMinimalReturnPeriod Q state
    states := divisionMinimalCycleStates Q state
    representative := divisionCanonicalCycleRepresentative Q state
  }

/-- All nonzero-cycle outcomes exposed by the certified E8 horizon. -/
def divisionCycleOutcomes
    (Q N : GaussianInt) : List DivisionCycleOutcome :=
  (divisionNonzeroCycleEntryWitnesses
      Q N (divisionDecisionHorizon Q N)).map
    (mkDivisionCycleOutcome Q N)

/-- Exact membership characterization of the bounded cycle-outcome list. -/
theorem mem_divisionCycleOutcomes_iff
    (Q N : GaussianInt) (outcome : DivisionCycleOutcome) :
    outcome ∈ divisionCycleOutcomes Q N ↔
      ∃ entry : ℕ,
        entry ≤ divisionDecisionHorizon Q N ∧
        divisionIterate Q N entry ≠ 0 ∧
        DivisionPeriodicState Q (divisionIterate Q N entry) ∧
        mkDivisionCycleOutcome Q N entry = outcome := by
  constructor
  · intro houtcome
    rcases List.mem_map.mp houtcome with ⟨entry, hentry, hmk⟩
    have hw :=
      (mem_divisionNonzeroCycleEntryWitnesses_iff Q N
        (divisionDecisionHorizon Q N) entry).mp hentry
    exact ⟨entry, hw.1, hw.2.1, hw.2.2, hmk⟩
  · rintro ⟨entry, hbound, hnonzero, hperiodic, hmk⟩
    exact List.mem_map.mpr
      ⟨entry, (mem_divisionNonzeroCycleEntryWitnesses_iff Q N
        (divisionDecisionHorizon Q N) entry).mpr
          ⟨hbound, hnonzero, hperiodic⟩, hmk⟩

/-- Every cycle-outcome entry is bounded and nonzero, and its enriched data
    gives the exact least positive return period, primitive-cycle cardinality,
    and canonical catalogue representative. -/
theorem divisionCycleOutcome_spec
    (Q N : GaussianInt) {outcome : DivisionCycleOutcome}
    (houtcome : outcome ∈ divisionCycleOutcomes Q N) :
    outcome.entry ≤ divisionDecisionHorizon Q N ∧
      outcome.state = divisionIterate Q N outcome.entry ∧
      outcome.state ≠ 0 ∧
      DivisionPeriodicState Q outcome.state ∧
      0 < outcome.period ∧
      divisionIterate Q outcome.state outcome.period = outcome.state ∧
      (∀ period : ℕ, 0 < period →
        divisionIterate Q outcome.state period = outcome.state →
        outcome.period ≤ period) ∧
      outcome.states = divisionMinimalCycleStates Q outcome.state ∧
      outcome.states.card = outcome.period ∧
      outcome.representative =
        divisionCanonicalCycleRepresentative Q outcome.state ∧
      outcome.representative ∈ divisionCycleCatalogueExec Q := by
  rcases (mem_divisionCycleOutcomes_iff Q N outcome).mp houtcome with
    ⟨entry, hbound, hnonzero, hperiodic, hmk⟩
  subst outcome
  let state := divisionIterate Q N entry
  have hminimal :=
    divisionMinimalReturnPeriod_spec Q state hperiodic
  have hcard :=
    divisionMinimalCycleStates_card Q state hperiodic
  have hcatalogue :=
    divisionCanonicalCycleRepresentative_mem_catalogue Q state hperiodic
  refine ⟨hbound, rfl, hnonzero, hperiodic,
    hminimal.1, hminimal.2.2.1, hminimal.2.2.2, rfl, ?_, rfl, hcatalogue⟩
  simpa [mkDivisionCycleOutcome, state] using hcard

/-- For an admissible divisor, the cycle-outcome payload is nonempty exactly
    when the divisor does not divide the numerator. -/
theorem divisionCycleOutcomes_nonempty_iff_not_dvd
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    divisionCycleOutcomes Q N ≠ [] ↔ ¬ Q ∣ N := by
  simpa [divisionCycleOutcomes] using
    divisionNonzeroCycleEntryWitnesses_nonempty_iff_not_dvd Q N hQ

/-- The executable E10 result: exact certificates or canonical cycle
    certificates, selected by E8's exact Boolean decision. -/
inductive DivisionOutcome where
  | exact (outcomes : List DivisionExactOutcome)
  | cycle (outcomes : List DivisionCycleOutcome)
deriving DecidableEq

/-- Run the certified bounded division-outcome machine. -/
def divisionOutcomeExec
    (Q N : GaussianInt) : DivisionOutcome :=
  if divisionDividesExec Q N then
    .exact (divisionExactOutcomes Q N)
  else
    .cycle (divisionCycleOutcomes Q N)

/-- Executable branch observer for the exact outcome. -/
def DivisionOutcome.isExact : DivisionOutcome → Bool
  | .exact _ => true
  | .cycle _ => false

/-- Executable branch observer for the nonzero-cycle outcome. -/
def DivisionOutcome.isCycle : DivisionOutcome → Bool
  | .exact _ => false
  | .cycle _ => true

@[simp] theorem divisionOutcomeExec_isExact
    (Q N : GaussianInt) :
    (divisionOutcomeExec Q N).isExact = divisionDividesExec Q N := by
  cases h : divisionDividesExec Q N <;>
    simp [divisionOutcomeExec, h, DivisionOutcome.isExact]

@[simp] theorem divisionOutcomeExec_isCycle
    (Q N : GaussianInt) :
    (divisionOutcomeExec Q N).isCycle = !divisionDividesExec Q N := by
  cases h : divisionDividesExec Q N <;>
    simp [divisionOutcomeExec, h, DivisionOutcome.isCycle]

/-- The E10 exact branch is selected exactly for divisible numerators. -/
theorem divisionOutcomeExec_isExact_iff_dvd
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    (divisionOutcomeExec Q N).isExact = true ↔ Q ∣ N := by
  rw [divisionOutcomeExec_isExact]
  exact divisionDividesExec_eq_true_iff Q N hQ

/-- The E10 cycle branch is selected exactly for nondivisible numerators. -/
theorem divisionOutcomeExec_isCycle_iff_not_dvd
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    (divisionOutcomeExec Q N).isCycle = true ↔ ¬ Q ∣ N := by
  by_cases hdiv : Q ∣ N
  · have hdecision :
        divisionDividesExec Q N = true :=
      (divisionDividesExec_eq_true_iff Q N hQ).mpr hdiv
    simp [divisionOutcomeExec_isCycle, hdecision, hdiv]
  · have hdecision :
        divisionDividesExec Q N = false := by
      cases h : divisionDividesExec Q N with
      | false => rfl
      | true =>
          exact False.elim
            (hdiv ((divisionDividesExec_eq_true_iff Q N hQ).mp h))
    simp [divisionOutcomeExec_isCycle, hdecision, hdiv]

/-- Whichever branch is selected for an admissible divisor carries at least
    one certified bounded outcome. -/
def DivisionOutcome.PayloadNonempty : DivisionOutcome → Prop
  | .exact outcomes => outcomes ≠ []
  | .cycle outcomes => outcomes ≠ []

theorem divisionOutcomeExec_payload_nonempty
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    (divisionOutcomeExec Q N).PayloadNonempty := by
  cases hdecision : divisionDividesExec Q N with
  | false =>
      have hndiv : ¬ Q ∣ N := by
        intro hdiv
        have htrue :=
          (divisionDividesExec_eq_true_iff Q N hQ).mpr hdiv
        simp [hdecision] at htrue
      simpa [divisionOutcomeExec, hdecision,
        DivisionOutcome.PayloadNonempty] using
          (divisionCycleOutcomes_nonempty_iff_not_dvd
            Q N hQ).mpr hndiv
  | true =>
      have hdiv : Q ∣ N :=
        (divisionDividesExec_eq_true_iff Q N hQ).mp hdecision
      simpa [divisionOutcomeExec, hdecision,
        DivisionOutcome.PayloadNonempty] using
          (divisionExactOutcomes_nonempty_iff_dvd
            Q N hQ).mpr hdiv

end CNRSArithmetic
