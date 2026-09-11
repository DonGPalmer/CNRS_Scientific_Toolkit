/-
CNRSArithmetic Phase D: exact finite-state transducer for multiplication by 3.

For beta = -2+i, the reachable carry alphabet K_3 has exactly 32 Gaussian
states. This module certifies transition closure, exact reachability, breadth-
first generation counts, exact zero-input drain length, the stream invariant,
and finite-word correctness.
-/
import CNRSArithmetic.FixedMultiplierKi

namespace CNRSArithmetic

open Zsqrtd

/-- Fixed Gaussian multiplier c = 3. -/
def threeMultiplier : GaussianInt := digit (3 : Digit)

@[simp] theorem threeMultiplier_re : threeMultiplier.re = 3 := rfl
@[simp] theorem threeMultiplier_im : threeMultiplier.im = 0 := rfl

/-- The exact reachable carry alphabet K_3. -/
def threeCarrySet : Finset GaussianInt :=
  { gi (-5) (-4), gi (-5) (-3), gi (-5) (-2),
    gi (-4) (-3), gi (-4) (-2), gi (-4) (-1),
    gi (-3) (-3), gi (-3) (-2), gi (-3) (-1), gi (-3) 0,
    gi (-2) (-2), gi (-2) (-1), gi (-2) 0, gi (-2) 1,
    gi (-1) (-2), gi (-1) (-1), gi (-1) 0, gi (-1) 1,
    gi 0 (-1), gi 0 0, gi 0 1, gi 0 2,
    gi 1 (-1), gi 1 0, gi 1 1, gi 1 2,
    gi 2 0, gi 2 1, gi 2 2, gi 2 3,
    gi 3 2, gi 3 3 }

abbrev ThreeCarryState := ↥threeCarrySet

theorem threeCarrySet_card : threeCarrySet.card = 32 := by
  native_decide

theorem threeCarryState_card : Fintype.card ThreeCarryState = 32 := by
  native_decide

def threeZeroCarryState : ThreeCarryState := ⟨gi 0 0, by native_decide⟩

theorem threeCarry_closed :
    ∀ q : ThreeCarryState, ∀ a : Digit,
      (fixedMultiplierStep threeMultiplier q.1 a).carry ∈ threeCarrySet := by
  native_decide

def threeTransition (q : ThreeCarryState) (a : Digit) : ThreeCarryState :=
  ⟨(fixedMultiplierStep threeMultiplier q.1 a).carry, threeCarry_closed q a⟩

def threeOutput (q : ThreeCarryState) (a : Digit) : Digit :=
  (fixedMultiplierStep threeMultiplier q.1 a).output

theorem threeTransition_equation (q : ThreeCarryState) (a : Digit) :
    digit (threeOutput q a) + beta * (threeTransition q a).1 =
      q.1 + threeMultiplier * digit a := by
  simpa [threeOutput, threeTransition] using
    fixedMultiplierStep_equation threeMultiplier q.1 a

def runThreeState : ThreeCarryState → List Digit → ThreeCarryState
  | q, [] => q
  | q, a :: xs => runThreeState (threeTransition q a) xs

