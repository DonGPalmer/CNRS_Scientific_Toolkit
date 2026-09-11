/-
CNRSIntegration Phase E1: cross-project addition semantics.
This module is the first governed integration surface between
CNRSArithmetic and CnrsQ2. Neither downstream package depends on the other.
-/
import CNRSArithmetic.AdditionCorrectness
import CnrsQ2.FiniteSupportCarrierIntegration

open Zsqrtd

namespace CNRSIntegration

/-- CNRSArithmetic finite-state addition commutes with the Q2 finite Laurent evaluator. -/
theorem evalFiniteLaurent_addWords (xs ys : List (Fin 5)) :
    CnrsQ2.evalFiniteLaurent 0 (CNRSArithmetic.addWords xs ys) =
      CnrsQ2.evalFiniteLaurent 0 xs + CnrsQ2.evalFiniteLaurent 0 ys := by
  simp only [CnrsQ2.evalFiniteLaurent, pow_zero, div_one]
  change
    algebraMap GaussianInt CnrsQ2.GaussianFrac
        (CNRSArithmetic.wordValue (CNRSArithmetic.addWords xs ys)) =
      algebraMap GaussianInt CnrsQ2.GaussianFrac (CNRSArithmetic.wordValue xs) +
        algebraMap GaussianInt CnrsQ2.GaussianFrac (CNRSArithmetic.wordValue ys)
  rw [CNRSArithmetic.addWords_correct, map_add]

/-- The field-level 5-adic embedding preserves the E1 addition bridge. -/
theorem fracToPadic_evalFiniteLaurent_addWords (xs ys : List (Fin 5)) :
    CnrsQ2.fracToPadic
        (CnrsQ2.evalFiniteLaurent 0 (CNRSArithmetic.addWords xs ys)) =
      CnrsQ2.fracToPadic (CnrsQ2.evalFiniteLaurent 0 xs) +
        CnrsQ2.fracToPadic (CnrsQ2.evalFiniteLaurent 0 ys) := by
  rw [evalFiniteLaurent_addWords, map_add]

/-- A zero-shift finite-list carrier evaluates exactly as the Q2 field embedding
    of the corresponding zero-shift finite Laurent word. -/
theorem finiteLeftEval_finiteListCarrier_zero_eq_fracToPadic
    (ds : List (Fin 5)) :
    CnrsQ2.finiteLeftEval (CnrsQ2.finiteListCarrier 0 ds) =
      CnrsQ2.fracToPadic (CnrsQ2.evalFiniteLaurent 0 ds) := by
  rw [CnrsQ2.finiteLeftEval_finiteListCarrier]
  simp only [zpow_zero, one_mul, CnrsQ2.evalFiniteLaurent, pow_zero, div_one,
    CnrsQ2.fracToPadic_algebraMap]
  change
    (CnrsQ2.toPadic (CnrsQ2.evalGaussianDigits ds) : ℚ_[5]) =
      (CnrsQ2.toPadic (CnrsQ2.evalGaussianDigits ds) : ℚ_[5])
  rfl

/-- Finite-state addition therefore commutes with Q2 finite-left evaluation. -/
theorem finiteLeftEval_addWords (xs ys : List (Fin 5)) :
    CnrsQ2.finiteLeftEval
        (CnrsQ2.finiteListCarrier 0 (CNRSArithmetic.addWords xs ys)) =
      CnrsQ2.finiteLeftEval (CnrsQ2.finiteListCarrier 0 xs) +
        CnrsQ2.finiteLeftEval (CnrsQ2.finiteListCarrier 0 ys) := by
  rw [finiteLeftEval_finiteListCarrier_zero_eq_fracToPadic,
    finiteLeftEval_finiteListCarrier_zero_eq_fracToPadic,
    finiteLeftEval_finiteListCarrier_zero_eq_fracToPadic]
  exact fracToPadic_evalFiniteLaurent_addWords xs ys

/-- The finite-left result carrier produced by addition has finite support. -/
theorem addWords_finiteLeft_hasFiniteSupport (xs ys : List (Fin 5)) :
    CnrsQ2.FiniteLeftHasFiniteSupport
      (CnrsQ2.finiteListCarrier 0 (CNRSArithmetic.addWords xs ys)) :=
  CnrsQ2.finiteListCarrier_finiteSupport 0 _

end CNRSIntegration
