/-
CNRSArithmetic Phase E2: exact division recurrence.

Scope is deliberately limited to the exact deterministic recurrence:
  d_n ≡ phi(N_n) * phi(Q)^(-1) (mod 5)
  N_(n+1) = (N_n - d_n Q) / beta.

This module proves one-step exactness, n-step reconstruction, and
determinism of every exact trajectory. It makes no claim here about
state bounds, periodicity, termination, or an online division transducer.
-/
import CNRSArithmetic.Digits
import CNRSCore.QuotientStep
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- A fixed divisor is admissible for the recurrence when its beta-residue is nonzero. -/
def DivisionAdmissible (Q : GaussianInt) : Prop := phi Q ≠ 0

/-- Every nonzero residue in `ZMod 5` is a unit. -/
theorem zmod5_isUnit_of_ne_zero (a : ZMod 5) (ha : a ≠ 0) : IsUnit a := by
  have hrepr : ((a.val : ℕ) : ZMod 5) = a := ZMod.natCast_zmod_val a
  have hval0 : a.val ≠ 0 := by
    intro hv
    apply ha
    rw [← hrepr]
    simp [hv]
  have hlt := ZMod.val_lt a
  have hcop : Nat.Coprime a.val 5 := by
    interval_cases hval : a.val
    · exact (hval0 rfl).elim
    · norm_num
    · norm_num
    · norm_num
    · norm_num
  have hu : IsUnit ((a.val : ℕ) : ZMod 5) :=
    (ZMod.isUnit_iff_coprime a.val 5).2 hcop
  rw [hrepr] at hu
  exact hu

/-- Canonical quotient digit index selected at numerator state `N` for fixed divisor `Q`. -/
def divisionDigitIndex (Q N : GaussianInt) : Digit :=
  ⟨(phi N * (phi Q)⁻¹).val, ZMod.val_lt (phi N * (phi Q)⁻¹)⟩

/-- Gaussian embedding of the selected quotient digit. -/
def divisionDigit (Q N : GaussianInt) : GaussianInt :=
  digit (divisionDigitIndex Q N)

/-- Every canonical digit reduces to its own index in `ZMod 5`. -/
theorem phi_digit_val (d : Digit) : phi (digit d) = (d.val : ZMod 5) := by
  simp [phi, digit, CNRSCore.phi, CNRSCore.digit]

/-- The selected quotient digit realizes the residue rule exactly. -/
theorem phi_divisionDigit (Q N : GaussianInt) :
    phi (divisionDigit Q N) = phi N * (phi Q)⁻¹ := by
  rw [divisionDigit, phi_digit_val]
  unfold divisionDigitIndex
  exact ZMod.natCast_zmod_val (phi N * (phi Q)⁻¹)

/-- Subtraction is preserved by the residue map. -/
theorem phi_sub (x y : GaussianInt) : phi (x - y) = phi x - phi y := by
  change CNRSCore.phi (x - y) = CNRSCore.phi x - CNRSCore.phi y
  simp [CNRSCore.phi]
  ring

/-- For an admissible divisor, the selected digit times the divisor has numerator residue. -/
theorem phi_divisionDigit_mul_divisor
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    phi (divisionDigit Q N * Q) = phi N := by
  unfold DivisionAdmissible at hQ
  rw [phi_mul, phi_divisionDigit]
  calc
    (phi N * (phi Q)⁻¹) * phi Q
        = phi N * ((phi Q)⁻¹ * phi Q) := by rw [mul_assoc]
    _ = phi N := by
      have hunit : IsUnit (phi Q) := zmod5_isUnit_of_ne_zero (phi Q) hQ
      have hinv : (phi Q)⁻¹ * phi Q = 1 := ZMod.inv_mul_of_unit (phi Q) hunit
      exact (congrArg (fun z => phi N * z) hinv).trans (mul_one (phi N))

/-- Numerator remainder after emitting the selected quotient digit. -/
def divisionResidual (Q N : GaussianInt) : GaussianInt :=
  N - divisionDigit Q N * Q

