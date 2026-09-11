/-
CNRSArithmetic Phase E9 candidate: canonical primitive-cycle representatives
and a deduplicated executable cycle catalogue.

This module builds on the executable least-period layer.  It gives each
Gaussian state an injective natural-number code, selects the least code on a
primitive cycle, decodes it back to a state, and proves that the result is
independent of the chosen rotation of the cycle.  For each fixed divisor `Q`,
filtering all periodic states through this canonical representative therefore
produces exactly one entry per primitive cycle.

The phase does not claim universal termination, a closed-form classification
of the resulting catalogue, or an online division transducer.
-/
import CNRSArithmetic.DivisionMinimalPeriod
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

set_option maxHeartbeats 1000000

/-- An executable injective natural-number code for Gaussian integers. -/
def gaussianStateCode (S : GaussianInt) : ℕ :=
  Nat.pair (Equiv.intEquivNat S.re) (Equiv.intEquivNat S.im)

/-- Executable total decoding of a Gaussian-state code through the inverse
    integer equivalence on each paired coordinate. -/
def gaussianStateDecode (code : ℕ) : GaussianInt :=
  ⟨Equiv.intEquivNat.symm (Nat.unpair code).1,
    Equiv.intEquivNat.symm (Nat.unpair code).2⟩

/-- Decoding a code produced from a Gaussian state returns that state. -/
@[simp] theorem gaussianStateDecode_code (S : GaussianInt) :
    gaussianStateDecode (gaussianStateCode S) = S := by
  ext <;> simp [gaussianStateDecode, gaussianStateCode]

/-- The Gaussian-state code loses no information. -/
theorem gaussianStateCode_injective :
    Function.Injective gaussianStateCode := by
  intro S T hcode
  have hpair :
      (Equiv.intEquivNat S.re, Equiv.intEquivNat S.im) =
        (Equiv.intEquivNat T.re, Equiv.intEquivNat T.im) := by
    simpa [gaussianStateCode] using congrArg Nat.unpair hcode
  ext
  · exact Equiv.intEquivNat.injective (congrArg Prod.fst hpair)
  · exact Equiv.intEquivNat.injective (congrArg Prod.snd hpair)

/-- A return period for a state is also a return period for every iterate of
    that state. -/
theorem divisionIterate_return_of_return
    (Q S : GaussianInt) {period : ℕ}
    (hreturn : divisionIterate Q S period = S) (n : ℕ) :
    divisionIterate Q (divisionIterate Q S n) period =
      divisionIterate Q S n := by
  calc
    divisionIterate Q (divisionIterate Q S n) period =
        divisionIterate Q S (n + period) :=
      (divisionIterate_add Q S n period).symm
    _ = divisionIterate Q S (period + n) := by rw [Nat.add_comm]
    _ = divisionIterate Q (divisionIterate Q S period) n :=
      divisionIterate_add Q S period n
    _ = divisionIterate Q S n := by rw [hreturn]

/-- Rotating the starting point within a primitive cycle does not change its
    executable least positive return period. -/
theorem divisionMinimalReturnPeriod_eq_of_mem_cycle
    (Q S T : GaussianInt) (hperiodic : DivisionPeriodicState Q S)
    (hT : T ∈ divisionMinimalCycleStates Q S) :
    divisionMinimalReturnPeriod Q T =
      divisionMinimalReturnPeriod Q S := by
  rcases (mem_divisionMinimalCycleStates_iff Q S T).mp hT with
    ⟨n, hn, hTiter⟩
  let periodS := divisionMinimalReturnPeriod Q S
  let periodT := divisionMinimalReturnPeriod Q T
  have hspecS := divisionMinimalReturnPeriod_spec Q S hperiodic
  have hperiodicT :=
    mem_divisionMinimalCycleStates_periodic Q S T hperiodic hT
  have hspecT := divisionMinimalReturnPeriod_spec Q T hperiodicT
  have hreturnT : divisionIterate Q T periodS = T := by
    rw [← hTiter]
    exact divisionIterate_return_of_return Q S hspecS.2.2.1 n
  have hTleS : periodT ≤ periodS :=
    hspecT.2.2.2 periodS hspecS.1 hreturnT
  have hnle : n ≤ periodS := by
    dsimp [periodS]
    exact Nat.le_of_lt hn
  have hback : divisionIterate Q T (periodS - n) = S := by
    rw [← hTiter]
    calc
      divisionIterate Q (divisionIterate Q S n) (periodS - n) =
          divisionIterate Q S (n + (periodS - n)) :=
        (divisionIterate_add Q S n (periodS - n)).symm
      _ = divisionIterate Q S periodS := by
        rw [Nat.add_sub_of_le hnle]
      _ = S := hspecS.2.2.1
  have hreturnS : divisionIterate Q S periodT = S := by
    calc
      divisionIterate Q S periodT =
          divisionIterate Q (divisionIterate Q T (periodS - n)) periodT := by
        rw [hback]
      _ = divisionIterate Q T ((periodS - n) + periodT) :=
        (divisionIterate_add Q T (periodS - n) periodT).symm
      _ = divisionIterate Q T (periodT + (periodS - n)) := by
        rw [Nat.add_comm]
      _ = divisionIterate Q (divisionIterate Q T periodT) (periodS - n) :=
        divisionIterate_add Q T periodT (periodS - n)
      _ = divisionIterate Q T (periodS - n) := by rw [hspecT.2.2.1]
      _ = S := hback
  have hSleT : periodS ≤ periodT :=
    hspecS.2.2.2 periodT hspecT.1 hreturnS
  exact le_antisymm hTleS hSleT

