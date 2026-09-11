/-
CNRSArithmetic Phase E4: division orbit repetition / eventual periodicity.

This module builds on the frozen E3 finite-orbit theorem. It proves that
every deterministic division trajectory repeats a state and therefore is
eventually periodic. For admissible divisors, this is interpreted as an
exact-division orbit statement via the frozen E2 recurrence.

It does not prove general termination, a termination/divisibility
characterization, or an online division transducer.
-/
import CNRSArithmetic.DivisionStateBounds
import Mathlib.Data.Fintype.Pigeonhole
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- Every deterministic E2/E3 division trajectory repeats some state. -/
theorem divisionOrbit_repeats (Q N : GaussianInt) :
    ∃ a b : ℕ, a < b ∧
      divisionIterate Q N a = divisionIterate Q N b := by
  let S : Set GaussianInt := Set.range (divisionIterate Q N)
  have hS : S.Finite := by
    simpa [S] using divisionOrbit_range_finite Q N
  let _ : Finite S := hS.to_subtype
  let f : ℕ → S := fun n =>
    ⟨divisionIterate Q N n, ⟨n, rfl⟩⟩
  obtain ⟨a, b, hab, hEq⟩ :=
    Finite.exists_ne_map_eq_of_infinite f
  have hstate :
      divisionIterate Q N a = divisionIterate Q N b := by
    exact congrArg Subtype.val hEq
  rcases lt_or_gt_of_ne hab with hablt | hbalt
  · exact ⟨a, b, hablt, hstate⟩
  · exact ⟨b, a, hbalt, hstate.symm⟩

/-- Equality of two trajectory states propagates forward by determinism. -/
theorem divisionIterate_eq_add_of_eq
    (Q N : GaussianInt) {a b : ℕ}
    (hEq : divisionIterate Q N a = divisionIterate Q N b) :
    ∀ k : ℕ,
      divisionIterate Q N (a + k) = divisionIterate Q N (b + k) := by
  intro k
  induction k with
  | zero => simpa using hEq
  | succ k ih =>
      rw [Nat.add_succ, Nat.add_succ,
        divisionIterate_succ, divisionIterate_succ]
      exact congrArg (divisionNext Q) ih

/-- Every deterministic division orbit is eventually periodic with a
    strictly positive period. -/
theorem divisionOrbit_eventually_periodic (Q N : GaussianInt) :
    ∃ start period : ℕ, 0 < period ∧
      ∀ k : ℕ,
        divisionIterate Q N (start + k + period) =
          divisionIterate Q N (start + k) := by
  obtain ⟨a, b, hab, hEq⟩ := divisionOrbit_repeats Q N
  refine ⟨a, b - a, Nat.sub_pos_of_lt hab, ?_⟩
  intro k
  have hprop := divisionIterate_eq_add_of_eq Q N hEq k
  have hidx : a + k + (b - a) = b + k := by omega
  rw [hidx]
  exact hprop.symm

/-- The eventual-periodicity theorem specialized to exact division:
    admissibility supplies the E2 exact-division interpretation. -/
theorem admissible_divisionOrbit_eventually_periodic
    (Q N : GaussianInt) (_hQ : DivisionAdmissible Q) :
    ∃ start period : ℕ, 0 < period ∧
      ∀ k : ℕ,
        divisionIterate Q N (start + k + period) =
          divisionIterate Q N (start + k) :=
  divisionOrbit_eventually_periodic Q N

/-- Every deterministic orbit either reaches zero, or it has an eventual
    positive-period tail whose states are all nonzero. This is a
    termination-or-cycle dichotomy, not a proof that termination occurs. -/
theorem divisionOrbit_zero_or_eventually_periodic_nonzero
    (Q N : GaussianInt) :
    (∃ n : ℕ, divisionIterate Q N n = 0) ∨
      ∃ start period : ℕ, 0 < period ∧
        (∀ k : ℕ,
          divisionIterate Q N (start + k + period) =
            divisionIterate Q N (start + k)) ∧
        (∀ k : ℕ, divisionIterate Q N (start + k) ≠ 0) := by
  by_cases hz : ∃ n : ℕ, divisionIterate Q N n = 0
  · exact Or.inl hz
  · right
    obtain ⟨start, period, hp, hper⟩ :=
      divisionOrbit_eventually_periodic Q N
    refine ⟨start, period, hp, hper, ?_⟩
    intro k hk
    exact hz ⟨start + k, hk⟩

end CNRSArithmetic
