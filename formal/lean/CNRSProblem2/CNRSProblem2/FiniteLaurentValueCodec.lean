import CNRSProblem2.BranchSerialization
import CnrsQ2.FiniteSupportCarrierIntegration
import CNRSCore.Finiteness
import Mathlib.Tactic

/-!
# CNRS Problem 2, Layer P2-L4: finite-Laurent CNRS-A value codec

This module deliberately reuses the governed `CnrsQ2` characterization of
`R_A = ℤ[i][(-2+i)⁻¹]`.  It adds the P2-facing finite code, a canonical
choice of code for every value, fail-closed decoding, exact value operations,
and composition with the P2-L3 branch codec.

The canonical encoder is noncomputable because the governed CnrsQ2 carrier
theorem is existential.  All representation and algebra laws are exact.
-/

open Zsqrtd

namespace CNRSProblem2

noncomputable section

private theorem betaFrac_ne_zero : CnrsQ2.betaFrac ≠ 0 := by
  intro h
  have hn := CnrsQ2.norm_fracToPadic_beta
  change ‖CnrsQ2.fracToPadic CnrsQ2.betaFrac‖ = (5 : ℝ)⁻¹ at hn
  rw [h, map_zero] at hn
  norm_num at hn

/-- The already-governed set `R_A`, packaged as a subring of the Gaussian
fraction field. -/
noncomputable def finiteLaurentSubring : Subring CnrsQ2.GaussianFrac where
  carrier := CnrsQ2.RAFrac
  zero_mem' := by
    refine ⟨0, 0, ?_⟩
    simp [CnrsQ2.betaFrac]
  one_mem' := by
    refine ⟨1, 0, ?_⟩
    simp [CnrsQ2.betaFrac]
  add_mem' := by
    rintro x y ⟨z, m, rfl⟩ ⟨w, n, rfl⟩
    refine ⟨z * CnrsQ2.beta ^ n + w * CnrsQ2.beta ^ m, m + n, ?_⟩
    have hbeta :
        algebraMap GaussianInt CnrsQ2.GaussianFrac CnrsQ2.beta ≠ 0 := by
      simpa [CnrsQ2.betaFrac] using betaFrac_ne_zero
    simp only [map_add, map_mul, map_pow, pow_add]
    simp only [CnrsQ2.betaFrac]
    field_simp [hbeta]
  neg_mem' := by
    rintro x ⟨z, m, rfl⟩
    refine ⟨-z, m, ?_⟩
    simp only [map_neg]
    ring
  mul_mem' := by
    rintro x y ⟨z, m, rfl⟩ ⟨w, n, rfl⟩
    refine ⟨z * w, m + n, ?_⟩
    simp only [map_mul, pow_add]
    field_simp [betaFrac_ne_zero]

/-- Exact finite-Laurent CNRS-A values. -/
abbrev RAValue := finiteLaurentSubring

/-- A finite Laurent word: an LSD-first canonical digit list divided by a
natural power of `β = -2+i`. -/
structure FiniteLaurentCode where
  shift : ℕ
  digits : List (Fin 5)
deriving DecidableEq

/-- Exact evaluation of a finite Laurent code. -/
noncomputable def FiniteLaurentCode.eval (code : FiniteLaurentCode) :
    CnrsQ2.GaussianFrac :=
  CnrsQ2.evalFiniteLaurent code.shift code.digits

theorem FiniteLaurentCode.eval_mem (code : FiniteLaurentCode) :
    code.eval ∈ CnrsQ2.RAFrac :=
  CnrsQ2.evalFiniteLaurent_mem_RAFrac code.shift code.digits

/-- Every raw finite code denotes an exact `R_A` value. -/
noncomputable def FiniteLaurentCode.value (code : FiniteLaurentCode) : RAValue :=
  ⟨code.eval, code.eval_mem⟩

/-- A denominator shift represents a value when it admits a Gaussian
numerator at that shift. -/
def HasLaurentShift (x : RAValue) (m : ℕ) : Prop :=
  ∃ z : GaussianInt,
    (x : CnrsQ2.GaussianFrac) =
      algebraMap GaussianInt CnrsQ2.GaussianFrac z / CnrsQ2.betaFrac ^ m

theorem hasLaurentShift_exists (x : RAValue) : ∃ m, HasLaurentShift x m := by
  rcases x.property with ⟨z, m, hz⟩
  exact ⟨m, z, hz⟩

/-- Least denominator shift available for the value. -/
noncomputable def canonicalLaurentShift (x : RAValue) : ℕ :=
  by
    classical
    exact Nat.find (hasLaurentShift_exists x)

