/-
CNRSArithmetic Phase D: exact finite-state transducer for multiplication by 2.

For beta = -2+i, the reachable carry alphabet K_2 has exactly the same
14 Gaussian states as the already-governed Phase-B addition carry alphabet.
This module certifies closure, exact reachability, generation counts, exact
zero-input drain length, the stream invariant, and finite-word correctness.
-/
import CNRSArithmetic.FixedMultiplierStep
import CNRSArithmetic.AdditionCarrySet
import CNRSArithmetic.AdditionCorrectness

namespace CNRSArithmetic

open Zsqrtd

/-- Fixed Gaussian multiplier c = 2. -/
def twoMultiplier : GaussianInt := digit (2 : Digit)

@[simp] theorem twoMultiplier_re : twoMultiplier.re = 2 := rfl
@[simp] theorem twoMultiplier_im : twoMultiplier.im = 0 := rfl

/-- The exact reachable carry alphabet for multiplication by 2. -/
def twoCarrySet : Finset GaussianInt := additionCarrySet

/-- A multiplier-by-two carry state. -/
abbrev TwoCarryState := ↥twoCarrySet

/-- K_2 contains exactly 14 states. -/
theorem twoCarrySet_card : twoCarrySet.card = 14 := by
  native_decide

/-- Equivalent Fintype state-count statement. -/
theorem twoCarryState_card : Fintype.card TwoCarryState = 14 := by
  native_decide

/-- Initial carry state. -/
def twoZeroCarryState : TwoCarryState := ⟨gi 0 0, by native_decide⟩

/-- Exhaustive 14 x 5 transition-closure certificate for c=2. -/
theorem twoCarry_closed :
    ∀ q : TwoCarryState, ∀ a : Digit,
      (fixedMultiplierStep twoMultiplier q.1 a).carry ∈ twoCarrySet := by
  native_decide

/-- Deterministic finite-state transition for multiplication by 2. -/
def twoTransition (q : TwoCarryState) (a : Digit) : TwoCarryState :=
  ⟨(fixedMultiplierStep twoMultiplier q.1 a).carry, twoCarry_closed q a⟩

/-- Deterministic output digit for multiplication by 2. -/
def twoOutput (q : TwoCarryState) (a : Digit) : Digit :=
  (fixedMultiplierStep twoMultiplier q.1 a).output

/-- One-column arithmetic invariant on the exact finite state alphabet. -/
theorem twoTransition_equation (q : TwoCarryState) (a : Digit) :
    digit (twoOutput q a) + beta * (twoTransition q a).1 =
      q.1 + twoMultiplier * digit a := by
  simpa [twoOutput, twoTransition] using
    fixedMultiplierStep_equation twoMultiplier q.1 a

/-- Run only the carry state over an LSD-first input word. -/
def runTwoState : TwoCarryState → List Digit → TwoCarryState
  | q, [] => q
  | q, a :: xs => runTwoState (twoTransition q a) xs

/-- Explicit shortest-or-near-shortest reachability certificates for all 14 states. -/
def twoReachWitness (q : TwoCarryState) : List Digit :=
  if q.1 = gi 0 0 then []
  else if q.1 = gi (-2) (-1) then [3]
  else if q.1 = gi 1 1 then [3, 0]
  else if q.1 = gi (-1) 0 then [3, 2]
  else if q.1 = gi 1 0 then [3, 0, 0]
  else if q.1 = gi (-1) (-1) then [3, 0, 1]
  else if q.1 = gi 2 1 then [3, 2, 0]
  else if q.1 = gi (-3) (-2) then [3, 0, 4]
  else if q.1 = gi 2 2 then [3, 0, 4, 0]
  else if q.1 = gi 0 1 then [3, 0, 4, 1]
  else if q.1 = gi (-3) (-1) then [3, 0, 1, 4]
  else if q.1 = gi (-2) 0 then [3, 0, 4, 4]
  else if q.1 = gi 0 (-1) then [3, 0, 4, 0, 0]
  else if q.1 = gi (-2) (-2) then [3, 0, 4, 0, 2]
  else []

/-- Every listed K_2 state is genuinely reachable from zero. -/
theorem twoCarry_reachable :
    ∀ q : TwoCarryState,
      runTwoState twoZeroCarryState (twoReachWitness q) = q := by
  native_decide

