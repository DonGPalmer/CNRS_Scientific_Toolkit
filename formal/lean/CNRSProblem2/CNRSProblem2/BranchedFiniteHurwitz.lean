import CNRSProblem2.BranchSerialization
import CNRSProblem2.FiniteHurwitz
import Mathlib.Tactic

/-!
# CNRS Problem 2, Layer P2-L6: branch-aware finite CNRS-H states

This layer composes the governed P2-L3 branch-index codec with the governed
P2-L5 finite-Hurwitz codec. A branch is metadata for a finite CNRS-H value.
Unary operations preserve that metadata; binary operations fail closed unless
both decoded inputs carry exactly the same branch.
-/

namespace CNRSProblem2

noncomputable section

/-- A finite-support CNRS-H value together with its explicit branch index. -/
abbrev BranchedFiniteHurwitzValue := FiniteHurwitzValue × ℤ

/-- Marker-delimited P2-L6 code, reusing both governed component codecs. -/
abbrev BranchedFiniteHurwitzCode :=
  MarkerSerialization finiteHurwitzCodec branchIndexCodec

noncomputable def encodeBranchedFiniteHurwitz
    (x : BranchedFiniteHurwitzValue) : BranchedFiniteHurwitzCode :=
  encodeMarker finiteHurwitzCodec branchIndexCodec x

noncomputable def decodeBranchedFiniteHurwitz
    (code : BranchedFiniteHurwitzCode) :
    Option BranchedFiniteHurwitzValue :=
  decodeMarker finiteHurwitzCodec branchIndexCodec code

@[simp] theorem decodeBranchedFiniteHurwitz_encodeBranchedFiniteHurwitz
    (x : BranchedFiniteHurwitzValue) :
    decodeBranchedFiniteHurwitz (encodeBranchedFiniteHurwitz x) = some x :=
  decodeMarker_encodeMarker finiteHurwitzCodec branchIndexCodec x

theorem encodeBranchedFiniteHurwitz_injective :
    Function.Injective encodeBranchedFiniteHurwitz := by
  intro x y h
  have := congrArg decodeBranchedFiniteHurwitz h
  simpa using this

def ValidBranchedFiniteHurwitzCode
    (code : BranchedFiniteHurwitzCode) : Prop :=
  ∃ x, code = encodeBranchedFiniteHurwitz x

theorem encodeBranchedFiniteHurwitz_valid
    (x : BranchedFiniteHurwitzValue) :
    ValidBranchedFiniteHurwitzCode (encodeBranchedFiniteHurwitz x) :=
  ⟨x, rfl⟩

theorem decodeBranchedFiniteHurwitz_eq_some_iff
    {code : BranchedFiniteHurwitzCode}
    {x : BranchedFiniteHurwitzValue} :
    decodeBranchedFiniteHurwitz code = some x ↔
      code = encodeBranchedFiniteHurwitz x := by
  rcases code with ⟨valueCode, branchCode⟩
  rcases x with ⟨value, branch⟩
  constructor
  · intro h
    cases hv : decodeFiniteHurwitz valueCode with
    | none =>
        simp [decodeBranchedFiniteHurwitz, decodeMarker,
          finiteHurwitzCodec, branchIndexCodec, hv] at h
    | some v =>
        cases hb : decodeBranchIndex branchCode with
        | none =>
            simp [decodeBranchedFiniteHurwitz, decodeMarker,
              finiteHurwitzCodec, branchIndexCodec, hv, hb] at h
        | some k =>
            have hpair : (v, k) = (value, branch) := Option.some.inj (by
              simpa [decodeBranchedFiniteHurwitz, decodeMarker,
                finiteHurwitzCodec, branchIndexCodec, hv, hb] using h)
            cases hpair
            have hvcode :
                valueCode = encodeFiniteHurwitz value :=
              decodeFiniteHurwitz_eq_some_iff.mp hv
            have hbcode :
                branchCode = encodeBranchIndex branch :=
              decodeBranchIndex_eq_some_iff.mp hb
            rw [hvcode, hbcode]
            rfl
  · intro h
    rw [h]
    simp

theorem decodeBranchedFiniteHurwitz_isSome_iff
    (code : BranchedFiniteHurwitzCode) :
    (decodeBranchedFiniteHurwitz code).isSome ↔
      ValidBranchedFiniteHurwitzCode code := by
  constructor
  · intro h
    obtain ⟨x, hx⟩ := Option.isSome_iff_exists.mp h
    exact ⟨x, decodeBranchedFiniteHurwitz_eq_some_iff.mp hx⟩
  · rintro ⟨x, rfl⟩
    simp

/-- Total raw interpretation used only for normalization and value semantics.
It does not make a noncanonical code decodable. -/
noncomputable def BranchedFiniteHurwitzCode.rawValue
    (code : BranchedFiniteHurwitzCode) : BranchedFiniteHurwitzValue :=
  (code.value.value,
    unzigzag (Nat.ofDigits 4 code.branch.dropLast))

