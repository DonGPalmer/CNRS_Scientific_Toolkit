/-
CNRSArithmetic Phase E7 candidate: constructive carrier enumeration and
complete executable cycle search.

This module replaces the theorem-level noncomputable presentation of the E3
height square with a definition that Lean can evaluate.  It then proves a
universal return horizon from the cardinality of that finite carrier and uses
the horizon to turn E6's bounded Boolean return test into an exact executable
classifier of every periodic division state.

The phase does not claim a closed-form description of the cycles, a minimal
period algorithm, universal termination, or an online division transducer.
-/
import CNRSArithmetic.DivisionCycleClassification
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- Computable enumeration of the Gaussian height square `H(N) ≤ B`. -/
def gaussianHeightCarrierExec (B : ℕ) : Finset GaussianInt :=
  ((Finset.range (2 * B + 1)).product
    (Finset.range (2 * B + 1))).image
      (fun p : ℕ × ℕ =>
        (⟨(p.1 : ℤ) - (B : ℤ), (p.2 : ℤ) - (B : ℤ)⟩ : GaussianInt))

/-- Exact membership characterization of the executable height square. -/
theorem mem_gaussianHeightCarrierExec_iff
    (B : ℕ) (N : GaussianInt) :
    N ∈ gaussianHeightCarrierExec B ↔
      CNRSCore.gaussianHeight N ≤ B := by
  constructor
  · intro hN
    rw [gaussianHeightCarrierExec] at hN
    rcases Finset.mem_image.mp hN with ⟨p, hp, rfl⟩
    rcases Finset.mem_product.mp hp with ⟨hre, him⟩
    rw [Finset.mem_range] at hre him
    change
      max ((p.1 : ℤ) - (B : ℤ)).natAbs
          ((p.2 : ℤ) - (B : ℤ)).natAbs ≤ B
    apply max_le
    · have hpNat : p.1 ≤ 2 * B := by omega
      have hpInt : (p.1 : ℤ) ≤ (2 * B : ℕ) := by exact_mod_cast hpNat
      have hlo : -(B : ℤ) ≤ (p.1 : ℤ) - (B : ℤ) := by omega
      have hhi : (p.1 : ℤ) - (B : ℤ) ≤ (B : ℤ) := by
        norm_num at hpInt ⊢
        omega
      have hsquare :
          ((p.1 : ℤ) - (B : ℤ)) * ((p.1 : ℤ) - (B : ℤ)) ≤
            (B : ℤ) * (B : ℤ) := by
        have hB : 0 ≤ (B : ℤ) := by positivity
        nlinarith
      have habs := Int.natAbs_le_iff_mul_self_le.mpr hsquare
      simpa using habs
    · have hpNat : p.2 ≤ 2 * B := by omega
      have hpInt : (p.2 : ℤ) ≤ (2 * B : ℕ) := by exact_mod_cast hpNat
      have hlo : -(B : ℤ) ≤ (p.2 : ℤ) - (B : ℤ) := by omega
      have hhi : (p.2 : ℤ) - (B : ℤ) ≤ (B : ℤ) := by
        norm_num at hpInt ⊢
        omega
      have hsquare :
          ((p.2 : ℤ) - (B : ℤ)) * ((p.2 : ℤ) - (B : ℤ)) ≤
            (B : ℤ) * (B : ℤ) := by
        have hB : 0 ≤ (B : ℤ) := by positivity
        nlinarith
      have habs := Int.natAbs_le_iff_mul_self_le.mpr hsquare
      simpa using habs
  · intro hN
    have hre : N.re.natAbs ≤ B :=
      le_trans (Nat.le_max_left _ _) hN
    have him : N.im.natAbs ≤ B :=
      le_trans (Nat.le_max_right _ _) hN
    have hreBound : -(B : ℤ) ≤ N.re ∧ N.re ≤ (B : ℤ) := by
      have hb : N.re.natAbs ≤ ((B : ℤ).natAbs) := by
        rw [Int.natAbs_natCast]
        exact hre
      have hsq := Int.natAbs_le_iff_mul_self_le.mp hb
      have hB : 0 ≤ (B : ℤ) := by positivity
      constructor <;> nlinarith
    have himBound : -(B : ℤ) ≤ N.im ∧ N.im ≤ (B : ℤ) := by
      have hb : N.im.natAbs ≤ ((B : ℤ).natAbs) := by
        rw [Int.natAbs_natCast]
        exact him
      have hsq := Int.natAbs_le_iff_mul_self_le.mp hb
      have hB : 0 ≤ (B : ℤ) := by positivity
      constructor <;> nlinarith
    let r : ℕ := (N.re + (B : ℤ)).toNat
    let i : ℕ := (N.im + (B : ℤ)).toNat
    have hrNonneg : 0 ≤ N.re + (B : ℤ) := by omega
    have hiNonneg : 0 ≤ N.im + (B : ℤ) := by omega
    have hrVal : (r : ℤ) = N.re + (B : ℤ) := by
      simpa [r] using (Int.toNat_of_nonneg hrNonneg).symm
    have hiVal : (i : ℤ) = N.im + (B : ℤ) := by
      simpa [i] using (Int.toNat_of_nonneg hiNonneg).symm
    have hrLe : r ≤ 2 * B := by
      exact_mod_cast (show (r : ℤ) ≤ (2 * B : ℕ) by
        norm_num at hrVal ⊢
        omega)
    have hiLe : i ≤ 2 * B := by
      exact_mod_cast (show (i : ℤ) ≤ (2 * B : ℕ) by
        norm_num at hiVal ⊢
        omega)
    rw [gaussianHeightCarrierExec]
    apply Finset.mem_image.mpr
    refine ⟨(r, i), Finset.mem_product.mpr ?_, ?_⟩
    · exact ⟨Finset.mem_range.mpr (by omega),
        Finset.mem_range.mpr (by omega)⟩
    · ext
      · change (r : ℤ) - (B : ℤ) = N.re
        rw [hrVal]
        ring
      · change (i : ℤ) - (B : ℤ) = N.im
        rw [hiVal]
        ring