/-- Every explicit K_2 reachability certificate has length at most five. -/
theorem twoReachWitness_length_le_five :
    ∀ q : TwoCarryState, (twoReachWitness q).length ≤ 5 := by
  native_decide

/-- Reachability as a predicate on ambient Gaussian carries. -/
def TwoReachable (x : GaussianInt) : Prop :=
  ∃ xs : List Digit, (runTwoState twoZeroCarryState xs).1 = x

/-- The displayed 14-state set is exactly the ambient reachable carry set K_2. -/
theorem twoReachable_iff_mem_twoCarrySet (x : GaussianInt) :
    TwoReachable x ↔ x ∈ twoCarrySet := by
  constructor
  · rintro ⟨xs, rfl⟩
    exact (runTwoState twoZeroCarryState xs).2
  · intro hx
    let q : TwoCarryState := ⟨x, hx⟩
    refine ⟨twoReachWitness q, ?_⟩
    have h := twoCarry_reachable q
    exact congrArg Subtype.val h

/-- The five possible input digits. -/
def twoInputAlphabet : Finset Digit := Finset.univ

/-- All one-step successors of a finite collection of K_2 states. -/
def twoSuccessors (s : Finset TwoCarryState) : Finset TwoCarryState :=
  s.biUnion fun q => twoInputAlphabet.image fun a => twoTransition q a

/-- States reachable from zero in at most n input columns. -/
def twoReachableUpTo : ℕ → Finset TwoCarryState
  | 0 => {twoZeroCarryState}
  | n + 1 =>
      let r := twoReachableUpTo n
      r ∪ twoSuccessors r

/-- Exact breadth-first K_2 generation counts. -/
theorem twoReachable_generation_cards :
    (twoReachableUpTo 0).card = 1 ∧
    (twoReachableUpTo 1).card = 2 ∧
    (twoReachableUpTo 2).card = 4 ∧
    (twoReachableUpTo 3).card = 8 ∧
    (twoReachableUpTo 4).card = 12 ∧
    (twoReachableUpTo 5).card = 14 := by
  native_decide

/-- All 14 K_2 states have appeared by generation five. -/
theorem twoReachable_complete_at_five :
    twoReachableUpTo 5 = Finset.univ := by
  native_decide

/-- Generation four is genuinely incomplete. -/
theorem twoReachable_not_complete_at_four :
    twoReachableUpTo 4 ≠ Finset.univ := by
  native_decide

/-- Iterate the zero-input multiplier transition. -/
def twoDrainState : ℕ → TwoCarryState → TwoCarryState
  | 0, q => q
  | n + 1, q => twoDrainState n (twoTransition q 0)

/-- Five zero-input columns drain every K_2 carry. -/
theorem twoDrain_five_suffices :
    ∀ q : TwoCarryState, twoDrainState 5 q = twoZeroCarryState := by
  native_decide

/-- A K_2 carry requiring the full five-column drain bound. -/
def twoDrainFiveWitness : TwoCarryState :=
  ⟨gi (-2) (-2), by native_decide⟩

/-- Four zero-input columns do not drain every K_2 carry. -/
theorem twoDrain_four_not_sufficient :
    twoDrainState 4 twoDrainFiveWitness ≠ twoZeroCarryState := by
  native_decide

/-- Exact maximum zero-input carry-drain length over K_2 is five. -/
theorem twoDrain_exact_max_five :
    (∀ q : TwoCarryState, twoDrainState 5 q = twoZeroCarryState) ∧
    (∃ q : TwoCarryState, twoDrainState 4 q ≠ twoZeroCarryState) := by
  exact ⟨twoDrain_five_suffices, twoDrainFiveWitness,
    twoDrain_four_not_sufficient⟩

/-- Run the full c=2 transducer, recording output digits and final carry. -/
def runTwo : TwoCarryState → List Digit → List Digit × TwoCarryState
  | q, [] => ([], q)
  | q, a :: xs =>
      let r := runTwo (twoTransition q a) xs
      (twoOutput q a :: r.1, r.2)

/-- The c=2 transducer emits exactly one digit per input digit. -/
theorem runTwo_output_length (q : TwoCarryState) (xs : List Digit) :
    (runTwo q xs).1.length = xs.length := by
  induction xs generalizing q with
  | nil => simp [runTwo]
  | cons a xs ih => simp [runTwo, ih]

