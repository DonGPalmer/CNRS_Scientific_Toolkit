import CNRSProblem1.Framework

namespace CNRSProblem1

noncomputable section

open scoped BigOperators

/-- The state reached after `n` Ito--Sadahiro steps. -/
def orbit (β x : ℝ) : ℕ → ℝ
  | 0 => x
  | n + 1 => transform β (orbit β x n)

/-- The digit emitted at step `n` (the paper's digit `d_(n+1)`). -/
def orbitDigit (β x : ℝ) (n : ℕ) : ℤ :=
  digit β (orbit β x n)

/-- Value of the first `n` emitted digits, accumulated from the leading digit. -/
def prefixValue (β x : ℝ) : ℕ → ℝ
  | 0 => 0
  | n + 1 =>
      (digit β x : ℝ) / (-β) +
        prefixValue β (transform β x) n / (-β)

/-- The actual deterministic digit word of length `n`. -/
def generatedPrefix (β x : ℝ) (n : ℕ) : List ℤ :=
  List.ofFn (fun k : Fin n => orbitDigit β x k)

@[simp] theorem orbit_zero (β x : ℝ) : orbit β x 0 = x := rfl

@[simp] theorem orbit_succ (β x : ℝ) (n : ℕ) :
    orbit β x (n + 1) = transform β (orbit β x n) := rfl

theorem orbit_transform (β x : ℝ) (n : ℕ) :
    orbit β (transform β x) n = orbit β x (n + 1) := by
  induction n with
  | zero => rfl
  | succ n ih =>
      simp only [orbit_succ]
      rw [ih, orbit_succ]

@[simp] theorem prefixValue_zero (β x : ℝ) :
    prefixValue β x 0 = 0 := rfl

@[simp] theorem prefixValue_succ (β x : ℝ) (n : ℕ) :
    prefixValue β x (n + 1) =
      (digit β x : ℝ) / (-β) +
        prefixValue β (transform β x) n / (-β) := rfl

/-- Every iterate remains in the fundamental interval. -/
theorem orbit_mem {β x : ℝ} (hβ : 1 < β)
    (hx : InFundamentalInterval β x) (n : ℕ) :
    InFundamentalInterval β (orbit β x n) := by
  induction n with
  | zero => simpa using hx
  | succ n ih =>
      simpa using transform_mem hβ

/-- Exact reconstruction from an `n`-digit prefix and the residual state. -/
theorem finite_prefix_reconstruction {β x : ℝ} (hβ : 1 < β) (n : ℕ) :
    x =
      prefixValue β x n +
        orbit β x n / (-β) ^ n := by
  induction n generalizing x with
  | zero => simp
  | succ n ih =>
      calc
        x = (digit β x : ℝ) / (-β) + transform β x / (-β) :=
          one_step_reconstruction hβ
        _ = (digit β x : ℝ) / (-β) +
              (prefixValue β (transform β x) n +
                orbit β (transform β x) n / (-β) ^ n) / (-β) := by
              exact congrArg
                (fun z : ℝ => (digit β x : ℝ) / (-β) + z / (-β))
                (ih (x := transform β x))
        _ = prefixValue β x (n + 1) +
              orbit β (transform β x) n / (-β) ^ (n + 1) := by
              rw [prefixValue_succ, add_div, div_div, pow_succ]
              ring
        _ = prefixValue β x (n + 1) +
              orbit β x (n + 1) / (-β) ^ (n + 1) := by
              rw [orbit_transform]

/-- The paper's explicit finite sum of the first `n` digits. -/
def paperPrefix (β x : ℝ) (n : ℕ) : ℝ :=
  (Finset.range n).sum
    (fun k => (orbitDigit β x k : ℝ) / (-β) ^ (k + 1))

@[simp] theorem paperPrefix_zero (β x : ℝ) :
    paperPrefix β x 0 = 0 := by
  simp [paperPrefix]

theorem paperPrefix_succ (β x : ℝ) (n : ℕ) :
    paperPrefix β x (n + 1) =
      paperPrefix β x n +
        (orbitDigit β x n : ℝ) / (-β) ^ (n + 1) := by
  simp [paperPrefix, Finset.sum_range_succ]

/-- Equation (finite form) matching P1 v12's digit-indexed value formula. -/
theorem paper_finite_prefix_reconstruction {β x : ℝ}
    (hβ : 1 < β) (n : ℕ) :
    x =
      paperPrefix β x n +
        orbit β x n / (-β) ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
      calc
        x = paperPrefix β x n + orbit β x n / (-β) ^ n := ih
        _ = paperPrefix β x n +
              ((orbitDigit β x n : ℝ) / (-β) +
                orbit β x (n + 1) / (-β)) / (-β) ^ n := by
              apply congrArg
                (fun z : ℝ => paperPrefix β x n + z / (-β) ^ n)
              simpa [orbitDigit] using
                (one_step_reconstruction hβ (x := orbit β x n))
        _ = paperPrefix β x n +
              (orbitDigit β x n : ℝ) / (-β) ^ (n + 1) +
                orbit β x (n + 1) / (-β) ^ (n + 1) := by
              rw [add_div, div_div, div_div, pow_succ]
              ring
        _ = paperPrefix β x (n + 1) +
              orbit β x (n + 1) / (-β) ^ (n + 1) := by
              rw [paperPrefix_succ]

theorem prefixValue_eq_paperPrefix {β x : ℝ} (hβ : 1 < β) (n : ℕ) :
    prefixValue β x n = paperPrefix β x n := by
  have h₁ := finite_prefix_reconstruction (β := β) (x := x) hβ n
  have h₂ := paper_finite_prefix_reconstruction (β := β) (x := x) hβ n
  linarith

/-- A finite word is admissible from `x` when it is exactly an emitted prefix. -/
def FiniteAdmissibleFrom (β x : ℝ) (w : List ℤ) : Prop :=
  w = generatedPrefix β x w.length

theorem finite_admissible_unique {β x : ℝ} {u v : List ℤ}
    (hu : FiniteAdmissibleFrom β x u)
    (hv : FiniteAdmissibleFrom β x v)
    (hlen : u.length = v.length) :
    u = v := by
  unfold FiniteAdmissibleFrom at hu hv
  rw [hu, hv, hlen]

end

end CNRSProblem1
