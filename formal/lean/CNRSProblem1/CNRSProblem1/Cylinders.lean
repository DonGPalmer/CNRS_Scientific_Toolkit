import CNRSProblem1.OrbitLanguage

namespace CNRSProblem1

noncomputable section

/-- The points whose first `n` emitted digits agree with a prescribed
infinite word. -/
def PrefixCylinder (β : ℝ) (a : DigitStream) (n : ℕ) : Set ℝ :=
  {x | InFundamentalInterval β x ∧
    ∀ k < n, orbitDigit β x k = a k}

theorem mem_prefixCylinder_iff {β x : ℝ} {a : DigitStream} {n : ℕ} :
    x ∈ PrefixCylinder β a n ↔
      InFundamentalInterval β x ∧
        ∀ k < n, orbitDigit β x k = a k := by
  rfl

/-- Every genuine orbit belongs to every cylinder cut out by its own stream. -/
theorem orbit_mem_own_prefixCylinder {β x : ℝ}
    (hx : InFundamentalInterval β x) (n : ℕ) :
    x ∈ PrefixCylinder β (orbitStream β x) n := by
  exact ⟨hx, by simp [orbitStream]⟩

/-- Longer prefix cylinders are nested inside shorter ones. -/
theorem prefixCylinder_antitone {β : ℝ} {a : DigitStream}
    {m n : ℕ} (hmn : m ≤ n) :
    PrefixCylinder β a n ⊆ PrefixCylinder β a m := by
  intro x hx
  exact ⟨hx.1, fun k hk => hx.2 k (lt_of_lt_of_le hk hmn)⟩

/-- Two points in the same length-`n` cylinder are at most
`β⁻ⁿ` apart. -/
theorem prefixCylinder_diameter
    {β x y : ℝ} {a : DigitStream} {n : ℕ}
    (hβ : 1 < β)
    (hx : x ∈ PrefixCylinder β a n)
    (hy : y ∈ PrefixCylinder β a n) :
    |x - y| ≤ 1 / β ^ n := by
  have hprefix : ∀ k < n,
      orbitDigit β x k = orbitDigit β y k := by
    intro k hk
    rw [hx.2 k hk, hy.2 k hk]
  have hstate := orbit_sub_eq_pow_mul_of_prefix hprefix
  have hxn := orbit_mem hβ hx.1 n
  have hyn := orbit_mem hβ hy.1 n
  have hdiff : |orbit β x n - orbit β y n| ≤ 1 := by
    rw [abs_le]
    constructor <;>
      linarith [interval_width hβ, hxn.1, hxn.2, hyn.1, hyn.2]
  have hβpos : 0 < β := lt_trans zero_lt_one hβ
  have habseq :
      |orbit β x n - orbit β y n| = β ^ n * |x - y| := by
    calc
      |orbit β x n - orbit β y n| =
          |(-β) ^ n * (x - y)| := congrArg abs hstate
      _ = β ^ n * |x - y| := by
        rw [abs_mul, abs_pow, abs_neg, abs_of_pos hβpos]
  have hprod : β ^ n * |x - y| ≤ 1 := by
    rw [← habseq]
    exact hdiff
  apply (le_div_iff₀ (pow_pos hβpos n)).2
  simpa [mul_comm] using hprod

/-- Realization of a complete digit word by a point in the fundamental
interval. -/
def RealizesOrbitStream (β : ℝ) (a : DigitStream) (x : ℝ) : Prop :=
  InFundamentalInterval β x ∧ orbitStream β x = a

theorem realizesOrbitStream_iff_all_cylinders
    {β x : ℝ} {a : DigitStream} :
    RealizesOrbitStream β a x ↔
      ∀ n, x ∈ PrefixCylinder β a n := by
  constructor
  · rintro ⟨hx, hstream⟩ n
    refine ⟨hx, ?_⟩
    intro k _
    change orbitStream β x k = a k
    exact congrFun hstream k
  · intro hall
    constructor
    · exact (hall 0).1
    · funext k
      exact (hall (k + 1)).2 k (Nat.lt_succ_self k)

/-- A word has at most one orbit realization.  The shrinking-cylinder
estimate above gives the quantitative form of the same uniqueness fact. -/
theorem realizesOrbitStream_unique
    {β : ℝ} (hβ : 1 < β) {a : DigitStream}
    {x y : ℝ}
    (hx : RealizesOrbitStream β a x)
    (hy : RealizesOrbitStream β a y) :
    x = y := by
  apply orbitStream_injective_of_closedBounds hβ
      (orbitClosedBounds_of_mem hβ hx.1)
      (orbitClosedBounds_of_mem hβ hy.1)
  exact hx.2.trans hy.2.symm

end

end CNRSProblem1
