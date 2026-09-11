/-
CNRSArithmetic Phase B: exact 14-element addition carry set.
-/
import CNRSArithmetic.AdditionStep

namespace CNRSArithmetic

open Zsqrtd

/-- Small constructor used to display the finite Gaussian carry set. -/
def gi (a b : ℤ) : GaussianInt := ⟨a, b⟩

@[simp] theorem gi_re (a b : ℤ) : (gi a b).re = a := rfl
@[simp] theorem gi_im (a b : ℤ) : (gi a b).im = b := rfl

/-- P3 v11 exact reachable carry list for addition in base -2+i. -/
def additionCarryList : List GaussianInt :=
  [ gi 0 0,
    gi 1 0,
    gi (-1) 0,
    gi 0 1,
    gi 0 (-1),
    gi 1 1,
    gi (-1) (-1),
    gi (-2) 0,
    gi 2 1,
    gi (-2) (-1),
    gi (-2) (-2),
    gi 2 2,
    gi (-3) (-1),
    gi (-3) (-2) ]

/-- The finite addition carry alphabet K. -/
def additionCarrySet : Finset GaussianInt := additionCarryList.toFinset

/-- A machine state is a Gaussian integer certified to lie in K. -/
abbrev CarryState := ↥additionCarrySet

/-- The listed carries are distinct, hence K has exactly 14 states. -/
theorem additionCarrySet_card : additionCarrySet.card = 14 := by
  native_decide

/-- Equivalent Fintype state-count statement. -/
theorem carryState_card : Fintype.card CarryState = 14 := by
  native_decide

/-- Zero carry is the initial machine state. -/
def zeroCarryState : CarryState := ⟨gi 0 0, by native_decide⟩

/-- Exhaustive 14 x 25 closure certificate for the next-carry map. -/
theorem additionCarry_closed :
    ∀ q : CarryState, ∀ a b : Digit,
      (addStep q.1 a b).carry ∈ additionCarrySet := by
  native_decide

/-- Deterministic transition on the finite carry alphabet. -/
def additionTransition (q : CarryState) (a b : Digit) : CarryState :=
  ⟨(addStep q.1 a b).carry, additionCarry_closed q a b⟩

/-- Deterministic output digit on the finite carry alphabet. -/
def additionOutput (q : CarryState) (a b : Digit) : Digit :=
  (addStep q.1 a b).output

/-- The finite transducer has 14*25 = 350 state/input transitions. -/
theorem additionTransition_count :
    Fintype.card CarryState * Fintype.card (Digit × Digit) = 350 := by
  native_decide

/-- Arithmetic invariant restated for the finite-state transducer. -/
theorem additionTransition_equation (q : CarryState) (a b : Digit) :
    digit (additionOutput q a b) + beta * (additionTransition q a b).1 =
      digit a + digit b + q.1 := by
  simpa [additionOutput, additionTransition] using addStep_equation q.1 a b

end CNRSArithmetic