/-- Prefix arithmetic invariant for the exact c=2 machine. -/
theorem runTwo_invariant (q : TwoCarryState) (xs : List Digit) :
    wordValue (runTwo q xs).1 + beta ^ xs.length * (runTwo q xs).2.1 =
      q.1 + twoMultiplier * wordValue xs := by
  induction xs generalizing q with
  | nil => simp [runTwo, wordValue]
  | cons a xs ih =>
      let q' := twoTransition q a
      have hi := ih q'
      have hs := twoTransition_equation q a
      change
        digit (twoOutput q a) + beta * wordValue (runTwo q' xs).1 +
            beta ^ (xs.length + 1) * (runTwo q' xs).2.1 =
          q.1 + twoMultiplier * (digit a + beta * wordValue xs)
      rw [pow_succ]
      calc
        digit (twoOutput q a) + beta * wordValue (runTwo q' xs).1 +
              (beta ^ xs.length * beta) * (runTwo q' xs).2.1
            = digit (twoOutput q a) +
                beta * (wordValue (runTwo q' xs).1 +
                  beta ^ xs.length * (runTwo q' xs).2.1) := by ring
        _ = digit (twoOutput q a) + beta * (q'.1 + twoMultiplier * wordValue xs) := by
              rw [hi]
        _ = (digit (twoOutput q a) + beta * q'.1) +
              beta * twoMultiplier * wordValue xs := by ring
        _ = (q.1 + twoMultiplier * digit a) +
              beta * twoMultiplier * wordValue xs := by rw [hs]
        _ = q.1 + twoMultiplier * (digit a + beta * wordValue xs) := by ring

/-- State composition over concatenated input words. -/
theorem runTwo_append_state (q : TwoCarryState) (xs ys : List Digit) :
    (runTwo q (xs ++ ys)).2 = (runTwo (runTwo q xs).2 ys).2 := by
  induction xs generalizing q with
  | nil => simp [runTwo]
  | cons a xs ih => simp [runTwo, ih]

/-- Numeric value decomposition over concatenated LSD-first words. -/
theorem wordValue_append (xs ys : List Digit) :
    wordValue (xs ++ ys) = wordValue xs + beta ^ xs.length * wordValue ys := by
  induction xs with
  | nil => simp [wordValue]
  | cons a xs ih =>
      simp [wordValue, ih, pow_succ]
      ring

/-- Five appended zero digits are sufficient to flush every K_2 carry. -/
def twoDrainInputs : List Digit := List.replicate 5 (0 : Digit)

/-- Appended drain digits have represented value zero. -/
theorem twoDrain_wordValue_zero : wordValue twoDrainInputs = 0 := by
  native_decide

/-- Running the five drain columns from any K_2 state leaves zero carry. -/
theorem runTwo_drain_final_zero :
    ∀ q : TwoCarryState, (runTwo q twoDrainInputs).2 = twoZeroCarryState := by
  native_decide

/-- Finite-word multiplication by two, including the exact five-column carry flush. -/
def multiplyByTwoWord (xs : List Digit) : List Digit :=
  (runTwo twoZeroCarryState (xs ++ twoDrainInputs)).1

/-- The forced drain always leaves zero final carry. -/
theorem multiplyByTwoWord_finalCarry_zero (xs : List Digit) :
    (runTwo twoZeroCarryState (xs ++ twoDrainInputs)).2 = twoZeroCarryState := by
  rw [runTwo_append_state]
  exact runTwo_drain_final_zero _

/-- End-to-end correctness of the exact 14-state c=2 transducer. -/
theorem multiplyByTwoWord_correct (xs : List Digit) :
    wordValue (multiplyByTwoWord xs) = twoMultiplier * wordValue xs := by
  have h := runTwo_invariant twoZeroCarryState (xs ++ twoDrainInputs)
  have hf := multiplyByTwoWord_finalCarry_zero xs
  rw [hf] at h
  rw [wordValue_append, twoDrain_wordValue_zero, mul_zero, add_zero] at h
  have hzero : (twoZeroCarryState : TwoCarryState).1 = (0 : GaussianInt) := by rfl
  rw [hzero] at h
  simp at h
  simpa [multiplyByTwoWord] using h

/-- The exact finite-state implementation emits five carry-flush positions. -/
theorem multiplyByTwoWord_length (xs : List Digit) :
    (multiplyByTwoWord xs).length = xs.length + 5 := by
  simp [multiplyByTwoWord, runTwo_output_length, twoDrainInputs]

end CNRSArithmetic
