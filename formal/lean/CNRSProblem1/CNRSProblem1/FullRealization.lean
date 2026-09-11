import CNRSProblem1.SeriesRealization

namespace CNRSProblem1

noncomputable section

open scoped BigOperators

/-- The negative-base power-series term represented by digit n. -/
def wordSeriesTerm (β : ℝ) (a : DigitStream) (n : ℕ) : ℝ :=
  (a n : ℝ) / (-β) ^ (n + 1)

/-- The real value represented by an infinite digit stream. -/
def wordSeriesValue (β : ℝ) (a : DigitStream) : ℝ :=
  ∑' n : ℕ, wordSeriesTerm β a n

theorem admissible_shift {β : ℝ} {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) (n : ℕ) :
    ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) (streamShift a n) := by
  intro k
  simpa [streamShift_add, Nat.add_assoc] using hadm (n + k)

theorem admissible_digit_bounds {β : ℝ} (hβ : 1 < β)
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) (n : ℕ) :
    0 ≤ a n ∧ a n ≤ ⌊β⌋ := by
  have hu : AltLE (streamShift a n) (rightBoundaryStream β) :=
    Or.inr (hadm n).2
  have hl := (hadm n).1
  have hzero := altLE_head_le hu
  have htop := altLE_head_le hl
  constructor
  · simpa [streamShift, rightBoundaryStream, orbitStream, orbitDigit,
      digit_rightBoundary hβ] using hzero
  · simpa [streamShift, lowerReference, orbitStream, orbitDigit,
      digit_leftEndpoint hβ] using htop

theorem wordSeries_summable {β : ℝ} (hβ : 1 < β)
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) :
    Summable (wordSeriesTerm β a) := by
  have hβ0 : 0 < β := lt_trans zero_lt_one hβ
  have hβne : β ≠ 0 := ne_of_gt hβ0
  have hq : ‖(β⁻¹ : ℝ)‖ < 1 := by
    rw [Real.norm_eq_abs, abs_inv, abs_of_pos hβ0]
    exact inv_lt_one_of_one_lt₀ hβ
  apply Summable.of_norm_bounded (summable_geometric_of_norm_lt_one hq)
  intro n
  have hd := admissible_digit_bounds hβ hadm n
  have hd0 : 0 ≤ (a n : ℝ) := by exact_mod_cast hd.1
  have hdβ : (a n : ℝ) ≤ β := by
    exact (Int.cast_le.mpr hd.2).trans (Int.floor_le β)
  change |(a n : ℝ) / (-β) ^ (n + 1)| ≤ (β⁻¹ : ℝ) ^ n
  rw [abs_div, abs_pow, abs_neg, abs_of_pos hβ0, abs_of_nonneg hd0]
  apply (div_le_iff₀ (pow_pos hβ0 (n + 1))).2
  calc
    (a n : ℝ) ≤ β := hdβ
    _ = (β⁻¹ : ℝ) ^ n * β ^ (n + 1) := by
      rw [pow_succ, inv_pow]
      field_simp [pow_ne_zero n hβne]

theorem wordPrefixValue_eq_sum (β : ℝ) (a : DigitStream) (N : ℕ) :
    wordPrefixValue β a N =
      ∑ n ∈ Finset.range N, wordSeriesTerm β a n := by
  induction N generalizing a with
  | zero => simp
  | succ N ih =>
      have htail :
          wordPrefixValue β (streamShift a 1) N / (-β) =
            ∑ n ∈ Finset.range N, wordSeriesTerm β a (n + 1) := by
        rw [ih, Finset.sum_div]
        apply Finset.sum_congr rfl
        intro n hn
        simp only [wordSeriesTerm, streamShift]
        rw [div_div, pow_succ]
        ring_nf
      rw [wordPrefixValue_succ, htail, Finset.sum_range_succ']
      simp [wordSeriesTerm, add_comm]

theorem wordPrefixValue_tendsto {β : ℝ} (hβ : 1 < β)
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) :
    Filter.Tendsto (fun N => wordPrefixValue β a N) Filter.atTop
      (nhds (wordSeriesValue β a)) := by
  have hs := wordSeries_summable hβ hadm
  simpa [wordPrefixValue_eq_sum, wordSeriesValue] using
    hs.hasSum.tendsto_sum_nat

theorem invPow_tendsto_zero {β : ℝ} (hβ : 1 < β) :
    Filter.Tendsto (fun N : ℕ => 1 / β ^ N) Filter.atTop
      (nhds 0) := by
  have hβ0 : 0 < β := lt_trans zero_lt_one hβ
  have hq : |(β⁻¹ : ℝ)| < 1 := by
    rw [abs_inv, abs_of_pos hβ0]
    exact inv_lt_one_of_one_lt₀ hβ
  simpa [one_div, inv_pow] using
    (tendsto_pow_atTop_nhds_zero_of_abs_lt_one hq)

