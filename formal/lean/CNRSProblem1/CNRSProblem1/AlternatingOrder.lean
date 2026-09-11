import CNRSProblem1.EndpointOrbits

namespace CNRSProblem1

abbrev DigitStream := ℕ → ℤ

def streamShift (a : DigitStream) (n : ℕ) : DigitStream :=
  fun k => a (n + k)

def FirstDifference (a b : DigitStream) (k : ℕ) : Prop :=
  (∀ j < k, a j = b j) ∧ a k ≠ b k

def AltLT (a b : DigitStream) : Prop :=
  ∃ k, FirstDifference a b k ∧
    (if Even k then b k < a k else a k < b k)

def AltLE (a b : DigitStream) : Prop := a = b ∨ AltLT a b

@[simp] theorem streamShift_zero (a : DigitStream) :
    streamShift a 0 = a := by
  funext k
  simp [streamShift]

theorem streamShift_add (a : DigitStream) (m n : ℕ) :
    streamShift (streamShift a m) n = streamShift a (m + n) := by
  funext k
  simp [streamShift, Nat.add_assoc]

theorem altLT_of_first
    {a b : DigitStream} (hne : a 0 ≠ b 0) (hlt : b 0 < a 0) :
    AltLT a b := by
  refine ⟨0, ?_, ?_⟩
  · exact ⟨by simp, hne⟩
  · simpa using hlt

theorem altLT_of_second
    {a b : DigitStream}
    (hzero : a 0 = b 0)
    (hne : a 1 ≠ b 1)
    (hlt : a 1 < b 1) :
    AltLT a b := by
  refine ⟨1, ?_, ?_⟩
  · constructor
    · intro j hj
      have : j = 0 := by omega
      simpa [this] using hzero
    · exact hne
  · simp only [show ¬ Even 1 by decide, if_false]
    exact hlt

theorem not_altLE_of_second_reverse
    {a b : DigitStream}
    (hzero : a 0 = b 0)
    (hreverse : b 1 < a 1) :
    ¬ AltLE a b := by
  intro h
  rcases h with hEq | ⟨k, hfirst, hord⟩
  · have h : a 1 = b 1 := by simpa using congrFun hEq 1
    omega
  · rcases hfirst with ⟨hprefix, hne⟩
    rcases Nat.eq_zero_or_pos k with rfl | hk
    · exact hne hzero
    · rcases Nat.eq_or_lt_of_le hk with rfl | hk
      · simp only [show ¬ Even 1 by decide, if_false] at hord
        change a 1 < b 1 at hord
        omega
      · have hsame := hprefix 1 hk
        change a 1 = b 1 at hsame
        omega

theorem altLE_refl (a : DigitStream) : AltLE a a := Or.inl rfl

end CNRSProblem1