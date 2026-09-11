/-
CNRSCore v1 candidate: constructive finite canonical expansion for beta = -2+i.
This proof depends only on the shared finite-word and quotient-step primitives.
It uses max-coordinate height and strict descent after three greedy quotient steps.
-/
import CNRSCore.FiniteWords
import CNRSCore.QuotientStep
import Mathlib.Data.Int.Order.Lemmas
import Mathlib.Tactic

namespace CNRSCore

open Zsqrtd

/-- Max-coordinate height on Gaussian integers. -/
def gaussianHeight (x : GaussianInt) : ℕ :=
  max x.re.natAbs x.im.natAbs

@[simp] theorem gaussianHeight_zero : gaussianHeight (0 : GaussianInt) = 0 := by
  rfl

/-- Two and three successive greedy quotient steps. -/
def nextQuotient2 (x : GaussianInt) : GaussianInt :=
  nextQuotient (nextQuotient x)

def nextQuotient3 (x : GaussianInt) : GaussianInt :=
  nextQuotient (nextQuotient2 x)

/-- One-step coordinate identity for the real part of the greedy quotient. -/
theorem five_mul_nextQuotient_re (x : GaussianInt) :
    (5 : ℤ) * (nextQuotient x).re =
      x.im - 2 * x.re + 2 * ((residueIndex x : ℕ) : ℤ) := by
  have ht := five_mul_quotientScalar x
  change (5 : ℤ) * (x.im - 2 * quotientScalar x) = _
  dsimp [quotientNumerator] at ht
  linarith

/-- One-step coordinate identity for the imaginary part of the greedy quotient. -/
theorem five_mul_nextQuotient_im (x : GaussianInt) :
    (5 : ℤ) * (nextQuotient x).im =
      -x.re - 2 * x.im + ((residueIndex x : ℕ) : ℤ) := by
  have ht := five_mul_quotientScalar x
  change (5 : ℤ) * (-quotientScalar x) = _
  dsimp [quotientNumerator] at ht
  linarith

/-- Every selected residue index is at most four. -/
theorem residueIndex_le_four (x : GaussianInt) : (residueIndex x : ℕ) ≤ 4 := by
  have h := (residueIndex x).isLt
  omega

/-- A coarse but uniform one-step height estimate. -/
theorem nextQuotient_height_bound (x : GaussianInt) :
    5 * gaussianHeight (nextQuotient x) ≤ 3 * gaussianHeight x + 8 := by
  have hr : (residueIndex x : ℕ) ≤ 4 := residueIndex_le_four x
  have hxre : x.re.natAbs ≤ gaussianHeight x := Nat.le_max_left _ _
  have hxim : x.im.natAbs ≤ gaussianHeight x := Nat.le_max_right _ _

  have hqre : 5 * (nextQuotient x).re.natAbs ≤ 3 * gaussianHeight x + 8 := by
    calc
      5 * (nextQuotient x).re.natAbs =
          ((5 : ℤ) * (nextQuotient x).re).natAbs := by
            simp [Int.natAbs_mul]
      _ = (x.im - 2 * x.re + 2 * ((residueIndex x : ℕ) : ℤ)).natAbs := by
            rw [five_mul_nextQuotient_re]
      _ ≤ (x.im - 2 * x.re).natAbs +
            (2 * ((residueIndex x : ℕ) : ℤ)).natAbs := by
            exact Int.natAbs_add_le _ _
      _ ≤ (x.im.natAbs + (2 * x.re).natAbs) +
            (2 * ((residueIndex x : ℕ) : ℤ)).natAbs := by
            exact Nat.add_le_add_right (Int.natAbs_sub_le _ _) _
      _ = x.im.natAbs + 2 * x.re.natAbs + 2 * (residueIndex x : ℕ) := by
            simp [Int.natAbs_mul]
      _ ≤ 3 * gaussianHeight x + 8 := by
            omega

  have hqim : 5 * (nextQuotient x).im.natAbs ≤ 3 * gaussianHeight x + 8 := by
    calc
      5 * (nextQuotient x).im.natAbs =
          ((5 : ℤ) * (nextQuotient x).im).natAbs := by
            simp [Int.natAbs_mul]
      _ = (-x.re - 2 * x.im + ((residueIndex x : ℕ) : ℤ)).natAbs := by
            rw [five_mul_nextQuotient_im]
      _ ≤ (-x.re - 2 * x.im).natAbs +
            (((residueIndex x : ℕ) : ℤ)).natAbs := by
            exact Int.natAbs_add_le _ _
      _ ≤ ((-x.re).natAbs + (2 * x.im).natAbs) +
            (((residueIndex x : ℕ) : ℤ)).natAbs := by
            exact Nat.add_le_add_right (Int.natAbs_sub_le _ _) _
      _ = x.re.natAbs + 2 * x.im.natAbs + (residueIndex x : ℕ) := by
            simp [Int.natAbs_mul]
      _ ≤ 3 * gaussianHeight x + 8 := by
            omega

  unfold gaussianHeight
  by_cases hle : (nextQuotient x).re.natAbs ≤ (nextQuotient x).im.natAbs
  · rw [max_eq_right hle]
    exact hqim
  · have hge : (nextQuotient x).im.natAbs ≤ (nextQuotient x).re.natAbs := by
      omega
    rw [max_eq_left hge]
    exact hqre

