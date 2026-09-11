/-
CNRSArithmetic Phase C compatibility layer over CNRSCore constructive finiteness.
The independent proof now lives in the shared finite core; Arithmetic preserves its
historical public names as reducible aliases and theorem adapters.
-/
import CNRSArithmetic.AdditionCorrectness
import CNRSCore.Finiteness

namespace CNRSArithmetic

open Zsqrtd

abbrev gaussianHeight : GaussianInt → ℕ := CNRSCore.gaussianHeight

@[simp] theorem gaussianHeight_zero : gaussianHeight (0 : GaussianInt) = 0 :=
  CNRSCore.gaussianHeight_zero

abbrev nextCarry2 : GaussianInt → GaussianInt := CNRSCore.nextQuotient2
abbrev nextCarry3 : GaussianInt → GaussianInt := CNRSCore.nextQuotient3

theorem five_mul_nextCarry_re (x : GaussianInt) :
    (5 : ℤ) * (nextCarryFromSum x).re =
      x.im - 2 * x.re + 2 * ((residueIndex x : ℕ) : ℤ) :=
  CNRSCore.five_mul_nextQuotient_re x

theorem five_mul_nextCarry_im (x : GaussianInt) :
    (5 : ℤ) * (nextCarryFromSum x).im =
      -x.re - 2 * x.im + ((residueIndex x : ℕ) : ℤ) :=
  CNRSCore.five_mul_nextQuotient_im x

theorem residueIndex_le_four (x : GaussianInt) : (residueIndex x : ℕ) ≤ 4 :=
  CNRSCore.residueIndex_le_four x

theorem nextCarry_height_bound (x : GaussianInt) :
    5 * gaussianHeight (nextCarryFromSum x) ≤ 3 * gaussianHeight x + 8 :=
  CNRSCore.nextQuotient_height_bound x

theorem nextCarry3_height_lt (x : GaussianInt) (hx : x ≠ 0) :
    gaussianHeight (nextCarry3 x) < gaussianHeight x :=
  CNRSCore.nextQuotient3_height_lt x hx

theorem oneStep_reconstruct (x : GaussianInt) :
    digit (residueIndex x) + beta * nextCarryFromSum x = x :=
  CNRSCore.oneStep_reconstruct x

theorem twoStep_reconstruct (x : GaussianInt) :
    digit (residueIndex x) +
        beta * (digit (residueIndex (nextCarryFromSum x)) + beta * nextCarry2 x) = x :=
  CNRSCore.twoStep_reconstruct x

theorem threeStep_reconstruct (x : GaussianInt) :
    digit (residueIndex x) +
      beta * (digit (residueIndex (nextCarryFromSum x)) +
        beta * (digit (residueIndex (nextCarry2 x)) + beta * nextCarry3 x)) = x :=
  CNRSCore.threeStep_reconstruct x

theorem oneStep_terminal (x : GaussianInt) (h : nextCarryFromSum x = 0) :
    digit (residueIndex x) = x :=
  CNRSCore.oneStep_terminal x h

theorem twoStep_terminal (x : GaussianInt) (h : nextCarry2 x = 0) :
    digit (residueIndex x) + beta * digit (residueIndex (nextCarryFromSum x)) = x :=
  CNRSCore.twoStep_terminal x h

abbrev greedyDigits : GaussianInt → List Digit := CNRSCore.greedyDigits

theorem greedyDigits_correct (x : GaussianInt) : wordValue (greedyDigits x) = x :=
  CNRSCore.greedyDigits_correct x

theorem finiteness_property_constructive (x : GaussianInt) :
    ∃ ds : List Digit, wordValue ds = x :=
  CNRSCore.finiteExpansion x

end CNRSArithmetic
