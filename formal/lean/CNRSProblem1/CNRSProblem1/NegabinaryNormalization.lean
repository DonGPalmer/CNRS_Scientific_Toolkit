import CNRSProblem1.FullRealization

namespace CNRSProblem1

noncomputable section

open scoped BigOperators

/-!
# P1-L7: the beta = 2 endpoint normalization

At the integer base `beta = 2`, the canonical Ito--Sadahiro alphabet contains
the digit `2`, while the standard binary negabinary alphabet is `{0, 1}`.  This
module isolates the discrepancy: digit `2` occurs only at the included left
endpoint, where it is absorbing.  The canonical endpoint word `2^omega` and
the binary word `(10)^omega` have the same negative-base value.  Consequently
an orbit that reaches the left endpoint may replace its resulting `2^omega`
tail by `(10)^omega` without changing the represented value.
-/

/-- The real base magnitude underlying ordinary binary base `-2`. -/
def negabinaryBase : ℝ := 2

theorem negabinary_base_gt_one : 1 < negabinaryBase := by
  norm_num [negabinaryBase]

theorem negabinary_leftEndpoint :
    leftEndpoint negabinaryBase = -(2 : ℝ) / 3 := by
  norm_num [negabinaryBase, leftEndpoint]

theorem negabinary_rightEndpoint :
    rightEndpoint negabinaryBase = (1 : ℝ) / 3 := by
  norm_num [negabinaryBase, rightEndpoint]

theorem negabinary_digit_left :
    digit negabinaryBase (leftEndpoint negabinaryBase) = 2 := by
  simpa [negabinaryBase] using
    (digit_leftEndpoint (β := (2 : ℝ)) (by norm_num))

theorem negabinary_transform_left :
    transform negabinaryBase (leftEndpoint negabinaryBase) =
      leftEndpoint negabinaryBase := by
  rw [transform, negabinary_digit_left]
  norm_num [negabinaryBase, leftEndpoint]

theorem negabinary_left_orbit (n : ℕ) :
    orbit negabinaryBase (leftEndpoint negabinaryBase) n =
      leftEndpoint negabinaryBase := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [orbit_succ, ih, negabinary_transform_left]

theorem negabinary_left_digits (n : ℕ) :
    orbitDigit negabinaryBase (leftEndpoint negabinaryBase) n = 2 := by
  rw [orbitDigit, negabinary_left_orbit, negabinary_digit_left]

/-- Within the half-open I--S interval at beta = 2, digit `2` occurs exactly
at the included left endpoint. -/
theorem negabinary_digit_eq_two_iff {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) :
    digit negabinaryBase x = 2 ↔
      x = leftEndpoint negabinaryBase := by
  constructor
  · intro hd
    have hfloor :
        (digit negabinaryBase x : ℝ) ≤
          -negabinaryBase * x - leftEndpoint negabinaryBase := by
      unfold digit
      exact Int.floor_le _
    rw [hd] at hfloor
    have hxleft := hx.1
    rw [negabinary_leftEndpoint] at hxleft hfloor ⊢
    norm_num [negabinaryBase] at hfloor
    linarith
  · intro hxleft
    rw [hxleft]
    exact negabinary_digit_left

/-- Every non-endpoint canonical digit at beta = 2 is already binary. -/
theorem negabinary_digit_binary_of_ne_left {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x)
    (hne : x ≠ leftEndpoint negabinaryBase) :
    digit negabinaryBase x = 0 ∨ digit negabinaryBase x = 1 := by
  have hd := digit_mem_alphabet negabinary_base_gt_one hx
  have hdtop : digit negabinaryBase x ≤ 2 := by
    simpa [negabinaryBase] using hd.2
  have hdne : digit negabinaryBase x ≠ 2 := by
    intro htwo
    exact hne ((negabinary_digit_eq_two_iff hx).mp htwo)
  omega

theorem negabinary_orbit_emits_two_iff_left {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) (n : ℕ) :
    orbitDigit negabinaryBase x n = 2 ↔
      orbit negabinaryBase x n = leftEndpoint negabinaryBase := by
  unfold orbitDigit
  exact negabinary_digit_eq_two_iff
    (orbit_mem negabinary_base_gt_one hx n)