/-- Every suffix series value is trapped in the closed fundamental interval. -/
theorem admissible_series_closedBounds {β : ℝ} (hβ : 1 < β)
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) (n : ℕ) :
    leftEndpoint β ≤ wordSeriesValue β (streamShift a n) ∧
      wordSeriesValue β (streamShift a n) ≤ rightEndpoint β := by
  have hadmN := admissible_shift hadm n
  have ht := wordPrefixValue_tendsto hβ hadmN
  have he := invPow_tendsto_zero hβ
  have hlref : AltLE (streamShift (rightBoundaryStream β) 1)
      (streamShift a n) := by
    rw [rightBoundary_shift_one hβ]
    exact (hadm n).1
  have href : AltLE (streamShift a n)
      (streamShift (rightBoundaryStream β) 0) := by
    rw [streamShift_zero]
    exact Or.inr (hadm n).2
  have hest := wordPrefixValue_boundary_estimates hβ a hadm
  have hl : ∀ N, boundaryState β 1 - 1 / β ^ N ≤
      wordPrefixValue β (streamShift a n) N :=
    fun N => (hest N 1 n).1 hlref
  have hu : ∀ N, wordPrefixValue β (streamShift a n) N ≤
      boundaryState β 0 + 1 / β ^ N :=
    fun N => (hest N 0 n).2 href
  have hleft : boundaryState β 1 = leftEndpoint β := by
    change transform β (rightEndpoint β) = leftEndpoint β
    exact transform_rightBoundary hβ
  have hright : boundaryState β 0 = rightEndpoint β := by
    simp [boundaryState]
  have hlt : Filter.Tendsto
      (fun N : ℕ => boundaryState β 1 - 1 / β ^ N) Filter.atTop
      (nhds (boundaryState β 1)) := by
    simpa using (tendsto_const_nhds.sub he)
  have hut : Filter.Tendsto
      (fun N : ℕ => boundaryState β 0 + 1 / β ^ N) Filter.atTop
      (nhds (boundaryState β 0)) := by
    simpa using (tendsto_const_nhds.add he)
  constructor
  · rw [← hleft]
    exact le_of_tendsto_of_tendsto
      hlt ht (Filter.Eventually.of_forall hl)
  · rw [← hright]
    exact le_of_tendsto_of_tendsto
      ht hut (Filter.Eventually.of_forall hu)

/-- Splitting the convergent word series after its leading digit. -/
theorem wordSeriesValue_recurrence {β : ℝ} (hβ : 1 < β)
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) :
    wordSeriesValue β a =
      (a 0 : ℝ) / (-β) +
        wordSeriesValue β (streamShift a 1) / (-β) := by
  have hs := wordSeries_summable hβ hadm
  unfold wordSeriesValue
  rw [hs.tsum_eq_zero_add]
  congr 1
  · simp [wordSeriesTerm]
  · rw [← tsum_div_const]
    apply tsum_congr
    intro n
    simp only [wordSeriesTerm, streamShift]
    rw [div_div, ← pow_succ]
    simp [Nat.add_comm]

theorem admissible_suffixValue_recurrence {β : ℝ} (hβ : 1 < β)
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) (n : ℕ) :
    wordSeriesValue β (streamShift a n) =
      (a n : ℝ) / (-β) +
        wordSeriesValue β (streamShift a (n + 1)) / (-β) := by
  have h := wordSeriesValue_recurrence hβ (admissible_shift hadm n)
  simpa [streamShift, streamShift_add, Nat.add_assoc] using h

theorem suffixValue_eq_boundaryState_of_prefix
    {β : ℝ} (hβ : 1 < β) {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a)
    {m n k : ℕ}
    (hzero : wordSeriesValue β (streamShift a n) = boundaryState β m)
    (hpre : ∀ j < k, streamShift a n j =
      streamShift (rightBoundaryStream β) m j) :
    wordSeriesValue β (streamShift a (n + k)) =
      boundaryState β (m + k) := by
  induction k with
  | zero => simpa using hzero
  | succ k ih =>
      have hik := ih (fun j hj => hpre j (Nat.lt_succ_of_lt hj))
      have hd := hpre k (Nat.lt_succ_self k)
      have hrec := admissible_suffixValue_recurrence hβ hadm (n + k)
      have href := boundaryState_reconstruction hβ (m + k)
      rw [hrec, href] at hik
      field_simp [beta_ne_zero hβ] at hik
      have hd' : a (n + k) = rightBoundaryStream β (m + k) := by
        simpa [streamShift, Nat.add_assoc] using hd
      rw [hd'] at hik
      have hnext :
          wordSeriesValue β (streamShift a (n + k + 1)) =
            boundaryState β (m + k + 1) := by
        linarith
      simpa [Nat.add_assoc] using hnext

theorem boundaryState_lt_right_of_pos {β : ℝ} (hβ : 1 < β)
    {m : ℕ} (hm : 0 < m) :
    boundaryState β m < rightEndpoint β := by
  obtain ⟨k, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hm)
  change orbit β (rightEndpoint β) (k + 1) < rightEndpoint β
  rw [orbit_rightBoundary_shift hβ]
  have hleft : InFundamentalInterval β (leftEndpoint β) := by
    exact ⟨le_rfl, by linarith [interval_width hβ]⟩
  exact (orbit_mem hβ hleft k).2

