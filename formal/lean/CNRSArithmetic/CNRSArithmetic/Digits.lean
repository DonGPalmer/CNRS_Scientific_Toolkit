/-
CNRSArithmetic compatibility adapter onto CNRSCore.Digits.
-/
import CNRSArithmetic.Base
import CNRSCore.Digits

namespace CNRSArithmetic

open Zsqrtd

abbrev Digit := CNRSCore.Digit
abbrev phi : GaussianInt → ZMod 5 := CNRSCore.phi

 theorem phi_add (x y : GaussianInt) : phi (x + y) = phi x + phi y := CNRSCore.phi_add x y
 theorem phi_mul (x y : GaussianInt) : phi (x * y) = phi x * phi y := CNRSCore.phi_mul x y
 theorem phi_one : phi 1 = 1 := CNRSCore.phi_one
 theorem phi_zero : phi 0 = 0 := CNRSCore.phi_zero
 theorem phi_beta : phi beta = 0 := CNRSCore.phi_beta

abbrev digit : Digit → GaussianInt := CNRSCore.digit

@[simp] theorem digit_re (k : Digit) : (digit k).re = (k : ℤ) := CNRSCore.digit_re k
@[simp] theorem digit_im (k : Digit) : (digit k).im = 0 := CNRSCore.digit_im k

theorem digit_bijective : Function.Bijective (fun k : Digit => phi (digit k)) :=
  CNRSCore.digit_bijective

end CNRSArithmetic