/-- The numerator at the least denominator shift. -/
noncomputable def canonicalLaurentNumerator (x : RAValue) : GaussianInt :=
  by
    classical
    exact Classical.choose (Nat.find_spec (hasLaurentShift_exists x))

theorem canonicalLaurentNumerator_spec (x : RAValue) :
    (x : CnrsQ2.GaussianFrac) =
      algebraMap GaussianInt CnrsQ2.GaussianFrac (canonicalLaurentNumerator x) /
        CnrsQ2.betaFrac ^ canonicalLaurentShift x :=
  by
    classical
    exact Classical.choose_spec (Nat.find_spec (hasLaurentShift_exists x))

/-- Canonical finite-Laurent encoding: least denominator shift followed by
the governed constructive greedy expansion of its Gaussian numerator. -/
noncomputable def encodeFiniteLaurent (x : RAValue) : FiniteLaurentCode where
  shift := canonicalLaurentShift x
  digits := CNRSCore.greedyDigits (canonicalLaurentNumerator x)

@[simp] theorem eval_encodeFiniteLaurent (x : RAValue) :
    (encodeFiniteLaurent x).eval = (x : CnrsQ2.GaussianFrac) := by
  simp only [encodeFiniteLaurent, FiniteLaurentCode.eval,
    CnrsQ2.evalFiniteLaurent, CnrsQ2.evalGaussianDigits,
    CNRSCore.greedyDigits_correct]
  exact (canonicalLaurentNumerator_spec x).symm

@[simp] theorem value_encodeFiniteLaurent (x : RAValue) :
    (encodeFiniteLaurent x).value = x := by
  apply Subtype.ext
  exact eval_encodeFiniteLaurent x

/-- Decode only the exact output of the canonical encoder.  Re-encoding makes
all noncanonical alternatives fail closed. -/
noncomputable def decodeFiniteLaurent (code : FiniteLaurentCode) : Option RAValue :=
  let x := code.value
  if code = encodeFiniteLaurent x then some x else none

def ValidFiniteLaurentCode (code : FiniteLaurentCode) : Prop :=
  ∃ x : RAValue, code = encodeFiniteLaurent x

theorem encodeFiniteLaurent_valid (x : RAValue) :
    ValidFiniteLaurentCode (encodeFiniteLaurent x) :=
  ⟨x, rfl⟩

@[simp] theorem decodeFiniteLaurent_encodeFiniteLaurent (x : RAValue) :
    decodeFiniteLaurent (encodeFiniteLaurent x) = some x := by
  simp [decodeFiniteLaurent, value_encodeFiniteLaurent]

theorem encodeFiniteLaurent_injective :
    Function.Injective encodeFiniteLaurent := by
  intro x y h
  have := congrArg decodeFiniteLaurent h
  simpa using this

theorem decodeFiniteLaurent_eq_some_iff
    {code : FiniteLaurentCode} {x : RAValue} :
    decodeFiniteLaurent code = some x ↔ code = encodeFiniteLaurent x := by
  unfold decodeFiniteLaurent
  dsimp only
  split_ifs with hcanon
  · constructor
    · intro h
      have hx : code.value = x := Option.some.inj h
      simp [hx] at hcanon
      exact hcanon
    · rintro rfl
      simp
  · constructor
    · simp
    · intro h
      subst code
      apply hcanon
      simp

theorem decodeFiniteLaurent_isSome_iff (code : FiniteLaurentCode) :
    (decodeFiniteLaurent code).isSome ↔ ValidFiniteLaurentCode code := by
  constructor
  · intro h
    obtain ⟨x, hx⟩ := Option.isSome_iff_exists.mp h
    exact ⟨x, decodeFiniteLaurent_eq_some_iff.mp hx⟩
  · rintro ⟨x, rfl⟩
    simp

/-- Canonical normalization of an arbitrary finite Laurent code. -/
noncomputable def normalizeFiniteLaurent (code : FiniteLaurentCode) :
    FiniteLaurentCode :=
  encodeFiniteLaurent code.value

theorem normalizeFiniteLaurent_valid (code : FiniteLaurentCode) :
    ValidFiniteLaurentCode (normalizeFiniteLaurent code) :=
  encodeFiniteLaurent_valid code.value

@[simp] theorem eval_normalizeFiniteLaurent (code : FiniteLaurentCode) :
    (normalizeFiniteLaurent code).eval = code.eval := by
  exact eval_encodeFiniteLaurent code.value

@[simp] theorem normalizeFiniteLaurent_idempotent (code : FiniteLaurentCode) :
    normalizeFiniteLaurent (normalizeFiniteLaurent code) =
      normalizeFiniteLaurent code := by
  simp [normalizeFiniteLaurent]

