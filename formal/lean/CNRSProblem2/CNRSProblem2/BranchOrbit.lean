import CNRSProblem2.BranchTransport
import Mathlib.Tactic

/-!
# CNRS Problem 2, Layer P2-L8: diagonal branch-transport orbits

This layer classifies pairs of branch-aware finite CNRS-H states under a common
integer branch transport.  It introduces a canonical relative-branch normal
form, but no arithmetic between unequal branches.
-/

namespace CNRSProblem2

noncomputable section

abbrev BranchedFiniteHurwitzPair :=
  BranchedFiniteHurwitzValue × BranchedFiniteHurwitzValue

/-- Simultaneous transport of both entries of a pair. -/
def diagonalBranchShift (m : ℤ) (p : BranchedFiniteHurwitzPair) :
    BranchedFiniteHurwitzPair :=
  (shiftBranchedFiniteHurwitz m p.1,
    shiftBranchedFiniteHurwitz m p.2)

@[simp] theorem diagonalBranchShift_zero (p : BranchedFiniteHurwitzPair) :
    diagonalBranchShift 0 p = p := by
  rcases p with ⟨p, q⟩
  simp [diagonalBranchShift]

@[simp] theorem diagonalBranchShift_add
    (m n : ℤ) (p : BranchedFiniteHurwitzPair) :
    diagonalBranchShift m (diagonalBranchShift n p) =
      diagonalBranchShift (n + m) p := by
  rcases p with ⟨p, q⟩
  simp [diagonalBranchShift]

/-- The branch of the second entry relative to that of the first. -/
def relativeBranch (p : BranchedFiniteHurwitzPair) : ℤ :=
  p.2.2 - p.1.2

@[simp] theorem relativeBranch_diagonalBranchShift
    (m : ℤ) (p : BranchedFiniteHurwitzPair) :
    relativeBranch (diagonalBranchShift m p) = relativeBranch p := by
  simp [relativeBranch, diagonalBranchShift, shiftBranchedFiniteHurwitz]

/-- Two pairs are orbit-equivalent when one is a common transport of the other. -/
def BranchPairOrbit (p q : BranchedFiniteHurwitzPair) : Prop :=
  ∃ m : ℤ, q = diagonalBranchShift m p

@[refl] theorem BranchPairOrbit.refl (p : BranchedFiniteHurwitzPair) :
    BranchPairOrbit p p :=
  ⟨0, (diagonalBranchShift_zero p).symm⟩

@[symm] theorem BranchPairOrbit.symm {p q : BranchedFiniteHurwitzPair}
    (h : BranchPairOrbit p q) : BranchPairOrbit q p := by
  rcases h with ⟨m, rfl⟩
  refine ⟨-m, ?_⟩
  rw [diagonalBranchShift_add]
  simp

@[trans] theorem BranchPairOrbit.trans {p q r : BranchedFiniteHurwitzPair}
    (hpq : BranchPairOrbit p q) (hqr : BranchPairOrbit q r) :
    BranchPairOrbit p r := by
  rcases hpq with ⟨m, rfl⟩
  rcases hqr with ⟨n, rfl⟩
  exact ⟨m + n, diagonalBranchShift_add n m p⟩

theorem branchPairOrbit_iff
    (p q : BranchedFiniteHurwitzPair) :
    BranchPairOrbit p q ↔
      p.1.1 = q.1.1 ∧ p.2.1 = q.2.1 ∧
        relativeBranch p = relativeBranch q := by
  constructor
  · rintro ⟨m, rfl⟩
    simp [diagonalBranchShift, shiftBranchedFiniteHurwitz, relativeBranch]
  · rintro ⟨hx, hy, hd⟩
    rcases p with ⟨⟨x, k⟩, ⟨y, l⟩⟩
    rcases q with ⟨⟨x', k'⟩, ⟨y', l'⟩⟩
    change x = x' at hx
    change y = y' at hy
    change l - k = l' - k' at hd
    subst x'
    subst y'
    refine ⟨k' - k, ?_⟩
    simp [diagonalBranchShift, shiftBranchedFiniteHurwitz]
    omega

/-- Canonical orbit representative: first branch zero, second branch relative. -/
def canonicalRelativePair (p : BranchedFiniteHurwitzPair) :
    BranchedFiniteHurwitzPair :=
  diagonalBranchShift (-p.1.2) p

@[simp] theorem canonicalRelativePair_fst_branch
    (p : BranchedFiniteHurwitzPair) :
    (canonicalRelativePair p).1.2 = 0 := by
  simp [canonicalRelativePair, diagonalBranchShift,
    shiftBranchedFiniteHurwitz]