/-- The recurrence residual is exactly divisible by beta at the residue level. -/
theorem phi_divisionResidual_zero
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    phi (divisionResidual Q N) = 0 := by
  rw [divisionResidual, phi_sub, phi_divisionDigit_mul_divisor Q N hQ]
  simp

/-- A zero-residue residual has Core-selected digit zero. -/
theorem selectedDigit_divisionResidual_zero
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    CNRSCore.selectedDigit (divisionResidual Q N) = 0 := by
  have hphi := phi_divisionResidual_zero Q N hQ
  simp [CNRSCore.selectedDigit, CNRSCore.residueIndex, hphi]

/-- Deterministic next numerator state, using Core's exact beta quotient. -/
def divisionNext (Q N : GaussianInt) : GaussianInt :=
  CNRSCore.nextQuotient (divisionResidual Q N)

/-- The residual is exactly beta times the next state. -/
theorem beta_mul_divisionNext
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    beta * divisionNext Q N = divisionResidual Q N := by
  have h := CNRSCore.selectedDigit_add_beta_mul_nextQuotient
    (divisionResidual Q N)
  rw [selectedDigit_divisionResidual_zero Q N hQ] at h
  simpa [divisionNext] using h

/-- One exact division step reconstructs the current numerator state. -/
theorem divisionStep_reconstruct
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    divisionDigit Q N * Q + beta * divisionNext Q N = N := by
  rw [beta_mul_divisionNext Q N hQ]
  simp [divisionResidual]

/-- Numerator state after `n` deterministic quotient steps. -/
def divisionIterate (Q N : GaussianInt) : ℕ → GaussianInt
  | 0 => N
  | n + 1 => divisionNext Q (divisionIterate Q N n)

@[simp] theorem divisionIterate_zero (Q N : GaussianInt) :
    divisionIterate Q N 0 = N := rfl

@[simp] theorem divisionIterate_succ (Q N : GaussianInt) (n : ℕ) :
    divisionIterate Q N (n + 1) = divisionNext Q (divisionIterate Q N n) := rfl

/-- Quotient digit emitted at step `n`. -/
def divisionDigitAt (Q N : GaussianInt) (n : ℕ) : Digit :=
  divisionDigitIndex Q (divisionIterate Q N n)

/-- Value of the first `n` emitted quotient digits, LSD first. -/
def divisionPrefixValue (Q N : GaussianInt) (n : ℕ) : GaussianInt :=
  Finset.sum (Finset.range n)
    (fun k => digit (divisionDigitAt Q N k) * beta ^ k)

theorem divisionPrefixValue_succ (Q N : GaussianInt) (n : ℕ) :
    divisionPrefixValue Q N (n + 1) =
      divisionPrefixValue Q N n +
        digit (divisionDigitAt Q N n) * beta ^ n := by
  simp [divisionPrefixValue, Finset.sum_range_succ]

/-- Exact n-step reconstruction invariant for the quotient recurrence. -/
theorem divisionIterate_reconstruct
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) (n : ℕ) :
    Q * divisionPrefixValue Q N n +
        beta ^ n * divisionIterate Q N n = N := by
  induction n with
  | zero => simp [divisionPrefixValue]
  | succ n ih =>
      rw [divisionPrefixValue_succ, divisionIterate_succ, pow_succ]
      have hstep :
          digit (divisionDigitAt Q N n) * Q +
              beta * divisionNext Q (divisionIterate Q N n) =
            divisionIterate Q N n := by
        simpa [divisionDigitAt, divisionDigit] using
          divisionStep_reconstruct Q (divisionIterate Q N n) hQ
      calc
        Q * (divisionPrefixValue Q N n +
              digit (divisionDigitAt Q N n) * beta ^ n) +
            (beta ^ n * beta) * divisionNext Q (divisionIterate Q N n)
            = Q * divisionPrefixValue Q N n +
                beta ^ n *
                  (digit (divisionDigitAt Q N n) * Q +
                    beta * divisionNext Q (divisionIterate Q N n)) := by ring
        _ = Q * divisionPrefixValue Q N n +
              beta ^ n * divisionIterate Q N n := by rw [hstep]
        _ = N := ih

