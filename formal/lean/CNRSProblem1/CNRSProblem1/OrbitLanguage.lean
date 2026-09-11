import CNRSProblem1.ModifiedUpper

namespace CNRSProblem1

noncomputable section

/-- Iteration from an already iterated state agrees with addition of step
counts. -/
theorem orbit_add_steps (β x : ℝ) (m n : ℕ) :
    orbit β x (m + n) = orbit β (orbit β x m) n := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Nat.add_succ, orbit_succ, orbit_succ, ih]

/-- Dropping the first `n` emitted digits is exactly the digit stream of the
state reached after `n` transformations. -/
theorem orbitStream_shift (β x : ℝ) (n : ℕ) :
    streamShift (orbitStream β x) n =
      orbitStream β (orbit β x n) := by
  funext k
  simp only [streamShift, orbitStream, orbitDigit]
  rw [orbit_add_steps]

/-- Increasing the state weakly decreases the selected integer digit. -/
theorem digit_antitone {β x y : ℝ} (hβ : 0 < β) (hxy : x ≤ y) :
    digit β y ≤ digit β x := by
  unfold digit
  apply Int.floor_mono
  nlinarith

/-- If the first `n` emitted digits agree, the difference of the states after
`n` steps is exactly the signed expanding image of the original difference. -/
theorem orbit_sub_eq_pow_mul_of_prefix
    {β x y : ℝ} {n : ℕ}
    (hprefix : ∀ j < n, orbitDigit β x j = orbitDigit β y j) :
    orbit β x n - orbit β y n = (-β) ^ n * (x - y) := by
  induction n with
  | zero => simp
  | succ n ih =>
      have hpre : ∀ j < n, orbitDigit β x j = orbitDigit β y j := by
        intro j hj
        exact hprefix j (Nat.lt_succ_of_lt hj)
      have hd : digit β (orbit β x n) = digit β (orbit β y n) := by
        simpa [orbitDigit] using hprefix n (Nat.lt_succ_self n)
      rw [orbit_succ, orbit_succ]
      unfold transform
      rw [hd, pow_succ]
      calc
        -β * orbit β x n - (digit β (orbit β y n) : ℝ) -
              (-β * orbit β y n - (digit β (orbit β y n) : ℝ)) =
            -β * (orbit β x n - orbit β y n) := by ring
        _ = -β * ((-β) ^ n * (x - y)) := by rw [ih hpre]
        _ = (-β) ^ n * (-β) * (x - y) := by ring

/-- Strict order of states is reflected by alternating lexicographic order as
soon as the two deterministic digit streams are known to differ. -/
theorem orbitStream_altLT_of_lt_of_ne
    {β x y : ℝ} (hβ : 0 < β) (hxy : x < y)
    (hne : orbitStream β x ≠ orbitStream β y) :
    AltLT (orbitStream β x) (orbitStream β y) := by
  have hex : ∃ k : ℕ, orbitStream β x k ≠ orbitStream β y k := by
    by_contra h
    push Not at h
    apply hne
    funext k
    exact h k
  let k : ℕ := Nat.find hex
  have hkne : orbitStream β x k ≠ orbitStream β y k := Nat.find_spec hex
  have hkprefix : ∀ j < k, orbitStream β x j = orbitStream β y j := by
    intro j hj
    by_contra hjne
    exact Nat.find_min hex hj hjne
  refine ⟨k, ⟨hkprefix, hkne⟩, ?_⟩
  have hstate :
      orbit β x k - orbit β y k = (-β) ^ k * (x - y) := by
    apply orbit_sub_eq_pow_mul_of_prefix
    simpa [orbitStream, orbitDigit] using hkprefix
  have hbne : -β ≠ 0 := by linarith
  have hdne :
      digit β (orbit β x k) ≠ digit β (orbit β y k) := by
    change orbitStream β x k ≠ orbitStream β y k
    exact hkne
  rcases Nat.even_or_odd k with heven | hodd
  · have hpow : 0 < (-β) ^ k := by
      rcases heven with ⟨m, hm⟩
      rw [hm, pow_add]
      exact mul_self_pos.mpr (pow_ne_zero m hbne)
    have hstate_lt : orbit β x k < orbit β y k := by
      nlinarith [mul_neg_of_pos_of_neg hpow (sub_neg.mpr hxy)]
    have hdle := digit_antitone hβ hstate_lt.le
    have hdlt : orbitStream β y k < orbitStream β x k := by
      change digit β (orbit β y k) < digit β (orbit β x k)
      omega
    simpa [heven] using hdlt
  · have hnotEven : ¬ Even k := by
      intro heven
      rcases heven with ⟨m, hm⟩
      rcases hodd with ⟨q, hq⟩
      omega
    have hpow : (-β) ^ k < 0 := by
      rcases hodd with ⟨m, hm⟩
      have hsq : 0 < (-β) ^ 2 := sq_pos_of_ne_zero hbne
      have hpos : 0 < ((-β) ^ 2) ^ m := pow_pos hsq m
      rw [hm, pow_succ, pow_mul]
      nlinarith
    have hstate_gt : orbit β y k < orbit β x k := by
      nlinarith [mul_pos_of_neg_of_neg hpow (sub_neg.mpr hxy)]
    have hdle := digit_antitone hβ hstate_gt.le
    have hdlt : orbitStream β x k < orbitStream β y k := by
      change digit β (orbit β x k) < digit β (orbit β y k)
      omega
    simpa [hnotEven] using hdlt