/-- Explicit shortest reachability certificates for all 32 K_3 states. -/
def threeReachWitness (q : ThreeCarryState) : List Digit :=
  if q.1 = gi (-5) (-4) then [2,0,4,0,4]
  else if q.1 = gi (-5) (-3) then [2,0,4]
  else if q.1 = gi (-5) (-2) then [4,0,0,4]
  else if q.1 = gi (-4) (-3) then [4,0,3]
  else if q.1 = gi (-4) (-2) then [4]
  else if q.1 = gi (-4) (-1) then [2,0,3,4]
  else if q.1 = gi (-3) (-3) then [2,0,4,0,2]
  else if q.1 = gi (-3) (-2) then [2,0,3]
  else if q.1 = gi (-3) (-1) then [2,3]
  else if q.1 = gi (-3) 0 then [2,0,4,4]
  else if q.1 = gi (-2) (-2) then [4,0,2]
  else if q.1 = gi (-2) (-1) then [2]
  else if q.1 = gi (-2) 0 then [4,3]
  else if q.1 = gi (-2) 1 then [2,0,4,0,4,3]
  else if q.1 = gi (-1) (-2) then [2,0,4,0,1]
  else if q.1 = gi (-1) (-1) then [2,0,1]
  else if q.1 = gi (-1) 0 then [2,2]
  else if q.1 = gi (-1) 1 then [2,0,4,2]
  else if q.1 = gi 0 (-1) then [4,0,0]
  else if q.1 = gi 0 0 then []
  else if q.1 = gi 0 1 then [4,1]
  else if q.1 = gi 0 2 then [2,0,4,0,4,1]
  else if q.1 = gi 1 (-1) then [2,0,4,0,0]
  else if q.1 = gi 1 0 then [2,0,0]
  else if q.1 = gi 1 1 then [2,0]
  else if q.1 = gi 1 2 then [2,0,4,1]
  else if q.1 = gi 2 0 then [2,0,4,0,4,1,0]
  else if q.1 = gi 2 1 then [2,2,0]
  else if q.1 = gi 2 2 then [4,0]
  else if q.1 = gi 2 3 then [2,0,4,0,4,0]
  else if q.1 = gi 3 2 then [2,0,3,4,0]
  else if q.1 = gi 3 3 then [2,0,4,0]
  else []

theorem threeCarry_reachable :
    ∀ q : ThreeCarryState,
      runThreeState threeZeroCarryState (threeReachWitness q) = q := by
  native_decide

theorem threeReachWitness_length_le_seven :
    ∀ q : ThreeCarryState, (threeReachWitness q).length ≤ 7 := by
  native_decide

def ThreeReachable (x : GaussianInt) : Prop :=
  ∃ xs : List Digit, (runThreeState threeZeroCarryState xs).1 = x

theorem threeReachable_iff_mem_threeCarrySet (x : GaussianInt) :
    ThreeReachable x ↔ x ∈ threeCarrySet := by
  constructor
  · rintro ⟨xs, rfl⟩
    exact (runThreeState threeZeroCarryState xs).2
  · intro hx
    let q : ThreeCarryState := ⟨x, hx⟩
    refine ⟨threeReachWitness q, ?_⟩
    exact congrArg Subtype.val (threeCarry_reachable q)

def threeInputAlphabet : Finset Digit := Finset.univ

def threeSuccessors (s : Finset ThreeCarryState) : Finset ThreeCarryState :=
  s.biUnion fun q => threeInputAlphabet.image fun a => threeTransition q a

def threeReachableUpTo : ℕ → Finset ThreeCarryState
  | 0 => {threeZeroCarryState}
  | n + 1 =>
      let r := threeReachableUpTo n
      r ∪ threeSuccessors r

theorem threeReachable_generation_cards :
    (threeReachableUpTo 0).card = 1 ∧
    (threeReachableUpTo 1).card = 3 ∧
    (threeReachableUpTo 2).card = 9 ∧
    (threeReachableUpTo 3).card = 17 ∧
    (threeReachableUpTo 4).card = 23 ∧
    (threeReachableUpTo 5).card = 28 ∧
    (threeReachableUpTo 6).card = 31 ∧
    (threeReachableUpTo 7).card = 32 := by
  native_decide

theorem threeReachable_complete_at_seven :
    threeReachableUpTo 7 = Finset.univ := by
  native_decide

theorem threeReachable_not_complete_at_six :
    threeReachableUpTo 6 ≠ Finset.univ := by
  native_decide

def threeDrainState : ℕ → ThreeCarryState → ThreeCarryState
  | 0, q => q
  | n + 1, q => threeDrainState n (threeTransition q 0)

theorem threeDrain_five_suffices :
    ∀ q : ThreeCarryState, threeDrainState 5 q = threeZeroCarryState := by
  native_decide

def threeDrainFiveWitness : ThreeCarryState :=
  ⟨gi (-4) (-2), by native_decide⟩

theorem threeDrain_four_not_sufficient :
    threeDrainState 4 threeDrainFiveWitness ≠ threeZeroCarryState := by
  native_decide

