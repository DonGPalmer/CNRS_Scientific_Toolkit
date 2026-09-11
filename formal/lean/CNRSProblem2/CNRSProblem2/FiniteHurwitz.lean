import CNRSProblem2.FiniteLaurentValueCodec
import Mathlib.Data.Nat.Choose.Sum
import Mathlib.Data.List.ToFinsupp
import Mathlib.Tactic

/-!
# CNRS Problem 2, Layer P2-L5: finite-support CNRS-H algebra

The formal carrier is the finite-support part of the Hurwitz series ring over
the P2-L4 coefficient ring `RAValue`.  Multiplication is binomial convolution,
and the outer left shift is the Hurwitz derivation.
-/

namespace CNRSProblem2

noncomputable section

open scoped BigOperators

/-- Finite-support Hurwitz coefficient families. -/
structure FiniteHurwitz (R : Type*) [Zero R] where
  coeff : ℕ →₀ R

namespace FiniteHurwitz

variable {R : Type*}

instance [Zero R] : CoeFun (FiniteHurwitz R) (fun _ => ℕ → R) :=
  ⟨fun x => x.coeff⟩

@[ext]
theorem ext [Zero R] {x y : FiniteHurwitz R} (h : ∀ n, x n = y n) : x = y := by
  cases x with
  | mk x =>
    cases y with
    | mk y =>
      congr
      ext n
      exact h n

instance [Zero R] : Zero (FiniteHurwitz R) := ⟨⟨0⟩⟩
instance [AddZeroClass R] : Add (FiniteHurwitz R) := ⟨fun x y => ⟨x.coeff + y.coeff⟩⟩
instance [AddGroup R] : Neg (FiniteHurwitz R) := ⟨fun x => ⟨-x.coeff⟩⟩

@[simp] theorem coeff_zero [Zero R] (n : ℕ) : (0 : FiniteHurwitz R) n = 0 := rfl
@[simp] theorem coeff_add [AddZeroClass R] (x y : FiniteHurwitz R) (n : ℕ) :
    (x + y) n = x n + y n := rfl
@[simp] theorem coeff_neg [AddGroup R] (x : FiniteHurwitz R) (n : ℕ) :
    (-x) n = -x n := rfl

instance [AddCommGroup R] : AddCommGroup (FiniteHurwitz R) where
  add_assoc x y z := by ext n; simp [add_assoc]
  zero_add x := by ext n; simp
  add_zero x := by ext n; simp
  add_comm x y := by ext n; simp [add_comm]
  neg_add_cancel x := by
    ext n
    change -x.coeff n + x.coeff n = 0
    simp
  nsmul := nsmulRec
  zsmul := zsmulRec

/-- Projection to one outer coefficient, as an additive homomorphism. -/
def coeffAddHom [AddCommGroup R] (n : ℕ) : FiniteHurwitz R →+ R where
  toFun := fun x => x n
  map_zero' := rfl
  map_add' := fun _ _ => rfl

/-- A single divided-power monomial. -/
def single [Zero R] (n : ℕ) (r : R) : FiniteHurwitz R :=
  ⟨Finsupp.single n r⟩

@[simp] theorem single_apply [Zero R] [DecidableEq R] (n m : ℕ) (r : R) :
    single n r m = if m = n then r else 0 := by
  classical
  by_cases h : m = n
  · subst m
    simp [single]
  · rw [if_neg h]
    exact Finsupp.single_eq_of_ne h

/-- Induction on a finite Hurwitz family by adjoining one supported coefficient. -/
theorem induction_on [AddZeroClass R] {P : FiniteHurwitz R → Prop}
    (x : FiniteHurwitz R) (hzero : P 0)
    (hadd : ∀ n a y, a ≠ 0 → P y → P (single n a + y)) : P x := by
  cases x with
  | mk f =>
    induction f using Finsupp.induction with
    | zero => exact hzero
    | single_add n a f hn ha ih =>
        exact hadd n a ⟨f⟩ ha ih

/-- Finite binomial convolution, defined by bilinear extension from basis terms. -/
def mul [CommRing R] (x y : FiniteHurwitz R) : FiniteHurwitz R :=
  ⟨x.coeff.sum fun i a =>
    y.coeff.sum fun j b =>
      Finsupp.single (i + j) ((i + j).choose i • (a * b))⟩

