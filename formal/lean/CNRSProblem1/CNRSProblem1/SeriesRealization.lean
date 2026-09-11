import CNRSProblem1.Cylinders

namespace CNRSProblem1

noncomputable section

/-!
# P1-L5: symbolic admissibility implies orbit realization

This file supplies the missing converse in the Ito--Sadahiro language
theorem.  The proof follows the finite-prefix estimate behind Lemma 9 of
Ito--Sadahiro: admissibility traps every partial negative-base value between
the two endpoint orbits, with an error that contracts by `β⁻¹` at each step.
-/

theorem altLE_head_le {a b : DigitStream} (h : AltLE a b) : b 0 ≤ a 0 := by
  rcases h with rfl | ⟨k, ⟨hpre, _hne⟩, hord⟩
  · exact le_rfl
  · cases k with
    | zero => simpa using hord.le
    | succ k =>
        have h0 := hpre 0 (Nat.zero_lt_succ k)
        omega

/-- Removing a common first digit reverses alternating order. -/
theorem altLE_shift_one_flip {a b : DigitStream}
    (h : AltLE a b) (h0 : a 0 = b 0) :
    AltLE (streamShift b 1) (streamShift a 1) := by
  rcases h with rfl | ⟨k, ⟨hpre, hne⟩, hord⟩
  · exact Or.inl rfl
  · cases k with
    | zero => exact (hne h0).elim
    | succ k =>
        apply Or.inr
        refine ⟨k, ?_, ?_⟩
        · constructor
          · intro j hj
            simpa [streamShift, Nat.add_comm, Nat.add_left_comm,
              Nat.add_assoc] using (hpre (j + 1) (by omega)).symm
          · simpa [streamShift, Nat.add_comm, Nat.add_left_comm,
              Nat.add_assoc] using (Ne.symm hne)
        · rcases Nat.even_or_odd k with hk | hk
          · have hks : ¬ Even (k + 1) := by
              rintro ⟨t, ht⟩
              rcases hk with ⟨s, hs⟩
              omega
            simpa [streamShift, hk, hks, Nat.add_comm, Nat.add_left_comm,
              Nat.add_assoc] using hord
          · have hknot : ¬ Even k := by
              rintro ⟨t, ht⟩
              rcases hk with ⟨s, hs⟩
              omega
            have hks : Even (k + 1) := by
              rcases hk with ⟨s, hs⟩
              refine ⟨s + 1, ?_⟩
              omega
            simpa [streamShift, hknot, hks, Nat.add_comm, Nat.add_left_comm,
              Nat.add_assoc] using hord

theorem rightBoundary_shift_one {β : ℝ} (hβ : 1 < β) :
    streamShift (rightBoundaryStream β) 1 = lowerReference β := by
  unfold rightBoundaryStream lowerReference
  rw [orbitStream_shift]
  rw [show (1 : ℕ) = 0 + 1 by omega, orbit_succ, orbit_zero,
    transform_rightBoundary hβ]

/-- The real state represented by the `m`th suffix of the formal right
boundary stream. -/
def boundaryState (β : ℝ) (m : ℕ) : ℝ :=
  orbit β (rightEndpoint β) m

theorem boundaryStream_shift (β : ℝ) (m : ℕ) :
    streamShift (rightBoundaryStream β) m =
      orbitStream β (boundaryState β m) := by
  exact orbitStream_shift β (rightEndpoint β) m

theorem boundaryState_bounds {β : ℝ} (hβ : 1 < β) (m : ℕ) :
    leftEndpoint β ≤ boundaryState β m ∧
      boundaryState β m ≤ rightEndpoint β :=
  rightEndpoint_orbitClosedBounds hβ m

theorem leftEndpoint_gt_neg_one {β : ℝ} (hβ : 1 < β) :
    -1 < leftEndpoint β := by
  unfold leftEndpoint
  have hp := beta_add_one_pos hβ
  apply (lt_div_iff₀ hp).2
  nlinarith

theorem rightEndpoint_lt_one {β : ℝ} (hβ : 1 < β) :
    rightEndpoint β < 1 := by
  unfold rightEndpoint
  have hp := beta_add_one_pos hβ
  apply (div_lt_iff₀ hp).2
  linarith

/-- Value of a finite digit prefix, with terminal state zero. -/
def wordPrefixValue (β : ℝ) (a : DigitStream) : ℕ → ℝ
  | 0 => 0
  | n + 1 => ((a 0 : ℤ) : ℝ) / (-β) +
      wordPrefixValue β (streamShift a 1) n / (-β)

@[simp] theorem wordPrefixValue_zero (β : ℝ) (a : DigitStream) :
    wordPrefixValue β a 0 = 0 := rfl