/-- The strict upper endpoint is where the modified-upper hypothesis is used:
an equality at the right endpoint would force either an impossible later
right endpoint, or an odd return of the lower endpoint. -/
theorem admissible_series_lt_right {β : ℝ} (hβ : 1 < β)
    (hno : ¬ HasOddPurePeriod (lowerReference β))
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) (n : ℕ) :
    wordSeriesValue β (streamShift a n) < rightEndpoint β := by
  have hclosed := admissible_series_closedBounds hβ hadm n
  apply lt_of_le_of_ne hclosed.2
  intro heq
  have hzero :
      wordSeriesValue β (streamShift a n) = boundaryState β 0 := by
    simpa [boundaryState] using heq
  rcases (hadm n).2 with ⟨k, hfirst, hord⟩
  have hkstate := suffixValue_eq_boundaryState_of_prefix hβ hadm hzero
    (m := 0) (k := k) (by
      intro j hj
      simpa [streamShift, Nat.add_assoc] using hfirst.1 j hj)
  have hrecA := admissible_suffixValue_recurrence hβ hadm (n + k)
  have hrecU := boundaryState_reconstruction hβ k
  simp only [Nat.zero_add] at hkstate
  rw [hrecA, hrecU] at hkstate
  field_simp [beta_ne_zero hβ] at hkstate
  have hxnext := admissible_series_closedBounds hβ hadm (n + k + 1)
  have hynext := boundaryState_bounds hβ (k + 1)
  have hwidth := interval_width hβ
  rcases Nat.even_or_odd k with heven | hodd
  · have hdk : rightBoundaryStream β k < a (n + k) := by
      simpa [heven, streamShift, Nat.add_assoc] using hord
    have hgap : (rightBoundaryStream β k : ℝ) + 1 ≤ (a (n + k) : ℝ) := by
      exact_mod_cast (show rightBoundaryStream β k + 1 ≤ a (n + k) by omega)
    have hyright : boundaryState β (k + 1) = rightEndpoint β := by
      nlinarith
    exact (boundaryState_lt_right_of_pos hβ (Nat.succ_pos k)).ne hyright
  · have hnotEven : ¬ Even k := by
      rintro ⟨t, ht⟩
      rcases hodd with ⟨s, hs⟩
      omega
    have hdk : a (n + k) < rightBoundaryStream β k := by
      simpa [hnotEven, streamShift, Nat.add_assoc] using hord
    have hgap : (a (n + k) : ℝ) + 1 ≤ (rightBoundaryStream β k : ℝ) := by
      exact_mod_cast (show a (n + k) + 1 ≤ rightBoundaryStream β k by omega)
    have hyleft : boundaryState β (k + 1) = leftEndpoint β := by
      nlinarith
    have hkpos : 0 < k := by
      rcases hodd with ⟨s, hs⟩
      omega
    have hreturn : orbit β (leftEndpoint β) k = leftEndpoint β := by
      rw [← orbit_rightBoundary_shift hβ k]
      simpa [boundaryState] using hyleft
    have hpure : HasPurePeriod (lowerReference β) k := by
      constructor
      · exact hkpos
      · intro j
        unfold lowerReference orbitStream orbitDigit
        rw [show j + k = k + j by omega, orbit_add_steps β
          (leftEndpoint β) k j, hreturn]
    exact hno ⟨k, hodd, hpure⟩