@[simp] theorem BranchedFiniteHurwitzCode.rawValue_encode
    (x : BranchedFiniteHurwitzValue) :
    (encodeBranchedFiniteHurwitz x).rawValue = x := by
  rcases x with ⟨value, branch⟩
  simp [BranchedFiniteHurwitzCode.rawValue,
    encodeBranchedFiniteHurwitz, encodeMarker, finiteHurwitzCodec,
    branchIndexCodec, encodeBranchIndex, ofDigits_canonicalBase4Digits]

noncomputable def normalizeBranchedFiniteHurwitz
    (code : BranchedFiniteHurwitzCode) : BranchedFiniteHurwitzCode :=
  encodeBranchedFiniteHurwitz code.rawValue

@[simp] theorem BranchedFiniteHurwitzCode.rawValue_normalize
    (code : BranchedFiniteHurwitzCode) :
    (normalizeBranchedFiniteHurwitz code).rawValue = code.rawValue := by
  simp [normalizeBranchedFiniteHurwitz]

theorem normalizeBranchedFiniteHurwitz_valid
    (code : BranchedFiniteHurwitzCode) :
    ValidBranchedFiniteHurwitzCode
      (normalizeBranchedFiniteHurwitz code) :=
  encodeBranchedFiniteHurwitz_valid code.rawValue

@[simp] theorem normalizeBranchedFiniteHurwitz_idempotent
    (code : BranchedFiniteHurwitzCode) :
    normalizeBranchedFiniteHurwitz
        (normalizeBranchedFiniteHurwitz code) =
      normalizeBranchedFiniteHurwitz code := by
  simp [normalizeBranchedFiniteHurwitz]

noncomputable def branchedFiniteHurwitzCodec :
    LosslessCodec BranchedFiniteHurwitzValue where
  Code := BranchedFiniteHurwitzCode
  encode := encodeBranchedFiniteHurwitz
  decode := decodeBranchedFiniteHurwitz
  decode_encode := decodeBranchedFiniteHurwitz_encodeBranchedFiniteHurwitz

noncomputable def addBranchedFiniteHurwitzCode
    (a b : BranchedFiniteHurwitzCode) :
    Option BranchedFiniteHurwitzCode := do
  let x ← decodeBranchedFiniteHurwitz a
  let y ← decodeBranchedFiniteHurwitz b
  if x.2 = y.2 then
    pure (encodeBranchedFiniteHurwitz (x.1 + y.1, x.2))
  else
    none

noncomputable def mulBranchedFiniteHurwitzCode
    (a b : BranchedFiniteHurwitzCode) :
    Option BranchedFiniteHurwitzCode := do
  let x ← decodeBranchedFiniteHurwitz a
  let y ← decodeBranchedFiniteHurwitz b
  if x.2 = y.2 then
    pure (encodeBranchedFiniteHurwitz (x.1 * y.1, x.2))
  else
    none

noncomputable def negBranchedFiniteHurwitzCode
    (a : BranchedFiniteHurwitzCode) :
    Option BranchedFiniteHurwitzCode := do
  let x ← decodeBranchedFiniteHurwitz a
  pure (encodeBranchedFiniteHurwitz (-x.1, x.2))

noncomputable def derivBranchedFiniteHurwitzCode
    (a : BranchedFiniteHurwitzCode) :
    Option BranchedFiniteHurwitzCode := do
  let x ← decodeBranchedFiniteHurwitz a
  pure (encodeBranchedFiniteHurwitz (FiniteHurwitz.deriv x.1, x.2))

@[simp] theorem addBranchedFiniteHurwitzCode_encode
    (x y : FiniteHurwitzValue) (k : ℤ) :
    addBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz (x, k))
        (encodeBranchedFiniteHurwitz (y, k)) =
      some (encodeBranchedFiniteHurwitz (x + y, k)) := by
  simp [addBranchedFiniteHurwitzCode]

@[simp] theorem mulBranchedFiniteHurwitzCode_encode
    (x y : FiniteHurwitzValue) (k : ℤ) :
    mulBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz (x, k))
        (encodeBranchedFiniteHurwitz (y, k)) =
      some (encodeBranchedFiniteHurwitz (x * y, k)) := by
  simp [mulBranchedFiniteHurwitzCode]

@[simp] theorem negBranchedFiniteHurwitzCode_encode
    (x : FiniteHurwitzValue) (k : ℤ) :
    negBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz (x, k)) =
      some (encodeBranchedFiniteHurwitz (-x, k)) := by
  simp [negBranchedFiniteHurwitzCode]

