import CNRSProblem1.ReferenceSystems

namespace CNRSProblem1

noncomputable section

def EventuallyPeriodic (a : DigitStream) : Prop :=
  ∃ N p : ℕ, 0 < p ∧
    ∀ n : ℕ, a (N + n + p) = a (N + n)

def PurelyPeriodic (a : DigitStream) : Prop :=
  ∃ p : ℕ, 0 < p ∧ ∀ n : ℕ, a (n + p) = a n

theorem purelyPeriodic_eventuallyPeriodic {a : DigitStream}
    (h : PurelyPeriodic a) : EventuallyPeriodic a := by
  rcases h with ⟨p, hp, hper⟩
  exact ⟨0, p, hp, by simpa using hper⟩

theorem sqrtTwo_lower_eventuallyPeriodic :
    EventuallyPeriodic (lowerReference sqrtTwoBase) := by
  refine ⟨1, 1, by omega, ?_⟩
  intro n
  rw [show 1 + n + 1 = (n + 1) + 1 by omega,
      show 1 + n = n + 1 by omega,
      sqrtTwo_lower_value_succ, sqrtTwo_lower_value_succ]

theorem sqrtThree_lower_eventuallyPeriodic :
    EventuallyPeriodic (lowerReference sqrtThreeBase) := by
  refine ⟨1, 1, by omega, ?_⟩
  intro n
  rw [show 1 + n + 1 = (n + 1) + 1 by omega,
      show 1 + n = n + 1 by omega,
      sqrtThree_lower_value_succ, sqrtThree_lower_value_succ]

theorem golden_lower_purelyPeriodic :
    PurelyPeriodic (lowerReference goldenBase) := by
  refine ⟨2, by omega, ?_⟩
  intro n
  rcases Nat.even_or_odd n with hn | hn
  · rcases hn with ⟨k, rfl⟩
    rw [show k + k + 2 = 2 * (k + 1) by omega,
      show k + k = 2 * k by omega,
      golden_lower_value_even, golden_lower_value_even]
  · rcases hn with ⟨k, rfl⟩
    rw [show 2 * k + 1 + 2 = 2 * (k + 1) + 1 by omega,
      golden_lower_value_odd, golden_lower_value_odd]

theorem all_three_lowerReferences_eventuallyPeriodic :
    EventuallyPeriodic (lowerReference sqrtTwoBase) ∧
    EventuallyPeriodic (lowerReference sqrtThreeBase) ∧
    EventuallyPeriodic (lowerReference goldenBase) :=
  ⟨sqrtTwo_lower_eventuallyPeriodic, sqrtThree_lower_eventuallyPeriodic,
    purelyPeriodic_eventuallyPeriodic golden_lower_purelyPeriodic⟩

theorem sqrtTwo_upper_eventuallyPeriodic :
    EventuallyPeriodic (rightBoundaryStream sqrtTwoBase) := by
  refine ⟨2, 1, by omega, ?_⟩
  intro n
  have h := sqrtTwo_rightBoundary_digits.2.2
  change orbitDigit sqrtTwoBase (rightEndpoint sqrtTwoBase) (2 + n + 1) =
    orbitDigit sqrtTwoBase (rightEndpoint sqrtTwoBase) (2 + n)
  rw [show 2 + n + 1 = (n + 1) + 2 by omega,
      show 2 + n = n + 2 by omega, h, h]

theorem sqrtThree_upper_eventuallyPeriodic :
    EventuallyPeriodic (rightBoundaryStream sqrtThreeBase) := by
  refine ⟨2, 1, by omega, ?_⟩
  intro n
  have h := sqrtThree_rightBoundary_digits.2.2
  change orbitDigit sqrtThreeBase (rightEndpoint sqrtThreeBase) (2 + n + 1) =
    orbitDigit sqrtThreeBase (rightEndpoint sqrtThreeBase) (2 + n)
  rw [show 2 + n + 1 = (n + 1) + 2 by omega,
      show 2 + n = n + 2 by omega, h, h]

theorem golden_upper_eventuallyPeriodic :
    EventuallyPeriodic (rightBoundaryStream goldenBase) := by
  refine ⟨1, 2, by omega, ?_⟩
  intro n
  change orbitDigit goldenBase (rightEndpoint goldenBase) (1 + n + 2) =
    orbitDigit goldenBase (rightEndpoint goldenBase) (1 + n)
  rcases Nat.even_or_odd n with hn | hn
  · rcases hn with ⟨k, rfl⟩
    rw [show 1 + (k + k) + 2 = 2 * (k + 1) + 1 by omega,
      show 1 + (k + k) = 2 * k + 1 by omega,
      golden_rightBoundary_digits.2.1,
      golden_rightBoundary_digits.2.1]
  · rcases hn with ⟨k, rfl⟩
    rw [show 1 + (2 * k + 1) + 2 = 2 * (k + 1) + 2 by omega,
      show 1 + (2 * k + 1) = 2 * k + 2 by omega,
      golden_rightBoundary_digits.2.2,
      golden_rightBoundary_digits.2.2]

