import CNRSProblem2.BranchedFiniteHurwitz
import Mathlib.Tactic

/-!
# CNRS Problem 2, Layer P2-L7: canonical branch transport

This layer equips the governed P2-L6 branch-aware finite CNRS-H state with an
explicit integer reindexing action. Transport changes branch metadata only.
It is not cross-branch arithmetic: P2-L6 binary operations still require equal
decoded branches, and simultaneous transport preserves that condition exactly.
-/

namespace CNRSProblem2

noncomputable section

/-- Explicit branch reindexing, leaving the finite-Hurwitz value unchanged. -/
def shiftBranchedFiniteHurwitz
    (m : ℤ) (x : BranchedFiniteHurwitzValue) :
    BranchedFiniteHurwitzValue :=
  (x.1, x.2 + m)

@[simp] theorem shiftBranchedFiniteHurwitz_fst
    (m : ℤ) (x : BranchedFiniteHurwitzValue) :
    (shiftBranchedFiniteHurwitz m x).1 = x.1 :=
  rfl

@[simp] theorem shiftBranchedFiniteHurwitz_snd
    (m : ℤ) (x : BranchedFiniteHurwitzValue) :
    (shiftBranchedFiniteHurwitz m x).2 = x.2 + m :=
  rfl

@[simp] theorem shiftBranchedFiniteHurwitz_zero
    (x : BranchedFiniteHurwitzValue) :
    shiftBranchedFiniteHurwitz 0 x = x := by
  rcases x with ⟨x, k⟩
  simp [shiftBranchedFiniteHurwitz]

@[simp] theorem shiftBranchedFiniteHurwitz_add
    (m n : ℤ) (x : BranchedFiniteHurwitzValue) :
    shiftBranchedFiniteHurwitz m
        (shiftBranchedFiniteHurwitz n x) =
      shiftBranchedFiniteHurwitz (n + m) x := by
  rcases x with ⟨x, k⟩
  simp [shiftBranchedFiniteHurwitz, add_assoc]

theorem shiftBranchedFiniteHurwitz_injective
    (m : ℤ) :
    Function.Injective (shiftBranchedFiniteHurwitz m) := by
  intro x y h
  rcases x with ⟨x, k⟩
  rcases y with ⟨y, l⟩
  simp [shiftBranchedFiniteHurwitz] at h
  exact Prod.ext h.1 h.2

@[simp] theorem shiftBranchedFiniteHurwitz_inj
    (m : ℤ) (x y : BranchedFiniteHurwitzValue) :
    shiftBranchedFiniteHurwitz m x =
        shiftBranchedFiniteHurwitz m y ↔
      x = y :=
  (shiftBranchedFiniteHurwitz_injective m).eq_iff

@[simp] theorem shiftBranchedFiniteHurwitz_neg
    (m : ℤ) (x : FiniteHurwitzValue) (k : ℤ) :
    shiftBranchedFiniteHurwitz m (-x, k) =
      (-(shiftBranchedFiniteHurwitz m (x, k)).1,
        (shiftBranchedFiniteHurwitz m (x, k)).2) := by
  rfl

@[simp] theorem shiftBranchedFiniteHurwitz_deriv
    (m : ℤ) (x : FiniteHurwitzValue) (k : ℤ) :
    shiftBranchedFiniteHurwitz m (FiniteHurwitz.deriv x, k) =
      (FiniteHurwitz.deriv
          (shiftBranchedFiniteHurwitz m (x, k)).1,
        (shiftBranchedFiniteHurwitz m (x, k)).2) := by
  rfl

@[simp] theorem shiftBranchedFiniteHurwitz_branch_eq_iff
    (m : ℤ) (x y : BranchedFiniteHurwitzValue) :
    (shiftBranchedFiniteHurwitz m x).2 =
        (shiftBranchedFiniteHurwitz m y).2 ↔
      x.2 = y.2 := by
  simp [shiftBranchedFiniteHurwitz]