/-- Closed endpoint bounds for every state in an orbit. -/
def OrbitClosedBounds (β x : ℝ) : Prop :=
  ∀ n : ℕ,
    leftEndpoint β ≤ orbit β x n ∧
      orbit β x n ≤ rightEndpoint β

theorem orbitClosedBounds_of_mem {β x : ℝ} (hβ : 1 < β)
    (hx : InFundamentalInterval β x) :
    OrbitClosedBounds β x := by
  intro n
  have hn := orbit_mem hβ hx n
  exact ⟨hn.1, hn.2.le⟩

theorem rightEndpoint_orbitClosedBounds {β : ℝ} (hβ : 1 < β) :
    OrbitClosedBounds β (rightEndpoint β) := by
  intro n
  cases n with
  | zero =>
      simp only [orbit_zero]
      constructor
      · linarith [interval_width hβ]
      · exact le_rfl
  | succ n =>
      have hn : InFundamentalInterval β
          (orbit β (rightEndpoint β) (n + 1)) := by
        rw [orbit_succ]
        exact transform_mem hβ
      exact ⟨hn.1, hn.2.le⟩

/-- On bounded Ito--Sadahiro orbits, the full deterministic digit stream
uniquely determines the starting state. -/
theorem orbitStream_injective_of_closedBounds
    {β x y : ℝ} (hβ : 1 < β)
    (hx : OrbitClosedBounds β x)
    (hy : OrbitClosedBounds β y)
    (hstream : orbitStream β x = orbitStream β y) :
    x = y := by
  by_contra hxy
  have habs : 0 < |x - y| := abs_pos.mpr (sub_ne_zero.mpr hxy)
  have hev : ∀ᶠ n : ℕ in Filter.atTop,
      1 / |x - y| < β ^ n :=
    (tendsto_pow_atTop_atTop_of_one_lt hβ).eventually_gt_atTop
      (1 / |x - y|)
  obtain ⟨n, hn⟩ := hev.exists
  have hprefix : ∀ j < n, orbitDigit β x j = orbitDigit β y j := by
    intro j _
    exact congrFun hstream j
  have hstate := orbit_sub_eq_pow_mul_of_prefix hprefix
  have hdiff :
      |orbit β x n - orbit β y n| ≤ 1 := by
    rw [abs_le]
    constructor <;>
      linarith [interval_width hβ, (hx n).1, (hx n).2,
        (hy n).1, (hy n).2]
  have hβpos : 0 < β := lt_trans zero_lt_one hβ
  have habseq :
      |orbit β x n - orbit β y n| = β ^ n * |x - y| := by
    calc
      |orbit β x n - orbit β y n| =
          |(-β) ^ n * (x - y)| := congrArg abs hstate
      _ = β ^ n * |x - y| := by
        rw [abs_mul, abs_pow, abs_neg, abs_of_pos hβpos]
  have hlarge : 1 < β ^ n * |x - y| :=
    (div_lt_iff₀ habs).mp hn
  rw [← habseq] at hlarge
  exact (not_lt_of_ge hdiff) hlarge

/-- Strict order of bounded states is reflected without an extra stream
disequality premise. -/
theorem orbitStream_altLT_of_lt_of_closedBounds
    {β x y : ℝ} (hβ : 1 < β) (hxy : x < y)
    (hx : OrbitClosedBounds β x)
    (hy : OrbitClosedBounds β y) :
    AltLT (orbitStream β x) (orbitStream β y) := by
  apply orbitStream_altLT_of_lt_of_ne (lt_trans zero_lt_one hβ) hxy
  intro hstream
  have := orbitStream_injective_of_closedBounds hβ hx hy hstream
  exact hxy.ne this

