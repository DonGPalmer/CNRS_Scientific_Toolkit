import CNRSProblem2.BranchCover
import Mathlib.Analysis.Complex.Exponential
import Mathlib.Algebra.Order.Floor.Ring
import Mathlib.Tactic

/-!
# CNRS Problem 2, Layer P2-L2: canonical coordinates and lifted logarithm

This module implements the frozen `(-π, π]` principal-angle convention,
canonical branch coordinates, the nonzero-complex projection, mutually inverse
lifted logarithm/exponential maps, and the canonical multiplication wrap
cocycle.  It deliberately makes no topological covering-space claim.
-/

namespace CNRSProblem2

noncomputable section

/-- The integer number of full turns removed by the locked `(-π, π]`
principal-angle convention. -/
def principalTurns (θ : ℝ) : ℤ :=
  ⌈(θ - Real.pi) / (2 * Real.pi)⌉

/-- Reduction of a real angle to the locked interval `(-π, π]`. -/
def principalAngle (θ : ℝ) : ℝ :=
  θ - 2 * Real.pi * (principalTurns θ : ℝ)

theorem principalTurns_spec (θ : ℝ) :
    principalAngle θ + 2 * Real.pi * (principalTurns θ : ℝ) = θ := by
  simp [principalAngle]

theorem principalAngle_le_pi (θ : ℝ) : principalAngle θ ≤ Real.pi := by
  have hp : 0 < 2 * Real.pi := by positivity
  have hceil : (θ - Real.pi) / (2 * Real.pi) ≤
      (principalTurns θ : ℝ) := by
    exact_mod_cast Int.le_ceil ((θ - Real.pi) / (2 * Real.pi))
  have h := (div_le_iff₀ hp).1 hceil
  dsimp [principalAngle]
  nlinarith

theorem principalAngle_gt_neg_pi (θ : ℝ) : -Real.pi < principalAngle θ := by
  have hp : 0 < 2 * Real.pi := by positivity
  have hceil : (principalTurns θ : ℝ) <
      (θ - Real.pi) / (2 * Real.pi) + 1 := by
    exact_mod_cast Int.ceil_lt_add_one ((θ - Real.pi) / (2 * Real.pi))
  have hdiv : (principalTurns θ : ℝ) - 1 <
      (θ - Real.pi) / (2 * Real.pi) := by linarith
  have h := (lt_div_iff₀ hp).1 hdiv
  dsimp [principalAngle]
  nlinarith

@[simp] theorem principalTurns_add_int_turns (θ : ℝ) (n : ℤ) :
    principalTurns (θ + 2 * Real.pi * (n : ℝ)) = principalTurns θ + n := by
  simp only [principalTurns]
  have hp : (2 * Real.pi : ℝ) ≠ 0 := ne_of_gt (by positivity)
  convert Int.ceil_add_intCast ((θ - Real.pi) / (2 * Real.pi)) n using 1
  field_simp
  ring_nf

@[simp] theorem principalAngle_add_int_turns (θ : ℝ) (n : ℤ) :
    principalAngle (θ + 2 * Real.pi * (n : ℝ)) = principalAngle θ := by
  simp [principalAngle]
  ring

@[simp] theorem principalTurns_pi : principalTurns Real.pi = 0 := by
  simp [principalTurns]

@[simp] theorem principalAngle_pi : principalAngle Real.pi = Real.pi := by
  simp [principalAngle]

@[simp] theorem principalTurns_neg_pi : principalTurns (-Real.pi) = -1 := by
  have hp : (Real.pi : ℝ) ≠ 0 := ne_of_gt Real.pi_pos
  simp [principalTurns]
  field_simp
  ring

@[simp] theorem principalAngle_neg_pi : principalAngle (-Real.pi) = Real.pi := by
  simp [principalAngle]
  ring

/-- A canonical `(radius, angle, branch)` coordinate with angle in `(-π, π]`. -/
structure CanonicalBranchCoord where
  radius : ℝ
  radius_pos : 0 < radius
  angle : ℝ
  angle_gt_neg_pi : -Real.pi < angle
  angle_le_pi : angle ≤ Real.pi
  branch : ℤ

