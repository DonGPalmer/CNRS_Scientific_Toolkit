import CNRSProblem2.CNRSIntegration
import Mathlib.Tactic

/-!
# CNRS Problem 2, Layer P2-L10: finite Hurwitz antiderivatives

This layer defines the coefficient-shift antiderivative on finite-support
Hurwitz families.  A chosen constant coefficient makes differentiation and
antidifferentiation exact inverse operations.  The construction is lifted to
the governed sparse codec and branch-aware carrier without introducing
analytic integration or infinite series.
-/

namespace CNRSProblem2

noncomputable section

namespace FiniteHurwitz

variable {R : Type*} [CommRing R]

/-- Insert a chosen constant coefficient and shift every existing coefficient
up by one outer index. -/
def antideriv (c : R) (x : FiniteHurwitz R) : FiniteHurwitz R :=
  single 0 c +
    ⟨x.coeff.sum fun n a => Finsupp.single (n + 1) a⟩

@[simp] theorem coeff_antideriv_zero (c : R) (x : FiniteHurwitz R) :
    antideriv c x 0 = c := by
  simp [antideriv, single]

@[simp] theorem coeff_antideriv_succ (c : R) (x : FiniteHurwitz R) (n : ℕ) :
    antideriv c x (n + 1) = x n := by
  change ((Finsupp.single 0 c +
    x.coeff.sum (fun i a => Finsupp.single (i + 1) a) : ℕ →₀ R) (n + 1)) =
      x.coeff n
  rw [Finsupp.add_apply]
  have hsum := congrArg (fun f : ℕ →₀ R => f n) (Finsupp.sum_single x.coeff)
  classical
  simpa [Finsupp.sum, Finsupp.single_apply] using hsum

/-- Differentiation is a right inverse of the chosen-constant antiderivative. -/
@[simp] theorem deriv_antideriv (c : R) (x : FiniteHurwitz R) :
    deriv (antideriv c x) = x := by
  ext n
  simp

/-- A finite Hurwitz family is recovered from its derivative and constant
coefficient. -/
@[simp] theorem antideriv_coeff_zero_deriv (x : FiniteHurwitz R) :
    antideriv (x 0) (deriv x) = x := by
  ext n
  cases n with
  | zero => simp
  | succ n => simp

theorem antideriv_injective (c : R) :
    Function.Injective (antideriv c : FiniteHurwitz R → FiniteHurwitz R) := by
  intro x y h
  have := congrArg deriv h
  simpa using this

/-- Equality is completely determined by the derivative and the chosen
constant coefficient. -/
theorem eq_iff_deriv_eq_and_coeff_zero_eq (x y : FiniteHurwitz R) :
    x = y ↔ deriv x = deriv y ∧ x 0 = y 0 := by
  constructor
  · rintro rfl
    exact ⟨rfl, rfl⟩
  · rintro ⟨hderiv, hzero⟩
    ext n
    cases n with
    | zero => exact hzero
    | succ n =>
        have := congrArg (fun z : FiniteHurwitz R => z n) hderiv
        simpa using this

end FiniteHurwitz

/-- Fail-closed decode-antidifferentiate-encode on the governed P2-L5 sparse
codec. -/
noncomputable def antiderivFiniteHurwitzCode
    (c : RAValue) (a : FiniteHurwitzCode) : Option FiniteHurwitzCode := do
  let x ← decodeFiniteHurwitz a
  pure (encodeFiniteHurwitz (FiniteHurwitz.antideriv c x))

@[simp] theorem antiderivFiniteHurwitzCode_encode
    (c : RAValue) (x : FiniteHurwitzValue) :
    antiderivFiniteHurwitzCode c (encodeFiniteHurwitz x) =
      some (encodeFiniteHurwitz (FiniteHurwitz.antideriv c x)) := by
  simp [antiderivFiniteHurwitzCode]