@[simp] theorem derivBranchedFiniteHurwitzCode_encode
    (x : FiniteHurwitzValue) (k : ℤ) :
    derivBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz (x, k)) =
      some (encodeBranchedFiniteHurwitz
        (FiniteHurwitz.deriv x, k)) := by
  simp [derivBranchedFiniteHurwitzCode]

theorem addBranchedFiniteHurwitzCode_encode_ne
    (x y : FiniteHurwitzValue) {k l : ℤ} (h : k ≠ l) :
    addBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz (x, k))
        (encodeBranchedFiniteHurwitz (y, l)) = none := by
  simp [addBranchedFiniteHurwitzCode, h]

theorem mulBranchedFiniteHurwitzCode_encode_ne
    (x y : FiniteHurwitzValue) {k l : ℤ} (h : k ≠ l) :
    mulBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz (x, k))
        (encodeBranchedFiniteHurwitz (y, l)) = none := by
  simp [mulBranchedFiniteHurwitzCode, h]

theorem addBranchedFiniteHurwitzCode_eq_some_iff
    {a b c : BranchedFiniteHurwitzCode} :
    addBranchedFiniteHurwitzCode a b = some c ↔
      ∃ x y : FiniteHurwitzValue, ∃ k : ℤ,
        decodeBranchedFiniteHurwitz a = some (x, k) ∧
        decodeBranchedFiniteHurwitz b = some (y, k) ∧
        c = encodeBranchedFiniteHurwitz (x + y, k) := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none => simp [addBranchedFiniteHurwitzCode, ha]
  | some x =>
      rcases x with ⟨x, k⟩
      cases hb : decodeBranchedFiniteHurwitz b with
      | none => simp [addBranchedFiniteHurwitzCode, ha, hb]
      | some y =>
          rcases y with ⟨y, l⟩
          by_cases hkl : k = l
          · subst l
            simp [addBranchedFiniteHurwitzCode, ha, hb, eq_comm]
          · simp [addBranchedFiniteHurwitzCode, ha, hb,
              Ne.symm hkl, eq_comm]

theorem mulBranchedFiniteHurwitzCode_eq_some_iff
    {a b c : BranchedFiniteHurwitzCode} :
    mulBranchedFiniteHurwitzCode a b = some c ↔
      ∃ x y : FiniteHurwitzValue, ∃ k : ℤ,
        decodeBranchedFiniteHurwitz a = some (x, k) ∧
        decodeBranchedFiniteHurwitz b = some (y, k) ∧
        c = encodeBranchedFiniteHurwitz (x * y, k) := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none => simp [mulBranchedFiniteHurwitzCode, ha]
  | some x =>
      rcases x with ⟨x, k⟩
      cases hb : decodeBranchedFiniteHurwitz b with
      | none => simp [mulBranchedFiniteHurwitzCode, ha, hb]
      | some y =>
          rcases y with ⟨y, l⟩
          by_cases hkl : k = l
          · subst l
            simp [mulBranchedFiniteHurwitzCode, ha, hb, eq_comm]
          · simp [mulBranchedFiniteHurwitzCode, ha, hb,
              Ne.symm hkl, eq_comm]

theorem negBranchedFiniteHurwitzCode_eq_some_iff
    {a c : BranchedFiniteHurwitzCode} :
    negBranchedFiniteHurwitzCode a = some c ↔
      ∃ x : FiniteHurwitzValue, ∃ k : ℤ,
        decodeBranchedFiniteHurwitz a = some (x, k) ∧
        c = encodeBranchedFiniteHurwitz (-x, k) := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none => simp [negBranchedFiniteHurwitzCode, ha]
  | some x =>
      rcases x with ⟨x, k⟩
      simp [negBranchedFiniteHurwitzCode, ha, eq_comm]

theorem derivBranchedFiniteHurwitzCode_eq_some_iff
    {a c : BranchedFiniteHurwitzCode} :
    derivBranchedFiniteHurwitzCode a = some c ↔
      ∃ x : FiniteHurwitzValue, ∃ k : ℤ,
        decodeBranchedFiniteHurwitz a = some (x, k) ∧
        c = encodeBranchedFiniteHurwitz
          (FiniteHurwitz.deriv x, k) := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none => simp [derivBranchedFiniteHurwitzCode, ha]
  | some x =>
      rcases x with ⟨x, k⟩
      simp [derivBranchedFiniteHurwitzCode, ha, eq_comm]

