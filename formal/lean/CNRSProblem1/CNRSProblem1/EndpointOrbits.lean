import CNRSProblem1.Iteration
import CNRSProblem1.QuadraticBases

namespace CNRSProblem1

noncomputable section

set_option maxHeartbeats 300000

/-!
# Exact endpoint dynamics for the three P1 quadratic bases

The right endpoint is excluded from the fundamental interval.  Results whose names
contain `rightBoundary` therefore describe the formal recurrence obtained by
applying the same digit/transform formula at that boundary; they do not assert
membership of the boundary in the fundamental interval.
-/

theorem digit_leftEndpoint {β : ℝ} (hβ : 1 < β) :
    digit β (leftEndpoint β) = ⌊β⌋ := by
  unfold digit
  rw [digit_argument_at_left hβ]

theorem digit_rightBoundary {β : ℝ} (hβ : 1 < β) :
    digit β (rightEndpoint β) = 0 := by
  unfold digit
  rw [digit_argument_at_right hβ]
  norm_num

theorem transform_rightBoundary {β : ℝ} (hβ : 1 < β) :
    transform β (rightEndpoint β) = leftEndpoint β := by
  rw [transform, digit_rightBoundary hβ]
  norm_num
  unfold rightEndpoint leftEndpoint
  field_simp [ne_of_gt (beta_add_one_pos hβ)]

theorem orbit_rightBoundary_shift {β : ℝ} (hβ : 1 < β) (n : ℕ) :
    orbit β (rightEndpoint β) (n + 1) =
      orbit β (leftEndpoint β) n := by
  rw [← orbit_transform, transform_rightBoundary hβ]

@[simp] theorem floor_sqrt_two : ⌊Real.sqrt 2⌋ = 1 := by
  rw [Int.floor_eq_iff]
  norm_num [sqrt_two_bounds.1.le, sqrt_two_bounds.2]

@[simp] theorem floor_sqrt_three_sub_one :
    ⌊Real.sqrt 3 - 1⌋ = 0 := by
  rw [Int.floor_eq_iff]
  constructor
  · norm_num
  · have h : Real.sqrt 3 < 2 := sqrt_three_bounds.2
    norm_num only [Int.cast_zero, zero_add] at *
    linarith

/-! ## Base 1 + sqrt 2 -/

def sqrtTwoFixed : ℝ := -rightEndpoint sqrtTwoBase

theorem sqrtTwo_digit_left :
    digit sqrtTwoBase (leftEndpoint sqrtTwoBase) = 2 := by
  rw [digit_leftEndpoint]
  · exact floor_sqrtTwoBase
  · linarith [sqrtTwoBase_between.1]

theorem sqrtTwo_transform_left :
    transform sqrtTwoBase (leftEndpoint sqrtTwoBase) = sqrtTwoFixed := by
  rw [transform, sqrtTwo_digit_left]
  unfold sqrtTwoFixed
  rw [sqrtTwo_leftEndpoint, sqrtTwo_rightEndpoint]
  unfold sqrtTwoBase
  nlinarith [sqrt_two_sq]

theorem sqrtTwo_digit_fixed :
    digit sqrtTwoBase sqrtTwoFixed = 1 := by
  unfold digit sqrtTwoFixed
  rw [sqrtTwo_rightEndpoint, sqrtTwo_leftEndpoint]
  unfold sqrtTwoBase
  have harg :
      -(1 + Real.sqrt 2) * (-(1 - Real.sqrt 2 / 2)) -
          (-(Real.sqrt 2) / 2) = Real.sqrt 2 := by
    nlinarith [sqrt_two_sq]
  rw [harg]
  exact floor_sqrt_two

theorem sqrtTwo_transform_fixed :
    transform sqrtTwoBase sqrtTwoFixed = sqrtTwoFixed := by
  rw [transform, sqrtTwo_digit_fixed]
  unfold sqrtTwoFixed
  rw [sqrtTwo_rightEndpoint]
  unfold sqrtTwoBase
  nlinarith [sqrt_two_sq]

theorem sqrtTwo_left_orbit_after_first (n : ℕ) :
    orbit sqrtTwoBase (leftEndpoint sqrtTwoBase) (n + 1) =
      sqrtTwoFixed := by
  induction n with
  | zero =>
      simpa using sqrtTwo_transform_left
  | succ n ih =>
      rw [orbit_succ, ih, sqrtTwo_transform_fixed]