theorem threeDrain_exact_max_five :
    (∀ q : ThreeCarryState, threeDrainState 5 q = threeZeroCarryState) ∧
    (∃ q : ThreeCarryState, threeDrainState 4 q ≠ threeZeroCarryState) := by
  exact ⟨threeDrain_five_suffices, threeDrainFiveWitness,
    threeDrain_four_not_sufficient⟩

def runThree : ThreeCarryState → List Digit → List Digit × ThreeCarryState
  | q, [] => ([], q)
  | q, a :: xs =>
      let r := runThree (threeTransition q a) xs
      (threeOutput q a :: r.1, r.2)

theorem runThree_output_length (q : ThreeCarryState) (xs : List Digit) :
    (runThree q xs).1.length = xs.length := by
  induction xs generalizing q with
  | nil => simp [runThree]
  | cons a xs ih => simp [runThree, ih]

theorem runThree_invariant (q : ThreeCarryState) (xs : List Digit) :
    wordValue (runThree q xs).1 + beta ^ xs.length * (runThree q xs).2.1 =
      q.1 + threeMultiplier * wordValue xs := by
  induction xs generalizing q with
  | nil => simp [runThree, wordValue]
  | cons a xs ih =>
      let q' := threeTransition q a
      have hi := ih q'
      have hs := threeTransition_equation q a
      change
        digit (threeOutput q a) + beta * wordValue (runThree q' xs).1 +
            beta ^ (xs.length + 1) * (runThree q' xs).2.1 =
          q.1 + threeMultiplier * (digit a + beta * wordValue xs)
      rw [pow_succ]
      calc
        digit (threeOutput q a) + beta * wordValue (runThree q' xs).1 +
              (beta ^ xs.length * beta) * (runThree q' xs).2.1
            = digit (threeOutput q a) +
                beta * (wordValue (runThree q' xs).1 +
                  beta ^ xs.length * (runThree q' xs).2.1) := by ring
        _ = digit (threeOutput q a) + beta * (q'.1 + threeMultiplier * wordValue xs) := by rw [hi]
        _ = (digit (threeOutput q a) + beta * q'.1) +
              beta * threeMultiplier * wordValue xs := by ring
        _ = (q.1 + threeMultiplier * digit a) +
              beta * threeMultiplier * wordValue xs := by rw [hs]
        _ = q.1 + threeMultiplier * (digit a + beta * wordValue xs) := by ring

theorem runThree_append_state (q : ThreeCarryState) (xs ys : List Digit) :
    (runThree q (xs ++ ys)).2 = (runThree (runThree q xs).2 ys).2 := by
  induction xs generalizing q with
  | nil => simp [runThree]
  | cons a xs ih => simp [runThree, ih]

def threeDrainInputs : List Digit := List.replicate 5 (0 : Digit)

theorem threeDrain_wordValue_zero : wordValue threeDrainInputs = 0 := by
  native_decide

theorem runThree_drain_final_zero :
    ∀ q : ThreeCarryState, (runThree q threeDrainInputs).2 = threeZeroCarryState := by
  native_decide

def multiplyByThreeWord (xs : List Digit) : List Digit :=
  (runThree threeZeroCarryState (xs ++ threeDrainInputs)).1

theorem multiplyByThreeWord_finalCarry_zero (xs : List Digit) :
    (runThree threeZeroCarryState (xs ++ threeDrainInputs)).2 = threeZeroCarryState := by
  rw [runThree_append_state]
  exact runThree_drain_final_zero _

theorem multiplyByThreeWord_correct (xs : List Digit) :
    wordValue (multiplyByThreeWord xs) = threeMultiplier * wordValue xs := by
  have h := runThree_invariant threeZeroCarryState (xs ++ threeDrainInputs)
  have hf := multiplyByThreeWord_finalCarry_zero xs
  rw [hf] at h
  rw [wordValue_append, threeDrain_wordValue_zero, mul_zero, add_zero] at h
  have hzero : (threeZeroCarryState : ThreeCarryState).1 = (0 : GaussianInt) := by rfl
  rw [hzero] at h
  simp at h
  simpa [multiplyByThreeWord] using h

theorem multiplyByThreeWord_length (xs : List Digit) :
    (multiplyByThreeWord xs).length = xs.length + 5 := by
  simp [multiplyByThreeWord, runThree_output_length, threeDrainInputs]

end CNRSArithmetic
