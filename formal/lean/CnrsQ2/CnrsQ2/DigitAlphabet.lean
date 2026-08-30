/-
CNRS Q2 formalization — Phase 2 (RECOVERED and ported, Session 116).
Original: Phase2_DigitAlphabet.lean, Session 115, found intact in Dropbox at
/_SSC/20_Program/80_Strategy/30_Lean4/ (uploaded Aug 18 13:34, before Session 116
began — the Session 116 "files lost" conclusion was wrong; see BC/FR correction).
Ported changes only: z0 → beta (Session 116 naming), import path updated.
Mathematical content unchanged: D = {0,1,2,3,4} is a complete residue system for
O_β/βO_β ≅ F_5 via φ(A+Bi) = (A+2B) mod 5 — thm:q2_digit_carrier(i).
-/
import CnrsQ2.Basic
import Mathlib.Data.ZMod.Basic

namespace CnrsQ2

open Zsqrtd

/-- The residue map φ : ℤ[i] → F₅, φ(A+Bi) = (A + 2B) mod 5.
    (Coefficient 2 because beta = -2+i, so i ≡ 2 mod beta.) -/
def phi (x : GaussianInt) : ZMod 5 := (x.re : ZMod 5) + 2 * (x.im : ZMod 5)

/-- φ is additive. -/
theorem phi_add (x y : GaussianInt) : phi (x + y) = phi x + phi y := by
  simp only [phi, Zsqrtd.re_add, Zsqrtd.im_add]
  push_cast
  ring

/-- φ is multiplicative. This is where the specific value beta = -2+i enters:
    re_mul carries a `d * x.im * y.im` term with d = -1 (GaussianInt = ℤ√(-1)),
    and closing this needs 2*2 ≡ -1 (mod 5), i.e. the defining fact N(beta) = 5. -/
theorem phi_mul (x y : GaussianInt) : phi (x * y) = phi x * phi y := by
  simp only [phi, Zsqrtd.re_mul, Zsqrtd.im_mul]
  push_cast
  have hneg : (-1 : ZMod 5) = 4 := by decide
  rw [hneg]
  ring

theorem phi_one : phi 1 = 1 := by simp [phi]

theorem phi_zero : phi 0 = 0 := by simp [phi]

/-- φ vanishes on beta (sanity check that φ is reduction mod beta). -/
theorem phi_beta : phi beta = 0 := by
  simp [phi, beta]

/-- The digit alphabet D = {0,1,2,3,4}, embedded in ℤ[i] as real integers. -/
def digit (k : Fin 5) : GaussianInt := ⟨(k : ℤ), 0⟩

/-- Milestone 2: D is a complete residue system — φ ∘ digit is a bijection
    Fin 5 ≃ ZMod 5. This is the formal content of thm:q2_digit_carrier(i). -/
theorem digit_bijective : Function.Bijective (fun k : Fin 5 => phi (digit k)) := by
  decide

end CnrsQ2
