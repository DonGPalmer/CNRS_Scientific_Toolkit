/-
CNRSArithmetic Phase E5 candidate: exact-division termination criterion.

This module proves that, for an admissible divisor Q, the deterministic
E2 division orbit reaches zero exactly when Q divides the initial Gaussian
numerator.  Combined with E4, nondivisibility therefore selects the nonzero
eventually-periodic branch of the orbit dichotomy.
-/
import CNRSArithmetic.DivisionOrbitPeriodicity
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- A finite LSD-first digit word reconstructs one suffix from its current
    digit and the following suffix. The default digit is zero after the word
    has been exhausted. -/
theorem wordValue_drop_step (ds : List Digit) (n : ℕ) :
    CNRSCore.wordValue (ds.drop n) =
      digit (ds.getD n 0) + beta * CNRSCore.wordValue (ds.drop (n + 1)) := by
  induction ds generalizing n with
  | nil => simp
  | cons d ds ih =>
      cases n with
      | zero => simp
      | succ n => simpa [CNRSCore.wordValue, Nat.succ_eq_add_one] using ih n

/-- If an admissible divisor divides the numerator, its deterministic exact
    division orbit reaches zero after finitely many quotient digits. -/
theorem divisionIterate_terminates_of_dvd
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    (hdiv : Q ∣ N) :
    ∃ n : ℕ, divisionIterate Q N n = 0 := by
  rcases hdiv with ⟨M, hM⟩
  obtain ⟨ds, hds⟩ := CNRSCore.finiteExpansion M
  let S : ℕ → GaussianInt := fun n => Q * CNRSCore.wordValue (ds.drop n)
  let D : ℕ → Digit := fun n => ds.getD n 0
  have h0 : S 0 = N := by
    simp [S, hds, hM]
  have hstep : ∀ n, digit (D n) * Q + beta * S (n + 1) = S n := by
    intro n
    dsimp [S, D]
    rw [wordValue_drop_step ds n]
    ring
  have huniq := divisionTrajectory_state_unique Q N hQ S D h0 hstep
  refine ⟨ds.length, ?_⟩
  rw [← huniq ds.length]
  simp [S]

/-- Exact termination criterion for the deterministic E2 recurrence. -/
theorem divisionOrbit_terminates_iff_dvd
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q) :
    (∃ n : ℕ, divisionIterate Q N n = 0) ↔ Q ∣ N := by
  constructor
  · rintro ⟨n, hn⟩
    refine ⟨divisionPrefixValue Q N n, ?_⟩
    exact (divisionIterate_eq_zero_implies_exact Q N hQ n hn).symm
  · exact divisionIterate_terminates_of_dvd Q N hQ

/-- For an admissible divisor and a nondivisible numerator, E4's alternative
    is necessarily a nonzero eventually-periodic tail. -/
theorem not_dvd_implies_eventually_periodic_nonzero
    (Q N : GaussianInt) (hQ : DivisionAdmissible Q)
    (hndiv : ¬ Q ∣ N) :
    ∃ start period : ℕ, 0 < period ∧
      (∀ k : ℕ,
        divisionIterate Q N (start + k + period) =
          divisionIterate Q N (start + k)) ∧
      (∀ k : ℕ, divisionIterate Q N (start + k) ≠ 0) := by
  rcases divisionOrbit_zero_or_eventually_periodic_nonzero Q N with hz | hcycle
  · exact False.elim (hndiv ((divisionOrbit_terminates_iff_dvd Q N hQ).1 hz))
  · exact hcycle

end CNRSArithmetic

