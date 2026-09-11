import Mathlib

namespace CNRSProblem1

noncomputable section

/-- The left endpoint of the Ito--Sadahiro fundamental interval. -/
def leftEndpoint (β : ℝ) : ℝ := -β / (β + 1)

/-- The excluded right endpoint of the Ito--Sadahiro fundamental interval. -/
def rightEndpoint (β : ℝ) : ℝ := 1 / (β + 1)

/-- Membership in the half-open Ito--Sadahiro fundamental interval. -/
def InFundamentalInterval (β x : ℝ) : Prop :=
  leftEndpoint β ≤ x ∧ x < rightEndpoint β

/-- The deterministic Ito--Sadahiro digit selected at a state. -/
def digit (β x : ℝ) : ℤ :=
  ⌊-β * x - leftEndpoint β⌋

/-- One step of the Ito--Sadahiro negative-base transformation. -/
def transform (β x : ℝ) : ℝ :=
  -β * x - (digit β x : ℝ)

theorem beta_ne_zero {β : ℝ} (hβ : 1 < β) : β ≠ 0 := by
  linarith

theorem beta_add_one_pos {β : ℝ} (hβ : 1 < β) : 0 < β + 1 := by
  linarith

theorem interval_width {β : ℝ} (hβ : 1 < β) :
    rightEndpoint β - leftEndpoint β = 1 := by
  unfold rightEndpoint leftEndpoint
  field_simp [ne_of_gt (beta_add_one_pos hβ)]
  ring

theorem right_eq_left_add_one {β : ℝ} (hβ : 1 < β) :
    rightEndpoint β = leftEndpoint β + 1 := by
  linarith [interval_width hβ]

theorem digit_argument_at_right {β : ℝ} (hβ : 1 < β) :
    -β * rightEndpoint β - leftEndpoint β = 0 := by
  unfold rightEndpoint leftEndpoint
  field_simp [ne_of_gt (beta_add_one_pos hβ)]
  ring

theorem digit_argument_at_left {β : ℝ} (hβ : 1 < β) :
    -β * leftEndpoint β - leftEndpoint β = β := by
  unfold leftEndpoint
  field_simp [ne_of_gt (beta_add_one_pos hβ)]
  ring

theorem digit_argument_bounds {β x : ℝ} (hβ : 1 < β)
    (hx : InFundamentalInterval β x) :
    0 ≤ -β * x - leftEndpoint β ∧
      -β * x - leftEndpoint β ≤ β := by
  have hβ0 : 0 < β := lt_trans zero_lt_one hβ
  have hlower := mul_lt_mul_of_pos_left hx.2 hβ0
  have hupper := mul_le_mul_of_nonneg_left hx.1 hβ0.le
  constructor
  · linarith [digit_argument_at_right hβ]
  · linarith [digit_argument_at_left hβ]

/-- Every selected digit belongs to the Ito--Sadahiro alphabet. -/
theorem digit_mem_alphabet {β x : ℝ} (hβ : 1 < β)
    (hx : InFundamentalInterval β x) :
    0 ≤ digit β x ∧ digit β x ≤ ⌊β⌋ := by
  have hb := digit_argument_bounds hβ hx
  unfold digit
  constructor
  · exact Int.floor_nonneg.mpr hb.1
  · apply Int.floor_le_iff.mpr
    exact lt_of_le_of_lt hb.2 (Int.lt_floor_add_one β)

theorem floor_strip_mem (y : ℝ) :
    0 ≤ y - (⌊y⌋ : ℝ) ∧ y - (⌊y⌋ : ℝ) < 1 := by
  constructor
  · linarith [Int.floor_le y]
  · linarith [Int.lt_floor_add_one y]

theorem transform_eq_left_add_fraction (β x : ℝ) :
    transform β x =
      leftEndpoint β +
        ((-β * x - leftEndpoint β) -
          (⌊-β * x - leftEndpoint β⌋ : ℝ)) := by
  unfold transform digit
  ring

/-- The Ito--Sadahiro transformation preserves its fundamental interval. -/
theorem transform_mem {β x : ℝ} (hβ : 1 < β) :
    InFundamentalInterval β (transform β x) := by
  let y : ℝ := -β * x - leftEndpoint β
  have hf := floor_strip_mem y
  have ht :
      transform β x = leftEndpoint β + (y - (⌊y⌋ : ℝ)) := by
    simpa [y] using transform_eq_left_add_fraction β x
  constructor
  · rw [ht]
    linarith [hf.1]
  · rw [ht, right_eq_left_add_one hβ]
    linarith [hf.2]

/-- Exact one-step reconstruction from the selected digit and next state. -/
theorem one_step_reconstruction {β x : ℝ} (hβ : 1 < β) :
    x =
      (digit β x : ℝ) / (-β) +
        transform β x / (-β) := by
  unfold transform
  field_simp [beta_ne_zero hβ]
  ring

/-- The digit and next state are functions, hence the one-step process is deterministic. -/
theorem step_deterministic {β x : ℝ} {d₁ d₂ : ℤ} {y₁ y₂ : ℝ}
    (hd₁ : d₁ = digit β x) (hy₁ : y₁ = transform β x)
    (hd₂ : d₂ = digit β x) (hy₂ : y₂ = transform β x) :
    d₁ = d₂ ∧ y₁ = y₂ := by
  constructor <;> simp_all

end

end CNRSProblem1
