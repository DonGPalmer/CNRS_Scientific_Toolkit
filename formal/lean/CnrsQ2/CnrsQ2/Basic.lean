/-
CNRS Q2 formalization — Phase 1: the base β = -2+i in ℤ[i], primality via norm.
Rebuilt Session 116 (August 18, 2026); prior session's files were not uploaded.
-/
import Mathlib.NumberTheory.Zsqrtd.GaussianInt

open Zsqrtd

namespace CnrsQ2

/-- The CNRS base β = -2 + i as a Gaussian integer. -/
def beta : GaussianInt := ⟨-2, 1⟩

@[simp] lemma beta_re : beta.re = -2 := rfl
@[simp] lemma beta_im : beta.im = 1 := rfl

/-- The norm of β is 5. -/
lemma norm_beta : beta.norm = 5 := by
  simp [Zsqrtd.norm, beta]

/-- natAbs of the norm of β is 5. -/
lemma natAbs_norm_beta : beta.norm.natAbs = 5 := by
  rw [norm_beta]; rfl

/-- Any Gaussian integer whose norm has prime absolute value is irreducible. -/
lemma irreducible_of_natAbs_norm_prime {z : GaussianInt}
    (hz : Nat.Prime z.norm.natAbs) : Irreducible z := by
  constructor
  · intro hu
    have h1 : z.norm.natAbs = 1 := Zsqrtd.norm_eq_one_iff.mpr hu
    rw [h1] at hz
    exact Nat.not_prime_one hz
  · intro a b hab
    have hnorm : z.norm.natAbs = a.norm.natAbs * b.norm.natAbs := by
      rw [hab, Zsqrtd.norm_mul, Int.natAbs_mul]
    rcases (Nat.Prime.eq_one_or_self_of_dvd hz a.norm.natAbs
      ⟨b.norm.natAbs, hnorm⟩) with h | h
    · exact Or.inl (Zsqrtd.norm_eq_one_iff.mp h)
    · right
      apply Zsqrtd.norm_eq_one_iff.mp
      have hb : z.norm.natAbs * b.norm.natAbs = z.norm.natAbs * 1 := by
        rw [mul_one]
        calc z.norm.natAbs * b.norm.natAbs
            = a.norm.natAbs * b.norm.natAbs := by rw [h]
          _ = z.norm.natAbs := hnorm.symm
      exact Nat.eq_of_mul_eq_mul_left hz.pos hb

/-- β is prime in ℤ[i]. -/
lemma prime_beta : Prime beta := by
  have h : Nat.Prime beta.norm.natAbs := by
    rw [natAbs_norm_beta]; exact Nat.prime_five
  exact (irreducible_of_natAbs_norm_prime h).prime

end CnrsQ2