/-- The executable carrier is extensionally the E3 theorem-level carrier. -/
theorem gaussianHeightCarrierExec_eq_gaussianHeightCarrier (B : ℕ) :
    gaussianHeightCarrierExec B = gaussianHeightCarrier B := by
  ext N
  rw [mem_gaussianHeightCarrierExec_iff]
  constructor
  · exact mem_gaussianHeightCarrier_of_height_le B N
  · exact gaussianHeight_le_of_mem_gaussianHeightCarrier B N

/-- Computable divisor-dependent invariant carrier. -/
def divisionStateCarrierExec (Q : GaussianInt) : Finset GaussianInt :=
  gaussianHeightCarrierExec (divisionStateBound Q)

/-- The executable and structural divisor carriers coincide. -/
theorem divisionStateCarrierExec_eq_divisionStateCarrier
    (Q : GaussianInt) :
    divisionStateCarrierExec Q = divisionStateCarrier Q := by
  exact gaussianHeightCarrierExec_eq_gaussianHeightCarrier
    (divisionStateBound Q)

/-- Exact membership characterization of the executable divisor carrier. -/
theorem mem_divisionStateCarrierExec_iff
    (Q N : GaussianInt) :
    N ∈ divisionStateCarrierExec Q ↔
      CNRSCore.gaussianHeight N ≤ divisionStateBound Q := by
  exact mem_gaussianHeightCarrierExec_iff (divisionStateBound Q) N

/-- Every vertex of the executable carrier has its successor in the same
    executable carrier. -/
theorem divisionStateCarrierExec_successor_mem
    (Q N : GaussianInt) (hN : N ∈ divisionStateCarrierExec Q) :
    divisionNext Q N ∈ divisionStateCarrierExec Q := by
  rw [mem_divisionStateCarrierExec_iff] at hN ⊢
  exact divisionNext_height_le_stateBound Q N hN

/-- Executable universal search horizon: the number of states in the complete
    divisor-dependent invariant carrier. -/
def divisionSearchHorizon (Q : GaussianInt) : ℕ :=
  (divisionStateCarrierExec Q).card

/-- A periodic state has a positive return period no larger than the executable
    carrier cardinality. -/