instance [CommRing R] : Mul (FiniteHurwitz R) := ⟨mul⟩

@[simp] theorem single_mul_single [CommRing R] (i j : ℕ) (a b : R) :
    single i a * single j b =
      single (i + j) ((i + j).choose i • (a * b)) := by
  ext n
  change (mul (single i a) (single j b)) n = _
  simp [mul, single]

theorem hurwitz_add_mul [CommRing R] (x y z : FiniteHurwitz R) :
    (x + y) * z = x * z + y * z := by
  classical
  apply ext
  intro n
  change ((x.coeff + y.coeff).sum fun i a =>
      z.coeff.sum fun j b => Finsupp.single (i + j) ((i + j).choose i • (a * b))) n = _
  rw [Finsupp.sum_add_index']
  · rfl
  · intro i
    simp
  · intro i a b
    simp_rw [_root_.add_mul, nsmul_add, Finsupp.single_add]
    ext m
    simp only [Finsupp.sum]
    rw [Finset.sum_add_distrib]

theorem hurwitz_mul_add [CommRing R] (x y z : FiniteHurwitz R) :
    x * (y + z) = x * y + x * z := by
  classical
  apply ext
  intro n
  change (x.coeff.sum fun i a =>
      (y.coeff + z.coeff).sum fun j b =>
        Finsupp.single (i + j) ((i + j).choose i • (a * b))) n =
    ((x.coeff.sum fun i a => y.coeff.sum fun j b =>
        Finsupp.single (i + j) ((i + j).choose i • (a * b))) +
      (x.coeff.sum fun i a => z.coeff.sum fun j b =>
        Finsupp.single (i + j) ((i + j).choose i • (a * b)))) n
  apply congrArg (fun f : ℕ →₀ R => f n)
  calc
    x.coeff.sum (fun i a =>
        (y.coeff + z.coeff).sum fun j b =>
          Finsupp.single (i + j) ((i + j).choose i • (a * b))) =
        x.coeff.sum (fun i a =>
          (y.coeff.sum fun j b =>
              Finsupp.single (i + j) ((i + j).choose i • (a * b))) +
            (z.coeff.sum fun j b =>
              Finsupp.single (i + j) ((i + j).choose i • (a * b)))) := by
      apply Finsupp.sum_congr
      intro i hi
      rw [Finsupp.sum_add_index']
      · intro j
        simp
      · intro j a b
        rw [_root_.mul_add, nsmul_add, Finsupp.single_add]
    _ = _ := by
      simp only [Finsupp.sum]
      rw [Finset.sum_add_distrib]

theorem hurwitz_zero_mul [CommRing R] (x : FiniteHurwitz R) : 0 * x = 0 := by
  apply ext
  intro n
  change ((0 : ℕ →₀ R).sum fun i a =>
      x.coeff.sum fun j b => Finsupp.single (i + j) ((i + j).choose i • (a * b))) n = 0
  simp

theorem hurwitz_mul_zero [CommRing R] (x : FiniteHurwitz R) : x * 0 = 0 := by
  apply ext
  intro n
  change (x.coeff.sum fun i a =>
      (0 : ℕ →₀ R).sum fun j b => Finsupp.single (i + j) ((i + j).choose i • (a * b))) n = 0
  simp

theorem single_mul_comm [CommRing R] (i : ℕ) (a : R) (y : FiniteHurwitz R) :
    single i a * y = y * single i a := by
  induction y using induction_on with
  | hzero => simp [hurwitz_mul_zero, hurwitz_zero_mul]
  | hadd j b y hb ih =>
      rw [hurwitz_mul_add, hurwitz_add_mul, ih]
      rw [single_mul_single, single_mul_single]
      rw [show j + i = i + j by omega]
      rw [Nat.choose_symm_add]
      simp [mul_comm]

theorem hurwitz_mul_comm [CommRing R] (x y : FiniteHurwitz R) : x * y = y * x := by
  induction x using induction_on with
  | hzero => simp [hurwitz_mul_zero, hurwitz_zero_mul]
  | hadd i a x ha ih =>
      rw [hurwitz_add_mul, hurwitz_mul_add, ih, single_mul_comm]

instance [CommRing R] : One (FiniteHurwitz R) := ⟨single 0 1⟩

@[simp] theorem one_mul [CommRing R] (x : FiniteHurwitz R) : 1 * x = x := by
  induction x using induction_on with
  | hzero => exact hurwitz_mul_zero 1
  | hadd i a x ha ih =>
      rw [hurwitz_mul_add, ih]
      congr 1
      change single 0 1 * single i a = single i a
      simp [single_mul_single]

@[simp] theorem mul_one [CommRing R] (x : FiniteHurwitz R) : x * 1 = x := by
  rw [hurwitz_mul_comm, one_mul]

theorem choose_assoc (i j k : ℕ) :
    (i + j).choose i * (i + j + k).choose (i + j) =
      (j + k).choose j * (i + j + k).choose i := by
  have h := Nat.choose_mul (n := i + j + k) (k := i + j) (s := i) (by omega)
  rw [show i + j + k - i = j + k by omega,
    show i + j - i = j by omega] at h
  calc
    (i + j).choose i * (i + j + k).choose (i + j) =
        (i + j + k).choose (i + j) * (i + j).choose i := Nat.mul_comm _ _
    _ = (i + j + k).choose i * (j + k).choose j := h
    _ = (j + k).choose j * (i + j + k).choose i := Nat.mul_comm _ _

theorem single_mul_assoc [CommRing R] (i j k : ℕ) (a b c : R) :
    (single i a * single j b) * single k c =
      single i a * (single j b * single k c) := by
  simp only [single_mul_single]
  rw [show i + j + k = i + (j + k) by omega]
  congr 1
  have hc :
      (((i + j).choose i * (i + (j + k)).choose (i + j) : ℕ) : R) =
        (((j + k).choose j * (i + (j + k)).choose i : ℕ) : R) := by
    simpa [add_assoc] using
      congrArg (fun n : ℕ => (n : R)) (choose_assoc i j k)
  simp only [nsmul_eq_mul, Nat.cast_mul] at hc ⊢
  calc
    ↑((i + (j + k)).choose (i + j)) *
          (↑((i + j).choose i) * (a * b) * c) =
        (↑((i + j).choose i) * ↑((i + (j + k)).choose (i + j))) *
          (a * b * c) := by
            ring
    _ = (↑((j + k).choose j) * ↑((i + (j + k)).choose i)) *
          (a * b * c) := by rw [hc]
    _ = ↑((i + (j + k)).choose i) *
          (a * (↑((j + k).choose j) * (b * c))) := by
            ring

theorem single_single_mul_assoc [CommRing R]
    (i j : ℕ) (a b : R) (z : FiniteHurwitz R) :
    (single i a * single j b) * z = single i a * (single j b * z) := by
  induction z using induction_on with
  | hzero => simp [hurwitz_mul_zero]
  | hadd k c z hc ih =>
      rw [hurwitz_mul_add, hurwitz_mul_add, hurwitz_mul_add,
        single_mul_assoc, ih]

theorem single_mul_assoc_left [CommRing R]
    (i : ℕ) (a : R) (y z : FiniteHurwitz R) :
    (single i a * y) * z = single i a * (y * z) := by
  induction y using induction_on with
  | hzero => simp [hurwitz_mul_zero, hurwitz_zero_mul]
  | hadd j b y hb ih =>
      rw [hurwitz_mul_add, hurwitz_add_mul, hurwitz_add_mul,
        hurwitz_mul_add, single_single_mul_assoc, ih]

theorem hurwitz_mul_assoc [CommRing R] (x y z : FiniteHurwitz R) :
    (x * y) * z = x * (y * z) := by
  induction x using induction_on with
  | hzero => simp [hurwitz_zero_mul]
  | hadd i a x ha ih =>
      rw [hurwitz_add_mul, hurwitz_add_mul, hurwitz_add_mul,
        single_mul_assoc_left, ih]

/-- The finite-support Hurwitz carrier is a commutative ring. -/
instance [CommRing R] : CommRing (FiniteHurwitz R) where
  mul_assoc := hurwitz_mul_assoc
  one_mul := one_mul
  mul_one := mul_one
  left_distrib := hurwitz_mul_add
  right_distrib := hurwitz_add_mul
  zero_mul := hurwitz_zero_mul
  mul_zero := hurwitz_mul_zero
  mul_comm := hurwitz_mul_comm

/-- Coefficient semantics of finite binomial convolution, written as a sum
over the two finite supports. -/
theorem coeff_mul_support [CommRing R] (x y : FiniteHurwitz R) (n : ℕ) :
    (x * y) n =
      ∑ i ∈ x.coeff.support, ∑ j ∈ y.coeff.support,
        if i + j = n then (i + j).choose i • (x i * y j) else 0 := by
  classical
  change (mul x y) n = _
  change (x.coeff.sum fun i a =>
    y.coeff.sum fun j b =>
      Finsupp.single (i + j) ((i + j).choose i • (a * b))) n = _
  simp [Finsupp.sum, Finsupp.single_apply, eq_comm]

/-- Exact coefficient theorem for binomial convolution.  The finite-support
form makes the finiteness witness explicit. -/
theorem coeff_mul [CommRing R] (x y : FiniteHurwitz R) (n : ℕ) :
    (x * y) n =
      ∑ i ∈ x.coeff.support, ∑ j ∈ y.coeff.support,
        if i + j = n then n.choose i • (x i * y j) else 0 := by
  rw [coeff_mul_support]
  apply Finset.sum_congr rfl
  intro i hi
  apply Finset.sum_congr rfl
  intro j hj
  split_ifs with h
  · subst n
    rfl
  · rfl

/-- Hurwitz differentiation: remove the constant coefficient and shift every
remaining coefficient down by one outer index. -/
def deriv [CommRing R] (x : FiniteHurwitz R) : FiniteHurwitz R :=
  ⟨x.coeff.sum fun i a =>
    match i with
    | 0 => 0
    | n + 1 => Finsupp.single n a⟩

@[simp] theorem deriv_single_zero [CommRing R] (a : R) :
    deriv (single 0 a) = 0 := by
  ext n
  simp [deriv, single]

@[simp] theorem deriv_single_succ [CommRing R] (n : ℕ) (a : R) :
    deriv (single (n + 1) a) = single n a := by
  ext m
  simp [deriv, single]

@[simp] theorem deriv_zero [CommRing R] : deriv (0 : FiniteHurwitz R) = 0 := by
  ext n
  change ((0 : ℕ →₀ R).sum fun i a =>
    match i with
    | 0 => 0
    | m + 1 => Finsupp.single m a) n = 0
  simp

theorem deriv_add [CommRing R] (x y : FiniteHurwitz R) :
    deriv (x + y) = deriv x + deriv y := by
  classical
  apply ext
  intro n
  change ((x.coeff + y.coeff).sum fun i a =>
    match i with
    | 0 => 0
    | m + 1 => Finsupp.single m a) n = _
  rw [Finsupp.sum_add_index']
  · rfl
  · intro i
    cases i <;> simp
  · intro i a b
    cases i <;> simp [Finsupp.single_add]

@[simp] theorem coeff_deriv [CommRing R] (x : FiniteHurwitz R) (n : ℕ) :
    deriv x n = x (n + 1) := by
  induction x using induction_on with
  | hzero => simp
  | hadd i a x ha ih =>
      rw [deriv_add]
      cases i with
      | zero =>
          simp only [deriv_single_zero, coeff_add, coeff_zero, ih]
          congr 1
          symm
          change (Finsupp.single 0 a : ℕ →₀ R) (n + 1) = 0
          simp
      | succ i =>
          simp only [deriv_single_succ, coeff_add, ih]
          congr 1
          change (Finsupp.single i a : ℕ →₀ R) n =
            (Finsupp.single (i + 1) a : ℕ →₀ R) (n + 1)
          classical
          simp [Finsupp.single_apply]

/-- The Hurwitz derivative as an additive homomorphism. -/
def derivAddHom [CommRing R] : FiniteHurwitz R →+ FiniteHurwitz R where
  toFun := deriv
  map_zero' := deriv_zero
  map_add' := deriv_add

theorem deriv_single_mul_single [CommRing R]
    (i j : ℕ) (a b : R) :
    deriv (single i a * single j b) =
      deriv (single i a) * single j b + single i a * deriv (single j b) := by
  cases i with
  | zero =>
    cases j <;> simp [single_mul_single]
  | succ i =>
    cases j with
    | zero => simp [single_mul_single]
    | succ j =>
      simp only [single_mul_single, deriv_single_succ]
      rw [show i + 1 + (j + 1) = (i + j + 1) + 1 by omega,
        deriv_single_succ]
      rw [show i + (j + 1) = i + j + 1 by omega,
        show i + 1 + j = i + j + 1 by omega]
      rw [Nat.choose_succ_succ]
      rw [show single (i + j + 1)
          (((i + j + 1).choose i) • (a * b)) +
            single (i + j + 1)
              (((i + j + 1).choose (i + 1)) • (a * b)) =
          single (i + j + 1)
            ((((i + j + 1).choose i) • (a * b)) +
              (((i + j + 1).choose (i + 1)) • (a * b))) by
        ext n
        simp [single]]
      congr 1
      ring

theorem deriv_single_mul [CommRing R]
    (i : ℕ) (a : R) (y : FiniteHurwitz R) :
    deriv (single i a * y) = deriv (single i a) * y + single i a * deriv y := by
  induction y using induction_on with
  | hzero => simp
  | hadd j b y hb ih =>
      rw [hurwitz_mul_add, deriv_add, ih, deriv_add,
        hurwitz_mul_add, hurwitz_mul_add, deriv_single_mul_single]
      abel

/-- Exact Leibniz rule for finite-support CNRS-H differentiation. -/
theorem deriv_mul [CommRing R] (x y : FiniteHurwitz R) :
    deriv (x * y) = deriv x * y + x * deriv y := by
  induction x using induction_on with
  | hzero => simp
  | hadd i a x ha ih =>
      rw [hurwitz_add_mul, deriv_add, ih, deriv_add,
        hurwitz_add_mul, hurwitz_add_mul, deriv_single_mul]
      abel

end FiniteHurwitz

/-- P2-L5 finite-support CNRS-H values over the P2-L4 coefficient ring. -/
abbrev FiniteHurwitzValue := FiniteHurwitz RAValue

/-- Sparse outer serialization.  Each coefficient is encoded by the canonical
P2-L4 finite-Laurent codec and indices are emitted in the canonical order of
the finite support. -/
structure FiniteHurwitzCode where
  entries : List (ℕ × FiniteLaurentCode)
deriving DecidableEq

/-- Exact value of any raw sparse outer code.  Duplicate indices, if supplied
in a noncanonical raw code, add in the coefficient ring. -/
noncomputable def FiniteHurwitzCode.value (code : FiniteHurwitzCode) :
    FiniteHurwitzValue :=
  code.entries.map (fun e => FiniteHurwitz.single e.1 e.2.value) |>.sum

/-- Canonical sparse encoding: increasing finite-support indices, with every
coefficient encoded by P2-L4. -/
noncomputable def encodeFiniteHurwitz (x : FiniteHurwitzValue) :
    FiniteHurwitzCode where
  entries := x.coeff.support.toList.map fun n =>
    (n, encodeFiniteLaurent (x n))

@[simp] theorem value_encodeFiniteHurwitz (x : FiniteHurwitzValue) :
    (encodeFiniteHurwitz x).value = x := by
  classical
  ext n
  simp [encodeFiniteHurwitz, FiniteHurwitzCode.value]
  change FiniteHurwitz.coeffAddHom n (∑ i ∈ x.coeff.support,
    FiniteHurwitz.single i (x.coeff i)) = x.coeff n
  rw [map_sum]
  change (∑ i ∈ x.coeff.support, Finsupp.single i (x.coeff i) n) = x.coeff n
  have h := congrArg (fun f : ℕ →₀ RAValue => f n) (Finsupp.sum_single x.coeff)
  simpa [Finsupp.sum] using h

theorem encodeFiniteHurwitz_indices (x : FiniteHurwitzValue) :
    (encodeFiniteHurwitz x).entries.map Prod.fst = x.coeff.support.toList := by
  simp [encodeFiniteHurwitz, Function.comp_def]

/-- Decode only exact canonical sparse encodings. -/
noncomputable def decodeFiniteHurwitz (code : FiniteHurwitzCode) :
    Option FiniteHurwitzValue :=
  let x := code.value
  if code = encodeFiniteHurwitz x then some x else none

def ValidFiniteHurwitzCode (code : FiniteHurwitzCode) : Prop :=
  ∃ x : FiniteHurwitzValue, code = encodeFiniteHurwitz x

theorem encodeFiniteHurwitz_valid (x : FiniteHurwitzValue) :
    ValidFiniteHurwitzCode (encodeFiniteHurwitz x) :=
  ⟨x, rfl⟩

@[simp] theorem decodeFiniteHurwitz_encodeFiniteHurwitz
    (x : FiniteHurwitzValue) :
    decodeFiniteHurwitz (encodeFiniteHurwitz x) = some x := by
  simp [decodeFiniteHurwitz, value_encodeFiniteHurwitz]

theorem encodeFiniteHurwitz_injective :
    Function.Injective encodeFiniteHurwitz := by
  intro x y h
  have := congrArg decodeFiniteHurwitz h
  simpa using this

theorem decodeFiniteHurwitz_eq_some_iff
    {code : FiniteHurwitzCode} {x : FiniteHurwitzValue} :
    decodeFiniteHurwitz code = some x ↔ code = encodeFiniteHurwitz x := by
  unfold decodeFiniteHurwitz
  dsimp only
  split_ifs with hcanon
  · constructor
    · intro h
      have hx : code.value = x := Option.some.inj h
      simpa [hx] using hcanon
    · rintro rfl
      simp
  · constructor
    · simp
    · intro h
      subst code
      apply hcanon
      simp

theorem decodeFiniteHurwitz_isSome_iff (code : FiniteHurwitzCode) :
    (decodeFiniteHurwitz code).isSome ↔ ValidFiniteHurwitzCode code := by
  constructor
  · intro h
    obtain ⟨x, hx⟩ := Option.isSome_iff_exists.mp h
    exact ⟨x, decodeFiniteHurwitz_eq_some_iff.mp hx⟩
  · rintro ⟨x, rfl⟩
    simp

/-- Canonical sparse normalization of an arbitrary raw outer code. -/
noncomputable def normalizeFiniteHurwitz (code : FiniteHurwitzCode) :
    FiniteHurwitzCode :=
  encodeFiniteHurwitz code.value

@[simp] theorem value_normalizeFiniteHurwitz (code : FiniteHurwitzCode) :
    (normalizeFiniteHurwitz code).value = code.value := by
  simp [normalizeFiniteHurwitz]

theorem normalizeFiniteHurwitz_valid (code : FiniteHurwitzCode) :
    ValidFiniteHurwitzCode (normalizeFiniteHurwitz code) :=
  encodeFiniteHurwitz_valid code.value

@[simp] theorem normalizeFiniteHurwitz_idempotent (code : FiniteHurwitzCode) :
    normalizeFiniteHurwitz (normalizeFiniteHurwitz code) =
      normalizeFiniteHurwitz code := by
  simp [normalizeFiniteHurwitz]

/-- P2-L5's lossless finite-support CNRS-H codec. -/
noncomputable def finiteHurwitzCodec : LosslessCodec FiniteHurwitzValue where
  Code := FiniteHurwitzCode
  encode := encodeFiniteHurwitz
  decode := decodeFiniteHurwitz
  decode_encode := decodeFiniteHurwitz_encodeFiniteHurwitz

/-- Fail-closed decode-operate-encode addition. -/
noncomputable def addFiniteHurwitzCode
    (a b : FiniteHurwitzCode) : Option FiniteHurwitzCode := do
  let x ← decodeFiniteHurwitz a
  let y ← decodeFiniteHurwitz b
  pure (encodeFiniteHurwitz (x + y))

/-- Fail-closed decode-operate-encode Hurwitz multiplication. -/
noncomputable def mulFiniteHurwitzCode
    (a b : FiniteHurwitzCode) : Option FiniteHurwitzCode := do
  let x ← decodeFiniteHurwitz a
  let y ← decodeFiniteHurwitz b
  pure (encodeFiniteHurwitz (x * y))

/-- Fail-closed decode-operate-encode negation. -/
noncomputable def negFiniteHurwitzCode
    (a : FiniteHurwitzCode) : Option FiniteHurwitzCode := do
  let x ← decodeFiniteHurwitz a
  pure (encodeFiniteHurwitz (-x))

/-- Fail-closed decode-differentiate-encode shift differentiation. -/
noncomputable def derivFiniteHurwitzCode
    (a : FiniteHurwitzCode) : Option FiniteHurwitzCode := do
  let x ← decodeFiniteHurwitz a
  pure (encodeFiniteHurwitz (FiniteHurwitz.deriv x))

@[simp] theorem addFiniteHurwitzCode_encode (x y : FiniteHurwitzValue) :
    addFiniteHurwitzCode (encodeFiniteHurwitz x) (encodeFiniteHurwitz y) =
      some (encodeFiniteHurwitz (x + y)) := by
  simp [addFiniteHurwitzCode]

@[simp] theorem mulFiniteHurwitzCode_encode (x y : FiniteHurwitzValue) :
    mulFiniteHurwitzCode (encodeFiniteHurwitz x) (encodeFiniteHurwitz y) =
      some (encodeFiniteHurwitz (x * y)) := by
  simp [mulFiniteHurwitzCode]

@[simp] theorem negFiniteHurwitzCode_encode (x : FiniteHurwitzValue) :
    negFiniteHurwitzCode (encodeFiniteHurwitz x) =
      some (encodeFiniteHurwitz (-x)) := by
  simp [negFiniteHurwitzCode]

@[simp] theorem derivFiniteHurwitzCode_encode (x : FiniteHurwitzValue) :
    derivFiniteHurwitzCode (encodeFiniteHurwitz x) =
      some (encodeFiniteHurwitz (FiniteHurwitz.deriv x)) := by
  simp [derivFiniteHurwitzCode]

theorem addFiniteHurwitzCode_eq_some_iff
    {a b c : FiniteHurwitzCode} :
    addFiniteHurwitzCode a b = some c ↔
      ∃ x y : FiniteHurwitzValue,
        decodeFiniteHurwitz a = some x ∧
        decodeFiniteHurwitz b = some y ∧
        c = encodeFiniteHurwitz (x + y) := by
  constructor
  · intro h
    cases ha : decodeFiniteHurwitz a with
    | none => simp [addFiniteHurwitzCode, ha] at h
    | some x =>
        cases hb : decodeFiniteHurwitz b with
        | none => simp [addFiniteHurwitzCode, ha, hb] at h
        | some y =>
            refine ⟨x, y, rfl, rfl, ?_⟩
            simpa [addFiniteHurwitzCode, ha, hb] using h.symm
  · rintro ⟨x, y, ha, hb, rfl⟩
    simp [addFiniteHurwitzCode, ha, hb]

theorem mulFiniteHurwitzCode_eq_some_iff
    {a b c : FiniteHurwitzCode} :
    mulFiniteHurwitzCode a b = some c ↔
      ∃ x y : FiniteHurwitzValue,
        decodeFiniteHurwitz a = some x ∧
        decodeFiniteHurwitz b = some y ∧
        c = encodeFiniteHurwitz (x * y) := by
  constructor
  · intro h
    cases ha : decodeFiniteHurwitz a with
    | none => simp [mulFiniteHurwitzCode, ha] at h
    | some x =>
        cases hb : decodeFiniteHurwitz b with
        | none => simp [mulFiniteHurwitzCode, ha, hb] at h
        | some y =>
            refine ⟨x, y, rfl, rfl, ?_⟩
            simpa [mulFiniteHurwitzCode, ha, hb] using h.symm
  · rintro ⟨x, y, ha, hb, rfl⟩
    simp [mulFiniteHurwitzCode, ha, hb]

theorem negFiniteHurwitzCode_eq_some_iff
    {a c : FiniteHurwitzCode} :
    negFiniteHurwitzCode a = some c ↔
      ∃ x : FiniteHurwitzValue,
        decodeFiniteHurwitz a = some x ∧
        c = encodeFiniteHurwitz (-x) := by
  constructor
  · intro h
    cases ha : decodeFiniteHurwitz a with
    | none => simp [negFiniteHurwitzCode, ha] at h
    | some x =>
        refine ⟨x, rfl, ?_⟩
        simpa [negFiniteHurwitzCode, ha] using h.symm
  · rintro ⟨x, ha, rfl⟩
    simp [negFiniteHurwitzCode, ha]

theorem derivFiniteHurwitzCode_eq_some_iff
    {a c : FiniteHurwitzCode} :
    derivFiniteHurwitzCode a = some c ↔
      ∃ x : FiniteHurwitzValue,
        decodeFiniteHurwitz a = some x ∧
        c = encodeFiniteHurwitz (FiniteHurwitz.deriv x) := by
  constructor
  · intro h
    cases ha : decodeFiniteHurwitz a with
    | none => simp [derivFiniteHurwitzCode, ha] at h
    | some x =>
        refine ⟨x, rfl, ?_⟩
        simpa [derivFiniteHurwitzCode, ha] using h.symm
  · rintro ⟨x, ha, rfl⟩
    simp [derivFiniteHurwitzCode, ha]

@[simp] theorem addFiniteHurwitzCode_eq_none_iff
    (a b : FiniteHurwitzCode) :
    addFiniteHurwitzCode a b = none ↔
      decodeFiniteHurwitz a = none ∨ decodeFiniteHurwitz b = none := by
  cases ha : decodeFiniteHurwitz a <;>
    cases hb : decodeFiniteHurwitz b <;>
      simp [addFiniteHurwitzCode, ha, hb]

@[simp] theorem mulFiniteHurwitzCode_eq_none_iff
    (a b : FiniteHurwitzCode) :
    mulFiniteHurwitzCode a b = none ↔
      decodeFiniteHurwitz a = none ∨ decodeFiniteHurwitz b = none := by
  cases ha : decodeFiniteHurwitz a <;>
    cases hb : decodeFiniteHurwitz b <;>
      simp [mulFiniteHurwitzCode, ha, hb]

@[simp] theorem negFiniteHurwitzCode_eq_none_iff (a : FiniteHurwitzCode) :
    negFiniteHurwitzCode a = none ↔ decodeFiniteHurwitz a = none := by
  cases ha : decodeFiniteHurwitz a <;>
    simp [negFiniteHurwitzCode, ha]

@[simp] theorem derivFiniteHurwitzCode_eq_none_iff (a : FiniteHurwitzCode) :
    derivFiniteHurwitzCode a = none ↔ decodeFiniteHurwitz a = none := by
  cases ha : decodeFiniteHurwitz a <;>
    simp [derivFiniteHurwitzCode, ha]

theorem value_addFiniteHurwitzCode
    {a b c : FiniteHurwitzCode}
    (h : addFiniteHurwitzCode a b = some c) :
    c.value = a.value + b.value := by
  rcases addFiniteHurwitzCode_eq_some_iff.mp h with ⟨x, y, ha, hb, rfl⟩
  rw [decodeFiniteHurwitz_eq_some_iff.mp ha,
    decodeFiniteHurwitz_eq_some_iff.mp hb]
  simp

theorem value_mulFiniteHurwitzCode
    {a b c : FiniteHurwitzCode}
    (h : mulFiniteHurwitzCode a b = some c) :
    c.value = a.value * b.value := by
  rcases mulFiniteHurwitzCode_eq_some_iff.mp h with ⟨x, y, ha, hb, rfl⟩
  rw [decodeFiniteHurwitz_eq_some_iff.mp ha,
    decodeFiniteHurwitz_eq_some_iff.mp hb]
  simp

theorem value_negFiniteHurwitzCode
    {a c : FiniteHurwitzCode}
    (h : negFiniteHurwitzCode a = some c) :
    c.value = -a.value := by
  rcases negFiniteHurwitzCode_eq_some_iff.mp h with ⟨x, ha, rfl⟩
  rw [decodeFiniteHurwitz_eq_some_iff.mp ha]
  simp

theorem value_derivFiniteHurwitzCode
    {a c : FiniteHurwitzCode}
    (h : derivFiniteHurwitzCode a = some c) :
    c.value = FiniteHurwitz.deriv a.value := by
  rcases derivFiniteHurwitzCode_eq_some_iff.mp h with ⟨x, ha, rfl⟩
  rw [decodeFiniteHurwitz_eq_some_iff.mp ha]
  simp

end


end CNRSProblem2
