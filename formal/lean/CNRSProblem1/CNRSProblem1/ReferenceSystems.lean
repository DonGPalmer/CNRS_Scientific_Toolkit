import CNRSProblem1.Admissibility

namespace CNRSProblem1

noncomputable section

theorem sqrtTwo_lower_value_zero :
    lowerReference sqrtTwoBase 0 = 2 :=
  sqrtTwo_left_digits.1

theorem sqrtTwo_lower_value_succ (n : ℕ) :
    lowerReference sqrtTwoBase (n + 1) = 1 :=
  sqrtTwo_left_digits.2 n

theorem sqrtThree_lower_value_zero :
    lowerReference sqrtThreeBase 0 = 2 :=
  sqrtThree_left_digits.1

theorem sqrtThree_lower_value_succ (n : ℕ) :
    lowerReference sqrtThreeBase (n + 1) = 0 :=
  sqrtThree_left_digits.2 n

theorem golden_lower_value_even (n : ℕ) :
    lowerReference goldenBase (2 * n) = 2 :=
  (golden_left_digits n).1

theorem golden_lower_value_odd (n : ℕ) :
    lowerReference goldenBase (2 * n + 1) = 1 :=
  (golden_left_digits n).2

theorem lowerReferences_pairwise_distinct :
    lowerReference sqrtTwoBase ≠ lowerReference sqrtThreeBase ∧
    lowerReference sqrtTwoBase ≠ lowerReference goldenBase ∧
    lowerReference sqrtThreeBase ≠ lowerReference goldenBase := by
  constructor
  · intro h
    have := congrFun h 1
    rw [sqrtTwo_lower_value_succ 0, sqrtThree_lower_value_succ 0] at this
    norm_num at this
  constructor
  · intro h
    have := congrFun h 2
    rw [sqrtTwo_lower_value_succ 1,
      show (2 : ℕ) = 2 * 1 by norm_num, golden_lower_value_even 1] at this
    norm_num at this
  · intro h
    have := congrFun h 1
    rw [sqrtThree_lower_value_succ 0,
      show (1 : ℕ) = 2 * 0 + 1 by norm_num, golden_lower_value_odd 0] at this
    norm_num at this

theorem rightBoundary_first_two
    (h : (1 : ℝ) < β) :
    rightBoundaryStream β 0 = 0 ∧
    rightBoundaryStream β 1 = lowerReference β 0 := by
  constructor
  · exact digit_rightBoundary h
  · change orbitDigit β (rightEndpoint β) 1 =
      orbitDigit β (leftEndpoint β) 0
    rw [orbitDigit, orbitDigit, show (1 : ℕ) = 0 + 1 by omega,
      orbit_rightBoundary_shift h]

theorem sqrtThree_lower_shift_succ (n : ℕ) :
    streamShift (lowerReference sqrtThreeBase) (n + 1) = fun _ => 0 := by
  funext k
  simp only [streamShift]
  rw [show n + 1 + k = (n + k) + 1 by omega,
    sqrtThree_lower_value_succ]

theorem sqrtThree_lower_symbolicallyAdmissible :
    SymbolicallyAdmissibleFor sqrtThreeReferenceSystem
      (lowerReference sqrtThreeBase) := by
  change ISAdmissibleBetween (lowerReference sqrtThreeBase)
    (rightBoundaryStream sqrtThreeBase) (lowerReference sqrtThreeBase)
  intro n
  rcases n with _ | n
  · rw [streamShift_zero]
    constructor
    · exact altLE_refl _
    · apply altLT_of_first
      · rw [sqrtThree_lower_value_zero,
          (rightBoundary_first_two (by linarith [sqrtThreeBase_between.1])).1]
        norm_num
      · rw [sqrtThree_lower_value_zero,
          (rightBoundary_first_two (by linarith [sqrtThreeBase_between.1])).1]
        norm_num
  · rw [sqrtThree_lower_shift_succ]
    constructor
    · exact Or.inr (altLT_of_first (by rw [sqrtThree_lower_value_zero]; norm_num)
          (by rw [sqrtThree_lower_value_zero]; norm_num))
    · apply altLT_of_second
      · rw [(rightBoundary_first_two
          (by linarith [sqrtThreeBase_between.1])).1]
      · rw [(rightBoundary_first_two
          (by linarith [sqrtThreeBase_between.1])).2,
          sqrtThree_lower_value_zero]
        norm_num
      · rw [(rightBoundary_first_two
          (by linarith [sqrtThreeBase_between.1])).2,
          sqrtThree_lower_value_zero]
        norm_num

theorem sqrtThree_lower_not_sqrtTwo_symbolicallyAdmissible :
    ¬ SymbolicallyAdmissibleFor sqrtTwoReferenceSystem
      (lowerReference sqrtThreeBase) := by
  change ¬ ISAdmissibleBetween (lowerReference sqrtTwoBase)
    (rightBoundaryStream sqrtTwoBase) (lowerReference sqrtThreeBase)
  intro h
  have h0 := (h 0).1
  rw [streamShift_zero] at h0
  apply (not_altLE_of_second_reverse
    (a := lowerReference sqrtTwoBase)
    (b := lowerReference sqrtThreeBase))
  · rw [sqrtTwo_lower_value_zero, sqrtThree_lower_value_zero]
  · rw [sqrtTwo_lower_value_succ 0, sqrtThree_lower_value_succ 0]
    norm_num
  · simpa using h0

