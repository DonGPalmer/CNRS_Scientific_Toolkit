import CNRSProblem2.CanonicalLiftedLog
import Mathlib.Data.Nat.Digits.Lemmas
import Mathlib.Logic.Equiv.Nat

/-!
# CNRS Problem 2, Layer P2-L3: lossless branch serialization

This module formalizes the branch-control serialization from Branch-Index
Incorporation v8.  It deliberately abstracts over the value codec: the concrete
CNRS-A digit-string representation belongs to its own governed development.
-/

namespace CNRSProblem2

/-- The paper's zigzag enumeration: nonnegative integers receive even codes
and negative integers receive odd codes. -/
def zigzag : ℤ ≃ ℕ := Equiv.intEquivNat

def unzigzag (n : ℕ) : ℤ := zigzag.symm n

@[simp] theorem unzigzag_zigzag (k : ℤ) : unzigzag (zigzag k) = k :=
  zigzag.symm_apply_apply k

@[simp] theorem zigzag_unzigzag (n : ℕ) : zigzag (unzigzag n) = n :=
  zigzag.apply_symm_apply n

@[simp] theorem zigzag_ofNat (n : ℕ) : zigzag (Int.ofNat n) = 2 * n := rfl

@[simp] theorem zigzag_negSucc (n : ℕ) : zigzag (Int.negSucc n) = 2 * n + 1 := rfl

/-- Canonical little-endian base-4 digits, with the paper's explicit `[0]`
representation for zero. -/
def canonicalBase4Digits (n : ℕ) : List ℕ :=
  if n = 0 then [0] else Nat.digits 4 n

@[simp] theorem canonicalBase4Digits_zero : canonicalBase4Digits 0 = [0] := by
  simp [canonicalBase4Digits]

theorem ofDigits_canonicalBase4Digits (n : ℕ) :
    Nat.ofDigits 4 (canonicalBase4Digits n) = n := by
  by_cases h : n = 0
  · simp [canonicalBase4Digits, h]
  · simp [canonicalBase4Digits, h, Nat.ofDigits_digits]

theorem canonicalBase4Digits_ne_nil (n : ℕ) : canonicalBase4Digits n ≠ [] := by
  by_cases h : n = 0
  · simp [canonicalBase4Digits, h]
  · simp [canonicalBase4Digits, h, Nat.digits_ne_nil_iff_ne_zero]

theorem canonicalBase4Digits_lt_four (n d : ℕ)
    (h : d ∈ canonicalBase4Digits n) : d < 4 := by
  by_cases hn : n = 0
  · simp [canonicalBase4Digits, hn] at h
    omega
  · exact Nat.digits_lt_base (by omega) (by simpa [canonicalBase4Digits, hn] using h)

/-- Self-delimiting branch block, in parser scan order: little-endian base-4
payload followed by the dedicated terminator `4`. -/
def encodeBranchIndex (k : ℤ) : List ℕ :=
  canonicalBase4Digits (zigzag k) ++ [4]

/-- Decode only exact canonical branch blocks.  Re-encoding after numeric
decoding makes malformed and noncanonical alternatives fail closed. -/
def decodeBranchIndex (block : List ℕ) : Option ℤ :=
  let k := unzigzag (Nat.ofDigits 4 block.dropLast)
  if block = encodeBranchIndex k then some k else none

def ValidBranchBlock (block : List ℕ) : Prop := ∃ k, block = encodeBranchIndex k

theorem encodeBranchIndex_valid (k : ℤ) : ValidBranchBlock (encodeBranchIndex k) :=
  ⟨k, rfl⟩

theorem encodeBranchIndex_payload_digits (k : ℤ) (d : ℕ)
    (h : d ∈ (encodeBranchIndex k).dropLast) : d < 4 := by
  have heq : (encodeBranchIndex k).dropLast = canonicalBase4Digits (zigzag k) := by
    simp [encodeBranchIndex]
  rw [heq] at h
  exact canonicalBase4Digits_lt_four (zigzag k) d h

@[simp] theorem encodeBranchIndex_last (k : ℤ) :
    (encodeBranchIndex k).getLast? = some 4 := by
  simp [encodeBranchIndex]

@[simp] theorem decodeBranchIndex_encodeBranchIndex (k : ℤ) :
    decodeBranchIndex (encodeBranchIndex k) = some k := by
  simp [decodeBranchIndex, encodeBranchIndex, ofDigits_canonicalBase4Digits]

theorem encodeBranchIndex_injective : Function.Injective encodeBranchIndex := by
  intro a b h
  have := congrArg decodeBranchIndex h
  simpa using this

theorem decodeBranchIndex_eq_some_iff {block : List ℕ} {k : ℤ} :
    decodeBranchIndex block = some k ↔ block = encodeBranchIndex k := by
  unfold decodeBranchIndex
  dsimp only
  split_ifs with hcanon
  · constructor
    · intro h
      have hk : unzigzag (Nat.ofDigits 4 block.dropLast) = k := Option.some.inj h
      simpa [hk] using hcanon
    · intro h
      apply congrArg some
      apply encodeBranchIndex_injective
      calc
        encodeBranchIndex (unzigzag (Nat.ofDigits 4 block.dropLast)) = block := hcanon.symm
        _ = encodeBranchIndex k := h
  · constructor
    · simp
    · intro h
      subst block
      apply hcanon
      simp [encodeBranchIndex, ofDigits_canonicalBase4Digits]