theorem antiderivFiniteHurwitzCode_eq_some_iff
    {c : RAValue} {a b : FiniteHurwitzCode} :
    antiderivFiniteHurwitzCode c a = some b ↔
      ∃ x : FiniteHurwitzValue,
        decodeFiniteHurwitz a = some x ∧
        b = encodeFiniteHurwitz (FiniteHurwitz.antideriv c x) := by
  cases ha : decodeFiniteHurwitz a with
  | none => simp [antiderivFiniteHurwitzCode, ha]
  | some x => simp [antiderivFiniteHurwitzCode, ha, eq_comm]

@[simp] theorem antiderivFiniteHurwitzCode_eq_none_iff
    (c : RAValue) (a : FiniteHurwitzCode) :
    antiderivFiniteHurwitzCode c a = none ↔
      decodeFiniteHurwitz a = none := by
  cases ha : decodeFiniteHurwitz a <;>
    simp [antiderivFiniteHurwitzCode, ha]

theorem value_antiderivFiniteHurwitzCode
    {c : RAValue} {a b : FiniteHurwitzCode}
    (h : antiderivFiniteHurwitzCode c a = some b) :
    b.value = FiniteHurwitz.antideriv c a.value := by
  rcases antiderivFiniteHurwitzCode_eq_some_iff.mp h with ⟨x, ha, rfl⟩
  rw [decodeFiniteHurwitz_eq_some_iff.mp ha]
  simp

@[simp] theorem derivCode_antiderivCode_encode
    (c : RAValue) (x : FiniteHurwitzValue) :
    (antiderivFiniteHurwitzCode c (encodeFiniteHurwitz x)).bind
        derivFiniteHurwitzCode =
      some (encodeFiniteHurwitz x) := by
  simp

@[simp] theorem antiderivCode_derivCode_encode
    (x : FiniteHurwitzValue) :
    (derivFiniteHurwitzCode (encodeFiniteHurwitz x)).bind
        (antiderivFiniteHurwitzCode (x 0)) =
      some (encodeFiniteHurwitz x) := by
  simp

/-- Branch-aware antiderivation preserves the explicit branch metadata. -/
def antiderivBranchedFiniteHurwitz
    (c : RAValue) (x : BranchedFiniteHurwitzValue) :
    BranchedFiniteHurwitzValue :=
  (FiniteHurwitz.antideriv c x.1, x.2)

@[simp] theorem antiderivBranchedFiniteHurwitz_value
    (c : RAValue) (x : BranchedFiniteHurwitzValue) :
    (antiderivBranchedFiniteHurwitz c x).1 =
      FiniteHurwitz.antideriv c x.1 := rfl

@[simp] theorem antiderivBranchedFiniteHurwitz_branch
    (c : RAValue) (x : BranchedFiniteHurwitzValue) :
    (antiderivBranchedFiniteHurwitz c x).2 = x.2 := rfl

@[simp] theorem deriv_antideriv_branched
    (c : RAValue) (x : BranchedFiniteHurwitzValue) :
    (FiniteHurwitz.deriv (antiderivBranchedFiniteHurwitz c x).1,
      (antiderivBranchedFiniteHurwitz c x).2) = x := by
  rcases x with ⟨x, k⟩
  simp [antiderivBranchedFiniteHurwitz]

@[simp] theorem antideriv_coeff_deriv_branched
    (x : BranchedFiniteHurwitzValue) :
    antiderivBranchedFiniteHurwitz (x.1 0)
        (FiniteHurwitz.deriv x.1, x.2) = x := by
  rcases x with ⟨x, k⟩
  simp [antiderivBranchedFiniteHurwitz]

/-- Fail-closed branch-preserving antiderivation on P2-L6 codes. -/
noncomputable def antiderivBranchedFiniteHurwitzCode
    (c : RAValue) (a : BranchedFiniteHurwitzCode) :
    Option BranchedFiniteHurwitzCode := do
  let x ← decodeBranchedFiniteHurwitz a
  pure (encodeBranchedFiniteHurwitz
    (antiderivBranchedFiniteHurwitz c x))