/-- Every state in the primitive cycle rooted at a rotation `T` already lies
    in the primitive cycle rooted at `S`. -/
theorem divisionMinimalCycleStates_subset_of_mem
    (Q S T : GaussianInt) (hperiodic : DivisionPeriodicState Q S)
    (hT : T ∈ divisionMinimalCycleStates Q S) :
    divisionMinimalCycleStates Q T ⊆
      divisionMinimalCycleStates Q S := by
  intro U hU
  rcases (mem_divisionMinimalCycleStates_iff Q S T).mp hT with
    ⟨n, hn, hTiter⟩
  rcases (mem_divisionMinimalCycleStates_iff Q T U).mp hU with
    ⟨i, hi, hUiter⟩
  let period := divisionMinimalReturnPeriod Q S
  have hspec := divisionMinimalReturnPeriod_spec Q S hperiodic
  have hperiodEq :=
    divisionMinimalReturnPeriod_eq_of_mem_cycle Q S T hperiodic hT
  have hi' : i < period := by simpa [period, hperiodEq] using hi
  by_cases hsum : n + i < period
  · exact (mem_divisionMinimalCycleStates_iff Q S U).mpr
      ⟨n + i, hsum, by
        calc
          divisionIterate Q S (n + i) =
              divisionIterate Q (divisionIterate Q S n) i :=
            divisionIterate_add Q S n i
          _ = divisionIterate Q T i := by rw [hTiter]
          _ = U := hUiter⟩
  · let j := n + i - period
    have hj : j < period := by
      dsimp [j]
      omega
    exact (mem_divisionMinimalCycleStates_iff Q S U).mpr
      ⟨j, hj, by
        calc
          divisionIterate Q S j =
              divisionIterate Q (divisionIterate Q S period) j := by
            rw [hspec.2.2.1]
          _ = divisionIterate Q S (period + j) :=
            (divisionIterate_add Q S period j).symm
          _ = divisionIterate Q S (n + i) := by
            congr 1
            dsimp [j]
            omega
          _ = divisionIterate Q (divisionIterate Q S n) i :=
            divisionIterate_add Q S n i
          _ = divisionIterate Q T i := by rw [hTiter]
          _ = U := hUiter⟩

/-- Primitive-cycle state enumeration is independent of which state on the
    cycle is chosen as its starting rotation. -/
theorem divisionMinimalCycleStates_eq_of_mem_cycle
    (Q S T : GaussianInt) (hperiodic : DivisionPeriodicState Q S)
    (hT : T ∈ divisionMinimalCycleStates Q S) :
    divisionMinimalCycleStates Q T =
      divisionMinimalCycleStates Q S := by
  apply Finset.Subset.antisymm
  · exact divisionMinimalCycleStates_subset_of_mem Q S T hperiodic hT
  · rcases (mem_divisionMinimalCycleStates_iff Q S T).mp hT with
      ⟨n, hn, hTiter⟩
    by_cases hnzero : n = 0
    · subst n
      simp at hTiter
      subst T
      exact fun _ h => h
    · let period := divisionMinimalReturnPeriod Q S
      have hspec := divisionMinimalReturnPeriod_spec Q S hperiodic
      have hperiodEq :=
        divisionMinimalReturnPeriod_eq_of_mem_cycle Q S T hperiodic hT
      have hnle : n ≤ period := by
        dsimp [period]
        exact Nat.le_of_lt hn
      have hback : divisionIterate Q T (period - n) = S := by
        rw [← hTiter]
        calc
          divisionIterate Q (divisionIterate Q S n) (period - n) =
              divisionIterate Q S (n + (period - n)) :=
            (divisionIterate_add Q S n (period - n)).symm
          _ = divisionIterate Q S period := by
            rw [Nat.add_sub_of_le hnle]
          _ = S := hspec.2.2.1
      have hbackLt : period - n < divisionMinimalReturnPeriod Q T := by
        rw [hperiodEq]
        dsimp [period]
        omega
      have hSmem : S ∈ divisionMinimalCycleStates Q T :=
        (mem_divisionMinimalCycleStates_iff Q T S).mpr
          ⟨period - n, hbackLt, hback⟩
      have hperiodicT :=
        mem_divisionMinimalCycleStates_periodic Q S T hperiodic hT
      exact divisionMinimalCycleStates_subset_of_mem
        Q T S hperiodicT hSmem

