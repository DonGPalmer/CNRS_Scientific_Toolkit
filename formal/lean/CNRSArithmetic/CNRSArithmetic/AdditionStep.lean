/-
CNRSArithmetic Phase B compatibility layer over the neutral CNRSCore quotient step.
-/
import CNRSArithmetic.Digits
import CNRSCore.QuotientStep
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-- The unnormalised one-column sum a+b+kappa. -/
def stepSum (κ : GaussianInt) (a b : Digit) : GaussianInt :=
  digit a + digit b + κ

abbrev residueIndex : GaussianInt → Digit := CNRSCore.residueIndex

/-- Historical Arithmetic spelling of the canonical selected digit. -/
def selectedDigit (x : GaussianInt) : GaussianInt :=
  digit (residueIndex x)

@[simp] theorem selectedDigit_re (x : GaussianInt) :
    (selectedDigit x).re = ((residueIndex x : ℕ) : ℤ) := rfl

@[simp] theorem selectedDigit_im (x : GaussianInt) :
    (selectedDigit x).im = 0 := rfl

theorem residueIndex_cast (x : GaussianInt) :
    ((residueIndex x : ℕ) : ZMod 5) = phi x := CNRSCore.residueIndex_cast x

theorem phi_selectedDigit (x : GaussianInt) : phi (selectedDigit x) = phi x := by
  simpa [selectedDigit, CNRSCore.selectedDigit] using CNRSCore.phi_selectedDigit x

abbrev carryNumerator : GaussianInt → ℤ := CNRSCore.quotientNumerator

theorem five_dvd_carryNumerator (x : GaussianInt) :
    (5 : ℤ) ∣ carryNumerator x := CNRSCore.five_dvd_quotientNumerator x

abbrev carryQuotient : GaussianInt → ℤ := CNRSCore.quotientScalar

theorem five_mul_carryQuotient (x : GaussianInt) :
    (5 : ℤ) * carryQuotient x = carryNumerator x := CNRSCore.five_mul_quotientScalar x

abbrev nextCarryFromSum : GaussianInt → GaussianInt := CNRSCore.nextQuotient

theorem selectedDigit_add_beta_mul_nextCarry (x : GaussianInt) :
    selectedDigit x + beta * nextCarryFromSum x = x := by
  simpa [selectedDigit, CNRSCore.selectedDigit] using
    CNRSCore.selectedDigit_add_beta_mul_nextQuotient x

/-- One deterministic CNRS-A addition transition. -/
structure AdditionStepResult where
  output : Digit
  carry : GaussianInt
  deriving DecidableEq

/-- Read one digit from each input and advance the Gaussian carry. -/
def addStep (κ : GaussianInt) (a b : Digit) : AdditionStepResult :=
  let s := stepSum κ a b
  { output := residueIndex s
    carry := nextCarryFromSum s }

/-- Fundamental one-step arithmetic invariant. -/
theorem addStep_equation (κ : GaussianInt) (a b : Digit) :
    digit (addStep κ a b).output + beta * (addStep κ a b).carry =
      digit a + digit b + κ := by
  simpa [addStep, stepSum, selectedDigit] using
    selectedDigit_add_beta_mul_nextCarry (stepSum κ a b)

end CNRSArithmetic