@[simp] theorem wordPrefixValue_succ (β : ℝ) (a : DigitStream) (n : ℕ) :
    wordPrefixValue β a (n + 1) = ((a 0 : ℤ) : ℝ) / (-β) +
      wordPrefixValue β (streamShift a 1) n / (-β) := rfl

theorem boundaryState_reconstruction {β : ℝ} (hβ : 1 < β) (m : ℕ) :
    boundaryState β m =
      (((rightBoundaryStream β m : ℤ) : ℝ) +
        boundaryState β (m + 1)) / (-β) := by
  have h := one_step_reconstruction
    (β := β) (x := boundaryState β m) hβ
  have hd : digit β (boundaryState β m) = rightBoundaryStream β m := by
    rfl
  have ht : transform β (boundaryState β m) = boundaryState β (m + 1) := by
    simp [boundaryState, orbit_succ]
  rw [hd, ht] at h
  calc
    boundaryState β m =
        ((rightBoundaryStream β m : ℤ) : ℝ) / (-β) +
          boundaryState β (m + 1) / (-β) := h
    _ = (((rightBoundaryStream β m : ℤ) : ℝ) +
          boundaryState β (m + 1)) / (-β) := by ring

theorem invPow_succ {β : ℝ} (hβ : 1 < β) (n : ℕ) :
    1 / β ^ (n + 1) = (1 / β ^ n) / β := by
  rw [pow_succ]
  field_simp [beta_ne_zero hβ]