theorem divisionPeriodicState_has_period_le_searchHorizon
    (Q N : GaussianInt) (hperiodic : DivisionPeriodicState Q N) :
    ∃ period : ℕ, 0 < period ∧
      period ≤ divisionSearchHorizon Q ∧
      divisionIterate Q N period = N := by
  classical
  let period : ℕ := Nat.find hperiodic
  have hperiodSpec :
      0 < period ∧ divisionIterate Q N period = N :=
    Nat.find_spec hperiodic
  have hheight :
      CNRSCore.gaussianHeight N ≤ divisionStateBound Q :=
    divisionPeriodicState_height_le_stateBound Q N hperiodic
  let visited : Finset GaussianInt :=
    (Finset.range period).image (divisionIterate Q N)
  have hstrict :
      ∀ {i j : ℕ}, i < j → j < period →
        divisionIterate Q N i = divisionIterate Q N j → False := by
    intro i j hij hj hEq
    have hprop :=
      divisionIterate_eq_add_of_eq Q N hEq (period - j)
    have hjindex : j + (period - j) = period := by omega
    have hsmallPos : 0 < i + (period - j) := by omega
    have hsmallLt : i + (period - j) < period := by omega
    have hsmallReturn :
        divisionIterate Q N (i + (period - j)) = N := by
      rw [hjindex] at hprop
      exact hprop.trans hperiodSpec.2
    have hminimal : period ≤ i + (period - j) :=
      Nat.find_min' hperiodic ⟨hsmallPos, hsmallReturn⟩
    omega
  have hinjective :
      Set.InjOn (divisionIterate Q N) (Finset.range period : Set ℕ) := by
    intro i hi j hj hEq
    have hiLt : i < period := Finset.mem_range.mp hi
    have hjLt : j < period := Finset.mem_range.mp hj
    by_contra hne
    rcases lt_or_gt_of_ne hne with hij | hji
    · exact hstrict hij hjLt hEq
    · exact hstrict hji hiLt hEq.symm
  have hvisitedCard : visited.card = period := by
    simpa [visited] using
      (Finset.card_image_iff.mpr hinjective)
  have hvisitedSubset : visited ⊆ divisionStateCarrierExec Q := by
    intro M hM
    rcases Finset.mem_image.mp hM with ⟨n, hn, rfl⟩
    rw [mem_divisionStateCarrierExec_iff]
    exact divisionIterate_height_le_stateBound_of_le Q N hheight n
  have hcard : period ≤ divisionSearchHorizon Q := by
    rw [divisionSearchHorizon]
    rw [← hvisitedCard]
    exact Finset.card_le_card hvisitedSubset
  exact ⟨period, hperiodSpec.1, hcard, hperiodSpec.2⟩

/-- The universal executable horizon is complete for periodicity. -/
theorem divisionReturnsWithin_searchHorizon_eq_true_iff
    (Q N : GaussianInt) :
    divisionReturnsWithin Q N (divisionSearchHorizon Q) = true ↔
      DivisionPeriodicState Q N := by
  constructor
  · intro h
    rcases (divisionReturnsWithin_eq_true_iff
      Q N (divisionSearchHorizon Q)).mp h with
      ⟨period, hpositive, _hbound, hreturn⟩
    exact ⟨period, hpositive, hreturn⟩
  · intro h
    rcases divisionPeriodicState_has_period_le_searchHorizon Q N h with
      ⟨period, hpositive, hbound, hreturn⟩
    exact (divisionReturnsWithin_eq_true_iff
      Q N (divisionSearchHorizon Q)).mpr
        ⟨period, hpositive, hbound, hreturn⟩

/-- Fully executable classifier of all periodic states for a fixed divisor. -/
def divisionCycleStatesExec (Q : GaussianInt) : Finset GaussianInt :=
  (divisionStateCarrierExec Q).filter
    (fun N =>
      divisionReturnsWithin Q N (divisionSearchHorizon Q) = true)

/-- The executable E7 classifier is sound and complete for periodicity. -/
theorem mem_divisionCycleStatesExec_iff
    (Q N : GaussianInt) :
    N ∈ divisionCycleStatesExec Q ↔ DivisionPeriodicState Q N := by
  constructor
  · intro h
    exact divisionReturnsWithin_searchHorizon_eq_true_iff Q N |>.mp
      (Finset.mem_filter.mp h).2
  · intro h
    apply Finset.mem_filter.mpr
    refine ⟨?_,
      (divisionReturnsWithin_searchHorizon_eq_true_iff Q N).mpr h⟩
    rw [mem_divisionStateCarrierExec_iff]
    exact divisionPeriodicState_height_le_stateBound Q N h

/-- The executable E7 classifier equals E6's exact theorem-level classifier. -/
theorem divisionCycleStatesExec_eq_divisionCycleStates
    (Q : GaussianInt) :
    divisionCycleStatesExec Q = divisionCycleStates Q := by
  ext N
  rw [mem_divisionCycleStatesExec_iff, mem_divisionCycleStates_iff]

end CNRSArithmetic