/-- Once a canonical beta = 2 orbit emits `2`, its complete remaining tail is
the fixed word `2^omega`. -/
theorem negabinary_two_tail_of_hit {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) {n : ℕ}
    (hn : orbitDigit negabinaryBase x n = 2) (k : ℕ) :
    orbitDigit negabinaryBase x (n + k) = 2 := by
  have hstate := (negabinary_orbit_emits_two_iff_left hx n).mp hn
  unfold orbitDigit
  rw [orbit_add_steps, hstate, negabinary_left_orbit]
  exact negabinary_digit_left

/-- A stream uses only the standard binary negabinary digits. -/
def IsBinaryNegabinaryStream (a : DigitStream) : Prop :=
  ∀ n : ℕ, a n = 0 ∨ a n = 1

/-- The binary endpoint convention `(10)^omega`. -/
def binaryNegabinaryEndpointStream : DigitStream :=
  fun n => if n % 2 = 0 then 1 else 0

theorem binaryNegabinaryEndpointStream_binary :
    IsBinaryNegabinaryStream binaryNegabinaryEndpointStream := by
  intro n
  by_cases h : n % 2 = 0
  · right
    simp [binaryNegabinaryEndpointStream, h]
  · left
    simp [binaryNegabinaryEndpointStream, h]

@[simp] theorem binaryNegabinaryEndpointStream_zero :
    binaryNegabinaryEndpointStream 0 = 1 := by
  simp [binaryNegabinaryEndpointStream]

@[simp] theorem binaryNegabinaryEndpointStream_one :
    binaryNegabinaryEndpointStream 1 = 0 := by
  norm_num [binaryNegabinaryEndpointStream]

theorem binaryNegabinaryEndpointStream_shift_two :
    streamShift binaryNegabinaryEndpointStream 2 =
      binaryNegabinaryEndpointStream := by
  funext n
  simp [streamShift, binaryNegabinaryEndpointStream]

/-- The canonical I--S left-endpoint stream `2^omega`. -/
def canonicalTwoEndpointStream : DigitStream := fun _ => 2

theorem negabinary_lowerReference_eq_twoEndpoint :
    lowerReference negabinaryBase = canonicalTwoEndpointStream := by
  funext n
  change orbitDigit negabinaryBase (leftEndpoint negabinaryBase) n = 2
  exact negabinary_left_digits n

/-- A bounded digit stream at beta = 2 has an absolutely convergent value. -/
theorem negabinary_wordSeries_summable
    {a : DigitStream} (ha : ∀ n, 0 ≤ a n ∧ a n ≤ 2) :
    Summable (wordSeriesTerm negabinaryBase a) := by
  have hq : ‖((2 : ℝ)⁻¹)‖ < 1 := by norm_num
  apply Summable.of_norm_bounded (summable_geometric_of_norm_lt_one hq)
  intro n
  have hd := ha n
  have hd0 : 0 ≤ (a n : ℝ) := by exact_mod_cast hd.1
  have hd2 : (a n : ℝ) ≤ 2 := by exact_mod_cast hd.2
  change |(a n : ℝ) / (-(2 : ℝ)) ^ (n + 1)| ≤ ((2 : ℝ)⁻¹) ^ n
  rw [abs_div, abs_pow, abs_neg, abs_of_pos (by norm_num : (0 : ℝ) < 2),
    abs_of_nonneg hd0]
  apply (div_le_iff₀ (pow_pos (by norm_num : (0 : ℝ) < 2) (n + 1))).2
  calc
    (a n : ℝ) ≤ 2 := hd2
    _ = ((2 : ℝ)⁻¹) ^ n * (2 : ℝ) ^ (n + 1) := by
      rw [pow_succ, inv_pow]
      field_simp [pow_ne_zero n (by norm_num : (2 : ℝ) ≠ 0)]

/-- Leading-digit recurrence for every beta = 2 stream bounded by `{0,1,2}`. -/
theorem negabinary_wordSeriesValue_recurrence
    {a : DigitStream} (ha : ∀ n, 0 ≤ a n ∧ a n ≤ 2) :
    wordSeriesValue negabinaryBase a =
      (a 0 : ℝ) / (-negabinaryBase) +
        wordSeriesValue negabinaryBase (streamShift a 1) /
          (-negabinaryBase) := by
  have hs := negabinary_wordSeries_summable ha
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

