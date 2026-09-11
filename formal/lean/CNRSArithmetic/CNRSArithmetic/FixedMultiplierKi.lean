/-
CNRSArithmetic Phase D: exact finite-state transducer for multiplication by i.

For beta = -2+i, the reachable carry alphabet K_i has exactly 12 Gaussian
states. This module certifies transition closure, exact reachability, breadth-
first generation counts, exact zero-input drain length, the stream invariant,
and finite-word correctness.
-/
import CNRSArithmetic.FixedMultiplierStep
import CNRSArithmetic.FixedMultiplierK2

namespace CNRSArithmetic

open Zsqrtd

/-- Fixed Gaussian multiplier c = i. -/
def iMultiplier : GaussianInt := gi 0 1

@[simp] theorem iMultiplier_re : iMultiplier.re = 0 := rfl
@[simp] theorem iMultiplier_im : iMultiplier.im = 1 := rfl

/-- The canonical finite word `[2,1]` represents i because `2 + beta = i`. -/
theorem wordValue_two_one_eq_iMultiplier : wordValue [2, 1] = iMultiplier := by
  native_decide

/-- The exact reachable carry alphabet K_i. -/
def iCarrySet : Finset GaussianInt :=
  { gi (-1) 0,
    gi 0 (-2),
    gi 0 (-1),
    gi 0 0,
    gi 0 1,
    gi 1 (-2),
    gi 1 (-1),
    gi 1 0,
    gi 1 1,
    gi 2 (-1),
    gi 2 0,
    gi 2 1 }

/-- A multiplier-by-i carry state. -/
abbrev ICarryState := ↥iCarrySet

/-- K_i contains exactly 12 states. -/
theorem iCarrySet_card : iCarrySet.card = 12 := by
  native_decide

/-- Equivalent Fintype state-count statement. -/
theorem iCarryState_card : Fintype.card ICarryState = 12 := by
  native_decide

/-- Initial carry state. -/
def iZeroCarryState : ICarryState := ⟨gi 0 0, by native_decide⟩

/-- Exhaustive 12 x 5 transition-closure certificate for c=i. -/
theorem iCarry_closed :
    ∀ q : ICarryState, ∀ a : Digit,
      (fixedMultiplierStep iMultiplier q.1 a).carry ∈ iCarrySet := by
  native_decide

/-- Deterministic finite-state transition for multiplication by i. -/
def iTransition (q : ICarryState) (a : Digit) : ICarryState :=
  ⟨(fixedMultiplierStep iMultiplier q.1 a).carry, iCarry_closed q a⟩

/-- Deterministic output digit for multiplication by i. -/
def iOutput (q : ICarryState) (a : Digit) : Digit :=
  (fixedMultiplierStep iMultiplier q.1 a).output

/-- One-column arithmetic invariant on the exact finite state alphabet. -/
theorem iTransition_equation (q : ICarryState) (a : Digit) :
    digit (iOutput q a) + beta * (iTransition q a).1 =
      q.1 + iMultiplier * digit a := by
  simpa [iOutput, iTransition] using
    fixedMultiplierStep_equation iMultiplier q.1 a

/-- Run only the carry state over an LSD-first input word. -/
def runIState : ICarryState → List Digit → ICarryState
  | q, [] => q
  | q, a :: xs => runIState (iTransition q a) xs

/-- Explicit shortest reachability certificates for all 12 K_i states. -/
def iReachWitness (q : ICarryState) : List Digit :=
  if q.1 = gi 0 0 then []
  else if q.1 = gi 1 (-1) then [3]
  else if q.1 = gi 1 0 then [1]
  else if q.1 = gi 2 (-1) then [4]
  else if q.1 = gi 2 0 then [2]
  else if q.1 = gi (-1) 0 then [4, 0]
  else if q.1 = gi 0 (-2) then [2, 4]
  else if q.1 = gi 0 (-1) then [1, 2]
  else if q.1 = gi 1 1 then [3, 0]
  else if q.1 = gi 0 1 then [2, 4, 0]
  else if q.1 = gi 1 (-2) then [3, 0, 4]
  else if q.1 = gi 2 1 then [4, 0, 0]
  else []