@[ext] theorem CanonicalBranchCoord.ext {x y : CanonicalBranchCoord}
    (hr : x.radius = y.radius) (ha : x.angle = y.angle)
    (hk : x.branch = y.branch) : x = y := by
  cases x
  cases y
  simp_all

def CanonicalBranchCoord.totalAngle (x : CanonicalBranchCoord) : ℝ :=
  x.angle + 2 * Real.pi * (x.branch : ℝ)

def CanonicalBranchCoord.toBranchPoint (x : CanonicalBranchCoord) : BranchPoint where
  radius := x.radius
  radius_pos := x.radius_pos
  totalAngle := x.totalAngle

/-- The unique canonical coordinate of a branch point. -/
def BranchPoint.canonicalCoord (x : BranchPoint) : CanonicalBranchCoord where
  radius := x.radius
  radius_pos := x.radius_pos
  angle := principalAngle x.totalAngle
  angle_gt_neg_pi := principalAngle_gt_neg_pi _
  angle_le_pi := principalAngle_le_pi _
  branch := principalTurns x.totalAngle

@[simp] theorem BranchPoint.canonicalCoord_toBranchPoint (x : BranchPoint) :
    x.canonicalCoord.toBranchPoint = x := by
  apply BranchPoint.ext
  · rfl
  · exact principalTurns_spec x.totalAngle

theorem principalTurns_eq_of_range {θ : ℝ} {k : ℤ}
    (hl : -Real.pi < θ) (hu : θ ≤ Real.pi) :
    principalTurns (θ + 2 * Real.pi * (k : ℝ)) = k := by
  rw [principalTurns_add_int_turns]
  have hp : 0 < 2 * Real.pi := by positivity
  have hz : principalTurns θ = 0 := by
    apply Int.ceil_eq_iff.mpr
    constructor
    · apply (lt_div_iff₀ hp).2
      norm_num
      nlinarith [Real.pi_pos]
    · apply (div_le_iff₀ hp).2
      norm_num
      nlinarith
  simp [hz]

theorem principalAngle_eq_of_range {θ : ℝ}
    (hl : -Real.pi < θ) (hu : θ ≤ Real.pi) : principalAngle θ = θ := by
  have h : principalTurns θ = 0 := by
    simpa using principalTurns_eq_of_range (θ := θ) (k := 0) hl hu
  simp [principalAngle, h]

@[simp] theorem CanonicalBranchCoord.toBranchPoint_canonicalCoord
    (x : CanonicalBranchCoord) : x.toBranchPoint.canonicalCoord = x := by
  apply CanonicalBranchCoord.ext
  · rfl
  · simp only [CanonicalBranchCoord.toBranchPoint, BranchPoint.canonicalCoord,
      CanonicalBranchCoord.totalAngle]
    rw [principalAngle_add_int_turns]
    exact principalAngle_eq_of_range x.angle_gt_neg_pi x.angle_le_pi
  · exact principalTurns_eq_of_range x.angle_gt_neg_pi x.angle_le_pi

theorem CanonicalBranchCoord.toBranchPoint_injective :
    Function.Injective CanonicalBranchCoord.toBranchPoint := by
  intro x y h
  have := congrArg BranchPoint.canonicalCoord h
  simpa using this

theorem BranchPoint.canonicalCoord_unique (x : BranchPoint)
    (c : CanonicalBranchCoord) (h : c.toBranchPoint = x) :
    c = x.canonicalCoord := by
  apply CanonicalBranchCoord.toBranchPoint_injective
  simpa using h

/-- Canonical coordinates are equivalent to the P2-L1 branch carrier. -/
def CanonicalBranchCoord.equivBranchPoint : CanonicalBranchCoord ≃ BranchPoint where
  toFun := CanonicalBranchCoord.toBranchPoint
  invFun := BranchPoint.canonicalCoord
  left_inv := CanonicalBranchCoord.toBranchPoint_canonicalCoord
  right_inv := BranchPoint.canonicalCoord_toBranchPoint