theorem canonicalTwoEndpointStream_value :
    wordSeriesValue negabinaryBase canonicalTwoEndpointStream =
      leftEndpoint negabinaryBase := by
  have hb : ∀ n, 0 ≤ canonicalTwoEndpointStream n ∧
      canonicalTwoEndpointStream n ≤ 2 := by
    intro n
    simp [canonicalTwoEndpointStream]
  have hrec := negabinary_wordSeriesValue_recurrence hb
  have hshift :
      streamShift canonicalTwoEndpointStream 1 =
        canonicalTwoEndpointStream := by
    rfl
  rw [hshift] at hrec
  change wordSeriesValue negabinaryBase canonicalTwoEndpointStream =
      (2 : ℝ) / (-negabinaryBase) +
        wordSeriesValue negabinaryBase canonicalTwoEndpointStream /
          (-negabinaryBase) at hrec
  rw [negabinary_leftEndpoint]
  norm_num [negabinaryBase] at hrec ⊢
  linarith

theorem binaryNegabinaryEndpointStream_value :
    wordSeriesValue negabinaryBase binaryNegabinaryEndpointStream =
      leftEndpoint negabinaryBase := by
  have hb : ∀ n, 0 ≤ binaryNegabinaryEndpointStream n ∧
      binaryNegabinaryEndpointStream n ≤ 2 := by
    intro n
    rcases binaryNegabinaryEndpointStream_binary n with hzero | hone
    · rw [hzero]
      omega
    · rw [hone]
      omega
  have hbshift : ∀ n,
      0 ≤ streamShift binaryNegabinaryEndpointStream 1 n ∧
      streamShift binaryNegabinaryEndpointStream 1 n ≤ 2 := by
    intro n
    exact hb (1 + n)
  have hrec0 := negabinary_wordSeriesValue_recurrence hb
  have hrec1 := negabinary_wordSeriesValue_recurrence hbshift
  have hshift :
      streamShift (streamShift binaryNegabinaryEndpointStream 1) 1 =
        binaryNegabinaryEndpointStream := by
    rw [streamShift_add]
    norm_num
    exact binaryNegabinaryEndpointStream_shift_two
  have hhead0 : binaryNegabinaryEndpointStream 0 = 1 :=
    binaryNegabinaryEndpointStream_zero
  have hhead1 :
      streamShift binaryNegabinaryEndpointStream 1 0 = 0 := by
    simp [streamShift]
  rw [hhead0] at hrec0
  rw [hhead1] at hrec1
  rw [hshift] at hrec1
  rw [negabinary_leftEndpoint]
  norm_num [negabinaryBase] at hrec0 hrec1 ⊢
  linarith

/-- The beta = 2 normalization convention: the canonical endpoint word
`2^omega` and the binary word `(10)^omega` represent the same value. -/
theorem negabinary_endpoint_normalization :
    wordSeriesValue negabinaryBase (lowerReference negabinaryBase) =
      wordSeriesValue negabinaryBase binaryNegabinaryEndpointStream := by
  rw [negabinary_lowerReference_eq_twoEndpoint,
    canonicalTwoEndpointStream_value,
    binaryNegabinaryEndpointStream_value]

/-- Operational form of the endpoint convention.  If a canonical beta = 2
orbit reaches the left endpoint at step `n`, the value of its entire remaining
canonical tail is exactly the value of the binary `(10)^omega` tail. -/
theorem negabinary_orbit_tail_normalization {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) {n : ℕ}
    (hn : orbitDigit negabinaryBase x n = 2) :
    wordSeriesValue negabinaryBase
        (streamShift (orbitStream negabinaryBase x) n) =
      wordSeriesValue negabinaryBase binaryNegabinaryEndpointStream := by
  have hstate := (negabinary_orbit_emits_two_iff_left hx n).mp hn
  rw [orbitStream_shift, hstate]
  simpa [lowerReference] using negabinary_endpoint_normalization