/-- Least encoded state on the primitive cycle, or the state's own code when
    the input is not periodic. -/
def divisionCanonicalCycleCode (Q S : GaussianInt) : ℕ :=
  if h : (divisionMinimalCycleStates Q S).Nonempty then
    ((divisionMinimalCycleStates Q S).image gaussianStateCode).min'
      (h.image gaussianStateCode)
  else gaussianStateCode S

/-- The canonical representative is the decoded least state-code on the
    primitive cycle. -/
def divisionCanonicalCycleRepresentative
    (Q S : GaussianInt) : GaussianInt :=
  gaussianStateDecode (divisionCanonicalCycleCode Q S)

/-- For a periodic state, the canonical code is attained on its primitive
    cycle and is no larger than the code of any other state on that cycle. -/
theorem divisionCanonicalCycleCode_spec
    (Q S : GaussianInt) (hperiodic : DivisionPeriodicState Q S) :
    gaussianStateDecode (divisionCanonicalCycleCode Q S) ∈
        divisionMinimalCycleStates Q S ∧
      ∀ T : GaussianInt, T ∈ divisionMinimalCycleStates Q S →
        divisionCanonicalCycleCode Q S ≤ gaussianStateCode T := by
  let states := divisionMinimalCycleStates Q S
  let codes := states.image gaussianStateCode
  have hstates : states.Nonempty := by
    have hpositive := (divisionMinimalReturnPeriod_spec Q S hperiodic).1
    exact ⟨S, (mem_divisionMinimalCycleStates_iff Q S S).mpr
      ⟨0, hpositive, by simp⟩⟩
  have hcodes : codes.Nonempty := hstates.image gaussianStateCode
  have hvalue : divisionCanonicalCycleCode Q S = codes.min' hcodes := by
    simp [divisionCanonicalCycleCode, states, codes, hstates]
  have hcodeMem : divisionCanonicalCycleCode Q S ∈ codes := by
    rw [hvalue]
    exact Finset.min'_mem codes hcodes
  rcases Finset.mem_image.mp hcodeMem with ⟨T, hT, hTcode⟩
  constructor
  · have hdecode :
        gaussianStateDecode (divisionCanonicalCycleCode Q S) = T := by
      rw [← hTcode]
      exact gaussianStateDecode_code T
    simpa [states, hdecode] using hT
  · intro U hU
    have hUcode : gaussianStateCode U ∈ codes :=
      Finset.mem_image.mpr ⟨U, by simpa [states] using hU, rfl⟩
    rw [hvalue]
    exact Finset.min'_le codes (gaussianStateCode U) hUcode

/-- The canonical representative of a periodic state is on its primitive
    cycle. -/
theorem divisionCanonicalCycleRepresentative_mem
    (Q S : GaussianInt) (hperiodic : DivisionPeriodicState Q S) :
    divisionCanonicalCycleRepresentative Q S ∈
      divisionMinimalCycleStates Q S := by
  exact (divisionCanonicalCycleCode_spec Q S hperiodic).1

/-- The canonical code is independent of the selected rotation. -/
theorem divisionCanonicalCycleCode_eq_of_mem_cycle
    (Q S T : GaussianInt) (hperiodic : DivisionPeriodicState Q S)
    (hT : T ∈ divisionMinimalCycleStates Q S) :
    divisionCanonicalCycleCode Q T = divisionCanonicalCycleCode Q S := by
  have hstates :=
    divisionMinimalCycleStates_eq_of_mem_cycle Q S T hperiodic hT
  have hnonemptyS : (divisionMinimalCycleStates Q S).Nonempty := by
    have hp := (divisionMinimalReturnPeriod_spec Q S hperiodic).1
    exact ⟨S, (mem_divisionMinimalCycleStates_iff Q S S).mpr
      ⟨0, hp, by simp⟩⟩
  simp [divisionCanonicalCycleCode, hnonemptyS, hstates]

/-- The decoded canonical representative is rotation-independent. -/
theorem divisionCanonicalCycleRepresentative_eq_of_mem_cycle
    (Q S T : GaussianInt) (hperiodic : DivisionPeriodicState Q S)
    (hT : T ∈ divisionMinimalCycleStates Q S) :
    divisionCanonicalCycleRepresentative Q T =
      divisionCanonicalCycleRepresentative Q S := by
  simp [divisionCanonicalCycleRepresentative,
    divisionCanonicalCycleCode_eq_of_mem_cycle Q S T hperiodic hT]