theorem admissible_series_digit {β : ℝ} (hβ : 1 < β)
    (hno : ¬ HasOddPurePeriod (lowerReference β))
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) (n : ℕ) :
    digit β (wordSeriesValue β (streamShift a n)) = a n := by
  have hrec := admissible_suffixValue_recurrence hβ hadm n
  have hnextClosed := admissible_series_closedBounds hβ hadm (n + 1)
  have hnextStrict := admissible_series_lt_right hβ hno hadm (n + 1)
  have harg :
      -β * wordSeriesValue β (streamShift a n) - leftEndpoint β =
        (a n : ℝ) +
          (wordSeriesValue β (streamShift a (n + 1)) - leftEndpoint β) := by
    field_simp [beta_ne_zero hβ] at hrec
    nlinarith
  unfold digit
  rw [harg, Int.floor_eq_iff]
  constructor
  · exact_mod_cast (show (a n : ℝ) ≤
      (a n : ℝ) +
        (wordSeriesValue β (streamShift a (n + 1)) - leftEndpoint β) by
      linarith)
  · have hw := right_eq_left_add_one hβ
    exact_mod_cast (show
      (a n : ℝ) +
          (wordSeriesValue β (streamShift a (n + 1)) - leftEndpoint β) <
        (a n : ℝ) + 1 by linarith)

theorem admissible_series_transform {β : ℝ} (hβ : 1 < β)
    (hno : ¬ HasOddPurePeriod (lowerReference β))
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) (n : ℕ) :
    transform β (wordSeriesValue β (streamShift a n)) =
      wordSeriesValue β (streamShift a (n + 1)) := by
  have hrec := admissible_suffixValue_recurrence hβ hadm n
  rw [transform, admissible_series_digit hβ hno hadm n]
  field_simp [beta_ne_zero hβ] at hrec
  linarith

theorem admissible_series_orbit {β : ℝ} (hβ : 1 < β)
    (hno : ¬ HasOddPurePeriod (lowerReference β))
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) :
    ∀ n, orbit β (wordSeriesValue β a) n =
      wordSeriesValue β (streamShift a n) := by
  intro n
  induction n with
  | zero => simp
  | succ n ih =>
      rw [orbit_succ, ih, admissible_series_transform hβ hno hadm]

/-- Full realization: every symbolically admissible word for a nonexceptional
modified-upper system is the deterministic orbit word of its series value. -/
theorem admissible_realizesOrbitStream {β : ℝ} (hβ : 1 < β)
    (hno : ¬ HasOddPurePeriod (lowerReference β))
    {a : DigitStream}
    (hadm : ISAdmissibleBetween (lowerReference β)
      (rightBoundaryStream β) a) :
    RealizesOrbitStream β a (wordSeriesValue β a) := by
  constructor
  · exact ⟨by simpa using (admissible_series_closedBounds hβ hadm 0).1,
      by simpa using admissible_series_lt_right hβ hno hadm 0⟩
  · funext n
    unfold orbitStream orbitDigit
    rw [admissible_series_orbit hβ hno hadm n,
      admissible_series_digit hβ hno hadm n]

theorem sqrtTwo_symbolicallyAdmissible_iff_realized (a : DigitStream) :
    SymbolicallyAdmissibleFor sqrtTwoReferenceSystem a ↔
      ∃ x, RealizesOrbitStream sqrtTwoBase a x := by
  constructor
  · intro h
    exact ⟨wordSeriesValue sqrtTwoBase a,
      admissible_realizesOrbitStream
        (by linarith [sqrtTwoBase_between.1])
        sqrtTwo_noOddPurePeriod h⟩
  · rintro ⟨x, hx, hstream⟩
    rw [← hstream]
    exact sqrtTwo_orbitStream_symbolicallyAdmissible hx

theorem sqrtThree_symbolicallyAdmissible_iff_realized (a : DigitStream) :
    SymbolicallyAdmissibleFor sqrtThreeReferenceSystem a ↔
      ∃ x, RealizesOrbitStream sqrtThreeBase a x := by
  constructor
  · intro h
    exact ⟨wordSeriesValue sqrtThreeBase a,
      admissible_realizesOrbitStream
        (by linarith [sqrtThreeBase_between.1])
        sqrtThree_noOddPurePeriod h⟩
  · rintro ⟨x, hx, hstream⟩
    rw [← hstream]
    exact sqrtThree_orbitStream_symbolicallyAdmissible hx

theorem golden_symbolicallyAdmissible_iff_realized (a : DigitStream) :
    SymbolicallyAdmissibleFor goldenReferenceSystem a ↔
      ∃ x, RealizesOrbitStream goldenBase a x := by
  constructor
  · intro h
    exact ⟨wordSeriesValue goldenBase a,
      admissible_realizesOrbitStream
        (by linarith [goldenBase_between.1])
        golden_noOddPurePeriod h⟩
  · rintro ⟨x, hx, hstream⟩
    rw [← hstream]
    exact golden_orbitStream_symbolicallyAdmissible hx

end

end CNRSProblem1
