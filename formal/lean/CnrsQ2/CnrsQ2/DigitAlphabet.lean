import CnrsQ2.Basic
import CNRSCore.Digits
namespace CnrsQ2
open Zsqrtd
abbrev phi : GaussianInt -> ZMod 5 := CNRSCore.phi
theorem phi_add (x y : GaussianInt) : phi (x+y)=phi x+phi y := CNRSCore.phi_add x y
theorem phi_mul (x y : GaussianInt) : phi (x*y)=phi x*phi y := CNRSCore.phi_mul x y
theorem phi_one : phi 1=1 := CNRSCore.phi_one
theorem phi_zero : phi 0=0 := CNRSCore.phi_zero
theorem phi_beta : phi beta=0 := CNRSCore.phi_beta
abbrev digit : Fin 5 -> GaussianInt := CNRSCore.digit
theorem digit_bijective : Function.Bijective (fun k : Fin 5 => phi (digit k)) := CNRSCore.digit_bijective
end CnrsQ2