@[simp] theorem addBranchedFiniteHurwitzCode_eq_none_iff
    (a b : BranchedFiniteHurwitzCode) :
    addBranchedFiniteHurwitzCode a b = none ↔
      decodeBranchedFiniteHurwitz a = none ∨
      decodeBranchedFiniteHurwitz b = none ∨
      ∃ x y : FiniteHurwitzValue, ∃ k l : ℤ,
        decodeBranchedFiniteHurwitz a = some (x, k) ∧
        decodeBranchedFiniteHurwitz b = some (y, l) ∧ k ≠ l := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none => simp [addBranchedFiniteHurwitzCode, ha]
  | some x =>
      rcases x with ⟨x, k⟩
      cases hb : decodeBranchedFiniteHurwitz b with
      | none => simp [addBranchedFiniteHurwitzCode, ha, hb]
      | some y =>
          rcases y with ⟨y, l⟩
          by_cases hkl : k = l
          · subst l
            simp [addBranchedFiniteHurwitzCode, ha, hb]
          · simp [addBranchedFiniteHurwitzCode, ha, hb, hkl]

@[simp] theorem mulBranchedFiniteHurwitzCode_eq_none_iff
    (a b : BranchedFiniteHurwitzCode) :
    mulBranchedFiniteHurwitzCode a b = none ↔
      decodeBranchedFiniteHurwitz a = none ∨
      decodeBranchedFiniteHurwitz b = none ∨
      ∃ x y : FiniteHurwitzValue, ∃ k l : ℤ,
        decodeBranchedFiniteHurwitz a = some (x, k) ∧
        decodeBranchedFiniteHurwitz b = some (y, l) ∧ k ≠ l := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none => simp [mulBranchedFiniteHurwitzCode, ha]
  | some x =>
      rcases x with ⟨x, k⟩
      cases hb : decodeBranchedFiniteHurwitz b with
      | none => simp [mulBranchedFiniteHurwitzCode, ha, hb]
      | some y =>
          rcases y with ⟨y, l⟩
          by_cases hkl : k = l
          · subst l
            simp [mulBranchedFiniteHurwitzCode, ha, hb]
          · simp [mulBranchedFiniteHurwitzCode, ha, hb, hkl]

@[simp] theorem negBranchedFiniteHurwitzCode_eq_none_iff
    (a : BranchedFiniteHurwitzCode) :
    negBranchedFiniteHurwitzCode a = none ↔
      decodeBranchedFiniteHurwitz a = none := by
  cases ha : decodeBranchedFiniteHurwitz a <;>
    simp [negBranchedFiniteHurwitzCode, ha]

@[simp] theorem derivBranchedFiniteHurwitzCode_eq_none_iff
    (a : BranchedFiniteHurwitzCode) :
    derivBranchedFiniteHurwitzCode a = none ↔
      decodeBranchedFiniteHurwitz a = none := by
  cases ha : decodeBranchedFiniteHurwitz a <;>
    simp [derivBranchedFiniteHurwitzCode, ha]

theorem rawValue_addBranchedFiniteHurwitzCode
    {a b c : BranchedFiniteHurwitzCode}
    (h : addBranchedFiniteHurwitzCode a b = some c) :
    c.rawValue =
      (a.rawValue.1 + b.rawValue.1, a.rawValue.2) := by
  rcases addBranchedFiniteHurwitzCode_eq_some_iff.mp h with
    ⟨x, y, k, ha, hb, rfl⟩
  rw [decodeBranchedFiniteHurwitz_eq_some_iff.mp ha,
    decodeBranchedFiniteHurwitz_eq_some_iff.mp hb]
  simp

theorem rawValue_mulBranchedFiniteHurwitzCode
    {a b c : BranchedFiniteHurwitzCode}
    (h : mulBranchedFiniteHurwitzCode a b = some c) :
    c.rawValue =
      (a.rawValue.1 * b.rawValue.1, a.rawValue.2) := by
  rcases mulBranchedFiniteHurwitzCode_eq_some_iff.mp h with
    ⟨x, y, k, ha, hb, rfl⟩
  rw [decodeBranchedFiniteHurwitz_eq_some_iff.mp ha,
    decodeBranchedFiniteHurwitz_eq_some_iff.mp hb]
  simp

theorem rawValue_negBranchedFiniteHurwitzCode
    {a c : BranchedFiniteHurwitzCode}
    (h : negBranchedFiniteHurwitzCode a = some c) :
    c.rawValue = (-a.rawValue.1, a.rawValue.2) := by
  rcases negBranchedFiniteHurwitzCode_eq_some_iff.mp h with
    ⟨x, k, ha, rfl⟩
  rw [decodeBranchedFiniteHurwitz_eq_some_iff.mp ha]
  simp

theorem rawValue_derivBranchedFiniteHurwitzCode
    {a c : BranchedFiniteHurwitzCode}
    (h : derivBranchedFiniteHurwitzCode a = some c) :
    c.rawValue =
      (FiniteHurwitz.deriv a.rawValue.1, a.rawValue.2) := by
  rcases derivBranchedFiniteHurwitzCode_eq_some_iff.mp h with
    ⟨x, k, ha, rfl⟩
  rw [decodeBranchedFiniteHurwitz_eq_some_iff.mp ha]
  simp

end

end CNRSProblem2
