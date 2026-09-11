import CNRSProblem1.QuadraticBases

namespace CNRSProblem1

noncomputable section

theorem quadraticPisot_trace_norm_cases
    {β β' : ℝ} {m n : ℤ}
    (hβ : (2 : ℝ) < β ∧ β < 3)
    (hβ' : (-1 : ℝ) < β' ∧ β' < 1)
    (htrace : β + β' = m)
    (hnorm : β * β' = n) :
    (m = 2 ∧ n = -2) ∨
    (m = 2 ∧ n = -1) ∨
    (m = 3 ∧ n = 1) := by
  have hmlo : (1 : ℝ) < m := by linarith
  have hmhi : (m : ℝ) < 4 := by linarith
  have hmloz : (1 : ℤ) < m := by exact_mod_cast hmlo
  have hmhiz : m < (4 : ℤ) := by exact_mod_cast hmhi
  have hm : m = 2 ∨ m = 3 := by omega
  rcases hm with rfl | rfl
  · have hb' : β' = 2 - β := by norm_num at htrace ⊢; linarith
    have hnlo : (-3 : ℝ) < n := by
      rw [← hnorm, hb']
      nlinarith
    have hnhi : (n : ℝ) < 0 := by
      rw [← hnorm, hb']
      nlinarith
    have hnloz : (-3 : ℤ) < n := by exact_mod_cast hnlo
    have hnhiz : n < (0 : ℤ) := by exact_mod_cast hnhi
    have hn : n = -2 ∨ n = -1 := by omega
    rcases hn with rfl | rfl
    · exact Or.inl ⟨rfl, rfl⟩
    · exact Or.inr (Or.inl ⟨rfl, rfl⟩)
  · have hb' : β' = 3 - β := by norm_num at htrace ⊢; linarith
    have hnlo : (0 : ℝ) < n := by
      rw [← hnorm, hb']
      nlinarith
    have hnhi : (n : ℝ) < 2 := by
      rw [← hnorm, hb']
      nlinarith
    have hnloz : (0 : ℤ) < n := by exact_mod_cast hnlo
    have hnhiz : n < (2 : ℤ) := by exact_mod_cast hnhi
    have hn : n = 1 := by omega
    subst n
    exact Or.inr (Or.inr ⟨rfl, rfl⟩)

theorem classified_base_polynomials :
    sqrtTwoBase ^ 2 - 2 * sqrtTwoBase - 1 = 0 ∧
    sqrtThreeBase ^ 2 - 2 * sqrtThreeBase - 2 = 0 ∧
    goldenBase ^ 2 - 3 * goldenBase + 1 = 0 :=
  ⟨sqrtTwoBase_polynomial, sqrtThreeBase_polynomial,
    goldenBase_polynomial⟩

/-- Exact algebraic data used by the P1 quadratic classification.  The
conjugate is carried explicitly, so the theorem does not rely on an
unformalized ambient definition of "Pisot number". -/
structure QuadraticPisotIntervalData where
  beta : ℝ
  conjugate : ℝ
  trace : ℤ
  norm : ℤ
  beta_mem : (2 : ℝ) < beta ∧ beta < 3
  conjugate_mem : (-1 : ℝ) < conjugate ∧ conjugate < 1
  trace_eq : beta + conjugate = trace
  norm_eq : beta * conjugate = norm

theorem beta_polynomial_of_trace_norm
    (D : QuadraticPisotIntervalData) :
    D.beta ^ 2 - (D.trace : ℝ) * D.beta + D.norm = 0 := by
  rw [← D.norm_eq, ← D.trace_eq]
  ring

/-- The interval and integral trace/norm hypotheses select exactly the three
quadratic bases occurring in P1 v12. -/
theorem quadraticPisotIntervalData_classification
    (D : QuadraticPisotIntervalData) :
    D.beta = sqrtTwoBase ∨
    D.beta = sqrtThreeBase ∨
    D.beta = goldenBase := by
  have hcases := quadraticPisot_trace_norm_cases D.beta_mem D.conjugate_mem
    D.trace_eq D.norm_eq
  rcases hcases with h | h | h
  · rcases h with ⟨ht, hn⟩
    have hp := beta_polynomial_of_trace_norm D
    rw [ht, hn] at hp
    right; left
    unfold sqrtThreeBase
    have hfac :
        (D.beta - (1 + Real.sqrt 3)) *
          (D.beta - (1 - Real.sqrt 3)) = 0 := by
      norm_num at hp
      ring_nf
      nlinarith [sqrt_three_sq]
    rcases mul_eq_zero.mp hfac with hroot | hroot
    · linarith
    · have hs := Real.sqrt_nonneg 3
      nlinarith [D.beta_mem.1]
  · rcases h with ⟨ht, hn⟩
    have hp := beta_polynomial_of_trace_norm D
    rw [ht, hn] at hp
    left
    unfold sqrtTwoBase
    have hfac :
        (D.beta - (1 + Real.sqrt 2)) *
          (D.beta - (1 - Real.sqrt 2)) = 0 := by
      norm_num at hp
      ring_nf
      nlinarith [sqrt_two_sq]
    rcases mul_eq_zero.mp hfac with hroot | hroot
    · linarith
    · have hs := Real.sqrt_nonneg 2
      nlinarith [D.beta_mem.1]
  · rcases h with ⟨ht, hn⟩
    have hp := beta_polynomial_of_trace_norm D
    rw [ht, hn] at hp
    right; right
    unfold goldenBase
    have hfac :
        (D.beta - (3 + Real.sqrt 5) / 2) *
          (D.beta - (3 - Real.sqrt 5) / 2) = 0 := by
      norm_num at hp
      ring_nf
      nlinarith [sqrt_five_sq]
    rcases mul_eq_zero.mp hfac with hroot | hroot
    · linarith
    · have hs := Real.sqrt_nonneg 5
      nlinarith [D.beta_mem.1]

end

end CNRSProblem1