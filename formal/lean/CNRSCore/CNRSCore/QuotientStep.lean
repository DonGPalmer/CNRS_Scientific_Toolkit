/-
CNRSCore v1 candidate: universal canonical digit / exact beta-quotient step.
Neutral quotient terminology is used here; downstream arithmetic may provide carry aliases.
-/
import CNRSCore.Digits
import Mathlib.Tactic

namespace CNRSCore

open Zsqrtd

/-- The unique canonical digit index representing the residue of x modulo beta. -/
def residueIndex (x : GaussianInt) : Digit :=
  ⟨(phi x).val, ZMod.val_lt (phi x)⟩

/-- The canonical Gaussian digit selected from x. -/
def selectedDigit (x : GaussianInt) : GaussianInt :=
  digit (residueIndex x)

@[simp] theorem selectedDigit_re (x : GaussianInt) :
    (selectedDigit x).re = ((residueIndex x : ℕ) : ℤ) := rfl

@[simp] theorem selectedDigit_im (x : GaussianInt) :
    (selectedDigit x).im = 0 := rfl

/-- Casting the selected residue index back to ZMod 5 recovers phi x. -/
theorem residueIndex_cast (x : GaussianInt) :
    ((residueIndex x : ℕ) : ZMod 5) = phi x := by
  change ((phi x).val : ZMod 5) = phi x
  exact ZMod.natCast_zmod_val (phi x)

/-- The selected canonical digit has the same beta-residue as x. -/
theorem phi_selectedDigit (x : GaussianInt) : phi (selectedDigit x) = phi x := by
  simp [selectedDigit, digit, phi, residueIndex]

/-- Integer numerator used for exact division of x-selectedDigit(x) by beta. -/
def quotientNumerator (x : GaussianInt) : ℤ :=
  x.re + 2 * x.im - ((residueIndex x : ℕ) : ℤ)

/-- The quotient numerator is divisible by 5. -/
theorem five_dvd_quotientNumerator (x : GaussianInt) :
    (5 : ℤ) ∣ quotientNumerator x := by
  apply (ZMod.intCast_zmod_eq_zero_iff_dvd (quotientNumerator x) 5).mp
  simp only [quotientNumerator, Int.cast_sub, Int.cast_add, Int.cast_mul,
    Int.cast_ofNat, Int.cast_natCast]
  rw [residueIndex_cast]
  simp [phi]

/-- Exact scalar t=(Re x+2 Im x-r)/5. -/
def quotientScalar (x : GaussianInt) : ℤ := quotientNumerator x / 5

theorem five_mul_quotientScalar (x : GaussianInt) :
    (5 : ℤ) * quotientScalar x = quotientNumerator x := by
  exact Int.mul_ediv_cancel' (five_dvd_quotientNumerator x)

/-- Exact Gaussian quotient (x-selectedDigit(x))/beta. -/
def quotientByBeta (x : GaussianInt) : GaussianInt :=
  let t := quotientScalar x
  ⟨x.im - 2 * t, -t⟩

/-- Neutral name for the next quotient in the greedy canonical recurrence. -/
abbrev nextQuotient := quotientByBeta

/-- The selected digit and exact beta quotient reconstruct x. -/
theorem selectedDigit_add_beta_mul_nextQuotient (x : GaussianInt) :
    selectedDigit x + beta * nextQuotient x = x := by
  have ht := five_mul_quotientScalar x
  ext
  · simp only [selectedDigit_re, beta_re, beta_im, nextQuotient, quotientByBeta,
      Zsqrtd.re_add, Zsqrtd.re_mul]
    dsimp [quotientScalar, quotientNumerator] at ht ⊢
    linarith
  · simp only [selectedDigit_im, beta_re, beta_im, nextQuotient, quotientByBeta,
      Zsqrtd.im_add, Zsqrtd.im_mul]
    ring

end CNRSCore