/-- Executable deduplicated catalogue for a fixed divisor `Q`: canonical
    representatives of all periodic states in the complete E7 carrier. -/
def divisionCycleCatalogueExec (Q : GaussianInt) : Finset GaussianInt :=
  (divisionCycleStatesExec Q).image
    (divisionCanonicalCycleRepresentative Q)

/-- Exact existential characterization of the executable catalogue. -/
theorem mem_divisionCycleCatalogueExec_iff
    (Q R : GaussianInt) :
    R ∈ divisionCycleCatalogueExec Q ↔
      ∃ S : GaussianInt, DivisionPeriodicState Q S ∧
        divisionCanonicalCycleRepresentative Q S = R := by
  constructor
  · intro hR
    rcases Finset.mem_image.mp hR with ⟨S, hS, rfl⟩
    exact ⟨S, (mem_divisionCycleStatesExec_iff Q S).mp hS, rfl⟩
  · rintro ⟨S, hperiodic, rfl⟩
    exact Finset.mem_image.mpr
      ⟨S, (mem_divisionCycleStatesExec_iff Q S).mpr hperiodic, rfl⟩

/-- Catalogue entries are exactly the periodic states fixed by canonical
    representative selection. -/
theorem mem_divisionCycleCatalogueExec_iff_periodic_fixed
    (Q R : GaussianInt) :
    R ∈ divisionCycleCatalogueExec Q ↔
      DivisionPeriodicState Q R ∧
        divisionCanonicalCycleRepresentative Q R = R := by
  constructor
  · intro hR
    rcases (mem_divisionCycleCatalogueExec_iff Q R).mp hR with
      ⟨S, hperiodic, hrep⟩
    have hrepMem :=
      divisionCanonicalCycleRepresentative_mem Q S hperiodic
    have hperiodicR : DivisionPeriodicState Q R := by
      rw [← hrep]
      exact mem_divisionMinimalCycleStates_periodic Q S
        (divisionCanonicalCycleRepresentative Q S) hperiodic hrepMem
    have hinvariant :=
      divisionCanonicalCycleRepresentative_eq_of_mem_cycle Q S
        (divisionCanonicalCycleRepresentative Q S) hperiodic hrepMem
    exact ⟨hperiodicR, by rw [← hrep, hinvariant]⟩
  · rintro ⟨hperiodic, hfixed⟩
    exact (mem_divisionCycleCatalogueExec_iff Q R).mpr
      ⟨R, hperiodic, hfixed⟩

/-- For each periodic orbit of a fixed divisor `Q`, exactly one state from
    its primitive cycle occurs in the executable catalogue. -/
theorem divisionCycleCatalogue_unique_on_primitive_cycle
    (Q S : GaussianInt) (hperiodic : DivisionPeriodicState Q S) :
    ∃! R : GaussianInt,
      R ∈ divisionMinimalCycleStates Q S ∧
        R ∈ divisionCycleCatalogueExec Q := by
  let R := divisionCanonicalCycleRepresentative Q S
  have hcycle : R ∈ divisionMinimalCycleStates Q S := by
    exact divisionCanonicalCycleRepresentative_mem Q S hperiodic
  have hcatalogue : R ∈ divisionCycleCatalogueExec Q := by
    exact (mem_divisionCycleCatalogueExec_iff Q R).mpr
      ⟨S, hperiodic, rfl⟩
  refine ⟨R, ⟨hcycle, hcatalogue⟩, ?_⟩
  intro T hT
  have hfixed : divisionCanonicalCycleRepresentative Q T = T :=
    ((mem_divisionCycleCatalogueExec_iff_periodic_fixed Q T).mp hT.2).2
  have hinvariant :=
    divisionCanonicalCycleRepresentative_eq_of_mem_cycle
      Q S T hperiodic hT.1
  calc
    T = divisionCanonicalCycleRepresentative Q T := hfixed.symm
    _ = R := by simpa [R] using hinvariant

/-- Every periodic state has its canonical representative in the executable
    catalogue. -/
theorem divisionCanonicalCycleRepresentative_mem_catalogue
    (Q S : GaussianInt) (hperiodic : DivisionPeriodicState Q S) :
    divisionCanonicalCycleRepresentative Q S ∈
      divisionCycleCatalogueExec Q := by
  exact (mem_divisionCycleCatalogueExec_iff Q
    (divisionCanonicalCycleRepresentative Q S)).mpr
      ⟨S, hperiodic, rfl⟩

end CNRSArithmetic
