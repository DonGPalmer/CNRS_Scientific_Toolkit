/-
CNRSCore v1 candidate: canonical digit alphabet and residue map.
-/
import CNRSCore.Base
import Mathlib.Data.ZMod.Basic

namespace CNRSCore

open Zsqrtd

/-- Canonical CNRS digit type. -/
abbrev Digit := Fin 5

/-- Residue map phi : Z[i] -> F_5, phi(A+Bi) = A + 2B mod 5. -/
def phi (x : GaussianInt) : ZMod 5 := (x.re : ZMod 5) + 2 * (x.im : ZMod 5)

/-- phi is additive. -/
theorem phi_add (x y : GaussianInt) : phi (x + y) = phi x + phi y := by
  simp only [phi, Zsqrtd.re_add, Zsqrtd.im_add]
  push_cast
  ring

/-- phi is multiplicative. -/
theorem phi_mul (x y : GaussianInt) : phi (x * y) = phi x * phi y := by
  simp only [phi, Zsqrtd.re_mul, Zsqrtd.im_mul]
  push_cast
  have hneg : (-1 : ZMod 5) = 4 := by decide
  rw [hneg]
  ring

theorem phi_one : phi 1 = 1 := by simp [phi]

theorem phi_zero : phi 0 = 0 := by simp [phi]

/-- beta reduces to zero under phi. -/
theorem phi_beta : phi beta = 0 := by
  simp [phi, beta]

/-- The canonical digit alphabet D = {0,1,2,3,4}. -/
def digit (k : Digit) : GaussianInt := ⟨(k : ℤ), 0⟩

@[simp] theorem digit_re (k : Digit) : (digit k).re = (k : ℤ) := rfl
@[simp] theorem digit_im (k : Digit) : (digit k).im = 0 := rfl
@[simp] theorem digit_zero : digit (0 : Digit) = (0 : GaussianInt) := by
  ext <;> simp

/-- The five canonical digits form a complete residue system modulo beta. -/
theorem digit_bijective : Function.Bijective (fun k : Digit => phi (digit k)) := by
  decide

end CNRSCore