theorem sqrtTwo_left_digits :
    orbitDigit sqrtTwoBase (leftEndpoint sqrtTwoBase) 0 = 2 ∧
      ∀ n : ℕ,
        orbitDigit sqrtTwoBase (leftEndpoint sqrtTwoBase) (n + 1) = 1 := by
  constructor
  · exact sqrtTwo_digit_left
  · intro n
    rw [orbitDigit, sqrtTwo_left_orbit_after_first]
    exact sqrtTwo_digit_fixed

theorem sqrtTwo_rightBoundary_digits :
    orbitDigit sqrtTwoBase (rightEndpoint sqrtTwoBase) 0 = 0 ∧
      orbitDigit sqrtTwoBase (rightEndpoint sqrtTwoBase) 1 = 2 ∧
      ∀ n : ℕ,
        orbitDigit sqrtTwoBase (rightEndpoint sqrtTwoBase) (n + 2) = 1 := by
  have hb : 1 < sqrtTwoBase := by linarith [sqrtTwoBase_between.1]
  constructor
  · exact digit_rightBoundary hb
  constructor
  · rw [orbitDigit, show (1 : ℕ) = 0 + 1 by omega,
        orbit_rightBoundary_shift hb]
    exact sqrtTwo_digit_left
  · intro n
    rw [orbitDigit, show n + 2 = (n + 1) + 1 by omega,
        orbit_rightBoundary_shift hb, sqrtTwo_left_orbit_after_first]
    exact sqrtTwo_digit_fixed

/-! ## Base 1 + sqrt 3 -/

theorem sqrtThree_digit_left :
    digit sqrtThreeBase (leftEndpoint sqrtThreeBase) = 2 := by
  rw [digit_leftEndpoint]
  · exact floor_sqrtThreeBase
  · linarith [sqrtThreeBase_between.1]

theorem sqrtThree_transform_left :
    transform sqrtThreeBase (leftEndpoint sqrtThreeBase) = 0 := by
  rw [transform, sqrtThree_digit_left, sqrtThree_leftEndpoint]
  unfold sqrtThreeBase
  calc
    -(1 + Real.sqrt 3) * (1 - Real.sqrt 3) - (2 : ℝ) =
        (Real.sqrt 3) ^ 2 - 3 := by ring
    _ = 0 := by rw [sqrt_three_sq]; norm_num

theorem sqrtThree_digit_zero : digit sqrtThreeBase 0 = 0 := by
  unfold digit
  rw [sqrtThree_leftEndpoint]
  simp only [mul_zero, zero_sub]
  convert floor_sqrt_three_sub_one using 1
  ring_nf

theorem sqrtThree_transform_zero : transform sqrtThreeBase 0 = 0 := by
  rw [transform, sqrtThree_digit_zero]
  norm_num

theorem sqrtThree_left_orbit_after_first (n : ℕ) :
    orbit sqrtThreeBase (leftEndpoint sqrtThreeBase) (n + 1) = 0 := by
  induction n with
  | zero =>
      simpa using sqrtThree_transform_left
  | succ n ih =>
      rw [orbit_succ, ih, sqrtThree_transform_zero]

theorem sqrtThree_left_digits :
    orbitDigit sqrtThreeBase (leftEndpoint sqrtThreeBase) 0 = 2 ∧
      ∀ n : ℕ,
        orbitDigit sqrtThreeBase (leftEndpoint sqrtThreeBase) (n + 1) = 0 := by
  constructor
  · exact sqrtThree_digit_left
  · intro n
    rw [orbitDigit, sqrtThree_left_orbit_after_first]
    exact sqrtThree_digit_zero

theorem sqrtThree_rightBoundary_digits :
    orbitDigit sqrtThreeBase (rightEndpoint sqrtThreeBase) 0 = 0 ∧
      orbitDigit sqrtThreeBase (rightEndpoint sqrtThreeBase) 1 = 2 ∧
      ∀ n : ℕ,
        orbitDigit sqrtThreeBase (rightEndpoint sqrtThreeBase) (n + 2) = 0 := by
  have hb : 1 < sqrtThreeBase := by linarith [sqrtThreeBase_between.1]
  constructor
  · exact digit_rightBoundary hb
  constructor
  · rw [orbitDigit, show (1 : ℕ) = 0 + 1 by omega,
        orbit_rightBoundary_shift hb]
    exact sqrtThree_digit_left
  · intro n
    rw [orbitDigit, show n + 2 = (n + 1) + 1 by omega,
        orbit_rightBoundary_shift hb, sqrtThree_left_orbit_after_first]
    exact sqrtThree_digit_zero

