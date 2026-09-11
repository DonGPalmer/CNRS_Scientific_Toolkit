/-
CNRSArithmetic Phase E3: division state bounds / orbit control.

This module builds only on the frozen E2 exact division recurrence.
It proves a coarse max-coordinate contraction estimate, an invariant
divisor-dependent height ball, strict descent outside that ball, and
a global height bound for every deterministic E2 iterate.

It does not prove orbit periodicity, general termination, or an online
finite-state division transducer.
-/
import CNRSArithmetic.ExactDivisionRecurrence
import CNRSCore.Finiteness
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- Every emitted E2 quotient digit index is at most four. -/
theorem divisionDigitIndex_le_four (Q N : GaussianInt) :
    (divisionDigitIndex Q N : ℕ) ≤ 4 := by
  have h := (divisionDigitIndex Q N).isLt
  omega

/-- The E2 residual has max-coordinate height at most
    `H(N) + 4 H(Q)`. -/
theorem divisionResidual_height_bound (Q N : GaussianInt) :
    CNRSCore.gaussianHeight (divisionResidual Q N) ≤
      CNRSCore.gaussianHeight N + 4 * CNRSCore.gaussianHeight Q := by
  have hd : (divisionDigitIndex Q N : ℕ) ≤ 4 :=
    divisionDigitIndex_le_four Q N
  have hNre : N.re.natAbs ≤ CNRSCore.gaussianHeight N :=
    Nat.le_max_left _ _
  have hNim : N.im.natAbs ≤ CNRSCore.gaussianHeight N :=
    Nat.le_max_right _ _
  have hQre : Q.re.natAbs ≤ CNRSCore.gaussianHeight Q :=
    Nat.le_max_left _ _
  have hQim : Q.im.natAbs ≤ CNRSCore.gaussianHeight Q :=
    Nat.le_max_right _ _
  have hdre :
      (divisionDigitIndex Q N : ℕ) * Q.re.natAbs ≤
        4 * CNRSCore.gaussianHeight Q :=
    Nat.mul_le_mul hd hQre
  have hdim :
      (divisionDigitIndex Q N : ℕ) * Q.im.natAbs ≤
        4 * CNRSCore.gaussianHeight Q :=
    Nat.mul_le_mul hd hQim
  have hre :
      (divisionResidual Q N).re.natAbs ≤
        CNRSCore.gaussianHeight N + 4 * CNRSCore.gaussianHeight Q := by
    calc
      (divisionResidual Q N).re.natAbs =
          (N.re - ((divisionDigitIndex Q N : ℕ) : ℤ) * Q.re).natAbs := by
            simp [divisionResidual, divisionDigit]
      _ ≤ N.re.natAbs +
          (((divisionDigitIndex Q N : ℕ) : ℤ) * Q.re).natAbs := by
            exact Int.natAbs_sub_le _ _
      _ = N.re.natAbs +
          (divisionDigitIndex Q N : ℕ) * Q.re.natAbs := by
            simp [Int.natAbs_mul]
      _ ≤ CNRSCore.gaussianHeight N +
          4 * CNRSCore.gaussianHeight Q :=
            Nat.add_le_add hNre hdre
  have him :
      (divisionResidual Q N).im.natAbs ≤
        CNRSCore.gaussianHeight N + 4 * CNRSCore.gaussianHeight Q := by
    calc
      (divisionResidual Q N).im.natAbs =
          (N.im - ((divisionDigitIndex Q N : ℕ) : ℤ) * Q.im).natAbs := by
            simp [divisionResidual, divisionDigit]
      _ ≤ N.im.natAbs +
          (((divisionDigitIndex Q N : ℕ) : ℤ) * Q.im).natAbs := by
            exact Int.natAbs_sub_le _ _
      _ = N.im.natAbs +
          (divisionDigitIndex Q N : ℕ) * Q.im.natAbs := by
            simp [Int.natAbs_mul]
      _ ≤ CNRSCore.gaussianHeight N +
          4 * CNRSCore.gaussianHeight Q :=
            Nat.add_le_add hNim hdim
  unfold CNRSCore.gaussianHeight
  exact max_le hre him

