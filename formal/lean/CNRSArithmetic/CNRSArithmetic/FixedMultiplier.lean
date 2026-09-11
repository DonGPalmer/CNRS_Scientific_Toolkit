/-
CNRSArithmetic Phase D: fixed multiplication by finite canonical CNRS-A words.

The core construction is finite convolution followed by the already-verified
Phase-C normalizer.  This module proves that the convolution coefficient string
has the product value and therefore that normalization returns a finite canonical
word representing the exact product.
-/
import CNRSArithmetic.Normalization

namespace CNRSArithmetic

open Zsqrtd

/-- Pointwise addition of finite coefficient strings, padding the shorter tail by zero. -/
def addCoeffLists : List GaussianInt → List GaussianInt → List GaussianInt
  | [], ys => ys
  | xs, [] => xs
  | x :: xs, y :: ys => (x + y) :: addCoeffLists xs ys

/-- Coefficient-string addition preserves represented value. -/
theorem coeffValue_addCoeffLists (xs ys : List GaussianInt) :
    coeffValue (addCoeffLists xs ys) = coeffValue xs + coeffValue ys := by
  induction xs generalizing ys with
  | nil => simp [addCoeffLists, coeffValue]
  | cons x xs ih =>
      cases ys with
      | nil => simp [addCoeffLists, coeffValue]
      | cons y ys =>
          simp [addCoeffLists, coeffValue, ih]
          ring

/-- Multiply every coefficient in a finite coefficient string by a fixed Gaussian integer. -/
def scaleCoeffList (a : GaussianInt) (cs : List GaussianInt) : List GaussianInt :=
  cs.map (fun c => a * c)

/-- Scaling a coefficient string scales its represented value. -/
theorem coeffValue_scaleCoeffList (a : GaussianInt) (cs : List GaussianInt) :
    coeffValue (scaleCoeffList a cs) = a * coeffValue cs := by
  induction cs with
  | nil => simp [scaleCoeffList, coeffValue]
  | cons c cs ih =>
      change a * c + beta * coeffValue (scaleCoeffList a cs) =
        a * (c + beta * coeffValue cs)
      rw [ih]
      ring

/-- One convolution row contributed by a single input digit. -/
def digitProductRow (d : Digit) (ys : List Digit) : List GaussianInt :=
  ys.map (fun e => digit d * digit e)

/-- A convolution row represents `digit d * wordValue ys`. -/
theorem coeffValue_digitProductRow (d : Digit) (ys : List Digit) :
    coeffValue (digitProductRow d ys) = digit d * wordValue ys := by
  induction ys with
  | nil => simp [digitProductRow, coeffValue, wordValue]
  | cons e es ih =>
      change digit d * digit e + beta * coeffValue (digitProductRow d es) =
        digit d * (digit e + beta * wordValue es)
      rw [ih]
      ring

/-- Finite schoolbook convolution of two LSD-first canonical digit words. -/
def convolutionCoefficients : List Digit → List Digit → List GaussianInt
  | [], _ => []
  | d :: ds, ys =>
      addCoeffLists (digitProductRow d ys) (0 :: convolutionCoefficients ds ys)

/-- The finite convolution coefficient string represents the exact product. -/
theorem coeffValue_convolutionCoefficients (xs ys : List Digit) :
    coeffValue (convolutionCoefficients xs ys) = wordValue xs * wordValue ys := by
  induction xs with
  | nil => simp [convolutionCoefficients, coeffValue, wordValue]
  | cons d ds ih =>
      simp [convolutionCoefficients, coeffValue_addCoeffLists,
        coeffValue_digitProductRow, coeffValue, wordValue, ih]
      ring

/-- Fixed multiplication: convolve with a fixed canonical multiplier, then normalize. -/
def fixedMultiply (multiplier input : List Digit) : List Digit :=
  normalizeCoefficients (convolutionCoefficients input multiplier)

/-- Phase D end-to-end correctness theorem for fixed multiplication. -/
theorem fixedMultiply_correct (multiplier input : List Digit) :
    wordValue (fixedMultiply multiplier input) =
      wordValue input * wordValue multiplier := by
  rw [fixedMultiply, normalizeCoefficients_correct,
    coeffValue_convolutionCoefficients]

/-- Equivalent orientation of the product, convenient when the fixed word is written first. -/
theorem fixedMultiply_correct_fixed_first (multiplier input : List Digit) :
    wordValue (fixedMultiply multiplier input) =
      wordValue multiplier * wordValue input := by
  rw [fixedMultiply_correct]
  ring

/-- Canonical digit one is the multiplicative unit in the Gaussian embedding. -/
@[simp] theorem digit_one : digit (1 : Digit) = (1 : GaussianInt) := by
  native_decide

/-- Multiplication by a canonical one-digit zero word represents zero. -/
theorem fixedMultiply_zero_value (input : List Digit) :
    wordValue (fixedMultiply [0] input) = 0 := by
  rw [fixedMultiply_correct_fixed_first]
  simp [wordValue]

/-- Multiplication by the canonical one-digit one word preserves represented value. -/
theorem fixedMultiply_one_value (input : List Digit) :
    wordValue (fixedMultiply [1] input) = wordValue input := by
  rw [fixedMultiply_correct_fixed_first]
  simp [wordValue]

/-- The raw convolution is symmetric at the level of represented value. -/
theorem convolutionCoefficients_value_comm (xs ys : List Digit) :
    coeffValue (convolutionCoefficients xs ys) =
      coeffValue (convolutionCoefficients ys xs) := by
  rw [coeffValue_convolutionCoefficients, coeffValue_convolutionCoefficients]
  ring

/-- Normalized multiplication is commutative at the represented-value level. -/
theorem fixedMultiply_value_comm (xs ys : List Digit) :
    wordValue (fixedMultiply xs ys) = wordValue (fixedMultiply ys xs) := by
  rw [fixedMultiply_correct_fixed_first, fixedMultiply_correct_fixed_first]
  ring

end CNRSArithmetic