@[simp] theorem antiderivBranchedFiniteHurwitzCode_encode
    (c : RAValue) (x : BranchedFiniteHurwitzValue) :
    antiderivBranchedFiniteHurwitzCode c
        (encodeBranchedFiniteHurwitz x) =
      some (encodeBranchedFiniteHurwitz
        (antiderivBranchedFiniteHurwitz c x)) := by
  simp [antiderivBranchedFiniteHurwitzCode]

theorem antiderivBranchedFiniteHurwitzCode_eq_some_iff
    {c : RAValue} {a b : BranchedFiniteHurwitzCode} :
    antiderivBranchedFiniteHurwitzCode c a = some b ↔
      ∃ x : BranchedFiniteHurwitzValue,
        decodeBranchedFiniteHurwitz a = some x ∧
        b = encodeBranchedFiniteHurwitz
          (antiderivBranchedFiniteHurwitz c x) := by
  cases ha : decodeBranchedFiniteHurwitz a with
  | none => simp [antiderivBranchedFiniteHurwitzCode, ha]
  | some x => simp [antiderivBranchedFiniteHurwitzCode, ha, eq_comm]

@[simp] theorem antiderivBranchedFiniteHurwitzCode_eq_none_iff
    (c : RAValue) (a : BranchedFiniteHurwitzCode) :
    antiderivBranchedFiniteHurwitzCode c a = none ↔
      decodeBranchedFiniteHurwitz a = none := by
  cases ha : decodeBranchedFiniteHurwitz a <;>
    simp [antiderivBranchedFiniteHurwitzCode, ha]

theorem rawValue_antiderivBranchedFiniteHurwitzCode
    {c : RAValue} {a b : BranchedFiniteHurwitzCode}
    (h : antiderivBranchedFiniteHurwitzCode c a = some b) :
    b.rawValue = antiderivBranchedFiniteHurwitz c a.rawValue := by
  rcases antiderivBranchedFiniteHurwitzCode_eq_some_iff.mp h with
    ⟨x, ha, rfl⟩
  rw [decodeBranchedFiniteHurwitz_eq_some_iff.mp ha]
  simp

@[simp] theorem antiderivBranchedFiniteHurwitz_shift
    (m : ℤ) (c : RAValue) (x : BranchedFiniteHurwitzValue) :
    antiderivBranchedFiniteHurwitz c (shiftBranchedFiniteHurwitz m x) =
      shiftBranchedFiniteHurwitz m (antiderivBranchedFiniteHurwitz c x) := by
  rcases x with ⟨x, k⟩
  rfl

@[simp] theorem antiderivBranchedFiniteHurwitz_attach
    (c : RAValue) (p : BranchPoint) (x : FiniteHurwitzValue) :
    antiderivBranchedFiniteHurwitz c (attachFiniteHurwitz p x) =
      attachFiniteHurwitz p (FiniteHurwitz.antideriv c x) := by
  rfl

@[simp] theorem antiderivBranchedFiniteHurwitzCode_encodeAttached
    (c : RAValue) (p : BranchPoint) (x : FiniteHurwitzValue) :
    antiderivBranchedFiniteHurwitzCode c
        (encodeAttachedFiniteHurwitz p x) =
      some (encodeAttachedFiniteHurwitz p
        (FiniteHurwitz.antideriv c x)) := by
  simp [encodeAttachedFiniteHurwitz]

@[simp] theorem relativeBranch_antideriv_pair
    (c d : RAValue) (x y : BranchedFiniteHurwitzValue) :
    relativeBranch
        (antiderivBranchedFiniteHurwitz c x,
          antiderivBranchedFiniteHurwitz d y) =
      relativeBranch (x, y) := by
  rfl

end

end CNRSProblem2