/-- Every listed K_i state is genuinely reachable from zero. -/
theorem iCarry_reachable :
    ∀ q : ICarryState,
      runIState iZeroCarryState (iReachWitness q) = q := by
  native_decide

/-- Every explicit K_i reachability certificate has length at most three. -/
theorem iReachWitness_length_le_three :
    ∀ q : ICarryState, (iReachWitness q).length ≤ 3 := by
  native_decide

/-- Reachability as a predicate on ambient Gaussian carries. -/
def IReachable (x : GaussianInt) : Prop :=
  ∃ xs : List Digit, (runIState iZeroCarryState xs).1 = x

/-- The displayed 12-state set is exactly the ambient reachable carry set K_i. -/
theorem iReachable_iff_mem_iCarrySet (x : GaussianInt) :
    IReachable x ↔ x ∈ iCarrySet := by
  constructor
  · rintro ⟨xs, rfl⟩
    exact (runIState iZeroCarryState xs).2
  · intro hx
    let q : ICarryState := ⟨x, hx⟩
    refine ⟨iReachWitness q, ?_⟩
    have h := iCarry_reachable q
    exact congrArg Subtype.val h

/-- The five possible input digits. -/
def iInputAlphabet : Finset Digit := Finset.univ

/-- All one-step successors of a finite collection of K_i states. -/
def iSuccessors (s : Finset ICarryState) : Finset ICarryState :=
  s.biUnion fun q => iInputAlphabet.image fun a => iTransition q a

/-- States reachable from zero in at most n input columns. -/
def iReachableUpTo : ℕ → Finset ICarryState
  | 0 => {iZeroCarryState}
  | n + 1 =>
      let r := iReachableUpTo n
      r ∪ iSuccessors r

/-- Exact breadth-first K_i cumulative generation counts. -/
theorem iReachable_generation_cards :
    (iReachableUpTo 0).card = 1 ∧
    (iReachableUpTo 1).card = 5 ∧
    (iReachableUpTo 2).card = 9 ∧
    (iReachableUpTo 3).card = 12 := by
  native_decide

/-- All 12 K_i states have appeared by generation three. -/
theorem iReachable_complete_at_three :
    iReachableUpTo 3 = Finset.univ := by
  native_decide

/-- Generation two is genuinely incomplete. -/
theorem iReachable_not_complete_at_two :
    iReachableUpTo 2 ≠ Finset.univ := by
  native_decide

/-- Iterate the zero-input multiplier transition. -/
def iDrainState : ℕ → ICarryState → ICarryState
  | 0, q => q
  | n + 1, q => iDrainState n (iTransition q 0)

/-- Four zero-input columns drain every K_i carry. -/
theorem iDrain_four_suffices :
    ∀ q : ICarryState, iDrainState 4 q = iZeroCarryState := by
  native_decide

/-- A K_i carry requiring the full four-column drain bound. -/
def iDrainFourWitness : ICarryState :=
  ⟨gi 2 (-1), by native_decide⟩

/-- Three zero-input columns do not drain every K_i carry. -/
theorem iDrain_three_not_sufficient :
    iDrainState 3 iDrainFourWitness ≠ iZeroCarryState := by
  native_decide

/-- Exact maximum zero-input carry-drain length over K_i is four. -/
theorem iDrain_exact_max_four :
    (∀ q : ICarryState, iDrainState 4 q = iZeroCarryState) ∧
    (∃ q : ICarryState, iDrainState 3 q ≠ iZeroCarryState) := by
  exact ⟨iDrain_four_suffices, iDrainFourWitness,
    iDrain_three_not_sufficient⟩

/-- Run the full c=i transducer, recording output digits and final carry. -/
def runI : ICarryState → List Digit → List Digit × ICarryState
  | q, [] => ([], q)
  | q, a :: xs =>
      let r := runI (iTransition q a) xs
      (iOutput q a :: r.1, r.2)