@[simp] theorem shiftBranchedFiniteHurwitz_branch_sub
    (m : ℤ) (x y : BranchedFiniteHurwitzValue) :
    (shiftBranchedFiniteHurwitz m x).2 -
        (shiftBranchedFiniteHurwitz m y).2 =
      x.2 - y.2 := by
  simp [shiftBranchedFiniteHurwitz]

/-- Fail-closed decode-transport-encode operation on P2-L6 codes. -/
noncomputable def shiftBranchedFiniteHurwitzCode
    (m : ℤ) (code : BranchedFiniteHurwitzCode) :
    Option BranchedFiniteHurwitzCode := do
  let x ← decodeBranchedFiniteHurwitz code
  pure (encodeBranchedFiniteHurwitz
    (shiftBranchedFiniteHurwitz m x))

@[simp] theorem shiftBranchedFiniteHurwitzCode_encode
    (m : ℤ) (x : BranchedFiniteHurwitzValue) :
    shiftBranchedFiniteHurwitzCode m
        (encodeBranchedFiniteHurwitz x) =
      some (encodeBranchedFiniteHurwitz
        (shiftBranchedFiniteHurwitz m x)) := by
  simp [shiftBranchedFiniteHurwitzCode]

theorem shiftBranchedFiniteHurwitzCode_eq_some_iff
    {m : ℤ} {a c : BranchedFiniteHurwitzCode} :
    shiftBranchedFiniteHurwitzCode m a = some c ↔
      ∃ x : BranchedFiniteHurwitzValue,
        decodeBranchedFiniteHurwitz a = some x ∧
        c = encodeBranchedFiniteHurwitz
          (shiftBranchedFiniteHurwitz m x) := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none => simp [shiftBranchedFiniteHurwitzCode, ha]
  | some x =>
      simp [shiftBranchedFiniteHurwitzCode, ha, eq_comm]

@[simp] theorem shiftBranchedFiniteHurwitzCode_eq_none_iff
    (m : ℤ) (a : BranchedFiniteHurwitzCode) :
    shiftBranchedFiniteHurwitzCode m a = none ↔
      decodeBranchedFiniteHurwitz a = none := by
  cases ha : decodeBranchedFiniteHurwitz a <;>
    simp [shiftBranchedFiniteHurwitzCode, ha]

theorem shiftBranchedFiniteHurwitzCode_valid
    {m : ℤ} {a c : BranchedFiniteHurwitzCode}
    (h : shiftBranchedFiniteHurwitzCode m a = some c) :
    ValidBranchedFiniteHurwitzCode c := by
  rcases shiftBranchedFiniteHurwitzCode_eq_some_iff.mp h with
    ⟨x, _, rfl⟩
  exact encodeBranchedFiniteHurwitz_valid _

theorem rawValue_shiftBranchedFiniteHurwitzCode
    {m : ℤ} {a c : BranchedFiniteHurwitzCode}
    (h : shiftBranchedFiniteHurwitzCode m a = some c) :
    c.rawValue =
      shiftBranchedFiniteHurwitz m a.rawValue := by
  rcases shiftBranchedFiniteHurwitzCode_eq_some_iff.mp h with
    ⟨x, ha, rfl⟩
  rw [decodeBranchedFiniteHurwitz_eq_some_iff.mp ha]
  simp

@[simp] theorem shiftBranchedFiniteHurwitzCode_normalize
    (m : ℤ) (a : BranchedFiniteHurwitzCode) :
    shiftBranchedFiniteHurwitzCode m
        (normalizeBranchedFiniteHurwitz a) =
      some (encodeBranchedFiniteHurwitz
        (shiftBranchedFiniteHurwitz m a.rawValue)) := by
  simp [normalizeBranchedFiniteHurwitz]

@[simp] theorem shiftBranchedFiniteHurwitzCode_zero
    (a : BranchedFiniteHurwitzCode) :
    shiftBranchedFiniteHurwitzCode 0 a =
      (decodeBranchedFiniteHurwitz a).map
        encodeBranchedFiniteHurwitz := by
  cases ha : decodeBranchedFiniteHurwitz a <;>
    simp [shiftBranchedFiniteHurwitzCode, ha]

