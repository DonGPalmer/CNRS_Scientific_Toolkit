import CNRSProblem1.ReferenceSystems

namespace CNRSProblem1

noncomputable section

/-- A stream has pure period `q` when `q` is positive and every digit repeats
after `q` places. -/
def HasPurePeriod (a : DigitStream) (q : ℕ) : Prop :=
  0 < q ∧ ∀ n : ℕ, a (n + q) = a n

/-- The exceptional case in the Ito--Sadahiro definition of the modified upper
reference: the lower reference has a positive odd pure period. -/
def HasOddPurePeriod (a : DigitStream) : Prop :=
  ∃ q : ℕ, Odd q ∧ HasPurePeriod a q

/-- The periodic word
`(0,b₁,...,b_(q-1),b_q-1)^omega`, expressed using zero-based stream
indices.  This is the exceptional branch of the Ito--Sadahiro `d*`
construction when the lower word has odd pure period `q`. -/
def oddModifiedUpper (lower : DigitStream) (q : ℕ) : DigitStream :=
  fun n =>
    let r := n % (q + 1)
    if r = 0 then 0
    else if r = q then lower (q - 1) - 1
    else lower (r - 1)

/-- The general modified upper reference.  `Nat.find` selects the least odd
pure period when the exceptional case exists; otherwise the formal right
boundary word is used. -/
noncomputable def modifiedUpperReference
    (lower boundary : DigitStream) : DigitStream := by
  classical
  exact if h : HasOddPurePeriod lower then
    oddModifiedUpper lower (Nat.find h)
  else
    boundary

theorem modifiedUpperReference_eq_boundary
    {lower boundary : DigitStream}
    (h : ¬ HasOddPurePeriod lower) :
    modifiedUpperReference lower boundary = boundary := by
  classical
  simp [modifiedUpperReference, h]

theorem sqrtTwo_noOddPurePeriod :
    ¬ HasOddPurePeriod (lowerReference sqrtTwoBase) := by
  rintro ⟨q, _hodd, hq, hperiod⟩
  have h := hperiod 0
  have hform : q = (q - 1) + 1 := by omega
  rw [Nat.zero_add, hform, sqrtTwo_lower_value_succ,
      sqrtTwo_lower_value_zero] at h
  norm_num at h

theorem sqrtThree_noOddPurePeriod :
    ¬ HasOddPurePeriod (lowerReference sqrtThreeBase) := by
  rintro ⟨q, _hodd, hq, hperiod⟩
  have h := hperiod 0
  have hform : q = (q - 1) + 1 := by omega
  rw [Nat.zero_add, hform, sqrtThree_lower_value_succ,
      sqrtThree_lower_value_zero] at h
  norm_num at h

theorem golden_noOddPurePeriod :
    ¬ HasOddPurePeriod (lowerReference goldenBase) := by
  rintro ⟨q, hodd, _hq, hperiod⟩
  rcases hodd with ⟨k, hk⟩
  have hqodd : q = 2 * k + 1 := by omega
  have h := hperiod 0
  rw [Nat.zero_add, hqodd, golden_lower_value_odd] at h
  have hzero : lowerReference goldenBase 0 = 2 := by
    simpa using golden_lower_value_even 0
  rw [hzero] at h
  norm_num at h

theorem sqrtTwo_modifiedUpperReference :
    modifiedUpperReference (lowerReference sqrtTwoBase)
      (rightBoundaryStream sqrtTwoBase) =
        rightBoundaryStream sqrtTwoBase :=
  modifiedUpperReference_eq_boundary sqrtTwo_noOddPurePeriod

theorem sqrtThree_modifiedUpperReference :
    modifiedUpperReference (lowerReference sqrtThreeBase)
      (rightBoundaryStream sqrtThreeBase) =
        rightBoundaryStream sqrtThreeBase :=
  modifiedUpperReference_eq_boundary sqrtThree_noOddPurePeriod

theorem golden_modifiedUpperReference :
    modifiedUpperReference (lowerReference goldenBase)
      (rightBoundaryStream goldenBase) =
        rightBoundaryStream goldenBase :=
  modifiedUpperReference_eq_boundary golden_noOddPurePeriod

/-- A reference system using the Ito--Sadahiro modified-upper construction
rather than assuming the right-boundary recurrence is always the correct upper
word.  This definition supplies the standard reference pair; the language
realization equivalence is proved separately. -/
noncomputable def modifiedUpperReferenceSystem (β : ℝ) : ReferenceSystem :=
  ⟨lowerReference β,
    modifiedUpperReference (lowerReference β) (rightBoundaryStream β)⟩

theorem sqrtTwo_modifiedUpperReferenceSystem :
    modifiedUpperReferenceSystem sqrtTwoBase = sqrtTwoReferenceSystem := by
  unfold modifiedUpperReferenceSystem sqrtTwoReferenceSystem
  rw [sqrtTwo_modifiedUpperReference]

theorem sqrtThree_modifiedUpperReferenceSystem :
    modifiedUpperReferenceSystem sqrtThreeBase = sqrtThreeReferenceSystem := by
  unfold modifiedUpperReferenceSystem sqrtThreeReferenceSystem
  rw [sqrtThree_modifiedUpperReference]

theorem golden_modifiedUpperReferenceSystem :
    modifiedUpperReferenceSystem goldenBase = goldenReferenceSystem := by
  unfold modifiedUpperReferenceSystem goldenReferenceSystem
  rw [golden_modifiedUpperReference]

end

end CNRSProblem1
