/-
CNRSCore v1 candidate: elementary LSD-first finite-word evaluation.
This module is intentionally independent of quotient machinery.
-/
import CNRSCore.Digits

namespace CNRSCore

open Zsqrtd

/-- Numeric value of an LSD-first canonical digit word. -/
def wordValue : List Digit → GaussianInt
  | [] => 0
  | d :: ds => digit d + beta * wordValue ds

@[simp] theorem wordValue_nil : wordValue [] = 0 := rfl

@[simp] theorem wordValue_cons (d : Digit) (ds : List Digit) :
    wordValue (d :: ds) = digit d + beta * wordValue ds := rfl

/-- Finite-word evaluation decomposes across concatenation. -/
theorem wordValue_append (xs ys : List Digit) :
    wordValue (xs ++ ys) = wordValue xs + beta ^ xs.length * wordValue ys := by
  induction xs with
  | nil => simp [wordValue]
  | cons d ds ih =>
      simp [wordValue, ih, pow_succ]
      ring

end CNRSCore
