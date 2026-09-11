/-
CNRSArithmetic Phase D: exact finite-state transducer for multiplication by 4.

For beta = -2+i, the reachable carry alphabet K_4 has exactly 50 Gaussian
states. This module certifies transition closure, exact reachability, breadth-
first generation counts, exact zero-input drain length, the stream invariant,
and finite-word correctness.
-/
import CNRSArithmetic.FixedMultiplierK3

namespace CNRSArithmetic

open Zsqrtd

/-- Fixed Gaussian multiplier c = 4. -/
def fourMultiplier : GaussianInt := digit (4 : Digit)

@[simp] theorem fourMultiplier_re : fourMultiplier.re = 4 := rfl
@[simp] theorem fourMultiplier_im : fourMultiplier.im = 0 := rfl

/-- The exact reachable carry alphabet K_4. -/
def fourCarrySet : Finset GaussianInt :=
  { gi (-7) (-5), gi (-7) (-4), gi (-7) (-3),
    gi (-6) (-5), gi (-6) (-4), gi (-6) (-3), gi (-6) (-2),
    gi (-5) (-4), gi (-5) (-3), gi (-5) (-2), gi (-5) (-1), gi (-5) 0,
    gi (-4) (-4), gi (-4) (-3), gi (-4) (-2), gi (-4) (-1), gi (-4) 0,
    gi (-3) (-3), gi (-3) (-2), gi (-3) (-1), gi (-3) 0, gi (-3) 1,
    gi (-2) (-3), gi (-2) (-2), gi (-2) (-1), gi (-2) 0, gi (-2) 1,
    gi (-1) (-2), gi (-1) (-1), gi (-1) 0, gi (-1) 1, gi (-1) 2,
    gi 0 (-2), gi 0 (-1), gi 0 0, gi 0 1, gi 0 2,
    gi 1 (-1), gi 1 0, gi 1 1, gi 1 2, gi 1 3,
    gi 2 0, gi 2 1, gi 2 2, gi 2 3,
    gi 3 1, gi 3 2, gi 3 3, gi 3 4 }

abbrev FourCarryState := ↥fourCarrySet

theorem fourCarrySet_card : fourCarrySet.card = 50 := by
  native_decide

theorem fourCarryState_card : Fintype.card FourCarryState = 50 := by
  native_decide

def fourZeroCarryState : FourCarryState := ⟨gi 0 0, by native_decide⟩

theorem fourCarry_closed :
    ∀ q : FourCarryState, ∀ a : Digit,
      (fixedMultiplierStep fourMultiplier q.1 a).carry ∈ fourCarrySet := by
  native_decide

def fourTransition (q : FourCarryState) (a : Digit) : FourCarryState :=
  ⟨(fixedMultiplierStep fourMultiplier q.1 a).carry, fourCarry_closed q a⟩

def fourOutput (q : FourCarryState) (a : Digit) : Digit :=
  (fixedMultiplierStep fourMultiplier q.1 a).output

theorem fourTransition_equation (q : FourCarryState) (a : Digit) :
    digit (fourOutput q a) + beta * (fourTransition q a).1 =
      q.1 + fourMultiplier * digit a := by
  simpa [fourOutput, fourTransition] using
    fixedMultiplierStep_equation fourMultiplier q.1 a

def runFourState : FourCarryState → List Digit → FourCarryState
  | q, [] => q
  | q, a :: xs => runFourState (fourTransition q a) xs