/-! ## Base (3 + sqrt 5) / 2 -/

def goldenCycleNext : ℝ := (2 * Real.sqrt 5 - 5) / 5

theorem golden_digit_left :
    digit goldenBase (leftEndpoint goldenBase) = 2 := by
  rw [digit_leftEndpoint]
  · exact floor_goldenBase
  · linarith [goldenBase_between.1]

theorem golden_transform_left :
    transform goldenBase (leftEndpoint goldenBase) = goldenCycleNext := by
  rw [transform, golden_digit_left, golden_leftEndpoint]
  unfold goldenBase goldenCycleNext
  nlinarith [sqrt_five_sq]

theorem golden_digit_cycleNext :
    digit goldenBase goldenCycleNext = 1 := by
  unfold digit goldenCycleNext
  rw [golden_leftEndpoint]
  unfold goldenBase
  have harg :
      -((3 + Real.sqrt 5) / 2) * ((2 * Real.sqrt 5 - 5) / 5) -
          (-(5 + Real.sqrt 5) / 10) = 1 := by
    nlinarith [sqrt_five_sq]
  rw [harg]
  norm_num

theorem golden_transform_cycleNext :
    transform goldenBase goldenCycleNext =
      leftEndpoint goldenBase := by
  rw [transform, golden_digit_cycleNext, golden_leftEndpoint]
  unfold goldenBase goldenCycleNext
  nlinarith [sqrt_five_sq]

theorem golden_left_orbit_pair (n : ℕ) :
    orbit goldenBase (leftEndpoint goldenBase) (2 * n) =
        leftEndpoint goldenBase ∧
      orbit goldenBase (leftEndpoint goldenBase) (2 * n + 1) =
        goldenCycleNext := by
  induction n with
  | zero =>
      constructor
      · simp
      · simpa using golden_transform_left
  | succ n ih =>
      have heven :
          orbit goldenBase (leftEndpoint goldenBase) (2 * (n + 1)) =
            leftEndpoint goldenBase := by
        calc
          orbit goldenBase (leftEndpoint goldenBase) (2 * (n + 1)) =
              transform goldenBase
                (orbit goldenBase (leftEndpoint goldenBase) (2 * n + 1)) := by
                  rw [show 2 * (n + 1) = (2 * n + 1) + 1 by omega,
                      orbit_succ]
          _ = leftEndpoint goldenBase := by
                rw [ih.2, golden_transform_cycleNext]
      constructor
      · exact heven
      · calc
          orbit goldenBase (leftEndpoint goldenBase) (2 * (n + 1) + 1) =
              transform goldenBase
                (orbit goldenBase (leftEndpoint goldenBase) (2 * (n + 1))) := by
                  rw [orbit_succ]
          _ = goldenCycleNext := by
                rw [heven, golden_transform_left]

theorem golden_left_digits (n : ℕ) :
    orbitDigit goldenBase (leftEndpoint goldenBase) (2 * n) = 2 ∧
      orbitDigit goldenBase (leftEndpoint goldenBase) (2 * n + 1) = 1 := by
  rw [orbitDigit, orbitDigit, (golden_left_orbit_pair n).1,
      (golden_left_orbit_pair n).2]
  exact ⟨golden_digit_left, golden_digit_cycleNext⟩

theorem golden_rightBoundary_digits :
    orbitDigit goldenBase (rightEndpoint goldenBase) 0 = 0 ∧
      (∀ n : ℕ,
        orbitDigit goldenBase (rightEndpoint goldenBase) (2 * n + 1) = 2) ∧
      (∀ n : ℕ,
        orbitDigit goldenBase (rightEndpoint goldenBase) (2 * n + 2) = 1) := by
  have hb : 1 < goldenBase := by linarith [goldenBase_between.1]
  constructor
  · exact digit_rightBoundary hb
  constructor
  · intro n
    rw [orbitDigit, show 2 * n + 1 = (2 * n) + 1 by omega,
        orbit_rightBoundary_shift hb, (golden_left_orbit_pair n).1]
    exact golden_digit_left
  · intro n
    rw [orbitDigit, show 2 * n + 2 = (2 * n + 1) + 1 by omega,
        orbit_rightBoundary_shift hb, (golden_left_orbit_pair n).2]
    exact golden_digit_cycleNext

end

end CNRSProblem1