/-- Projection from the branch carrier to a nonzero ordinary complex value. -/
def BranchPoint.toComplex (x : BranchPoint) : {z : ℂ // z ≠ 0} :=
  ⟨(x.radius : ℂ) * Complex.exp (Complex.I * x.totalAngle),
    mul_ne_zero (by exact_mod_cast ne_of_gt x.radius_pos)
      (Complex.exp_ne_zero _)⟩

theorem BranchPoint.toComplex_ne_zero (x : BranchPoint) :
    (x.toComplex : ℂ) ≠ 0 := x.toComplex.property

@[simp] theorem BranchPoint.toComplex_mul (x y : BranchPoint) :
    (x.mul y).toComplex = ⟨(x.toComplex : ℂ) * (y.toComplex : ℂ),
      mul_ne_zero x.toComplex.property y.toComplex.property⟩ := by
  apply Subtype.ext
  simp only [BranchPoint.toComplex, BranchPoint.mul, Complex.ofReal_mul]
  rw [show Complex.I * (↑(x.totalAngle + y.totalAngle) : ℂ) =
      Complex.I * x.totalAngle + Complex.I * y.totalAngle by push_cast; ring,
    Complex.exp_add]
  ring

@[simp] theorem BranchPoint.toComplex_one :
    BranchPoint.one.toComplex = ⟨1, one_ne_zero⟩ := by
  apply Subtype.ext
  simp [BranchPoint.toComplex, BranchPoint.one]

@[simp] theorem BranchPoint.toComplex_inv (x : BranchPoint) :
    (x.inv.toComplex : ℂ) = (x.toComplex : ℂ)⁻¹ := by
  simp [BranchPoint.toComplex, BranchPoint.inv, Complex.exp_neg]
  ring

def RawBranchCoord.toComplex (x : RawBranchCoord) : {z : ℂ // z ≠ 0} :=
  x.toBranchPoint.toComplex

@[simp] theorem RawBranchCoord.toComplex_reindex
    (x : RawBranchCoord) (n : ℤ) : (x.reindex n).toComplex = x.toComplex := by
  apply congrArg BranchPoint.toComplex
  apply BranchPoint.ext
  · rfl
  · exact x.totalAngle_reindex n

/-- The single-valued logarithm on the branch carrier. -/
def BranchPoint.liftedLog (x : BranchPoint) : ℂ :=
  Real.log x.radius + Complex.I * x.totalAngle

/-- The inverse lifted exponential from a complex logarithm value. -/
def BranchPoint.liftedExp (z : ℂ) : BranchPoint where
  radius := Real.exp z.re
  radius_pos := Real.exp_pos _
  totalAngle := z.im

@[simp] theorem BranchPoint.liftedLog_liftedExp (z : ℂ) :
    (BranchPoint.liftedExp z).liftedLog = z := by
  apply Complex.ext <;> simp [BranchPoint.liftedLog, BranchPoint.liftedExp]

@[simp] theorem BranchPoint.liftedExp_liftedLog (x : BranchPoint) :
    BranchPoint.liftedExp x.liftedLog = x := by
  apply BranchPoint.ext
  · simp [BranchPoint.liftedLog, BranchPoint.liftedExp,
      Real.exp_log x.radius_pos]
  · simp [BranchPoint.liftedLog, BranchPoint.liftedExp]

def BranchPoint.liftedLogEquiv : BranchPoint ≃ ℂ where
  toFun := BranchPoint.liftedLog
  invFun := BranchPoint.liftedExp
  left_inv := BranchPoint.liftedExp_liftedLog
  right_inv := BranchPoint.liftedLog_liftedExp

@[simp] theorem BranchPoint.liftedLog_mul (x y : BranchPoint) :
    (x.mul y).liftedLog = x.liftedLog + y.liftedLog := by
  have hx : x.radius ≠ 0 := ne_of_gt x.radius_pos
  have hy : y.radius ≠ 0 := ne_of_gt y.radius_pos
  simp [BranchPoint.liftedLog, BranchPoint.mul, Real.log_mul hx hy]
  ring

@[simp] theorem BranchPoint.liftedLog_one : BranchPoint.one.liftedLog = 0 := by
  simp [BranchPoint.liftedLog, BranchPoint.one]

@[simp] theorem BranchPoint.liftedLog_inv (x : BranchPoint) :
    x.inv.liftedLog = -x.liftedLog := by
  simp [BranchPoint.liftedLog, BranchPoint.inv, Real.log_inv]
  ring

@[simp] theorem BranchPoint.liftedExp_add (u v : ℂ) :
    BranchPoint.liftedExp (u + v) =
      (BranchPoint.liftedExp u).mul (BranchPoint.liftedExp v) := by
  apply BranchPoint.ext <;>
    simp [BranchPoint.liftedExp, BranchPoint.mul, Real.exp_add]

theorem BranchPoint.exp_liftedLog_eq_toComplex (x : BranchPoint) :
    Complex.exp x.liftedLog = (x.toComplex : ℂ) := by
  rw [show x.liftedLog = (Real.log x.radius : ℂ) +
      Complex.I * x.totalAngle by rfl, Complex.exp_add]
  rw [← Complex.ofReal_exp]
  simp [BranchPoint.toComplex, Real.exp_log x.radius_pos]

/-- Principal-sheet lift of a nonzero complex number. -/
def BranchPoint.principalLift (z : {z : ℂ // z ≠ 0}) : CanonicalBranchCoord where
  radius := ‖z.1‖
  radius_pos := norm_pos_iff.mpr z.property
  angle := Complex.arg z
  angle_gt_neg_pi := Complex.neg_pi_lt_arg z
  angle_le_pi := Complex.arg_le_pi z
  branch := 0

@[simp] theorem BranchPoint.principalLift_branch (z : {z : ℂ // z ≠ 0}) :
    (BranchPoint.principalLift z).branch = 0 := rfl

@[simp] theorem BranchPoint.toComplex_principalLift (z : {z : ℂ // z ≠ 0}) :
    (BranchPoint.principalLift z).toBranchPoint.toComplex = z := by
  apply Subtype.ext
  simp only [BranchPoint.principalLift, CanonicalBranchCoord.toBranchPoint,
    CanonicalBranchCoord.totalAngle, BranchPoint.toComplex, Int.cast_zero,
    mul_zero, add_zero]
  rw [_root_.mul_comm Complex.I (Complex.arg z.1 : ℂ)]
  exact Complex.norm_mul_exp_arg_mul_I z.1

theorem BranchPoint.liftedLog_principalLift (z : {z : ℂ // z ≠ 0}) :
    (BranchPoint.principalLift z).toBranchPoint.liftedLog =
      Real.log ‖z.1‖ + Complex.I * Complex.arg z := by
  simp [BranchPoint.principalLift, CanonicalBranchCoord.toBranchPoint,
    CanonicalBranchCoord.totalAngle, BranchPoint.liftedLog]

/-- The canonical multiplication wrap correction. -/
def CanonicalBranchCoord.wrapCocycle (θ₁ θ₂ : ℝ) : ℤ :=
  if Real.pi < θ₁ + θ₂ then 1
  else if θ₁ + θ₂ ≤ -Real.pi then -1
  else 0

theorem CanonicalBranchCoord.wrapCocycle_mem (θ₁ θ₂ : ℝ) :
    CanonicalBranchCoord.wrapCocycle θ₁ θ₂ = -1 ∨
    CanonicalBranchCoord.wrapCocycle θ₁ θ₂ = 0 ∨
    CanonicalBranchCoord.wrapCocycle θ₁ θ₂ = 1 := by
  simp only [CanonicalBranchCoord.wrapCocycle]
  split_ifs <;> omega

theorem principalTurns_add_of_principal
    {θ₁ θ₂ : ℝ}
    (h1l : -Real.pi < θ₁) (h1u : θ₁ ≤ Real.pi)
    (h2l : -Real.pi < θ₂) (h2u : θ₂ ≤ Real.pi) :
    principalTurns (θ₁ + θ₂) = CanonicalBranchCoord.wrapCocycle θ₁ θ₂ := by
  have hp : 0 < Real.pi := Real.pi_pos
  simp only [principalTurns, CanonicalBranchCoord.wrapCocycle]
  by_cases hu : Real.pi < θ₁ + θ₂
  · simp only [hu, if_true]
    have hl' : -Real.pi < θ₁ + θ₂ - 2 * Real.pi := by nlinarith
    have hu' : θ₁ + θ₂ - 2 * Real.pi ≤ Real.pi := by nlinarith
    have h := principalTurns_eq_of_range (θ := θ₁ + θ₂ - 2 * Real.pi)
      (k := 1) hl' hu'
    simp only [principalTurns] at h ⊢
    convert h using 1
    ring_nf
  · have hupper : θ₁ + θ₂ ≤ Real.pi := le_of_not_gt hu
    by_cases hl : θ₁ + θ₂ ≤ -Real.pi
    · simp only [hu, if_false, hl, if_true]
      have hl' : -Real.pi < θ₁ + θ₂ + 2 * Real.pi := by nlinarith
      have hu' : θ₁ + θ₂ + 2 * Real.pi ≤ Real.pi := by nlinarith
      have h := principalTurns_eq_of_range (θ := θ₁ + θ₂ + 2 * Real.pi)
        (k := -1) hl' hu'
      simp only [principalTurns] at h ⊢
      convert h using 1
      ring_nf
    · have hlower : -Real.pi < θ₁ + θ₂ := lt_of_not_ge hl
      simp only [hu, if_false, hl, if_false]
      simpa [principalTurns] using
        principalTurns_eq_of_range (θ := θ₁ + θ₂) (k := 0) hlower hupper

/-- Multiplication expressed directly in canonical coordinates. -/
def CanonicalBranchCoord.mul (x y : CanonicalBranchCoord) : CanonicalBranchCoord :=
  (x.toBranchPoint.mul y.toBranchPoint).canonicalCoord

@[simp] theorem CanonicalBranchCoord.angle_mul (x y : CanonicalBranchCoord) :
    (x.mul y).angle = principalAngle (x.angle + y.angle) := by
  simp only [CanonicalBranchCoord.mul, BranchPoint.canonicalCoord,
    CanonicalBranchCoord.toBranchPoint, CanonicalBranchCoord.totalAngle,
    BranchPoint.mul]
  rw [show x.angle + 2 * Real.pi * (x.branch : ℝ) +
      (y.angle + 2 * Real.pi * (y.branch : ℝ)) =
      (x.angle + y.angle) + 2 * Real.pi * ((x.branch + y.branch : ℤ) : ℝ) by
        push_cast; ring,
    principalAngle_add_int_turns]

@[simp] theorem CanonicalBranchCoord.branch_mul (x y : CanonicalBranchCoord) :
    (x.mul y).branch = x.branch + y.branch +
      CanonicalBranchCoord.wrapCocycle x.angle y.angle := by
  simp only [CanonicalBranchCoord.mul, BranchPoint.canonicalCoord,
    CanonicalBranchCoord.toBranchPoint, CanonicalBranchCoord.totalAngle,
    BranchPoint.mul]
  rw [show x.angle + 2 * Real.pi * (x.branch : ℝ) +
      (y.angle + 2 * Real.pi * (y.branch : ℝ)) =
      (x.angle + y.angle) + 2 * Real.pi * ((x.branch + y.branch : ℤ) : ℝ) by
        push_cast; ring,
    principalTurns_add_int_turns,
    principalTurns_add_of_principal x.angle_gt_neg_pi x.angle_le_pi
      y.angle_gt_neg_pi y.angle_le_pi]
  omega

@[simp] theorem CanonicalBranchCoord.totalAngle_mul (x y : CanonicalBranchCoord) :
    (x.mul y).totalAngle = x.totalAngle + y.totalAngle := by
  change (x.toBranchPoint.mul y.toBranchPoint).canonicalCoord.toBranchPoint.totalAngle = _
  rw [BranchPoint.canonicalCoord_toBranchPoint]
  rfl

@[simp] theorem CanonicalBranchCoord.toBranchPoint_mul
    (x y : CanonicalBranchCoord) :
    (x.mul y).toBranchPoint = x.toBranchPoint.mul y.toBranchPoint := by
  exact BranchPoint.canonicalCoord_toBranchPoint _

theorem CanonicalBranchCoord.mul_eq_canonicalCoord_mul
    (x y : CanonicalBranchCoord) :
    x.mul y = (x.toBranchPoint.mul y.toBranchPoint).canonicalCoord := rfl

@[simp] theorem CanonicalBranchCoord.wrapCocycle_pi_pi :
    CanonicalBranchCoord.wrapCocycle Real.pi Real.pi = 1 := by
  simp [CanonicalBranchCoord.wrapCocycle, Real.pi_pos]

theorem CanonicalBranchCoord.wrapCocycle_eq_neg_one_of_add_eq_neg_pi
    {θ₁ θ₂ : ℝ} (h : θ₁ + θ₂ = -Real.pi) :
    CanonicalBranchCoord.wrapCocycle θ₁ θ₂ = -1 := by
  simp [CanonicalBranchCoord.wrapCocycle, h, le_of_lt Real.pi_pos]

theorem CanonicalBranchCoord.wrapCocycle_eq_zero
    {θ₁ θ₂ : ℝ} (hl : -Real.pi < θ₁ + θ₂)
    (hu : θ₁ + θ₂ ≤ Real.pi) :
    CanonicalBranchCoord.wrapCocycle θ₁ θ₂ = 0 := by
  simp [CanonicalBranchCoord.wrapCocycle, not_lt.mpr hu, not_le.mpr hl]

/-- The upper-endpoint product closes at angle zero and advances one sheet. -/
theorem CanonicalBranchCoord.mul_pi_pi :
    (CanonicalBranchCoord.mk 1 (by norm_num) Real.pi
      (by nlinarith [Real.pi_pos]) (le_refl _) 0).mul
        (CanonicalBranchCoord.mk 1 (by norm_num) Real.pi
          (by nlinarith [Real.pi_pos]) (le_refl _) 0) =
      CanonicalBranchCoord.mk 1 (by norm_num) 0
        (by nlinarith [Real.pi_pos]) (le_of_lt Real.pi_pos) 1 := by
  apply CanonicalBranchCoord.ext
  · norm_num [CanonicalBranchCoord.mul, BranchPoint.canonicalCoord,
      CanonicalBranchCoord.toBranchPoint, BranchPoint.mul]
  · rw [CanonicalBranchCoord.angle_mul]
    have ht : principalTurns (Real.pi + Real.pi) = 1 := by
      rw [principalTurns_add_of_principal
        (by nlinarith [Real.pi_pos]) (le_refl _)
        (by nlinarith [Real.pi_pos]) (le_refl _)]
      exact CanonicalBranchCoord.wrapCocycle_pi_pi
    simp only [principalAngle, ht, Int.cast_one]
    ring
  · rw [CanonicalBranchCoord.branch_mul,
      CanonicalBranchCoord.wrapCocycle_pi_pi]
    norm_num

/-- At the lower excluded endpoint, canonical multiplication selects angle
`π` and applies the frozen branch correction `-1`. -/
theorem CanonicalBranchCoord.mul_angle_branch_of_add_eq_neg_pi
    (x y : CanonicalBranchCoord) (h : x.angle + y.angle = -Real.pi) :
    (x.mul y).angle = Real.pi ∧
      (x.mul y).branch = x.branch + y.branch - 1 := by
  constructor
  · rw [CanonicalBranchCoord.angle_mul, h, principalAngle_neg_pi]
  · rw [CanonicalBranchCoord.branch_mul,
      CanonicalBranchCoord.wrapCocycle_eq_neg_one_of_add_eq_neg_pi h]
    omega

end

end CNRSProblem2
