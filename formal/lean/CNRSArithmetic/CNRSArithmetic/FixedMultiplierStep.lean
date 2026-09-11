/-
CNRSArithmetic Phase D: generic one-column recurrence for multiplication by a
fixed Gaussian integer.

For fixed c, state kappa and input digit a, select the canonical residue digit
of kappa + c*a and divide the remainder exactly by beta.  This is the direct
LSD-first recurrence used by the fixed-multiplier transducer.
-/
import CNRSArithmetic.AdditionStep

namespace CNRSArithmetic

open Zsqrtd

/-- Unnormalised one-column value for multiplication by a fixed Gaussian c. -/
def fixedMultiplierStepSum (c κ : GaussianInt) (a : Digit) : GaussianInt :=
  κ + c * digit a

/-- Output digit and next Gaussian carry for one fixed-multiplier column. -/
structure FixedMultiplierStepResult where
  output : Digit
  carry : GaussianInt
  deriving DecidableEq

/-- Deterministic one-column fixed-multiplier transition. -/
def fixedMultiplierStep (c κ : GaussianInt) (a : Digit) :
    FixedMultiplierStepResult :=
  let s := fixedMultiplierStepSum c κ a
  { output := residueIndex s
    carry := nextCarryFromSum s }

/-- Fundamental one-column invariant for fixed multiplication. -/
theorem fixedMultiplierStep_equation (c κ : GaussianInt) (a : Digit) :
    digit (fixedMultiplierStep c κ a).output +
        beta * (fixedMultiplierStep c κ a).carry =
      κ + c * digit a := by
  simpa [fixedMultiplierStep, fixedMultiplierStepSum, selectedDigit] using
    selectedDigit_add_beta_mul_nextCarry (fixedMultiplierStepSum c κ a)

/-- The emitted digit is exactly the residue of the current multiplication column. -/
theorem phi_fixedMultiplierStep_output (c κ : GaussianInt) (a : Digit) :
    phi (digit (fixedMultiplierStep c κ a).output) =
      phi (κ + c * digit a) := by
  simpa [fixedMultiplierStep, fixedMultiplierStepSum, selectedDigit] using
    phi_selectedDigit (fixedMultiplierStepSum c κ a)

end CNRSArithmetic