/-- Coarse affine one-step bound for the deterministic E2 state map. -/
theorem divisionNext_height_affine_bound (Q N : GaussianInt) :
    5 * CNRSCore.gaussianHeight (divisionNext Q N) ≤
      3 * CNRSCore.gaussianHeight N +
        12 * CNRSCore.gaussianHeight Q + 8 := by
  have hcore := CNRSCore.nextQuotient_height_bound (divisionResidual Q N)
  have hres := divisionResidual_height_bound Q N
  change
    5 * CNRSCore.gaussianHeight (divisionNext Q N) ≤
      3 * CNRSCore.gaussianHeight (divisionResidual Q N) + 8 at hcore
  omega

/-- Divisor-dependent invariant height radius for E3. -/
def divisionStateBound (Q : GaussianInt) : ℕ :=
  6 * CNRSCore.gaussianHeight Q + 4

/-- The E3 height ball is forward invariant under one division step. -/
theorem divisionNext_height_le_stateBound
    (Q N : GaussianInt)
    (hN : CNRSCore.gaussianHeight N ≤ divisionStateBound Q) :
    CNRSCore.gaussianHeight (divisionNext Q N) ≤ divisionStateBound Q := by
  have h := divisionNext_height_affine_bound Q N
  unfold divisionStateBound at hN ⊢
  omega

/-- Outside the E3 height ball, one division step strictly decreases height. -/
theorem divisionNext_height_lt_of_stateBound_lt
    (Q N : GaussianInt)
    (hN : divisionStateBound Q < CNRSCore.gaussianHeight N) :
    CNRSCore.gaussianHeight (divisionNext Q N) < CNRSCore.gaussianHeight N := by
  have h := divisionNext_height_affine_bound Q N
  unfold divisionStateBound at hN
  omega

/-- Once an E2 trajectory is inside the E3 height ball, every later state stays inside. -/
theorem divisionIterate_height_le_stateBound_of_le
    (Q N : GaussianInt)
    (hN : CNRSCore.gaussianHeight N ≤ divisionStateBound Q) :
    ∀ n, CNRSCore.gaussianHeight (divisionIterate Q N n) ≤ divisionStateBound Q := by
  intro n
  induction n with
  | zero => simpa using hN
  | succ n ih =>
      rw [divisionIterate_succ]
      exact divisionNext_height_le_stateBound Q (divisionIterate Q N n) ih

/-- Every deterministic E2 orbit is globally bounded by the larger of
    its initial height and the invariant E3 divisor radius. -/
theorem divisionIterate_height_global_bound
    (Q N : GaussianInt) (n : ℕ) :
    CNRSCore.gaussianHeight (divisionIterate Q N n) ≤
      max (CNRSCore.gaussianHeight N) (divisionStateBound Q) := by
  induction n with
  | zero =>
      simp only [divisionIterate_zero]
      exact Nat.le_max_left _ _
  | succ n ih =>
      rw [divisionIterate_succ]
      by_cases hcur :
          CNRSCore.gaussianHeight (divisionIterate Q N n) ≤ divisionStateBound Q
      · exact le_trans
          (divisionNext_height_le_stateBound Q (divisionIterate Q N n) hcur)
          (Nat.le_max_right _ _)
      · have hgt :
            divisionStateBound Q <
              CNRSCore.gaussianHeight (divisionIterate Q N n) := by
          omega
        have hlt := divisionNext_height_lt_of_stateBound_lt
          Q (divisionIterate Q N n) hgt
        exact le_trans (Nat.le_of_lt hlt) ih

/-- At any iterate still outside the invariant E3 ball, the next iterate descends. -/
theorem divisionIterate_height_descends_outside
    (Q N : GaussianInt) (n : ℕ)
    (hN : divisionStateBound Q <
      CNRSCore.gaussianHeight (divisionIterate Q N n)) :
    CNRSCore.gaussianHeight (divisionIterate Q N (n + 1)) <
      CNRSCore.gaussianHeight (divisionIterate Q N n) := by
  rw [divisionIterate_succ]
  exact divisionNext_height_lt_of_stateBound_lt Q (divisionIterate Q N n) hN