/-- Split a bounded beta = 2 digit series after `N` digits. -/
theorem negabinary_wordSeriesValue_split
    {a : DigitStream} (ha : ∀ n, 0 ≤ a n ∧ a n ≤ 2) (N : ℕ) :
    wordSeriesValue negabinaryBase a =
      wordPrefixValue negabinaryBase a N +
        wordSeriesValue negabinaryBase (streamShift a N) /
          (-negabinaryBase) ^ N := by
  induction N generalizing a with
  | zero => simp
  | succ N ih =>
      have htail : ∀ n, 0 ≤ streamShift a 1 n ∧
          streamShift a 1 n ≤ 2 := by
        intro n
        exact ha (1 + n)
      have hrec := negabinary_wordSeriesValue_recurrence ha
      have hsplit := ih htail
      have hshift :
          streamShift (streamShift a 1) N = streamShift a (N + 1) := by
        simpa [Nat.add_comm] using streamShift_add a 1 N
      rw [hrec, hsplit, wordPrefixValue_succ, hshift, pow_succ]
      ring

/-- Equal first `N` digits give equal finite prefix values. -/
theorem negabinary_wordPrefixValue_congr
    {a b : DigitStream} {N : ℕ}
    (hprefix : ∀ k < N, a k = b k) :
    wordPrefixValue negabinaryBase a N =
      wordPrefixValue negabinaryBase b N := by
  induction N generalizing a b with
  | zero => simp
  | succ N ih =>
      have hzero : a 0 = b 0 := hprefix 0 (by omega)
      have htail : ∀ k < N,
          streamShift a 1 k = streamShift b 1 k := by
        intro k hk
        simpa [streamShift, Nat.add_comm] using
          hprefix (k + 1) (by omega)
      rw [wordPrefixValue_succ, wordPrefixValue_succ, hzero, ih htail]

/-- Replace a stream from position `N` onward by the binary endpoint word. -/
def negabinaryNormalizeAt (a : DigitStream) (N : ℕ) : DigitStream :=
  fun k => if k < N then a k else binaryNegabinaryEndpointStream (k - N)

theorem negabinaryNormalizeAt_prefix
    (a : DigitStream) {N k : ℕ} (hk : k < N) :
    negabinaryNormalizeAt a N k = a k := by
  simp [negabinaryNormalizeAt, hk]

theorem negabinaryNormalizeAt_shift
    (a : DigitStream) (N : ℕ) :
    streamShift (negabinaryNormalizeAt a N) N =
      binaryNegabinaryEndpointStream := by
  funext k
  have hnot : ¬N + k < N := by omega
  have hsub : N + k - N = k := by omega
  simp [streamShift, negabinaryNormalizeAt, hnot, hsub]

/-- Before the first occurrence of digit `2`, the canonical orbit stream is
already binary; replacing the first `2^omega` tail therefore gives an entirely
binary-negabinary stream. -/
theorem negabinaryNormalizeAt_binary {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) {N : ℕ}
    (hfirst : ∀ k < N, orbitDigit negabinaryBase x k ≠ 2) :
    IsBinaryNegabinaryStream
      (negabinaryNormalizeAt (orbitStream negabinaryBase x) N) := by
  intro k
  by_cases hk : k < N
  · rw [negabinaryNormalizeAt_prefix _ hk]
    have hstate :
        orbit negabinaryBase x k ≠ leftEndpoint negabinaryBase := by
      intro hs
      apply hfirst k hk
      exact (negabinary_orbit_emits_two_iff_left hx k).2 hs
    simpa [orbitStream, orbitDigit] using
      negabinary_digit_binary_of_ne_left
        (orbit_mem negabinary_base_gt_one hx k) hstate
  · simp [negabinaryNormalizeAt, hk]
    exact binaryNegabinaryEndpointStream_binary (k - N)

theorem negabinary_orbitStream_bounds {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) :
    ∀ n, 0 ≤ orbitStream negabinaryBase x n ∧
      orbitStream negabinaryBase x n ≤ 2 := by
  intro n
  have hd := digit_mem_alphabet negabinary_base_gt_one
    (orbit_mem negabinary_base_gt_one hx n)
  simpa [orbitStream, orbitDigit, negabinaryBase] using hd