/-- Explicit shortest reachability certificates for all 50 K_4 states. -/
def fourReachWitness (q : FourCarryState) : List Digit :=
  if q.1 = gi (-7) (-5) then [4,0,4]
  else if q.1 = gi (-7) (-4) then [2,1,0,4]
  else if q.1 = gi (-7) (-3) then [4,0,0,4]
  else if q.1 = gi (-6) (-5) then [4,0,4,0,4]
  else if q.1 = gi (-6) (-4) then [3,0,4]
  else if q.1 = gi (-6) (-3) then [4]
  else if q.1 = gi (-6) (-2) then [3,0,1,4]
  else if q.1 = gi (-5) (-4) then [4,0,3]
  else if q.1 = gi (-5) (-3) then [2,0,3]
  else if q.1 = gi (-5) (-2) then [2,4]
  else if q.1 = gi (-5) (-1) then [2,0,3,4]
  else if q.1 = gi (-5) 0 then [4,0,4,0,4,4]
  else if q.1 = gi (-4) (-4) then [4,0,4,0,3]
  else if q.1 = gi (-4) (-3) then [3,0,3]
  else if q.1 = gi (-4) (-2) then [3]
  else if q.1 = gi (-4) (-1) then [3,4]
  else if q.1 = gi (-4) 0 then [3,0,4,4]
  else if q.1 = gi (-3) (-3) then [4,0,2]
  else if q.1 = gi (-3) (-2) then [2,0,2]
  else if q.1 = gi (-3) (-1) then [2,3]
  else if q.1 = gi (-3) 0 then [4,3]
  else if q.1 = gi (-3) 1 then [4,0,4,3]
  else if q.1 = gi (-2) (-3) then [4,0,4,0,1]
  else if q.1 = gi (-2) (-2) then [3,0,1]
  else if q.1 = gi (-2) (-1) then [2]
  else if q.1 = gi (-2) 0 then [3,2]
  else if q.1 = gi (-2) 1 then [3,0,4,3]
  else if q.1 = gi (-1) (-2) then [4,0,1]
  else if q.1 = gi (-1) (-1) then [2,0,1]
  else if q.1 = gi (-1) 0 then [2,1]
  else if q.1 = gi (-1) 1 then [4,2]
  else if q.1 = gi (-1) 2 then [4,0,4,2]
  else if q.1 = gi 0 (-2) then [4,0,4,0,0]
  else if q.1 = gi 0 (-1) then [3,0,0]
  else if q.1 = gi 0 0 then []
  else if q.1 = gi 0 1 then [3,1]
  else if q.1 = gi 0 2 then [3,0,4,1]
  else if q.1 = gi 1 (-1) then [4,0,0]
  else if q.1 = gi 1 0 then [2,0,0]
  else if q.1 = gi 1 1 then [2,0]
  else if q.1 = gi 1 2 then [4,1]
  else if q.1 = gi 1 3 then [4,0,4,1]
  else if q.1 = gi 2 0 then [3,0,4,1,0]
  else if q.1 = gi 2 1 then [2,1,0]
  else if q.1 = gi 2 2 then [3,0]
  else if q.1 = gi 2 3 then [3,0,4,0]
  else if q.1 = gi 3 1 then [4,0,4,3,0]
  else if q.1 = gi 3 2 then [3,4,0]
  else if q.1 = gi 3 3 then [4,0]
  else if q.1 = gi 3 4 then [4,0,4,0]
  else []

theorem fourCarry_reachable :
    ∀ q : FourCarryState,
      runFourState fourZeroCarryState (fourReachWitness q) = q := by
  native_decide

theorem fourReachWitness_length_le_six :
    ∀ q : FourCarryState, (fourReachWitness q).length ≤ 6 := by
  native_decide

def FourReachable (x : GaussianInt) : Prop :=
  ∃ xs : List Digit, (runFourState fourZeroCarryState xs).1 = x

theorem fourReachable_iff_mem_fourCarrySet (x : GaussianInt) :
    FourReachable x ↔ x ∈ fourCarrySet := by
  constructor
  · rintro ⟨xs, rfl⟩
    exact (runFourState fourZeroCarryState xs).2
  · intro hx
    let q : FourCarryState := ⟨x, hx⟩
    refine ⟨fourReachWitness q, ?_⟩
    exact congrArg Subtype.val (fourCarry_reachable q)

def fourInputAlphabet : Finset Digit := Finset.univ

def fourSuccessors (s : Finset FourCarryState) : Finset FourCarryState :=
  s.biUnion fun q => fourInputAlphabet.image fun a => fourTransition q a

def fourReachableUpTo : ℕ → Finset FourCarryState
  | 0 => {fourZeroCarryState}
  | n + 1 =>
      let r := fourReachableUpTo n
      r ∪ fourSuccessors r

theorem fourReachable_generation_cards :
    (fourReachableUpTo 0).card = 1 ∧
    (fourReachableUpTo 1).card = 4 ∧
    (fourReachableUpTo 2).card = 16 ∧
    (fourReachableUpTo 3).card = 31 ∧
    (fourReachableUpTo 4).card = 43 ∧
    (fourReachableUpTo 5).card = 49 ∧
    (fourReachableUpTo 6).card = 50 := by
  native_decide

theorem fourReachable_complete_at_six :
    fourReachableUpTo 6 = Finset.univ := by
  native_decide

theorem fourReachable_not_complete_at_five :
    fourReachableUpTo 5 ≠ Finset.univ := by
  native_decide

def fourDrainState : ℕ → FourCarryState → FourCarryState
  | 0, q => q
  | n + 1, q => fourDrainState n (fourTransition q 0)

theorem fourDrain_five_suffices :
    ∀ q : FourCarryState, fourDrainState 5 q = fourZeroCarryState := by
  native_decide