/-- Explicit finite square of Gaussian integers of max-coordinate height at most `B`. -/
noncomputable def gaussianHeightCarrier (B : ℕ) : Finset GaussianInt :=
  ((Finset.Icc (-(B : ℤ)) (B : ℤ)).product
    (Finset.Icc (-(B : ℤ)) (B : ℤ))).image
      (fun p : ℤ × ℤ => (⟨p.1, p.2⟩ : GaussianInt))

/-- Every Gaussian integer of height at most `B` belongs to the explicit carrier. -/
theorem mem_gaussianHeightCarrier_of_height_le
    (B : ℕ) (x : GaussianInt)
    (hx : CNRSCore.gaussianHeight x ≤ B) :
    x ∈ gaussianHeightCarrier B := by
  apply Finset.mem_image.mpr
  refine ⟨(x.re, x.im), ?_, ?_⟩
  ·
    have hre : x.re.natAbs ≤ B :=
      le_trans (Nat.le_max_left _ _) hx
    have him : x.im.natAbs ≤ B :=
      le_trans (Nat.le_max_right _ _) hx
    have hre_bound : -(B : ℤ) ≤ x.re ∧ x.re ≤ (B : ℤ) := by
      have hb : x.re.natAbs ≤ ((B : ℤ).natAbs) := by
        rw [Int.natAbs_natCast]
        exact hre
      have hsq := Int.natAbs_le_iff_mul_self_le.mp hb
      have hB : 0 ≤ (B : ℤ) := by positivity
      constructor <;> nlinarith
    have him_bound : -(B : ℤ) ≤ x.im ∧ x.im ≤ (B : ℤ) := by
      have hb : x.im.natAbs ≤ ((B : ℤ).natAbs) := by
        rw [Int.natAbs_natCast]
        exact him
      have hsq := Int.natAbs_le_iff_mul_self_le.mp hb
      have hB : 0 ≤ (B : ℤ) := by positivity
      constructor <;> nlinarith
    exact Finset.mem_product.mpr ⟨Finset.mem_Icc.mpr hre_bound, Finset.mem_Icc.mpr him_bound⟩
  · ext <;> rfl

/-- The divisor-only E3 invariant finite carrier. -/
noncomputable def divisionStateCarrier (Q : GaussianInt) : Finset GaussianInt :=
  gaussianHeightCarrier (divisionStateBound Q)

/-- Any trajectory starting inside the E3 invariant ball stays in its explicit finite carrier. -/
theorem divisionIterate_mem_stateCarrier_of_le
    (Q N : GaussianInt)
    (hN : CNRSCore.gaussianHeight N ≤ divisionStateBound Q)
    (n : ℕ) :
    divisionIterate Q N n ∈ divisionStateCarrier Q := by
  apply mem_gaussianHeightCarrier_of_height_le
  exact divisionIterate_height_le_stateBound_of_le Q N hN n

/-- Global radius controlling the full orbit from arbitrary initial numerator `N`. -/
def divisionOrbitBound (Q N : GaussianInt) : ℕ :=
  max (CNRSCore.gaussianHeight N) (divisionStateBound Q)

/-- Explicit finite carrier for the complete deterministic E2 orbit from `N`. -/
noncomputable def divisionOrbitCarrier (Q N : GaussianInt) : Finset GaussianInt :=
  gaussianHeightCarrier (divisionOrbitBound Q N)

/-- Every deterministic E2 iterate belongs to the explicit global orbit carrier. -/
theorem divisionIterate_mem_orbitCarrier
    (Q N : GaussianInt) (n : ℕ) :
    divisionIterate Q N n ∈ divisionOrbitCarrier Q N := by
  apply mem_gaussianHeightCarrier_of_height_le
  exact divisionIterate_height_global_bound Q N n

/-- The set of states visited by any deterministic E2 orbit is finite. -/
theorem divisionOrbit_range_finite (Q N : GaussianInt) :
    Set.Finite (Set.range (divisionIterate Q N)) := by
  apply (divisionOrbitCarrier Q N).finite_toSet.subset
  rintro x ⟨n, rfl⟩
  exact divisionIterate_mem_orbitCarrier Q N n

end CNRSArithmetic
