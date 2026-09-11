/-
CNRSArithmetic Phase B: stream invariant, finite drain, and finite-support correctness.
Migrated onto the shared CNRSCore finite-word evaluator.
-/
import CNRSArithmetic.AdditionTransducer
import CNRSCore.FiniteWords

namespace CNRSArithmetic

/-- The canonical digit zero is the Gaussian integer zero. -/
@[simp] theorem digit_zero : digit (0 : Digit) = (0 : GaussianInt) := by
  ext <;> simp

/-- Numeric value of an LSD-first canonical digit word, supplied by CNRSCore. -/
abbrev wordValue : List Digit → GaussianInt := CNRSCore.wordValue

/-- Combined numeric value of an LSD-first stream of input digit pairs. -/
def pairValue : List (Digit × Digit) → GaussianInt
  | [] => 0
  | (a, b) :: xs => digit a + digit b + beta * pairValue xs

/-- Run the full finite transducer, recording all output digits and final carry. -/
def runAddition : CarryState → List (Digit × Digit) → List Digit × CarryState
  | q, [] => ([], q)
  | q, (a, b) :: xs =>
      let r := runAddition (additionTransition q a b) xs
      (additionOutput q a b :: r.1, r.2)

/-- The machine emits exactly one digit per input pair. -/
theorem runAddition_output_length (q : CarryState) (xs : List (Digit × Digit)) :
    (runAddition q xs).1.length = xs.length := by
  induction xs generalizing q with
  | nil => simp [runAddition]
  | cons p xs ih =>
      rcases p with ⟨a, b⟩
      simp [runAddition, ih]