/-- P2-L4's concrete lossless CNRS-A value codec. -/
noncomputable def finiteLaurentCodec : LosslessCodec RAValue where
  Code := FiniteLaurentCode
  encode := encodeFiniteLaurent
  decode := decodeFiniteLaurent
  decode_encode := decodeFiniteLaurent_encodeFiniteLaurent

/-- The finite-Laurent value map into the Gaussian fraction field. -/
noncomputable def finiteLaurentValueMap : RAValue →+* CnrsQ2.GaussianFrac :=
  finiteLaurentSubring.subtype

theorem finiteLaurentValueMap_add (x y : RAValue) :
    finiteLaurentValueMap (x + y) = finiteLaurentValueMap x + finiteLaurentValueMap y :=
  map_add finiteLaurentValueMap x y

theorem finiteLaurentValueMap_mul (x y : RAValue) :
    finiteLaurentValueMap (x * y) = finiteLaurentValueMap x * finiteLaurentValueMap y :=
  map_mul finiteLaurentValueMap x y

/-- Fail-closed decode-operate-encode addition on finite codes. -/
noncomputable def addFiniteLaurentCode (a b : FiniteLaurentCode) :
    Option FiniteLaurentCode := do
  let x ← decodeFiniteLaurent a
  let y ← decodeFiniteLaurent b
  pure (encodeFiniteLaurent (x + y))

/-- Fail-closed decode-operate-encode multiplication on finite codes. -/
noncomputable def mulFiniteLaurentCode (a b : FiniteLaurentCode) :
    Option FiniteLaurentCode := do
  let x ← decodeFiniteLaurent a
  let y ← decodeFiniteLaurent b
  pure (encodeFiniteLaurent (x * y))

/-- Fail-closed decode-operate-encode negation on finite codes. -/
noncomputable def negFiniteLaurentCode (a : FiniteLaurentCode) :
    Option FiniteLaurentCode := do
  let x ← decodeFiniteLaurent a
  pure (encodeFiniteLaurent (-x))

@[simp] theorem addFiniteLaurentCode_encodeFiniteLaurent (x y : RAValue) :
    addFiniteLaurentCode (encodeFiniteLaurent x) (encodeFiniteLaurent y) =
      some (encodeFiniteLaurent (x + y)) := by
  simp [addFiniteLaurentCode]

@[simp] theorem mulFiniteLaurentCode_encodeFiniteLaurent (x y : RAValue) :
    mulFiniteLaurentCode (encodeFiniteLaurent x) (encodeFiniteLaurent y) =
      some (encodeFiniteLaurent (x * y)) := by
  simp [mulFiniteLaurentCode]

@[simp] theorem negFiniteLaurentCode_encodeFiniteLaurent (x : RAValue) :
    negFiniteLaurentCode (encodeFiniteLaurent x) =
      some (encodeFiniteLaurent (-x)) := by
  simp [negFiniteLaurentCode]

theorem addFiniteLaurentCode_eq_some_iff
    {a b c : FiniteLaurentCode} :
    addFiniteLaurentCode a b = some c ↔
      ∃ x y : RAValue,
        decodeFiniteLaurent a = some x ∧
        decodeFiniteLaurent b = some y ∧
        c = encodeFiniteLaurent (x + y) := by
  constructor
  · intro h
    cases ha : decodeFiniteLaurent a with
    | none => simp [addFiniteLaurentCode, ha] at h
    | some x =>
        cases hb : decodeFiniteLaurent b with
        | none => simp [addFiniteLaurentCode, ha, hb] at h
        | some y =>
            refine ⟨x, y, rfl, rfl, ?_⟩
            simpa [addFiniteLaurentCode, ha, hb] using h.symm
  · rintro ⟨x, y, ha, hb, rfl⟩
    simp [addFiniteLaurentCode, ha, hb]

theorem mulFiniteLaurentCode_eq_some_iff
    {a b c : FiniteLaurentCode} :
    mulFiniteLaurentCode a b = some c ↔
      ∃ x y : RAValue,
        decodeFiniteLaurent a = some x ∧
        decodeFiniteLaurent b = some y ∧
        c = encodeFiniteLaurent (x * y) := by
  constructor
  · intro h
    cases ha : decodeFiniteLaurent a with
    | none => simp [mulFiniteLaurentCode, ha] at h
    | some x =>
        cases hb : decodeFiniteLaurent b with
        | none => simp [mulFiniteLaurentCode, ha, hb] at h
        | some y =>
            refine ⟨x, y, rfl, rfl, ?_⟩
            simpa [mulFiniteLaurentCode, ha, hb] using h.symm
  · rintro ⟨x, y, ha, hb, rfl⟩
    simp [mulFiniteLaurentCode, ha, hb]

