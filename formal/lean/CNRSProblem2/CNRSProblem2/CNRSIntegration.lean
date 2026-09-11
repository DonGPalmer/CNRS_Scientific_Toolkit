import CNRSProblem2.BranchOrbit
import Mathlib.Tactic

/-!
# CNRS Problem 2, Layer P2-L9: branch-carrier integration bridge

This layer connects the canonical `BranchPoint` sheet coordinate from P2-L2
to the explicit branch metadata of the finite CNRS-H carrier from P2-L6.
It proves compatibility with whole-turn transport, fail-closed coding, and
the P2-L8 relative-pair normal form.  No finite Hurwitz value is interpreted
as a polar radius or angle.
-/

namespace CNRSProblem2

noncomputable section

/-- The sheet index selected by the frozen canonical coordinate of a branch
point. -/
def BranchPoint.branchIndex (p : BranchPoint) : ℤ :=
  p.canonicalCoord.branch

@[simp] theorem BranchPoint.branchIndex_eq_principalTurns
    (p : BranchPoint) :
    p.branchIndex = principalTurns p.totalAngle :=
  rfl

/-- Move a branch point by an integral number of full turns on the universal
cover. -/
def BranchPoint.shiftByTurns (m : ℤ) (p : BranchPoint) : BranchPoint where
  radius := p.radius
  radius_pos := p.radius_pos
  totalAngle := p.totalAngle + 2 * Real.pi * (m : ℝ)

@[simp] theorem BranchPoint.shiftByTurns_radius
    (m : ℤ) (p : BranchPoint) :
    (p.shiftByTurns m).radius = p.radius :=
  rfl

@[simp] theorem BranchPoint.shiftByTurns_totalAngle
    (m : ℤ) (p : BranchPoint) :
    (p.shiftByTurns m).totalAngle =
      p.totalAngle + 2 * Real.pi * (m : ℝ) :=
  rfl

@[simp] theorem BranchPoint.shiftByTurns_zero (p : BranchPoint) :
    p.shiftByTurns 0 = p := by
  apply BranchPoint.ext <;> simp [BranchPoint.shiftByTurns]

@[simp] theorem BranchPoint.shiftByTurns_add
    (m n : ℤ) (p : BranchPoint) :
    (p.shiftByTurns n).shiftByTurns m = p.shiftByTurns (n + m) := by
  apply BranchPoint.ext
  · rfl
  · simp [BranchPoint.shiftByTurns]
    ring

@[simp] theorem BranchPoint.branchIndex_shiftByTurns
    (m : ℤ) (p : BranchPoint) :
    (p.shiftByTurns m).branchIndex = p.branchIndex + m := by
  simp [BranchPoint.branchIndex, BranchPoint.shiftByTurns,
    BranchPoint.canonicalCoord]

@[simp] theorem BranchPoint.canonicalAngle_shiftByTurns
    (m : ℤ) (p : BranchPoint) :
    (p.shiftByTurns m).canonicalCoord.angle = p.canonicalCoord.angle := by
  simp [BranchPoint.shiftByTurns, BranchPoint.canonicalCoord]

/-- Attach a finite CNRS-H value to the canonical sheet of a branch point. -/
def attachFiniteHurwitz
    (p : BranchPoint) (x : FiniteHurwitzValue) :
    BranchedFiniteHurwitzValue :=
  (x, p.branchIndex)

@[simp] theorem attachFiniteHurwitz_value
    (p : BranchPoint) (x : FiniteHurwitzValue) :
    (attachFiniteHurwitz p x).1 = x :=
  rfl

@[simp] theorem attachFiniteHurwitz_branch
    (p : BranchPoint) (x : FiniteHurwitzValue) :
    (attachFiniteHurwitz p x).2 = p.branchIndex :=
  rfl

theorem attachFiniteHurwitz_injective (p : BranchPoint) :
    Function.Injective (attachFiniteHurwitz p) := by
  intro x y h
  exact congrArg Prod.fst h

/-- Exact compatibility between a branch point and explicit finite-Hurwitz
branch metadata. -/
def CompatibleWithBranchPoint
    (p : BranchPoint) (x : BranchedFiniteHurwitzValue) : Prop :=
  x.2 = p.branchIndex