@[simp] theorem canonicalRelativePair_snd_branch
    (p : BranchedFiniteHurwitzPair) :
    (canonicalRelativePair p).2.2 = relativeBranch p := by
  simp [canonicalRelativePair, diagonalBranchShift,
    shiftBranchedFiniteHurwitz, relativeBranch, sub_eq_add_neg]

@[simp] theorem canonicalRelativePair_fst_value
    (p : BranchedFiniteHurwitzPair) :
    (canonicalRelativePair p).1.1 = p.1.1 := rfl

@[simp] theorem canonicalRelativePair_snd_value
    (p : BranchedFiniteHurwitzPair) :
    (canonicalRelativePair p).2.1 = p.2.1 := rfl

theorem canonicalRelativePair_orbit (p : BranchedFiniteHurwitzPair) :
    BranchPairOrbit p (canonicalRelativePair p) :=
  ⟨-p.1.2, rfl⟩

@[simp] theorem canonicalRelativePair_idempotent
    (p : BranchedFiniteHurwitzPair) :
    canonicalRelativePair (canonicalRelativePair p) =
      canonicalRelativePair p := by
  rcases p with ⟨⟨x, k⟩, ⟨y, l⟩⟩
  simp [canonicalRelativePair, diagonalBranchShift,
    shiftBranchedFiniteHurwitz]

theorem canonicalRelativePair_eq_iff
    (p q : BranchedFiniteHurwitzPair) :
    canonicalRelativePair p = canonicalRelativePair q ↔
      BranchPairOrbit p q := by
  rw [branchPairOrbit_iff]
  rcases p with ⟨⟨x, k⟩, ⟨y, l⟩⟩
  rcases q with ⟨⟨x', k'⟩, ⟨y', l'⟩⟩
  simp [canonicalRelativePair, diagonalBranchShift,
    shiftBranchedFiniteHurwitz, relativeBranch, sub_eq_add_neg]

@[simp] theorem relativeBranch_eq_zero_iff
    (p : BranchedFiniteHurwitzPair) :
    relativeBranch p = 0 ↔ p.1.2 = p.2.2 := by
  simp [relativeBranch, sub_eq_zero, eq_comm]

abbrev BranchedFiniteHurwitzPairCode :=
  BranchedFiniteHurwitzCode × BranchedFiniteHurwitzCode

noncomputable def encodeBranchedFiniteHurwitzPair
    (p : BranchedFiniteHurwitzPair) : BranchedFiniteHurwitzPairCode :=
  (encodeBranchedFiniteHurwitz p.1, encodeBranchedFiniteHurwitz p.2)

noncomputable def decodeBranchedFiniteHurwitzPair
    (c : BranchedFiniteHurwitzPairCode) : Option BranchedFiniteHurwitzPair := do
  let x ← decodeBranchedFiniteHurwitz c.1
  let y ← decodeBranchedFiniteHurwitz c.2
  pure (x, y)

@[simp] theorem decodeBranchedFiniteHurwitzPair_encode
    (p : BranchedFiniteHurwitzPair) :
    decodeBranchedFiniteHurwitzPair (encodeBranchedFiniteHurwitzPair p) =
      some p := by
  simp [decodeBranchedFiniteHurwitzPair, encodeBranchedFiniteHurwitzPair]

theorem encodeBranchedFiniteHurwitzPair_injective :
    Function.Injective encodeBranchedFiniteHurwitzPair := by
  intro p q h
  have := congrArg decodeBranchedFiniteHurwitzPair h
  simpa using this

theorem decodeBranchedFiniteHurwitzPair_eq_some_iff
    {c : BranchedFiniteHurwitzPairCode} {p : BranchedFiniteHurwitzPair} :
    decodeBranchedFiniteHurwitzPair c = some p ↔
      c = encodeBranchedFiniteHurwitzPair p := by
  rcases c with ⟨a, b⟩
  rcases p with ⟨x, y⟩
  constructor
  · intro h
    cases ha : decodeBranchedFiniteHurwitz a with
    | none => simp [decodeBranchedFiniteHurwitzPair, ha] at h
    | some x' =>
        cases hb : decodeBranchedFiniteHurwitz b with
        | none => simp [decodeBranchedFiniteHurwitzPair, ha, hb] at h
        | some y' =>
            have hp : (x', y') = (x, y) := Option.some.inj (by
              simpa [decodeBranchedFiniteHurwitzPair, ha, hb] using h)
            cases hp
            change (a, b) =
              (encodeBranchedFiniteHurwitz x, encodeBranchedFiniteHurwitz y)
            exact Prod.ext
              (decodeBranchedFiniteHurwitz_eq_some_iff.mp ha)
              (decodeBranchedFiniteHurwitz_eq_some_iff.mp hb)
  · intro h
    rw [h]
    exact decodeBranchedFiniteHurwitzPair_encode (x, y)

