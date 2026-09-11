/-
CNRSArithmetic Phase B: finite 14-state / 350-transition addition transducer.
-/
import CNRSArithmetic.AdditionCarrySet

namespace CNRSArithmetic

/-- Run only the carry-state component over an LSD-first input-pair stream. -/
def runAdditionState : CarryState → List (Digit × Digit) → CarryState
  | q, [] => q
  | q, (a, b) :: xs => runAdditionState (additionTransition q a b) xs

/-- Explicit finite reachability certificates, one for every member of K. -/
def additionReachWitness (q : CarryState) : List (Digit × Digit) :=
  if q.1 = gi 0 0 then []
  else if q.1 = gi 1 0 then [(1, 4), (0, 0), (0, 0)]
  else if q.1 = gi (-1) 0 then [(1, 4), (0, 4)]
  else if q.1 = gi 0 1 then [(1, 4), (0, 0), (3, 4), (0, 2)]
  else if q.1 = gi 0 (-1) then [(1, 4), (0, 0), (3, 4), (0, 0), (0, 0)]
  else if q.1 = gi 1 1 then [(1, 4), (0, 0)]
  else if q.1 = gi (-1) (-1) then [(1, 4), (0, 0), (0, 2)]
  else if q.1 = gi (-2) 0 then [(1, 4), (0, 0), (3, 4), (3, 4)]
  else if q.1 = gi 2 1 then [(1, 4), (0, 4), (0, 0)]
  else if q.1 = gi (-2) (-1) then [(1, 4)]
  else if q.1 = gi (-2) (-2) then [(1, 4), (0, 0), (3, 4), (0, 0), (0, 4)]
  else if q.1 = gi 2 2 then [(1, 4), (0, 0), (3, 4), (0, 0)]
  else if q.1 = gi (-3) (-1) then [(1, 4), (0, 0), (0, 2), (4, 4)]
  else if q.1 = gi (-3) (-2) then [(1, 4), (0, 0), (3, 4)]
  else []

/-- Every one of the 14 listed carry states is genuinely reachable from zero. -/
theorem additionCarry_reachable :
    ∀ q : CarryState,
      runAdditionState zeroCarryState (additionReachWitness q) = q := by
  native_decide

/-- Every explicit reachability certificate has length at most five. -/
theorem additionReachWitness_length_le_five :
    ∀ q : CarryState, (additionReachWitness q).length ≤ 5 := by
  native_decide

/-- Thus closure plus reachability certifies that K is the exact reachable state set. -/
theorem additionCarry_exact :
    (∀ q : CarryState, ∀ a b : Digit,
      (additionTransition q a b).1 ∈ additionCarrySet) ∧
    (∀ q : CarryState,
      runAdditionState zeroCarryState (additionReachWitness q) = q) := by
  constructor
  · intro q a b
    exact (additionTransition q a b).2
  · exact additionCarry_reachable

/-- Tight coordinate bounds read directly from the exact carry set. -/
theorem additionCarry_tight_bounds :
    ∀ q : CarryState,
      q.1.re.natAbs ≤ 3 ∧ q.1.im.natAbs ≤ 2 := by
  native_decide

/-- The 25 possible digit-pair inputs to one transducer column. -/
def additionInputAlphabet : Finset (Digit × Digit) := Finset.univ

/-- All one-step successor states of a finite set of carry states. -/
def additionSuccessors (s : Finset CarryState) : Finset CarryState :=
  s.biUnion fun q => additionInputAlphabet.image fun p =>
    additionTransition q p.1 p.2

/-- Cumulative states reachable from zero in at most n input columns. -/
def additionReachableUpTo : ℕ → Finset CarryState
  | 0 => {zeroCarryState}
  | n + 1 =>
      let r := additionReachableUpTo n
      r ∪ additionSuccessors r

/-- P3 v11 breadth-first reachable-state counts through generation five. -/
theorem additionReachable_generation_cards :
    (additionReachableUpTo 0).card = 1 ∧
    (additionReachableUpTo 1).card = 2 ∧
    (additionReachableUpTo 2).card = 4 ∧
    (additionReachableUpTo 3).card = 8 ∧
    (additionReachableUpTo 4).card = 12 ∧
    (additionReachableUpTo 5).card = 14 := by
  native_decide

/-- All 14 carry states have been reached by generation five. -/
theorem additionReachable_complete_at_five :
    additionReachableUpTo 5 = Finset.univ := by
  native_decide

/-- Generation four is still incomplete, so five generations are genuinely required. -/
theorem additionReachable_not_complete_at_four :
    additionReachableUpTo 4 ≠ Finset.univ := by
  native_decide

/-- Iterate the zero-input transition a prescribed number of times. -/
def additionDrainState : ℕ → CarryState → CarryState
  | 0, q => q
  | n + 1, q => additionDrainState n (additionTransition q 0 0)

/-- Five zero-input steps are sufficient to drain every reachable carry. -/
theorem additionDrain_five_suffices :
    ∀ q : CarryState, additionDrainState 5 q = zeroCarryState := by
  native_decide

/-- A concrete carry that requires the full five-step bound. -/
def additionDrainFiveWitness : CarryState :=
  ⟨gi (-2) (-2), by native_decide⟩

/-- Four zero-input steps do not drain every carry. -/
theorem additionDrain_four_not_sufficient :
    additionDrainState 4 additionDrainFiveWitness ≠ zeroCarryState := by
  native_decide

/-- Therefore the exact maximum zero-input drain length over K is five. -/
theorem additionDrain_exact_max_five :
    (∀ q : CarryState, additionDrainState 5 q = zeroCarryState) ∧
    (∃ q : CarryState, additionDrainState 4 q ≠ zeroCarryState) := by
  refine ⟨additionDrain_five_suffices, ?_⟩
  exact ⟨additionDrainFiveWitness, additionDrain_four_not_sufficient⟩

end CNRSArithmetic
