/-
Private-CI candidate bridge from the finite Gaussian CNS theorem to the
manuscript finite-support characterization of R_A = Z[i][beta^-1].

The governed CnrsQ2 v4 tree remains unchanged.  This module represents a
finite Laurent digit string by a finite least-significant-digit-first list and
a natural denominator shift m, i.e. beta^(-m) times a finite beta-polynomial.
-/
import CnrsQ2.GaussianCNS
import CnrsQ2.FieldLevel

open Zsqrtd

namespace CnrsQ2

/-- The ambient fraction field of the Gaussian integers. -/
abbrev GaussianFrac := FractionRing GaussianInt

/-- The image of beta in the Gaussian fraction field. -/
def betaFrac : GaussianFrac :=
  algebraMap GaussianInt GaussianFrac beta

/-- The localized ring R_A = Z[i][beta^-1], represented extensionally inside
    Frac(Z[i]) as Gaussian integers divided by a natural power of beta. -/
def RAFrac : Set GaussianFrac :=
  {x | ∃ z : GaussianInt, ∃ m : ℕ,
    x = algebraMap GaussianInt GaussianFrac z / betaFrac ^ m}

/-- Evaluate a finite Laurent digit string with denominator shift `m`.
    The list is least-significant-digit first, matching `evalGaussianDigits`. -/
noncomputable def evalFiniteLaurent (m : ℕ) (ds : List (Fin 5)) : GaussianFrac :=
  algebraMap GaussianInt GaussianFrac (evalGaussianDigits ds) / betaFrac ^ m

/-- Every finite Laurent digit string evaluates into R_A. -/
theorem evalFiniteLaurent_mem_RAFrac (m : ℕ) (ds : List (Fin 5)) :
    evalFiniteLaurent m ds ∈ RAFrac := by
  refine ⟨evalGaussianDigits ds, m, ?_⟩
  rfl

/-- Conversely, the finite Gaussian CNS theorem supplies a finite digit list
    for the Gaussian numerator of every element of R_A. -/
theorem mem_RAFrac_has_finite_digits {x : GaussianFrac} (hx : x ∈ RAFrac) :
    ∃ m : ℕ, ∃ ds : List (Fin 5), x = evalFiniteLaurent m ds := by
  rcases hx with ⟨z, m, hx⟩
  obtain ⟨ds, hds⟩ := gaussian_finite_expansion z
  refine ⟨m, ds, ?_⟩
  calc
    x = algebraMap GaussianInt GaussianFrac z / betaFrac ^ m := hx
    _ = algebraMap GaussianInt GaussianFrac (evalGaussianDigits ds) / betaFrac ^ m := by
      rw [hds]
    _ = evalFiniteLaurent m ds := rfl

/-- Values represented by finite Laurent digit strings. -/
def finiteSupportValues : Set GaussianFrac :=
  {x | ∃ m : ℕ, ∃ ds : List (Fin 5), x = evalFiniteLaurent m ds}

/-- **Finite-support capstone.** Finite Laurent CNRS digit strings represent
    exactly R_A = Z[i][beta^-1]. -/
theorem finiteSupportValues_eq_RAFrac : finiteSupportValues = RAFrac := by
  ext x
  constructor
  · rintro ⟨m, ds, rfl⟩
    exact evalFiniteLaurent_mem_RAFrac m ds
  · intro hx
    exact mem_RAFrac_has_finite_digits hx

end CnrsQ2