theorem shiftBranchedFiniteHurwitzCode_add
    (m n : ℤ) (a : BranchedFiniteHurwitzCode) :
    (shiftBranchedFiniteHurwitzCode n a >>= 
        shiftBranchedFiniteHurwitzCode m) =
      shiftBranchedFiniteHurwitzCode (n + m) a := by
  cases ha : decodeBranchedFiniteHurwitz a <;>
    simp [shiftBranchedFiniteHurwitzCode, ha]

theorem shiftBranchedFiniteHurwitzCode_neg_commute
    (m : ℤ) (a : BranchedFiniteHurwitzCode) :
    (shiftBranchedFiniteHurwitzCode m a >>=
        negBranchedFiniteHurwitzCode) =
      (negBranchedFiniteHurwitzCode a >>=
        shiftBranchedFiniteHurwitzCode m) := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none =>
      simp [shiftBranchedFiniteHurwitzCode,
        negBranchedFiniteHurwitzCode, ha]
  | some x =>
      rcases x with ⟨x, k⟩
      simp [shiftBranchedFiniteHurwitzCode,
        negBranchedFiniteHurwitzCode, ha,
        shiftBranchedFiniteHurwitz]

theorem shiftBranchedFiniteHurwitzCode_deriv_commute
    (m : ℤ) (a : BranchedFiniteHurwitzCode) :
    (shiftBranchedFiniteHurwitzCode m a >>=
        derivBranchedFiniteHurwitzCode) =
      (derivBranchedFiniteHurwitzCode a >>=
        shiftBranchedFiniteHurwitzCode m) := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none =>
      simp [shiftBranchedFiniteHurwitzCode,
        derivBranchedFiniteHurwitzCode, ha]
  | some x =>
      rcases x with ⟨x, k⟩
      simp [shiftBranchedFiniteHurwitzCode,
        derivBranchedFiniteHurwitzCode, ha,
        shiftBranchedFiniteHurwitz]

@[simp] theorem addBranchedFiniteHurwitzCode_shift_encode
    (m : ℤ) (x y : FiniteHurwitzValue) (k : ℤ) :
    addBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz
          (shiftBranchedFiniteHurwitz m (x, k)))
        (encodeBranchedFiniteHurwitz
          (shiftBranchedFiniteHurwitz m (y, k))) =
      some (encodeBranchedFiniteHurwitz
        (shiftBranchedFiniteHurwitz m (x + y, k))) := by
  simp [shiftBranchedFiniteHurwitz]

@[simp] theorem mulBranchedFiniteHurwitzCode_shift_encode
    (m : ℤ) (x y : FiniteHurwitzValue) (k : ℤ) :
    mulBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz
          (shiftBranchedFiniteHurwitz m (x, k)))
        (encodeBranchedFiniteHurwitz
          (shiftBranchedFiniteHurwitz m (y, k))) =
      some (encodeBranchedFiniteHurwitz
        (shiftBranchedFiniteHurwitz m (x * y, k))) := by
  simp [shiftBranchedFiniteHurwitz]

theorem addBranchedFiniteHurwitzCode_shift_encode_ne
    (m : ℤ) (x y : FiniteHurwitzValue)
    {k l : ℤ} (h : k ≠ l) :
    addBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz
          (shiftBranchedFiniteHurwitz m (x, k)))
        (encodeBranchedFiniteHurwitz
          (shiftBranchedFiniteHurwitz m (y, l))) = none := by
  apply addBranchedFiniteHurwitzCode_encode_ne
  simpa [shiftBranchedFiniteHurwitz] using h

theorem mulBranchedFiniteHurwitzCode_shift_encode_ne
    (m : ℤ) (x y : FiniteHurwitzValue)
    {k l : ℤ} (h : k ≠ l) :
    mulBranchedFiniteHurwitzCode
        (encodeBranchedFiniteHurwitz
          (shiftBranchedFiniteHurwitz m (x, k)))
        (encodeBranchedFiniteHurwitz
          (shiftBranchedFiniteHurwitz m (y, l))) = none := by
  apply mulBranchedFiniteHurwitzCode_encode_ne
  simpa [shiftBranchedFiniteHurwitz] using h

end

end CNRSProblem2