def fourDrainFiveWitness : FourCarryState :=
  ⟨gi (-6) (-3), by native_decide⟩

theorem fourDrain_four_not_sufficient :
    fourDrainState 4 fourDrainFiveWitness ≠ fourZeroCarryState := by
  native_decide

theorem fourDrain_exact_max_five :
    (∀ q : FourCarryState, fourDrainState 5 q = fourZeroCarryState) ∧
    (∃ q : FourCarryState, fourDrainState 4 q ≠ fourZeroCarryState) := by
  exact ⟨fourDrain_five_suffices, fourDrainFiveWitness,
    fourDrain_four_not_sufficient⟩

def runFour : FourCarryState → List Digit → List Digit × FourCarryState
  | q, [] => ([], q)
  | q, a :: xs =>
      let r := runFour (fourTransition q a) xs
      (fourOutput q a :: r.1, r.2)

theorem runFour_output_length (q : FourCarryState) (xs : List Digit) :
    (runFour q xs).1.length = xs.length := by
  induction xs generalizing q with
  | nil => simp [runFour]
  | cons a xs ih => simp [runFour, ih]

theorem runFour_invariant (q : FourCarryState) (xs : List Digit) :
    wordValue (runFour q xs).1 + beta ^ xs.length * (runFour q xs).2.1 =
      q.1 + fourMultiplier * wordValue xs := by
  induction xs generalizing q with
  | nil => simp [runFour, wordValue]
  | cons a xs ih =>
      let q' := fourTransition q a
      have hi := ih q'
      have hs := fourTransition_equation q a
      change
        digit (fourOutput q a) + beta * wordValue (runFour q' xs).1 +
            beta ^ (xs.length + 1) * (runFour q' xs).2.1 =
          q.1 + fourMultiplier * (digit a + beta * wordValue xs)
      rw [pow_succ]
      calc
        digit (fourOutput q a) + beta * wordValue (runFour q' xs).1 +
              (beta ^ xs.length * beta) * (runFour q' xs).2.1
            = digit (fourOutput q a) +
                beta * (wordValue (runFour q' xs).1 +
                  beta ^ xs.length * (runFour q' xs).2.1) := by ring
        _ = digit (fourOutput q a) + beta * (q'.1 + fourMultiplier * wordValue xs) := by rw [hi]
        _ = (digit (fourOutput q a) + beta * q'.1) +
              beta * fourMultiplier * wordValue xs := by ring
        _ = (q.1 + fourMultiplier * digit a) +
              beta * fourMultiplier * wordValue xs := by rw [hs]
        _ = q.1 + fourMultiplier * (digit a + beta * wordValue xs) := by ring

theorem runFour_append_state (q : FourCarryState) (xs ys : List Digit) :
    (runFour q (xs ++ ys)).2 = (runFour (runFour q xs).2 ys).2 := by
  induction xs generalizing q with
  | nil => simp [runFour]
  | cons a xs ih => simp [runFour, ih]

def fourDrainInputs : List Digit := List.replicate 5 (0 : Digit)

theorem fourDrain_wordValue_zero : wordValue fourDrainInputs = 0 := by
  native_decide

theorem runFour_drain_final_zero :
    ∀ q : FourCarryState, (runFour q fourDrainInputs).2 = fourZeroCarryState := by
  native_decide

def multiplyByFourWord (xs : List Digit) : List Digit :=
  (runFour fourZeroCarryState (xs ++ fourDrainInputs)).1

theorem multiplyByFourWord_finalCarry_zero (xs : List Digit) :
    (runFour fourZeroCarryState (xs ++ fourDrainInputs)).2 = fourZeroCarryState := by
  rw [runFour_append_state]
  exact runFour_drain_final_zero _

theorem multiplyByFourWord_correct (xs : List Digit) :
    wordValue (multiplyByFourWord xs) = fourMultiplier * wordValue xs := by
  have h := runFour_invariant fourZeroCarryState (xs ++ fourDrainInputs)
  have hf := multiplyByFourWord_finalCarry_zero xs
  rw [hf] at h
  rw [wordValue_append, fourDrain_wordValue_zero, mul_zero, add_zero] at h
  have hzero : (fourZeroCarryState : FourCarryState).1 = (0 : GaussianInt) := by rfl
  rw [hzero] at h
  simp at h
  simpa [multiplyByFourWord] using h

theorem multiplyByFourWord_length (xs : List Digit) :
    (multiplyByFourWord xs).length = xs.length + 5 := by
  simp [multiplyByFourWord, runFour_output_length, fourDrainInputs]

end CNRSArithmetic