/-- The precise order-theoretic obligation needed to turn every actual orbit
into a symbolically admissible word.  It is separated out so no appeal to the
Ito--Sadahiro admissibility theorem is hidden in a definition. -/
def CanonicalOrbitBounds (β : ℝ) (upper : DigitStream) : Prop :=
  ∀ x : ℝ, InFundamentalInterval β x →
    AltLE (lowerReference β) (orbitStream β x) ∧
    AltLT (orbitStream β x) upper

/-- Every actual orbit lies between the lower endpoint stream and the
ordinary excluded-right-endpoint stream. -/
theorem canonicalOrbitBounds_rightBoundary {β : ℝ} (hβ : 1 < β) :
    CanonicalOrbitBounds β (rightBoundaryStream β) := by
  intro x hx
  have hleftMem :
      InFundamentalInterval β (leftEndpoint β) := by
    constructor
    · exact le_rfl
    · linarith [interval_width hβ]
  constructor
  · by_cases heq : leftEndpoint β = x
    · exact Or.inl (by simp [lowerReference, heq])
    · apply Or.inr
      apply orbitStream_altLT_of_lt_of_closedBounds hβ
          (lt_of_le_of_ne hx.1 heq)
      · exact orbitClosedBounds_of_mem hβ hleftMem
      · exact orbitClosedBounds_of_mem hβ hx
  · apply orbitStream_altLT_of_lt_of_closedBounds hβ hx.2
    · exact orbitClosedBounds_of_mem hβ hx
    · exact rightEndpoint_orbitClosedBounds hβ

/-- Once the canonical endpoint bounds have been established for a base, every
actual orbit word satisfies them at every suffix. -/
theorem orbitStream_symbolicallyAdmissible
    {β x : ℝ} (hβ : 1 < β)
    (hx : InFundamentalInterval β x)
    (hbounds : CanonicalOrbitBounds β
      (modifiedUpperReference (lowerReference β)
        (rightBoundaryStream β))) :
    SymbolicallyAdmissibleFor (modifiedUpperReferenceSystem β)
      (orbitStream β x) := by
  intro n
  rw [orbitStream_shift]
  exact hbounds _ (orbit_mem hβ hx n)

/-- Soundness specialized to the first classified quadratic base. -/
theorem sqrtTwo_orbitStream_symbolicallyAdmissible
    {x : ℝ} (hx : InFundamentalInterval sqrtTwoBase x) :
    SymbolicallyAdmissibleFor sqrtTwoReferenceSystem
      (orbitStream sqrtTwoBase x) := by
  rw [← sqrtTwo_modifiedUpperReferenceSystem]
  apply orbitStream_symbolicallyAdmissible
      (hβ := by linarith [sqrtTwoBase_between.1]) hx
  simpa [sqrtTwo_modifiedUpperReference] using
    (canonicalOrbitBounds_rightBoundary
      (β := sqrtTwoBase) (by linarith [sqrtTwoBase_between.1]))

/-- Soundness specialized to the second classified quadratic base. -/
theorem sqrtThree_orbitStream_symbolicallyAdmissible
    {x : ℝ} (hx : InFundamentalInterval sqrtThreeBase x) :
    SymbolicallyAdmissibleFor sqrtThreeReferenceSystem
      (orbitStream sqrtThreeBase x) := by
  rw [← sqrtThree_modifiedUpperReferenceSystem]
  apply orbitStream_symbolicallyAdmissible
      (hβ := by linarith [sqrtThreeBase_between.1]) hx
  simpa [sqrtThree_modifiedUpperReference] using
    (canonicalOrbitBounds_rightBoundary
      (β := sqrtThreeBase) (by linarith [sqrtThreeBase_between.1]))

/-- Soundness specialized to the third classified quadratic base. -/
theorem golden_orbitStream_symbolicallyAdmissible
    {x : ℝ} (hx : InFundamentalInterval goldenBase x) :
    SymbolicallyAdmissibleFor goldenReferenceSystem
      (orbitStream goldenBase x) := by
  rw [← golden_modifiedUpperReferenceSystem]
  apply orbitStream_symbolicallyAdmissible
      (hβ := by linarith [goldenBase_between.1]) hx
  simpa [golden_modifiedUpperReference] using
    (canonicalOrbitBounds_rightBoundary
      (β := goldenBase) (by linarith [goldenBase_between.1]))

end

end CNRSProblem1
