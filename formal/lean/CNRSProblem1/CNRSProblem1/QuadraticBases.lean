import CNRSProblem1.Framework

namespace CNRSProblem1

noncomputable section

def sqrtTwoBase : ℝ := 1 + Real.sqrt 2
def sqrtThreeBase : ℝ := 1 + Real.sqrt 3
def goldenBase : ℝ := (3 + Real.sqrt 5) / 2

theorem sqrt_two_sq : (Real.sqrt 2) ^ 2 = 2 := by norm_num
theorem sqrt_three_sq : (Real.sqrt 3) ^ 2 = 3 := by norm_num
theorem sqrt_five_sq : (Real.sqrt 5) ^ 2 = 5 := by norm_num

theorem sqrt_two_bounds : (1 : ℝ) < Real.sqrt 2 ∧ Real.sqrt 2 < 2 := by
  have h := Real.sqrt_nonneg 2
  constructor <;> nlinarith [sqrt_two_sq]

theorem sqrt_three_bounds : (1 : ℝ) < Real.sqrt 3 ∧ Real.sqrt 3 < 2 := by
  have h := Real.sqrt_nonneg 3
  constructor <;> nlinarith [sqrt_three_sq]

theorem sqrt_five_bounds : (2 : ℝ) < Real.sqrt 5 ∧ Real.sqrt 5 < 3 := by
  have h := Real.sqrt_nonneg 5
  constructor <;> nlinarith [sqrt_five_sq]

theorem sqrtTwoBase_between : (2 : ℝ) < sqrtTwoBase ∧ sqrtTwoBase < 3 := by
  rcases sqrt_two_bounds with ⟨h₁, h₂⟩
  constructor <;> unfold sqrtTwoBase <;> linarith

theorem sqrtThreeBase_between : (2 : ℝ) < sqrtThreeBase ∧ sqrtThreeBase < 3 := by
  rcases sqrt_three_bounds with ⟨h₁, h₂⟩
  constructor <;> unfold sqrtThreeBase <;> linarith

theorem goldenBase_between : (2 : ℝ) < goldenBase ∧ goldenBase < 3 := by
  rcases sqrt_five_bounds with ⟨h₁, h₂⟩
  constructor <;> unfold goldenBase <;> linarith

@[simp] theorem floor_sqrtTwoBase : ⌊sqrtTwoBase⌋ = 2 := by
  rw [Int.floor_eq_iff]
  norm_num [sqrtTwoBase_between.1.le, sqrtTwoBase_between.2]

@[simp] theorem floor_sqrtThreeBase : ⌊sqrtThreeBase⌋ = 2 := by
  rw [Int.floor_eq_iff]
  norm_num [sqrtThreeBase_between.1.le, sqrtThreeBase_between.2]

@[simp] theorem floor_goldenBase : ⌊goldenBase⌋ = 2 := by
  rw [Int.floor_eq_iff]
  norm_num [goldenBase_between.1.le, goldenBase_between.2]

theorem sqrtTwoBase_polynomial :
    sqrtTwoBase ^ 2 - 2 * sqrtTwoBase - 1 = 0 := by
  unfold sqrtTwoBase
  nlinarith [sqrt_two_sq]

theorem sqrtThreeBase_polynomial :
    sqrtThreeBase ^ 2 - 2 * sqrtThreeBase - 2 = 0 := by
  unfold sqrtThreeBase
  nlinarith [sqrt_three_sq]

theorem goldenBase_polynomial :
    goldenBase ^ 2 - 3 * goldenBase + 1 = 0 := by
  unfold goldenBase
  nlinarith [sqrt_five_sq]

theorem sqrtTwo_leftEndpoint :
    leftEndpoint sqrtTwoBase = -(Real.sqrt 2) / 2 := by
  have hn : sqrtTwoBase + 1 ≠ 0 := by
    have := sqrtTwoBase_between.1
    linarith
  unfold leftEndpoint sqrtTwoBase
  field_simp
  nlinarith [sqrt_two_sq]

theorem sqrtTwo_rightEndpoint :
    rightEndpoint sqrtTwoBase = 1 - (Real.sqrt 2) / 2 := by
  have hn : sqrtTwoBase + 1 ≠ 0 := by
    have := sqrtTwoBase_between.1
    linarith
  unfold rightEndpoint sqrtTwoBase
  field_simp
  nlinarith [sqrt_two_sq]

theorem sqrtThree_leftEndpoint :
    leftEndpoint sqrtThreeBase = 1 - Real.sqrt 3 := by
  have hn : sqrtThreeBase + 1 ≠ 0 := by
    have := sqrtThreeBase_between.1
    linarith
  unfold leftEndpoint sqrtThreeBase
  field_simp
  nlinarith [sqrt_three_sq]

theorem sqrtThree_rightEndpoint :
    rightEndpoint sqrtThreeBase = 2 - Real.sqrt 3 := by
  have hn : sqrtThreeBase + 1 ≠ 0 := by
    have := sqrtThreeBase_between.1
    linarith
  unfold rightEndpoint sqrtThreeBase
  field_simp
  nlinarith [sqrt_three_sq]

theorem golden_leftEndpoint :
    leftEndpoint goldenBase = -(5 + Real.sqrt 5) / 10 := by
  have hn : goldenBase + 1 ≠ 0 := by
    have := goldenBase_between.1
    linarith
  unfold leftEndpoint goldenBase
  field_simp
  nlinarith [sqrt_five_sq]

theorem golden_rightEndpoint :
    rightEndpoint goldenBase = (5 - Real.sqrt 5) / 10 := by
  have hn : goldenBase + 1 ≠ 0 := by
    have := goldenBase_between.1
    linarith
  unfold rightEndpoint goldenBase
  field_simp
  nlinarith [sqrt_five_sq]

end

end CNRSProblem1