/-- The canonical beta = 2 orbit stream evaluates to its starting point. -/
theorem negabinary_orbitStream_value {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) :
    wordSeriesValue negabinaryBase (orbitStream negabinaryBase x) = x := by
  have hresidual : Filter.Tendsto
      (fun N : ℕ => orbit negabinaryBase x N / (-negabinaryBase) ^ N)
      Filter.atTop (nhds 0) := by
    apply squeeze_zero_norm
        (a := fun N : ℕ => 1 / negabinaryBase ^ N)
    · intro N
      have hstate := orbit_mem negabinary_base_gt_one hx N
      have hstateNorm : ‖orbit negabinaryBase x N‖ ≤ 1 := by
        have hleft := hstate.1
        have hright := hstate.2
        rw [negabinary_leftEndpoint] at hleft
        rw [negabinary_rightEndpoint] at hright
        rw [Real.norm_eq_abs, abs_le]
        constructor <;> linarith
      rw [norm_div, norm_pow]
      have hbaseNorm : ‖-negabinaryBase‖ = negabinaryBase := by
        norm_num [negabinaryBase]
      rw [hbaseNorm]
      exact div_le_div_of_nonneg_right hstateNorm
        (pow_nonneg (by norm_num [negabinaryBase]) N)
    · exact invPow_tendsto_zero negabinary_base_gt_one
  have hprefixSeries : Filter.Tendsto
      (fun N => wordPrefixValue negabinaryBase
        (orbitStream negabinaryBase x) N)
      Filter.atTop
      (nhds (wordSeriesValue negabinaryBase
        (orbitStream negabinaryBase x))) := by
    have hs := negabinary_wordSeries_summable
      (negabinary_orbitStream_bounds hx)
    simpa [wordPrefixValue_eq_sum, wordSeriesValue] using
      hs.hasSum.tendsto_sum_nat
  have hprefixEq : ∀ N,
      wordPrefixValue negabinaryBase (orbitStream negabinaryBase x) N =
        paperPrefix negabinaryBase x N := by
    intro N
    simp [wordPrefixValue_eq_sum, paperPrefix, wordSeriesTerm, orbitStream]
  have hpaperSeries : Filter.Tendsto
      (fun N => paperPrefix negabinaryBase x N)
      Filter.atTop
      (nhds (wordSeriesValue negabinaryBase
        (orbitStream negabinaryBase x))) := by
    exact hprefixSeries.congr'
      (Filter.Eventually.of_forall fun N => hprefixEq N)
  have hpaperValue : Filter.Tendsto
      (fun N => paperPrefix negabinaryBase x N)
      Filter.atTop (nhds x) := by
    have hsub : Filter.Tendsto
        (fun N : ℕ => x -
          orbit negabinaryBase x N / (-negabinaryBase) ^ N)
        Filter.atTop (nhds x) := by
      simpa using (tendsto_const_nhds.sub hresidual)
    apply hsub.congr'
    exact Filter.Eventually.of_forall fun N => by
      have hreconstruction := paper_finite_prefix_reconstruction
        (β := negabinaryBase) (x := x) negabinary_base_gt_one N
      linarith
  exact tendsto_nhds_unique hpaperSeries hpaperValue