/-- Prefix arithmetic invariant: emitted value plus weighted final carry equals input plus initial carry. -/
theorem runAddition_invariant (q : CarryState) (xs : List (Digit × Digit)) :
    wordValue (runAddition q xs).1 +
        beta ^ xs.length * (runAddition q xs).2.1 =
      q.1 + pairValue xs := by
  induction xs generalizing q with
  | nil =>
      simp [runAddition, wordValue, pairValue]
  | cons p xs ih =>
      rcases p with ⟨a, b⟩
      let q' := additionTransition q a b
      have hi := ih q'
      have hs := additionTransition_equation q a b
      change
        digit (additionOutput q a b) +
            beta * wordValue (runAddition q' xs).1 +
            beta ^ (xs.length + 1) * (runAddition q' xs).2.1 =
          q.1 + (digit a + digit b + beta * pairValue xs)
      rw [pow_succ]
      calc
        digit (additionOutput q a b) +
              beta * wordValue (runAddition q' xs).1 +
              (beta ^ xs.length * beta) * (runAddition q' xs).2.1
            = digit (additionOutput q a b) +
                beta * (wordValue (runAddition q' xs).1 +
                  beta ^ xs.length * (runAddition q' xs).2.1) := by ring
        _ = digit (additionOutput q a b) + beta * (q'.1 + pairValue xs) := by
              rw [hi]
        _ = (digit (additionOutput q a b) + beta * q'.1) +
              beta * pairValue xs := by ring
        _ = (digit a + digit b + q.1) + beta * pairValue xs := by
              rw [hs]
        _ = q.1 + (digit a + digit b + beta * pairValue xs) := by ring

/-- State composition across concatenated input streams. -/
theorem runAddition_append_state (q : CarryState)
    (xs ys : List (Digit × Digit)) :
    (runAddition q (xs ++ ys)).2 =
      (runAddition (runAddition q xs).2 ys).2 := by
  induction xs generalizing q with
  | nil => simp [runAddition]
  | cons p xs ih =>
      rcases p with ⟨a, b⟩
      simp [runAddition, ih]

/-- Value decomposition across concatenated pair streams. -/
theorem pairValue_append (xs ys : List (Digit × Digit)) :
    pairValue (xs ++ ys) =
      pairValue xs + beta ^ xs.length * pairValue ys := by
  induction xs with
  | nil => simp [pairValue]
  | cons p xs ih =>
      rcases p with ⟨a, b⟩
      simp [pairValue, ih, pow_succ]
      ring

/-- Five zero-input columns suffice to drain every one of the exact 14 carry states. -/
def additionDrainInputs : List (Digit × Digit) :=
  List.replicate 5 ((0 : Digit), (0 : Digit))

theorem additionDrain_final_zero :
    ∀ q : CarryState,
      (runAddition q additionDrainInputs).2 = zeroCarryState := by
  native_decide

/-- Zero drain columns add no input value. -/
theorem additionDrain_pairValue_zero : pairValue additionDrainInputs = 0 := by
  native_decide

/-- Full finite addition: process the finite aligned inputs and then five zero columns. -/
def addAligned (xs : List (Digit × Digit)) : List Digit :=
  (runAddition zeroCarryState (xs ++ additionDrainInputs)).1

/-- The forced drain always leaves zero final carry. -/
theorem addAligned_finalCarry_zero (xs : List (Digit × Digit)) :
    (runAddition zeroCarryState (xs ++ additionDrainInputs)).2 = zeroCarryState := by
  rw [runAddition_append_state]
  exact additionDrain_final_zero _

/-- End-to-end arithmetic correctness for a finite aligned pair stream. -/
theorem addAligned_correct (xs : List (Digit × Digit)) :
    wordValue (addAligned xs) = pairValue xs := by
  have h := runAddition_invariant zeroCarryState (xs ++ additionDrainInputs)
  have hf := addAligned_finalCarry_zero xs
  rw [hf] at h
  rw [pairValue_append, additionDrain_pairValue_zero, mul_zero, add_zero] at h
  have hzero : (zeroCarryState : CarryState).1 = (0 : GaussianInt) := by rfl
  rw [hzero] at h
  simp at h
  simpa [addAligned] using h

/-- Pair-stream value is exactly the sum of the two operand-word values. -/
theorem pairValue_eq_operand_values (xs : List (Digit × Digit)) :
    pairValue xs =
      wordValue (xs.map Prod.fst) + wordValue (xs.map Prod.snd) := by
  induction xs with
  | nil => simp [pairValue, wordValue]
  | cons p xs ih =>
      rcases p with ⟨a, b⟩
      simp [pairValue, wordValue, ih]
      ring

/-- Correctness for a finite aligned stream. -/
theorem addAligned_correct_operands (xs : List (Digit × Digit)) :
    wordValue (addAligned xs) =
      wordValue (xs.map Prod.fst) + wordValue (xs.map Prod.snd) := by
  rw [addAligned_correct, pairValue_eq_operand_values]

/-- The aligned result emits exactly five extra drain positions. -/
theorem addAligned_length (xs : List (Digit × Digit)) :
    (addAligned xs).length = xs.length + 5 := by
  simp [addAligned, runAddition_output_length, additionDrainInputs]

/-- Align arbitrary LSD-first finite words by padding the shorter word with zero digits. -/
def alignWords : List Digit → List Digit → List (Digit × Digit)
  | [], [] => []
  | [], b :: bs => (0, b) :: alignWords [] bs
  | a :: as, [] => (a, 0) :: alignWords as []
  | a :: as, b :: bs => (a, b) :: alignWords as bs

/-- Alignment does not change the numeric sum represented by the two words. -/
theorem pairValue_alignWords (xs ys : List Digit) :
    pairValue (alignWords xs ys) = wordValue xs + wordValue ys := by
  induction xs generalizing ys with
  | nil =>
      induction ys with
      | nil => simp [alignWords, pairValue, wordValue]
      | cons b bs ih =>
          simp [alignWords, pairValue, wordValue, ih]
  | cons a as ih =>
      cases ys with
      | nil =>
          simp [alignWords, pairValue, wordValue, ih]
      | cons b bs =>
          simp [alignWords, pairValue, wordValue, ih]
          ring

/-- Alignment length is the maximum operand length. -/
theorem alignWords_length (xs ys : List Digit) :
    (alignWords xs ys).length = max xs.length ys.length := by
  induction xs generalizing ys with
  | nil =>
      induction ys with
      | nil => simp [alignWords]
      | cons b bs ih => simp [alignWords, ih]
  | cons a as ih =>
      cases ys with
      | nil => simp [alignWords, ih]
      | cons b bs => simp [alignWords, ih, Nat.succ_max_succ]

/-- User-facing finite-word addition operation. -/
def addWords (xs ys : List Digit) : List Digit :=
  addAligned (alignWords xs ys)

/-- End-to-end correctness for arbitrary finite CNRS-A digit words. -/
theorem addWords_correct (xs ys : List Digit) :
    wordValue (addWords xs ys) = wordValue xs + wordValue ys := by
  rw [addWords, addAligned_correct, pairValue_alignWords]

/-- The fixed-drain implementation emits max input length plus five positions. -/
theorem addWords_length (xs ys : List Digit) :
    (addWords xs ys).length = max xs.length ys.length + 5 := by
  rw [addWords, addAligned_length, alignWords_length]

end CNRSArithmetic