/-- The c=i transducer emits exactly one digit per input digit. -/
theorem runI_output_length (q : ICarryState) (xs : List Digit) :
    (runI q xs).1.length = xs.length := by
  induction xs generalizing q with
  | nil => simp [runI]
  | cons a xs ih => simp [runI, ih]

/-- Prefix arithmetic invariant for the exact c=i machine. -/
theorem runI_invariant (q : ICarryState) (xs : List Digit) :
    wordValue (runI q xs).1 + beta ^ xs.length * (runI q xs).2.1 =
      q.1 + iMultiplier * wordValue xs := by
  induction xs generalizing q with
  | nil => simp [runI, wordValue]
  | cons a xs ih =>
      let q' := iTransition q a
      have hi := ih q'
      have hs := iTransition_equation q a
      change
        digit (iOutput q a) + beta * wordValue (runI q' xs).1 +
            beta ^ (xs.length + 1) * (runI q' xs).2.1 =
          q.1 + iMultiplier * (digit a + beta * wordValue xs)
      rw [pow_succ]
      calc
        digit (iOutput q a) + beta * wordValue (runI q' xs).1 +
              (beta ^ xs.length * beta) * (runI q' xs).2.1
            = digit (iOutput q a) +
                beta * (wordValue (runI q' xs).1 +
                  beta ^ xs.length * (runI q' xs).2.1) := by ring
        _ = digit (iOutput q a) + beta * (q'.1 + iMultiplier * wordValue xs) := by
              rw [hi]
        _ = (digit (iOutput q a) + beta * q'.1) +
              beta * iMultiplier * wordValue xs := by ring
        _ = (q.1 + iMultiplier * digit a) +
              beta * iMultiplier * wordValue xs := by rw [hs]
        _ = q.1 + iMultiplier * (digit a + beta * wordValue xs) := by ring

/-- State composition over concatenated input words. -/
theorem runI_append_state (q : ICarryState) (xs ys : List Digit) :
    (runI q (xs ++ ys)).2 = (runI (runI q xs).2 ys).2 := by
  induction xs generalizing q with
  | nil => simp [runI]
  | cons a xs ih => simp [runI, ih]

/-- Four appended zero digits are sufficient to flush every K_i carry. -/
def iDrainInputs : List Digit := List.replicate 4 (0 : Digit)

/-- Appended drain digits have represented value zero. -/
theorem iDrain_wordValue_zero : wordValue iDrainInputs = 0 := by
  native_decide

/-- Running the four drain columns from any K_i state leaves zero carry. -/
theorem runI_drain_final_zero :
    ∀ q : ICarryState, (runI q iDrainInputs).2 = iZeroCarryState := by
  native_decide

/-- Finite-word multiplication by i, including the exact four-column carry flush. -/
def multiplyByIWord (xs : List Digit) : List Digit :=
  (runI iZeroCarryState (xs ++ iDrainInputs)).1

/-- The forced drain always leaves zero final carry. -/
theorem multiplyByIWord_finalCarry_zero (xs : List Digit) :
    (runI iZeroCarryState (xs ++ iDrainInputs)).2 = iZeroCarryState := by
  rw [runI_append_state]
  exact runI_drain_final_zero _

/-- End-to-end correctness of the exact 12-state c=i transducer. -/
theorem multiplyByIWord_correct (xs : List Digit) :
    wordValue (multiplyByIWord xs) = iMultiplier * wordValue xs := by
  have h := runI_invariant iZeroCarryState (xs ++ iDrainInputs)
  have hf := multiplyByIWord_finalCarry_zero xs
  rw [hf] at h
  rw [wordValue_append, iDrain_wordValue_zero, mul_zero, add_zero] at h
  have hzero : (iZeroCarryState : ICarryState).1 = (0 : GaussianInt) := by rfl
  rw [hzero] at h
  simp at h
  simpa [multiplyByIWord] using h

/-- The exact finite-state implementation emits four carry-flush positions. -/
theorem multiplyByIWord_length (xs : List Digit) :
    (multiplyByIWord xs).length = xs.length + 4 := by
  simp [multiplyByIWord, runI_output_length, iDrainInputs]

end CNRSArithmetic