/-- Replacing a canonical tail beginning with digit `2` by `(10)^omega`
preserves the value of the complete infinite stream. -/
theorem negabinaryNormalizeAt_value {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) {N : ℕ}
    (hN : orbitDigit negabinaryBase x N = 2) :
    wordSeriesValue negabinaryBase
        (negabinaryNormalizeAt (orbitStream negabinaryBase x) N) =
      wordSeriesValue negabinaryBase (orbitStream negabinaryBase x) := by
  let a : DigitStream := orbitStream negabinaryBase x
  let b : DigitStream := negabinaryNormalizeAt a N
  have ha : ∀ n, 0 ≤ a n ∧ a n ≤ 2 := by
    simpa [a] using negabinary_orbitStream_bounds hx
  have hb : ∀ n, 0 ≤ b n ∧ b n ≤ 2 := by
    intro n
    by_cases hn : n < N
    · rw [show b n = a n by simp [b, negabinaryNormalizeAt, hn]]
      exact ha n
    · have hbinary := binaryNegabinaryEndpointStream_binary (n - N)
      simp only [b, negabinaryNormalizeAt, hn, if_false]
      rcases hbinary with hzero | hone
      · omega
      · omega
  have hprefix : wordPrefixValue negabinaryBase a N =
      wordPrefixValue negabinaryBase b N := by
    apply negabinary_wordPrefixValue_congr
    intro k hk
    simp [a, b, negabinaryNormalizeAt, hk]
  have hatail :
      wordSeriesValue negabinaryBase (streamShift a N) =
      wordSeriesValue negabinaryBase binaryNegabinaryEndpointStream := by
    simpa [a] using negabinary_orbit_tail_normalization hx hN
  have hbtail : streamShift b N = binaryNegabinaryEndpointStream := by
    simpa [b] using negabinaryNormalizeAt_shift a N
  have hsplitA := negabinary_wordSeriesValue_split ha N
  have hsplitB := negabinary_wordSeriesValue_split hb N
  rw [hprefix, hatail] at hsplitA
  rw [hbtail] at hsplitB
  linarith

/-- P1-L7 capstone.  At the first canonical digit `2`, the explicit
normalization produces a fully binary stream with exactly the original value. -/
theorem negabinary_firstHit_normalization {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) {N : ℕ}
    (hN : orbitDigit negabinaryBase x N = 2)
    (hfirst : ∀ k < N, orbitDigit negabinaryBase x k ≠ 2) :
    IsBinaryNegabinaryStream
        (negabinaryNormalizeAt (orbitStream negabinaryBase x) N) ∧
      wordSeriesValue negabinaryBase
          (negabinaryNormalizeAt (orbitStream negabinaryBase x) N) =
        wordSeriesValue negabinaryBase (orbitStream negabinaryBase x) := by
  exact ⟨negabinaryNormalizeAt_binary hx hfirst,
    negabinaryNormalizeAt_value hx hN⟩

/-- Every point of the beta = 2 fundamental interval has a value-equivalent
stream using only the binary negabinary digits `{0, 1}`. -/
theorem negabinary_binary_representation_exists {x : ℝ}
    (hx : InFundamentalInterval negabinaryBase x) :
    ∃ a : DigitStream,
      IsBinaryNegabinaryStream a ∧
        wordSeriesValue negabinaryBase a = x := by
  classical
  by_cases hhit : ∃ N : ℕ, orbitDigit negabinaryBase x N = 2
  · let N : ℕ := Nat.find hhit
    have hN : orbitDigit negabinaryBase x N = 2 := by
      exact Nat.find_spec hhit
    have hfirst : ∀ k < N, orbitDigit negabinaryBase x k ≠ 2 := by
      intro k hk htwo
      have hminimal : N ≤ k := Nat.find_min' hhit htwo
      omega
    have hnormalized := negabinary_firstHit_normalization hx hN hfirst
    refine ⟨negabinaryNormalizeAt (orbitStream negabinaryBase x) N,
      hnormalized.1, ?_⟩
    calc
      wordSeriesValue negabinaryBase
          (negabinaryNormalizeAt (orbitStream negabinaryBase x) N) =
          wordSeriesValue negabinaryBase
            (orbitStream negabinaryBase x) := hnormalized.2
      _ = x := negabinary_orbitStream_value hx
  · refine ⟨orbitStream negabinaryBase x, ?_,
      negabinary_orbitStream_value hx⟩
    intro n
    have htwo : orbitDigit negabinaryBase x n ≠ 2 := by
      intro hn
      exact hhit ⟨n, hn⟩
    have hstate :
        orbit negabinaryBase x n ≠ leftEndpoint negabinaryBase := by
      intro hs
      exact htwo ((negabinary_orbit_emits_two_iff_left hx n).2 hs)
    simpa [orbitStream, orbitDigit] using
      negabinary_digit_binary_of_ne_left
        (orbit_mem negabinary_base_gt_one hx n) hstate

end

end CNRSProblem1
