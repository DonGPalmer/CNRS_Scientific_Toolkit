import CNRSProblem1.AlternatingOrder

namespace CNRSProblem1

noncomputable section

def orbitStream (β x : ℝ) : DigitStream := orbitDigit β x

def lowerReference (β : ℝ) : DigitStream :=
  orbitStream β (leftEndpoint β)

/-- The digit orbit of the excluded right boundary.  This is intentionally
not called the general modified upper reference: for odd pure-period lower
expansions, the Ito--Sadahiro `d*` construction needs an additional case. -/
def rightBoundaryStream (β : ℝ) : DigitStream :=
  orbitStream β (rightEndpoint β)

structure ReferenceSystem where
  lower : DigitStream
  upper : DigitStream

def ISAdmissibleBetween
    (lower upper a : DigitStream) : Prop :=
  ∀ n : ℕ,
    AltLE lower (streamShift a n) ∧
    AltLT (streamShift a n) upper

def SymbolicallyAdmissibleFor (R : ReferenceSystem) (a : DigitStream) : Prop :=
  ISAdmissibleBetween R.lower R.upper a

def sqrtTwoReferenceSystem : ReferenceSystem :=
  ⟨lowerReference sqrtTwoBase, rightBoundaryStream sqrtTwoBase⟩

def sqrtThreeReferenceSystem : ReferenceSystem :=
  ⟨lowerReference sqrtThreeBase, rightBoundaryStream sqrtThreeBase⟩

def goldenReferenceSystem : ReferenceSystem :=
  ⟨lowerReference goldenBase, rightBoundaryStream goldenBase⟩

theorem sqrtTwo_admissibility_criterion (a : DigitStream) :
    SymbolicallyAdmissibleFor sqrtTwoReferenceSystem a ↔
      ∀ n : ℕ,
        AltLE (orbitStream sqrtTwoBase (leftEndpoint sqrtTwoBase))
          (streamShift a n) ∧
        AltLT (streamShift a n)
          (orbitStream sqrtTwoBase (rightEndpoint sqrtTwoBase)) := by
  rfl

theorem sqrtThree_admissibility_criterion (a : DigitStream) :
    SymbolicallyAdmissibleFor sqrtThreeReferenceSystem a ↔
      ∀ n : ℕ,
        AltLE (orbitStream sqrtThreeBase (leftEndpoint sqrtThreeBase))
          (streamShift a n) ∧
        AltLT (streamShift a n)
          (orbitStream sqrtThreeBase (rightEndpoint sqrtThreeBase)) := by
  rfl

theorem golden_admissibility_criterion (a : DigitStream) :
    SymbolicallyAdmissibleFor goldenReferenceSystem a ↔
      ∀ n : ℕ,
        AltLE (orbitStream goldenBase (leftEndpoint goldenBase))
          (streamShift a n) ∧
        AltLT (streamShift a n)
          (orbitStream goldenBase (rightEndpoint goldenBase)) := by
  rfl

def FiniteAltLT (u v : List ℤ) : Prop :=
  ∃ k : Fin (min u.length v.length),
    (∀ j < k.1, u[j]? = v[j]?) ∧
    (if Even k.1 then v[k.1]! < u[k.1]! else u[k.1]! < v[k.1]!)

instance (u v : List ℤ) : Decidable (FiniteAltLT u v) := by
  unfold FiniteAltLT
  infer_instance

def FiniteAltLE (u v : List ℤ) : Prop :=
  u = v ∨ FiniteAltLT u v

instance (u v : List ℤ) : Decidable (FiniteAltLE u v) := by
  unfold FiniteAltLE
  infer_instance

def FiniteISAdmissible
    (lower upper : List ℤ) (w : List ℤ) : Prop :=
  ∀ n : Fin w.length,
    (w.drop n = lower.take (w.length - n) ∨
      FiniteAltLT (lower.take (w.length - n)) (w.drop n)) ∧
    FiniteAltLE (w.drop n) (upper.take (w.length - n))

instance (lower upper w : List ℤ) :
    Decidable (FiniteISAdmissible lower upper w) := by
  unfold FiniteISAdmissible
  infer_instance

/-- A Boolean front end whose reduction is backed by the finite instances
above, rather than by classical proposition decidability. -/
def finiteISAdmissibleCheck
    (lower upper w : List ℤ) : Bool :=
  decide (FiniteISAdmissible lower upper w)

theorem finiteISAdmissibleCheck_eq_true
    (lower upper w : List ℤ) :
    finiteISAdmissibleCheck lower upper w = true ↔
      FiniteISAdmissible lower upper w := by
  simp [finiteISAdmissibleCheck]

end

end CNRSProblem1