@[simp] theorem compatibleWithBranchPoint_attach
    (p : BranchPoint) (x : FiniteHurwitzValue) :
    CompatibleWithBranchPoint p (attachFiniteHurwitz p x) :=
  rfl

theorem compatibleWithBranchPoint_iff_exists_attach
    (p : BranchPoint) (x : BranchedFiniteHurwitzValue) :
    CompatibleWithBranchPoint p x ↔
      ∃ value : FiniteHurwitzValue, x = attachFiniteHurwitz p value := by
  constructor
  · intro h
    exact ⟨x.1, Prod.ext rfl h⟩
  · rintro ⟨value, rfl⟩
    rfl

theorem compatibleWithBranchPoint_existsUnique
    (p : BranchPoint) (x : BranchedFiniteHurwitzValue)
    (h : CompatibleWithBranchPoint p x) :
    ∃! value : FiniteHurwitzValue, x = attachFiniteHurwitz p value := by
  refine ⟨x.1, Prod.ext rfl h, ?_⟩
  intro value hvalue
  exact congrArg Prod.fst hvalue.symm

@[simp] theorem compatibleWithBranchPoint_shift
    (m : ℤ) (p : BranchPoint) (x : BranchedFiniteHurwitzValue) :
    CompatibleWithBranchPoint (p.shiftByTurns m)
        (shiftBranchedFiniteHurwitz m x) ↔
      CompatibleWithBranchPoint p x := by
  simp [CompatibleWithBranchPoint]

@[simp] theorem attachFiniteHurwitz_shift
    (m : ℤ) (p : BranchPoint) (x : FiniteHurwitzValue) :
    attachFiniteHurwitz (p.shiftByTurns m) x =
      shiftBranchedFiniteHurwitz m (attachFiniteHurwitz p x) := by
  apply Prod.ext <;> simp [attachFiniteHurwitz]

/-- Canonical encoded finite-Hurwitz state attached to a branch point. -/
noncomputable def encodeAttachedFiniteHurwitz
    (p : BranchPoint) (x : FiniteHurwitzValue) :
    BranchedFiniteHurwitzCode :=
  encodeBranchedFiniteHurwitz (attachFiniteHurwitz p x)

/-- Decode only the canonical encoding attached to the specified branch
point.  Codes carrying any other branch fail closed. -/
noncomputable def decodeAttachedFiniteHurwitz
    (p : BranchPoint) (code : BranchedFiniteHurwitzCode) :
    Option FiniteHurwitzValue := do
  let x ← decodeBranchedFiniteHurwitz code
  if x.2 = p.branchIndex then some x.1 else none

@[simp] theorem decodeAttachedFiniteHurwitz_encode
    (p : BranchPoint) (x : FiniteHurwitzValue) :
    decodeAttachedFiniteHurwitz p (encodeAttachedFiniteHurwitz p x) =
      some x := by
  simp [decodeAttachedFiniteHurwitz, encodeAttachedFiniteHurwitz,
    attachFiniteHurwitz]

theorem decodeAttachedFiniteHurwitz_eq_some_iff
    {p : BranchPoint} {code : BranchedFiniteHurwitzCode}
    {x : FiniteHurwitzValue} :
    decodeAttachedFiniteHurwitz p code = some x ↔
      code = encodeAttachedFiniteHurwitz p x := by
  change decodeAttachedFiniteHurwitz p code = some x ↔
    code = encodeBranchedFiniteHurwitz (attachFiniteHurwitz p x)
  rw [← decodeBranchedFiniteHurwitz_eq_some_iff]
  cases hdecode : decodeBranchedFiniteHurwitz code with
  | none =>
      simp [decodeAttachedFiniteHurwitz, hdecode]
  | some value =>
      rcases value with ⟨value, branch⟩
      by_cases hbranch : branch = p.branchIndex
      · subst branch
        simp [decodeAttachedFiniteHurwitz, hdecode,
          attachFiniteHurwitz]
      · have hbranch' : branch ≠ principalTurns p.totalAngle := by
          intro h
          apply hbranch
          simpa only [BranchPoint.branchIndex_eq_principalTurns] using h
        simp [decodeAttachedFiniteHurwitz, hdecode, hbranch',
          attachFiniteHurwitz]