/-- Simultaneous lower and upper finite-prefix estimates.  The reference can
be any suffix of the formal right-boundary orbit. -/
theorem wordPrefixValue_boundary_estimates
    {β : ℝ} (hβ : 1 < β) (a : DigitStream)
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) :
    ∀ N m n : ℕ,
      (AltLE (streamShift (rightBoundaryStream β) m)
          (streamShift a n) →
        boundaryState β m - 1 / β ^ N ≤
          wordPrefixValue β (streamShift a n) N) ∧
      (AltLE (streamShift a n)
          (streamShift (rightBoundaryStream β) m) →
        wordPrefixValue β (streamShift a n) N ≤
          boundaryState β m + 1 / β ^ N) := by
  intro N
  induction N with
  | zero =>
      intro m n
      constructor
      · intro _
        simp only [wordPrefixValue_zero, pow_zero, div_one]
        have hb := (boundaryState_bounds hβ m).2
        linarith [rightEndpoint_lt_one hβ]
      · intro _
        simp only [wordPrefixValue_zero, pow_zero, div_one]
        have hb := (boundaryState_bounds hβ m).1
        linarith [leftEndpoint_gt_neg_one hβ]
  | succ N ih =>
      intro m n
      have hβ0 : 0 < β := lt_trans zero_lt_one hβ
      have hβneg : -β < 0 := neg_neg_of_pos hβ0
      have hwidth := interval_width hβ
      have hrefNext := boundaryState_bounds hβ (m + 1)
      constructor
      · intro hrel
        have hhead :
            streamShift a n 0 ≤
              streamShift (rightBoundaryStream β) m 0 :=
          altLE_head_le hrel
        have hnum :
            ((streamShift a n 0 : ℤ) : ℝ) +
                wordPrefixValue β (streamShift (streamShift a n) 1) N ≤
              ((streamShift (rightBoundaryStream β) m 0 : ℤ) : ℝ) +
                boundaryState β (m + 1) + 1 / β ^ N := by
          by_cases heq : streamShift a n 0 =
              streamShift (rightBoundaryStream β) m 0
          · have hflip := altLE_shift_one_flip hrel heq.symm
            have htail := (ih (m + 1) (n + 1)).2 (by
              simpa [streamShift_add, Nat.add_comm, Nat.add_left_comm,
                Nat.add_assoc] using hflip)
            have hshift :
                wordPrefixValue β (streamShift (streamShift a n) 1) N =
                  wordPrefixValue β (streamShift a (n + 1)) N := by
              simp [streamShift_add]
            rw [hshift, heq]
            linarith
          · have hgap :
                ((streamShift a n 0 : ℤ) : ℝ) + 1 ≤
                  ((streamShift (rightBoundaryStream β) m 0 : ℤ) : ℝ) := by
              exact_mod_cast (show streamShift a n 0 + 1 ≤
                streamShift (rightBoundaryStream β) m 0 by omega)
            have hupper : AltLE (streamShift a (n + 1))
                (streamShift (rightBoundaryStream β) 0) :=
              Or.inr (by simpa [streamShift_zero] using (hadm (n + 1)).2)
            have htail := (ih 0 (n + 1)).2 hupper
            have hright0 : boundaryState β 0 = rightEndpoint β := by
              simp [boundaryState]
            rw [hright0] at htail
            have hnext := hrefNext.1
            have hshift :
                wordPrefixValue β (streamShift (streamShift a n) 1) N =
                  wordPrefixValue β (streamShift a (n + 1)) N := by
              simp [streamShift_add]
            rw [hshift]
            linarith
        rw [wordPrefixValue_succ, invPow_succ hβ]
        have hdiv :
            ((((streamShift (rightBoundaryStream β) m 0 : ℤ) : ℝ) +
                boundaryState β (m + 1) + 1 / β ^ N) / (-β)) ≤
              ((((streamShift a n 0 : ℤ) : ℝ) +
                wordPrefixValue β (streamShift (streamShift a n) 1) N) / (-β)) := by
          apply (div_le_iff_of_neg hβneg).2
          rw [div_mul_cancel₀]
          · exact hnum
          · linarith
        calc
          boundaryState β m - (1 / β ^ N) / β =
              (((streamShift (rightBoundaryStream β) m 0 : ℤ) : ℝ) +
                boundaryState β (m + 1) + 1 / β ^ N) / (-β) := by
                  rw [boundaryState_reconstruction hβ m]
                  simp only [streamShift]
                  field_simp [beta_ne_zero hβ]
                  ring_nf
          _ ≤ (((streamShift a n 0 : ℤ) : ℝ) +
                wordPrefixValue β (streamShift (streamShift a n) 1) N) /
                (-β) := hdiv
          _ = ((streamShift a n 0 : ℤ) : ℝ) / (-β) +
                wordPrefixValue β (streamShift (streamShift a n) 1) N /
                  (-β) := by ring
      · intro hrel
        have hhead :
            streamShift (rightBoundaryStream β) m 0 ≤
              streamShift a n 0 := altLE_head_le hrel
        have hnum :
            ((streamShift (rightBoundaryStream β) m 0 : ℤ) : ℝ) +
                boundaryState β (m + 1) - 1 / β ^ N ≤
              ((streamShift a n 0 : ℤ) : ℝ) +
                wordPrefixValue β (streamShift (streamShift a n) 1) N := by
          by_cases heq : streamShift a n 0 =
              streamShift (rightBoundaryStream β) m 0
          · have hflip := altLE_shift_one_flip hrel heq
            have htail := (ih (m + 1) (n + 1)).1 (by
              simpa [streamShift_add, Nat.add_comm, Nat.add_left_comm,
                Nat.add_assoc] using hflip)
            have hshift :
                wordPrefixValue β (streamShift (streamShift a n) 1) N =
                  wordPrefixValue β (streamShift a (n + 1)) N := by
              simp [streamShift_add]
            rw [hshift, heq]
            linarith
          · have hgap :
                ((streamShift (rightBoundaryStream β) m 0 : ℤ) : ℝ) + 1 ≤
                  ((streamShift a n 0 : ℤ) : ℝ) := by
              exact_mod_cast (show streamShift (rightBoundaryStream β) m 0 + 1 ≤
                streamShift a n 0 by omega)
            have hlower : AltLE (streamShift (rightBoundaryStream β) 1)
                (streamShift a (n + 1)) := by
              rw [rightBoundary_shift_one hβ]
              exact (hadm (n + 1)).1
            have htail := (ih 1 (n + 1)).1 hlower
            have hleft1 : boundaryState β 1 = leftEndpoint β := by
              change transform β (rightEndpoint β) = leftEndpoint β
              exact transform_rightBoundary hβ
            rw [hleft1] at htail
            have hnext := hrefNext.2
            have hshift :
                wordPrefixValue β (streamShift (streamShift a n) 1) N =
                  wordPrefixValue β (streamShift a (n + 1)) N := by
              simp [streamShift_add]
            rw [hshift]
            linarith
        rw [wordPrefixValue_succ, invPow_succ hβ]
        have hdiv :
            ((((streamShift a n 0 : ℤ) : ℝ) +
                wordPrefixValue β (streamShift (streamShift a n) 1) N) / (-β)) ≤
              ((((streamShift (rightBoundaryStream β) m 0 : ℤ) : ℝ) +
                boundaryState β (m + 1) - 1 / β ^ N) / (-β)) := by
          apply (div_le_iff_of_neg hβneg).2
          rw [div_mul_cancel₀]
          · exact hnum
          · linarith
        calc
          ((streamShift a n 0 : ℤ) : ℝ) / (-β) +
                wordPrefixValue β (streamShift (streamShift a n) 1) N /
                  (-β) =
              (((streamShift a n 0 : ℤ) : ℝ) +
                wordPrefixValue β (streamShift (streamShift a n) 1) N) /
                (-β) := by ring
          _ ≤ (((streamShift (rightBoundaryStream β) m 0 : ℤ) : ℝ) +
                boundaryState β (m + 1) - 1 / β ^ N) / (-β) := hdiv
          _ = boundaryState β m + (1 / β ^ N) / β := by
                rw [boundaryState_reconstruction hβ m]
                simp only [streamShift]
                field_simp [beta_ne_zero hβ]
                ring_nf

end

end CNRSProblem1