theorem sqrtThree_lower_not_golden_symbolicallyAdmissible :
    ¬ SymbolicallyAdmissibleFor goldenReferenceSystem
      (lowerReference sqrtThreeBase) := by
  change ¬ ISAdmissibleBetween (lowerReference goldenBase)
    (rightBoundaryStream goldenBase) (lowerReference sqrtThreeBase)
  intro h
  have h0 := (h 0).1
  rw [streamShift_zero] at h0
  apply (not_altLE_of_second_reverse
    (a := lowerReference goldenBase)
    (b := lowerReference sqrtThreeBase))
  · rw [golden_lower_value_even 0, sqrtThree_lower_value_zero]
  · rw [golden_lower_value_odd 0, sqrtThree_lower_value_succ 0]
    norm_num
  · simpa using h0

theorem golden_lower_shift_even (n : ℕ) :
    streamShift (lowerReference goldenBase) (2 * n) =
      lowerReference goldenBase := by
  funext k
  rcases Nat.even_or_odd k with ⟨j, rfl⟩ | ⟨j, rfl⟩
  · rw [streamShift, show 2 * n + (j + j) = 2 * (n + j) by omega,
      show j + j = 2 * j by omega,
      golden_lower_value_even, golden_lower_value_even]
  · rw [streamShift,
      show 2 * n + (2 * j + 1) = 2 * (n + j) + 1 by omega,
      golden_lower_value_odd, golden_lower_value_odd]

theorem golden_lower_shift_odd (n : ℕ) :
    streamShift (lowerReference goldenBase) (2 * n + 1) =
      streamShift (lowerReference goldenBase) 1 := by
  rw [show 2 * n + 1 = 2 * n + 1 by rfl, ← streamShift_add,
    golden_lower_shift_even]

theorem golden_lower_symbolicallyAdmissible :
    SymbolicallyAdmissibleFor goldenReferenceSystem
      (lowerReference goldenBase) := by
  change ISAdmissibleBetween (lowerReference goldenBase)
    (rightBoundaryStream goldenBase) (lowerReference goldenBase)
  intro n
  rcases Nat.even_or_odd n with ⟨k, hk⟩ | ⟨k, hk⟩
  · rw [show n = 2 * k by omega, golden_lower_shift_even]
    constructor
    · exact altLE_refl _
    · apply altLT_of_first
      · rw [golden_lower_value_even 0,
          (rightBoundary_first_two (by linarith [goldenBase_between.1])).1]
        norm_num
      · rw [golden_lower_value_even 0,
          (rightBoundary_first_two (by linarith [goldenBase_between.1])).1]
        norm_num
  · rw [show n = 2 * k + 1 by omega, golden_lower_shift_odd]
    constructor
    · exact Or.inr (altLT_of_first
          (by rw [streamShift, golden_lower_value_even 0,
              golden_lower_value_odd 0]; norm_num)
          (by rw [streamShift, golden_lower_value_even 0,
              golden_lower_value_odd 0]; norm_num))
    · apply altLT_of_first
      · rw [streamShift, golden_lower_value_odd 0,
          (rightBoundary_first_two (by linarith [goldenBase_between.1])).1]
        norm_num
      · rw [streamShift, golden_lower_value_odd 0,
          (rightBoundary_first_two (by linarith [goldenBase_between.1])).1]
        norm_num

theorem golden_lower_not_sqrtTwo_symbolicallyAdmissible :
    ¬ SymbolicallyAdmissibleFor sqrtTwoReferenceSystem
      (lowerReference goldenBase) := by
  change ¬ ISAdmissibleBetween (lowerReference sqrtTwoBase)
    (rightBoundaryStream sqrtTwoBase) (lowerReference goldenBase)
  intro h
  have h0 := (h 0).1
  rw [streamShift_zero] at h0
  rcases h0 with heq | ⟨k, hfirst, hord⟩
  · have h := congrFun heq 2
    rw [sqrtTwo_lower_value_succ 1, golden_lower_value_even 1] at h
    norm_num at h
  · rcases hfirst with ⟨hprefix, hne⟩
    by_cases hk0 : k = 0
    · subst k
      exact hne (by rw [sqrtTwo_lower_value_zero, golden_lower_value_even 0])
    by_cases hk1 : k = 1
    · subst k
      exact hne (by rw [sqrtTwo_lower_value_succ 0, golden_lower_value_odd 0])
    by_cases hk2 : k = 2
    · subst k
      simp only [show Even 2 by decide, if_true] at hord
      rw [sqrtTwo_lower_value_succ 1, golden_lower_value_even 1] at hord
      omega
    · have hsame := hprefix 2 (by omega)
      rw [sqrtTwo_lower_value_succ 1, golden_lower_value_even 1] at hsame
      norm_num at hsame

/-- The three explicitly packaged symbolic languages are pairwise distinct.
The first witness is the sqrt-three lower word; the second is the golden
lower word. -/
theorem three_symbolic_languages_pairwise_distinct :
    (∃ a, SymbolicallyAdmissibleFor sqrtThreeReferenceSystem a ∧
      ¬ SymbolicallyAdmissibleFor sqrtTwoReferenceSystem a) ∧
    (∃ a, SymbolicallyAdmissibleFor sqrtThreeReferenceSystem a ∧
      ¬ SymbolicallyAdmissibleFor goldenReferenceSystem a) ∧
    (∃ a, SymbolicallyAdmissibleFor goldenReferenceSystem a ∧
      ¬ SymbolicallyAdmissibleFor sqrtTwoReferenceSystem a) :=
  ⟨⟨_, sqrtThree_lower_symbolicallyAdmissible,
      sqrtThree_lower_not_sqrtTwo_symbolicallyAdmissible⟩,
   ⟨⟨_, sqrtThree_lower_symbolicallyAdmissible,
      sqrtThree_lower_not_golden_symbolicallyAdmissible⟩,
    ⟨_, golden_lower_symbolicallyAdmissible,
      golden_lower_not_sqrtTwo_symbolicallyAdmissible⟩⟩⟩

end

end CNRSProblem1