theorem decodeBranchIndex_isSome_iff (block : List ℕ) :
    (decodeBranchIndex block).isSome ↔ ValidBranchBlock block := by
  constructor
  · intro h
    obtain ⟨k, hk⟩ := Option.isSome_iff_exists.mp h
    exact ⟨k, (decodeBranchIndex_eq_some_iff.mp hk)⟩
  · rintro ⟨k, rfl⟩
    simp

@[simp] theorem encodeBranchIndex_zero : encodeBranchIndex 0 = [0, 4] := by
  decide

@[simp] theorem encodeBranchIndex_one : encodeBranchIndex 1 = [2, 4] := by
  decide

@[simp] theorem encodeBranchIndex_neg_one : encodeBranchIndex (-1) = [1, 4] := by
  decide

/-- A lossless codec interface.  P2-L3 uses this boundary to compose branch
serialization with a separately verified value representation. -/
structure LosslessCodec (α : Type*) where
  Code : Type*
  encode : α → Code
  decode : Code → Option α
  decode_encode : ∀ x, decode (encode x) = some x

/-- The value-bearing portion of a canonical branch coordinate. -/
structure CanonicalValueCoord where
  radius : ℝ
  radius_pos : 0 < radius
  angle : ℝ
  angle_gt_neg_pi : -Real.pi < angle
  angle_le_pi : angle ≤ Real.pi

def CanonicalBranchCoord.valueCoord (x : CanonicalBranchCoord) : CanonicalValueCoord where
  radius := x.radius
  radius_pos := x.radius_pos
  angle := x.angle
  angle_gt_neg_pi := x.angle_gt_neg_pi
  angle_le_pi := x.angle_le_pi

def CanonicalValueCoord.withBranch (x : CanonicalValueCoord) (k : ℤ) :
    CanonicalBranchCoord where
  radius := x.radius
  radius_pos := x.radius_pos
  angle := x.angle
  angle_gt_neg_pi := x.angle_gt_neg_pi
  angle_le_pi := x.angle_le_pi
  branch := k

@[simp] theorem CanonicalValueCoord.withBranch_valueCoord
    (x : CanonicalValueCoord) (k : ℤ) : (x.withBranch k).valueCoord = x := by
  cases x
  rfl

@[simp] theorem CanonicalBranchCoord.valueCoord_withBranch
    (x : CanonicalBranchCoord) : x.valueCoord.withBranch x.branch = x := by
  cases x
  rfl

/-- Marker-delimited representation.  The marker is structural here; the
integer digit codec is supplied by the caller. -/
structure MarkerSerialization {α : Type*}
    (valueCodec : LosslessCodec α) (branchCodec : LosslessCodec ℤ) where
  value : valueCodec.Code
  branch : branchCodec.Code

def encodeMarker {α : Type*} (valueCodec : LosslessCodec α)
    (branchCodec : LosslessCodec ℤ) (x : α × ℤ) :
    MarkerSerialization valueCodec branchCodec :=
  ⟨valueCodec.encode x.1, branchCodec.encode x.2⟩

def decodeMarker {α : Type*} (valueCodec : LosslessCodec α)
    (branchCodec : LosslessCodec ℤ)
    (s : MarkerSerialization valueCodec branchCodec) : Option (α × ℤ) :=
  match valueCodec.decode s.value, branchCodec.decode s.branch with
  | some x, some k => some (x, k)
  | _, _ => none

@[simp] theorem decodeMarker_encodeMarker {α : Type*}
    (valueCodec : LosslessCodec α) (branchCodec : LosslessCodec ℤ)
    (x : α × ℤ) :
    decodeMarker valueCodec branchCodec (encodeMarker valueCodec branchCodec x) = some x := by
  simp [decodeMarker, encodeMarker, valueCodec.decode_encode, branchCodec.decode_encode]

/-- Self-delimiting serialization: the branch part is the concrete terminated
base-4 block from this layer. -/
structure SelfDelimitedSerialization (valueCodec : LosslessCodec CanonicalValueCoord) where
  value : valueCodec.Code
  branchBlock : List ℕ

def encodeSelfDelimited (valueCodec : LosslessCodec CanonicalValueCoord)
    (x : CanonicalBranchCoord) : SelfDelimitedSerialization valueCodec :=
  ⟨valueCodec.encode x.valueCoord, encodeBranchIndex x.branch⟩

def decodeSelfDelimited (valueCodec : LosslessCodec CanonicalValueCoord)
    (s : SelfDelimitedSerialization valueCodec) : Option CanonicalBranchCoord := do
  let value ← valueCodec.decode s.value
  let branch ← decodeBranchIndex s.branchBlock
  pure (value.withBranch branch)

@[simp] theorem decodeSelfDelimited_encodeSelfDelimited
    (valueCodec : LosslessCodec CanonicalValueCoord) (x : CanonicalBranchCoord) :
    decodeSelfDelimited valueCodec (encodeSelfDelimited valueCodec x) = some x := by
  simp [decodeSelfDelimited, encodeSelfDelimited, valueCodec.decode_encode]

theorem encodeSelfDelimited_injective
    (valueCodec : LosslessCodec CanonicalValueCoord) :
    Function.Injective (encodeSelfDelimited valueCodec) := by
  intro x y h
  have := congrArg (decodeSelfDelimited valueCodec) h
  simpa using this

theorem decodeSelfDelimited_preservesBranchPoint
    (valueCodec : LosslessCodec CanonicalValueCoord)
    (x : CanonicalBranchCoord) :
    (decodeSelfDelimited valueCodec (encodeSelfDelimited valueCodec x)).map
      CanonicalBranchCoord.toBranchPoint = some x.toBranchPoint := by
  simp

end CNRSProblem2