theorem negFiniteLaurentCode_eq_some_iff
    {a c : FiniteLaurentCode} :
    negFiniteLaurentCode a = some c ↔
      ∃ x : RAValue,
        decodeFiniteLaurent a = some x ∧
        c = encodeFiniteLaurent (-x) := by
  constructor
  · intro h
    cases ha : decodeFiniteLaurent a with
    | none => simp [negFiniteLaurentCode, ha] at h
    | some x =>
        refine ⟨x, rfl, ?_⟩
        simpa [negFiniteLaurentCode, ha] using h.symm
  · rintro ⟨x, ha, rfl⟩
    simp [negFiniteLaurentCode, ha]

theorem eval_addFiniteLaurentCode
    {a b c : FiniteLaurentCode}
    (h : addFiniteLaurentCode a b = some c) :
    c.eval = a.eval + b.eval := by
  rcases addFiniteLaurentCode_eq_some_iff.mp h with ⟨x, y, ha, hb, rfl⟩
  have hax := decodeFiniteLaurent_eq_some_iff.mp ha
  have hby := decodeFiniteLaurent_eq_some_iff.mp hb
  rw [hax, hby]
  simp

theorem eval_mulFiniteLaurentCode
    {a b c : FiniteLaurentCode}
    (h : mulFiniteLaurentCode a b = some c) :
    c.eval = a.eval * b.eval := by
  rcases mulFiniteLaurentCode_eq_some_iff.mp h with ⟨x, y, ha, hb, rfl⟩
  have hax := decodeFiniteLaurent_eq_some_iff.mp ha
  have hby := decodeFiniteLaurent_eq_some_iff.mp hb
  rw [hax, hby]
  simp

theorem eval_negFiniteLaurentCode
    {a c : FiniteLaurentCode}
    (h : negFiniteLaurentCode a = some c) :
    c.eval = -a.eval := by
  rcases negFiniteLaurentCode_eq_some_iff.mp h with ⟨x, ha, rfl⟩
  have hax := decodeFiniteLaurent_eq_some_iff.mp ha
  rw [hax]
  simp

@[simp] theorem addFiniteLaurentCode_eq_none_iff (a b : FiniteLaurentCode) :
    addFiniteLaurentCode a b = none ↔
      decodeFiniteLaurent a = none ∨ decodeFiniteLaurent b = none := by
  cases ha : decodeFiniteLaurent a <;>
    cases hb : decodeFiniteLaurent b <;>
      simp [addFiniteLaurentCode, ha, hb]

@[simp] theorem mulFiniteLaurentCode_eq_none_iff (a b : FiniteLaurentCode) :
    mulFiniteLaurentCode a b = none ↔
      decodeFiniteLaurent a = none ∨ decodeFiniteLaurent b = none := by
  cases ha : decodeFiniteLaurent a <;>
    cases hb : decodeFiniteLaurent b <;>
      simp [mulFiniteLaurentCode, ha, hb]

@[simp] theorem negFiniteLaurentCode_eq_none_iff (a : FiniteLaurentCode) :
    negFiniteLaurentCode a = none ↔ decodeFiniteLaurent a = none := by
  cases ha : decodeFiniteLaurent a <;>
    simp [negFiniteLaurentCode, ha]

/-- Concrete P2-L3 branch codec instance. -/
def branchIndexCodec : LosslessCodec ℤ where
  Code := List ℕ
  encode := encodeBranchIndex
  decode := decodeBranchIndex
  decode_encode := decodeBranchIndex_encodeBranchIndex

/-- Typed CNRS-A value plus branch serialization. -/
abbrev FiniteLaurentBranchSerialization :=
  MarkerSerialization finiteLaurentCodec branchIndexCodec

noncomputable def encodeFiniteLaurentBranch (x : RAValue × ℤ) :
    FiniteLaurentBranchSerialization :=
  encodeMarker finiteLaurentCodec branchIndexCodec x

noncomputable def decodeFiniteLaurentBranch
    (s : FiniteLaurentBranchSerialization) : Option (RAValue × ℤ) :=
  decodeMarker finiteLaurentCodec branchIndexCodec s

@[simp] theorem decodeFiniteLaurentBranch_encodeFiniteLaurentBranch
    (x : RAValue × ℤ) :
    decodeFiniteLaurentBranch (encodeFiniteLaurentBranch x) = some x :=
  decodeMarker_encodeMarker finiteLaurentCodec branchIndexCodec x

theorem encodeFiniteLaurentBranch_injective :
    Function.Injective encodeFiniteLaurentBranch := by
  intro x y h
  have := congrArg decodeFiniteLaurentBranch h
  simpa using this

end

end CNRSProblem2