/-- If an iterate reaches zero, the emitted finite prefix is an exact quotient value. -/
theorem divisionIterate_eq_zero_implies_exact
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) (n : ℕ)
    (hz : divisionIterate Q N n = 0) :
    Q * divisionPrefixValue Q N n = N := by
  have h := divisionIterate_reconstruct Q N hQ n
  rw [hz, mul_zero, add_zero] at h
  exact h

/-- Any exact one-step representation must use the canonical E2 digit and next state. -/
theorem divisionStep_unique
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    {d : Digit} {N' : GaussianInt}
    (hstep : digit d * Q + beta * N' = N) :
    d = divisionDigitIndex Q N ∧ N' = divisionNext Q N := by
  unfold DivisionAdmissible at hQ
  have hres : phi (digit d) * phi Q = phi N := by
    have h := congrArg phi hstep
    rw [phi_add, phi_mul, phi_mul, phi_beta] at h
    simpa using h
  have hdphi : phi (digit d) = phi (divisionDigit Q N) := by
    calc
      phi (digit d)
          = (phi (digit d) * phi Q) * (phi Q)⁻¹ := by
              have hunit : IsUnit (phi Q) := zmod5_isUnit_of_ne_zero (phi Q) hQ
              have hinv : phi Q * (phi Q)⁻¹ = 1 := by
                rw [mul_comm]
                exact ZMod.inv_mul_of_unit (phi Q) hunit
              calc
                phi (digit d) = phi (digit d) * 1 := (mul_one _).symm
                _ = phi (digit d) * (phi Q * (phi Q)⁻¹) :=
                  congrArg (fun z => phi (digit d) * z) hinv.symm
                _ = (phi (digit d) * phi Q) * (phi Q)⁻¹ := by rw [mul_assoc]
      _ = phi N * (phi Q)⁻¹ := by rw [hres]
      _ = phi (divisionDigit Q N) := (phi_divisionDigit Q N).symm
  have hd : d = divisionDigitIndex Q N := by
    apply digit_bijective.1
    simpa [divisionDigit] using hdphi
  subst d
  have hstep' : divisionDigit Q N * Q + beta * N' = N := by
    simpa [divisionDigit] using hstep
  have hcanon := divisionStep_reconstruct Q N hQ
  have hb : beta * N' = beta * divisionNext Q N :=
    add_left_cancel (hstep'.trans hcanon.symm)
  have hn : N' = divisionNext Q N := by
    exact mul_left_cancel₀ CNRSCore.prime_beta.ne_zero hb
  exact ⟨rfl, hn⟩

/-- Every exact trajectory with the same initial state has the canonical E2 states. -/
theorem divisionTrajectory_state_unique
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    (S : ℕ → GaussianInt) (D : ℕ → Digit)
    (h0 : S 0 = N)
    (hstep : ∀ n, digit (D n) * Q + beta * S (n + 1) = S n) :
    ∀ n, S n = divisionIterate Q N n := by
  intro n
  induction n with
  | zero => exact h0
  | succ n ih =>
      have hs := hstep n
      rw [ih] at hs
      simpa using (divisionStep_unique Q (divisionIterate Q N n) hQ hs).2

/-- Every exact trajectory with the same initial state emits the canonical E2 digits. -/
theorem divisionTrajectory_digit_unique
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    (S : ℕ → GaussianInt) (D : ℕ → Digit)
    (h0 : S 0 = N)
    (hstep : ∀ n, digit (D n) * Q + beta * S (n + 1) = S n)
    (n : ℕ) :
    D n = divisionDigitAt Q N n := by
  have hn := divisionTrajectory_state_unique Q N hQ S D h0 hstep n
  have hs := hstep n
  rw [hn] at hs
  have hd := (divisionStep_unique Q (divisionIterate Q N n) hQ hs).1
  simpa [divisionDigitAt] using hd

end CNRSArithmetic