noncomputable def BranchedFiniteHurwitzPairCode.rawValue
    (c : BranchedFiniteHurwitzPairCode) : BranchedFiniteHurwitzPair :=
  (c.1.rawValue, c.2.rawValue)

@[simp] theorem BranchedFiniteHurwitzPairCode.rawValue_encode
    (p : BranchedFiniteHurwitzPair) :
    (encodeBranchedFiniteHurwitzPair p).rawValue = p := by
  simp [BranchedFiniteHurwitzPairCode.rawValue,
    encodeBranchedFiniteHurwitzPair]

noncomputable def normalizeBranchedFiniteHurwitzPair
    (c : BranchedFiniteHurwitzPairCode) : BranchedFiniteHurwitzPairCode :=
  encodeBranchedFiniteHurwitzPair c.rawValue

@[simp] theorem BranchedFiniteHurwitzPairCode.rawValue_normalize
    (c : BranchedFiniteHurwitzPairCode) :
    (normalizeBranchedFiniteHurwitzPair c).rawValue = c.rawValue := by
  simp [normalizeBranchedFiniteHurwitzPair]

@[simp] theorem normalizeBranchedFiniteHurwitzPair_idempotent
    (c : BranchedFiniteHurwitzPairCode) :
    normalizeBranchedFiniteHurwitzPair
        (normalizeBranchedFiniteHurwitzPair c) =
      normalizeBranchedFiniteHurwitzPair c := by
  simp [normalizeBranchedFiniteHurwitzPair]

/-- Fail-closed decode-normal-form-encode operation. -/
noncomputable def canonicalRelativePairCode
    (c : BranchedFiniteHurwitzPairCode) : Option BranchedFiniteHurwitzPairCode := do
  let p ← decodeBranchedFiniteHurwitzPair c
  pure (encodeBranchedFiniteHurwitzPair (canonicalRelativePair p))

@[simp] theorem canonicalRelativePairCode_encode
    (p : BranchedFiniteHurwitzPair) :
    canonicalRelativePairCode (encodeBranchedFiniteHurwitzPair p) =
      some (encodeBranchedFiniteHurwitzPair (canonicalRelativePair p)) := by
  simp [canonicalRelativePairCode]

@[simp] theorem canonicalRelativePairCode_eq_none_iff
    (c : BranchedFiniteHurwitzPairCode) :
    canonicalRelativePairCode c = none ↔
      decodeBranchedFiniteHurwitzPair c = none := by
  cases h : decodeBranchedFiniteHurwitzPair c <;>
    simp [canonicalRelativePairCode, h]

theorem canonicalRelativePairCode_eq_some_iff
    {c d : BranchedFiniteHurwitzPairCode} :
    canonicalRelativePairCode c = some d ↔
      ∃ p, decodeBranchedFiniteHurwitzPair c = some p ∧
        d = encodeBranchedFiniteHurwitzPair (canonicalRelativePair p) := by
  cases h : decodeBranchedFiniteHurwitzPair c with
  | none => simp [canonicalRelativePairCode, h]
  | some p => simp [canonicalRelativePairCode, h, eq_comm]

theorem canonicalRelativePairCode_rawValue
    {c d : BranchedFiniteHurwitzPairCode}
    (h : canonicalRelativePairCode c = some d) :
    d.rawValue = canonicalRelativePair c.rawValue := by
  rcases canonicalRelativePairCode_eq_some_iff.mp h with ⟨p, hc, rfl⟩
  rw [decodeBranchedFiniteHurwitzPair_eq_some_iff.mp hc]
  simp

@[simp] theorem canonicalRelativePairCode_normalize
    (c : BranchedFiniteHurwitzPairCode) :
    canonicalRelativePairCode (normalizeBranchedFiniteHurwitzPair c) =
      some (encodeBranchedFiniteHurwitzPair
        (canonicalRelativePair c.rawValue)) := by
  simp [normalizeBranchedFiniteHurwitzPair]

theorem add_pair_encode_eq_none_iff
    (p : BranchedFiniteHurwitzPair) :
    addBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz p.1)
        (encodeBranchedFiniteHurwitz p.2) = none ↔
      relativeBranch p ≠ 0 := by
  rcases p with ⟨⟨x, k⟩, ⟨y, l⟩⟩
  simp [addBranchedFiniteHurwitzCode, relativeBranch]
  omega

theorem mul_pair_encode_eq_none_iff
    (p : BranchedFiniteHurwitzPair) :
    mulBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz p.1)
        (encodeBranchedFiniteHurwitz p.2) = none ↔
      relativeBranch p ≠ 0 := by
  rcases p with ⟨⟨x, k⟩, ⟨y, l⟩⟩
  simp [mulBranchedFiniteHurwitzCode, relativeBranch]
  omega

end

end CNRSProblem2