/-- Three greedy quotient steps strictly decrease max-coordinate height. -/
theorem nextQuotient3_height_lt (x : GaussianInt) (hx : x ≠ 0) :
    gaussianHeight (nextQuotient3 x) < gaussianHeight x := by
  by_cases hs : gaussianHeight x ≤ 4
  · rcases x with ⟨a, b⟩
    have hab : a ≠ 0 ∨ b ≠ 0 := by
      by_contra h
      push Not at h
      rcases h with ⟨ha0, hb0⟩
      subst a
      subst b
      exact hx rfl
    change max a.natAbs b.natAbs ≤ 4 at hs
    have ha : a.natAbs ≤ 4 := le_trans (Nat.le_max_left _ _) hs
    have hb : b.natAbs ≤ 4 := le_trans (Nat.le_max_right _ _) hs
    have ha2 : a * a ≤ (4 : ℤ) * 4 := by
      apply (Int.natAbs_le_iff_mul_self_le).mp
      simpa using ha
    have hb2 : b * b ≤ (4 : ℤ) * 4 := by
      apply (Int.natAbs_le_iff_mul_self_le).mp
      simpa using hb
    have hal : (-4 : ℤ) ≤ a := by nlinarith
    have hau : a ≤ (4 : ℤ) := by nlinarith
    have hbl : (-4 : ℤ) ≤ b := by nlinarith
    have hbu : b ≤ (4 : ℤ) := by nlinarith
    change gaussianHeight (nextQuotient3 ⟨a, b⟩) < max a.natAbs b.natAbs
    interval_cases a <;> interval_cases b <;> simp_all <;> native_decide
  · have h0 : 5 ≤ gaussianHeight x := by omega
    have h1 := nextQuotient_height_bound x
    have h2 := nextQuotient_height_bound (nextQuotient x)
    have h3 := nextQuotient_height_bound (nextQuotient2 x)
    change gaussianHeight (nextQuotient (nextQuotient2 x)) < gaussianHeight x
    change 5 * gaussianHeight (nextQuotient (nextQuotient2 x)) ≤
      3 * gaussianHeight (nextQuotient2 x) + 8 at h3
    change 5 * gaussianHeight (nextQuotient2 x) ≤
      3 * gaussianHeight (nextQuotient x) + 8 at h2
    omega

/-- One greedy digit step reconstructs the original Gaussian integer. -/
theorem oneStep_reconstruct (x : GaussianInt) :
    digit (residueIndex x) + beta * nextQuotient x = x := by
  simpa [selectedDigit] using selectedDigit_add_beta_mul_nextQuotient x

/-- Two greedy digit steps reconstruct the original Gaussian integer. -/
theorem twoStep_reconstruct (x : GaussianInt) :
    digit (residueIndex x) +
        beta * (digit (residueIndex (nextQuotient x)) + beta * nextQuotient2 x) = x := by
  have h0 := oneStep_reconstruct x
  have h1 := oneStep_reconstruct (nextQuotient x)
  have h1' :
      digit (residueIndex (nextQuotient x)) + beta * nextQuotient2 x =
        nextQuotient x := by
    simpa [nextQuotient2] using h1
  rw [h1', h0]

/-- Three greedy digit steps reconstruct the original Gaussian integer. -/
theorem threeStep_reconstruct (x : GaussianInt) :
    digit (residueIndex x) +
      beta * (digit (residueIndex (nextQuotient x)) +
        beta * (digit (residueIndex (nextQuotient2 x)) + beta * nextQuotient3 x)) = x := by
  have h0 := oneStep_reconstruct x
  have h1 := oneStep_reconstruct (nextQuotient x)
  have h2 := oneStep_reconstruct (nextQuotient2 x)
  have h1' :
      digit (residueIndex (nextQuotient x)) + beta * nextQuotient2 x =
        nextQuotient x := by
    simpa [nextQuotient2] using h1
  have h2' :
      digit (residueIndex (nextQuotient2 x)) + beta * nextQuotient3 x = nextQuotient2 x := by
    simpa [nextQuotient3] using h2
  rw [h2', h1', h0]

/-- Terminal one-step branch of the greedy expansion. -/
theorem oneStep_terminal (x : GaussianInt) (h : nextQuotient x = 0) :
    digit (residueIndex x) = x := by
  have hx := oneStep_reconstruct x
  rw [h, mul_zero, add_zero] at hx
  exact hx

/-- Terminal two-step branch of the greedy expansion. -/
theorem twoStep_terminal (x : GaussianInt) (h : nextQuotient2 x = 0) :
    digit (residueIndex x) + beta * digit (residueIndex (nextQuotient x)) = x := by
  have hx := twoStep_reconstruct x
  rw [h, mul_zero, add_zero] at hx
  exact hx

/-- Constructive finite greedy expansion of any Gaussian integer. -/
def greedyDigits (x : GaussianInt) : List Digit :=
  if hx : x = 0 then []
  else if h1 : nextQuotient x = 0 then
    [residueIndex x]
  else if h2 : nextQuotient2 x = 0 then
    [residueIndex x, residueIndex (nextQuotient x)]
  else
    residueIndex x ::
      residueIndex (nextQuotient x) ::
      residueIndex (nextQuotient2 x) ::
      greedyDigits (nextQuotient3 x)
termination_by gaussianHeight x
decreasing_by
  exact nextQuotient3_height_lt x hx

/-- The constructive greedy expansion represents exactly its input. -/
theorem greedyDigits_correct (x : GaussianInt) : wordValue (greedyDigits x) = x := by
  fun_induction greedyDigits x <;>
    simp_all [wordValue, oneStep_terminal, twoStep_terminal, threeStep_reconstruct]

/-- Shared finite-Gaussian CNS capstone. -/
theorem finiteExpansion (x : GaussianInt) :
    ∃ ds : List Digit, wordValue ds = x := by
  exact ⟨greedyDigits x, greedyDigits_correct x⟩

end CNRSCore