theorem encodeAttachedFiniteHurwitz_injective (p : BranchPoint) :
    Function.Injective (encodeAttachedFiniteHurwitz p) := by
  intro x y h
  have hdecode := congrArg (decodeAttachedFiniteHurwitz p) h
  simpa using hdecode

/-- Force an arbitrary raw code value onto the canonical sheet of a branch
point and canonically re-encode it. -/
noncomputable def normalizeAttachedFiniteHurwitz
    (p : BranchPoint) (code : BranchedFiniteHurwitzCode) :
    BranchedFiniteHurwitzCode :=
  encodeAttachedFiniteHurwitz p code.rawValue.1

@[simp] theorem BranchedFiniteHurwitzCode.rawValue_normalizeAttached
    (p : BranchPoint) (code : BranchedFiniteHurwitzCode) :
    (normalizeAttachedFiniteHurwitz p code).rawValue =
      attachFiniteHurwitz p code.rawValue.1 := by
  simp [normalizeAttachedFiniteHurwitz, encodeAttachedFiniteHurwitz]

@[simp] theorem normalizeAttachedFiniteHurwitz_idempotent
    (p : BranchPoint) (code : BranchedFiniteHurwitzCode) :
    normalizeAttachedFiniteHurwitz p
        (normalizeAttachedFiniteHurwitz p code) =
      normalizeAttachedFiniteHurwitz p code := by
  simp [normalizeAttachedFiniteHurwitz, encodeAttachedFiniteHurwitz]

@[simp] theorem shiftCode_normalizeAttachedFiniteHurwitz
    (m : ℤ) (p : BranchPoint) (code : BranchedFiniteHurwitzCode) :
    shiftBranchedFiniteHurwitzCode m
        (normalizeAttachedFiniteHurwitz p code) =
      some (normalizeAttachedFiniteHurwitz (p.shiftByTurns m) code) := by
  simp [normalizeAttachedFiniteHurwitz, encodeAttachedFiniteHurwitz,
    attachFiniteHurwitz, shiftBranchedFiniteHurwitz]

/-- Attach an ordered pair of finite-Hurwitz values to two branch points. -/
def attachFiniteHurwitzPair
    (p q : BranchPoint) (x y : FiniteHurwitzValue) :
    BranchedFiniteHurwitzPair :=
  (attachFiniteHurwitz p x, attachFiniteHurwitz q y)

/-- Relative canonical sheet displacement of two branch points. -/
def BranchPoint.relativeBranchIndex (p q : BranchPoint) : ℤ :=
  q.branchIndex - p.branchIndex

@[simp] theorem relativeBranch_attachFiniteHurwitzPair
    (p q : BranchPoint) (x y : FiniteHurwitzValue) :
    relativeBranch (attachFiniteHurwitzPair p q x y) =
      p.relativeBranchIndex q := by
  rfl

@[simp] theorem BranchPoint.relativeBranchIndex_shiftByTurns
    (m : ℤ) (p q : BranchPoint) :
    (p.shiftByTurns m).relativeBranchIndex (q.shiftByTurns m) =
      p.relativeBranchIndex q := by
  simp [BranchPoint.relativeBranchIndex]

theorem canonicalRelativePair_attachFiniteHurwitzPair
    (p q : BranchPoint) (x y : FiniteHurwitzValue) :
    canonicalRelativePair (attachFiniteHurwitzPair p q x y) =
      ((x, 0), (y, p.relativeBranchIndex q)) := by
  simp [canonicalRelativePair, diagonalBranchShift,
    shiftBranchedFiniteHurwitz, attachFiniteHurwitzPair,
    attachFiniteHurwitz, BranchPoint.relativeBranchIndex, sub_eq_add_neg]

@[simp] theorem canonicalRelativePairCode_encodeAttachedPair
    (p q : BranchPoint) (x y : FiniteHurwitzValue) :
    canonicalRelativePairCode
        (encodeBranchedFiniteHurwitzPair
          (attachFiniteHurwitzPair p q x y)) =
      some (encodeBranchedFiniteHurwitzPair
        ((x, 0), (y, p.relativeBranchIndex q))) := by
  rw [canonicalRelativePairCode_encode,
    canonicalRelativePair_attachFiniteHurwitzPair]

end

end CNRSProblem2