theorem all_three_reference_pairs_eventuallyPeriodic :
    (EventuallyPeriodic (lowerReference sqrtTwoBase) ∧
      EventuallyPeriodic (rightBoundaryStream sqrtTwoBase)) ∧
    (EventuallyPeriodic (lowerReference sqrtThreeBase) ∧
      EventuallyPeriodic (rightBoundaryStream sqrtThreeBase)) ∧
    (EventuallyPeriodic (lowerReference goldenBase) ∧
      EventuallyPeriodic (rightBoundaryStream goldenBase)) :=
  ⟨⟨sqrtTwo_lower_eventuallyPeriodic, sqrtTwo_upper_eventuallyPeriodic⟩,
   ⟨sqrtThree_lower_eventuallyPeriodic, sqrtThree_upper_eventuallyPeriodic⟩,
   ⟨purelyPeriodic_eventuallyPeriodic golden_lower_purelyPeriodic,
      golden_upper_eventuallyPeriodic⟩⟩

theorem orbit_add (β x : ℝ) (m n : ℕ) :
    orbit β x (m + n) = orbit β (orbit β x m) n := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Nat.add_succ, orbit_succ, orbit_succ, ih]

theorem state_repeat_implies_digit_periodicity
    {β x : ℝ} {N p : ℕ}
    (hp : 0 < p)
    (hrepeat : orbit β x (N + p) = orbit β x N) :
    EventuallyPeriodic (orbitStream β x) := by
  refine ⟨N, p, hp, ?_⟩
  intro n
  change digit β (orbit β x (N + n + p)) =
    digit β (orbit β x (N + n))
  have hs :
      orbit β x (N + n + p) = orbit β x (N + n) := by
    calc
      orbit β x (N + n + p) =
          orbit β x ((N + p) + n) := by
            rw [show N + n + p = (N + p) + n by omega]
      _ = orbit β (orbit β x (N + p)) n := orbit_add β x (N + p) n
      _ = orbit β (orbit β x N) n := by rw [hrepeat]
      _ = orbit β x (N + n) := (orbit_add β x N n).symm
  rw [hs]

def conjugateStep (γ q : ℝ) (d : ℤ) : ℝ :=
  -γ * q - d

theorem conjugateStep_abs_bound (γ q : ℝ) (d : ℤ) :
    |conjugateStep γ q d| ≤ |γ| * |q| + |(d : ℝ)| := by
  unfold conjugateStep
  calc
    |-γ * q - (d : ℝ)| ≤ |-γ * q| + |(d : ℝ)| := abs_sub _ _
    _ = |γ| * |q| + |(d : ℝ)| := by rw [abs_mul, abs_neg]

theorem conjugateStep_invariant_bound
    {γ q D B : ℝ} {d : ℤ}
    (hd : |(d : ℝ)| ≤ D)
    (hB : D ≤ (1 - |γ|) * B)
    (hq : |q| ≤ B) :
    |conjugateStep γ q d| ≤ B := by
  calc
    |conjugateStep γ q d| ≤ |γ| * |q| + |(d : ℝ)| :=
      conjugateStep_abs_bound γ q d
    _ ≤ |γ| * B + D := by gcongr
    _ ≤ |γ| * B + (1 - |γ|) * B := by gcongr
    _ = B := by ring

def conjugateOrbit (gamma q : ℝ) (digits : ℕ → ℤ) : ℕ → ℝ
  | 0 => q
  | n + 1 => conjugateStep gamma (conjugateOrbit gamma q digits n) (digits n)

/-- Iteration of the one-step conjugate bound.  This is the bounded-coordinate
part of the Pisot mechanism; no lattice finiteness premise is hidden here. -/
theorem conjugateOrbit_invariant_bound
    {gamma q D B : ℝ} {digits : ℕ → ℤ}
    (hdigits : ∀ n, |(digits n : ℝ)| ≤ D)
    (hB : D ≤ (1 - |gamma|) * B)
    (hq : |q| ≤ B) :
    ∀ n, |conjugateOrbit gamma q digits n| ≤ B := by
  intro n
  induction n with
  | zero => exact hq
  | succ n ih =>
      exact conjugateStep_invariant_bound (hdigits n) hB ih

end

end CNRSProblem1