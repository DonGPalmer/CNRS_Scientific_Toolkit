/-
CNRSArithmetic Phase D: generic finite-state bound for a fixed multiplier.

Migration adapter onto CNRSCore-owned Gaussian height. The theorem statements and
Phase-D constructions are unchanged; only the height-subadditivity proof is made
explicit against the qualified Core definition.
-/
import CNRSArithmetic.FixedMultiplier

namespace CNRSArithmetic

open Zsqrtd

/-- Max-coordinate height is subadditive. -/
theorem gaussianHeight_add_le (x y : GaussianInt) :
    gaussianHeight (x + y) ≤ gaussianHeight x + gaussianHeight y := by
  have hxre : x.re.natAbs ≤ gaussianHeight x := Nat.le_max_left _ _
  have hxim : x.im.natAbs ≤ gaussianHeight x := Nat.le_max_right _ _
  have hyre : y.re.natAbs ≤ gaussianHeight y := Nat.le_max_left _ _
  have hyim : y.im.natAbs ≤ gaussianHeight y := Nat.le_max_right _ _
  have hre : (x.re + y.re).natAbs ≤ gaussianHeight x + gaussianHeight y := by
    exact le_trans (Int.natAbs_add_le _ _) (Nat.add_le_add hxre hyre)
  have him : (x.im + y.im).natAbs ≤ gaussianHeight x + gaussianHeight y := by
    exact le_trans (Int.natAbs_add_le _ _) (Nat.add_le_add hxim hyim)
  change max (x.re + y.re).natAbs (x.im + y.im).natAbs ≤
    gaussianHeight x + gaussianHeight y
  exact max_le hre him

/-- A product of two canonical digits has height at most 16. -/
theorem gaussianHeight_digit_mul_digit_le (d e : Digit) :
    gaussianHeight (digit d * digit e) ≤ 16 := by
  fin_cases d <;> fin_cases e <;> native_decide

/-- Sliding convolution coefficient for two LSD-first windows, truncated at the shorter list. -/
def windowCoefficient : List Digit → List Digit → GaussianInt
  | [], _ => 0
  | _, [] => 0
  | m :: ms, d :: ds => digit m * digit d + windowCoefficient ms ds

/-- A fixed multiplier of J digits contributes at most 16*J to any sliding coefficient. -/
theorem windowCoefficient_height_le (ms ds : List Digit) :
    gaussianHeight (windowCoefficient ms ds) ≤ 16 * ms.length := by
  induction ms generalizing ds with
  | nil => simp [windowCoefficient, gaussianHeight]
  | cons m ms ih =>
      cases ds with
      | nil => simp [windowCoefficient, gaussianHeight]
      | cons d ds =>
          have hprod := gaussianHeight_digit_mul_digit_le m d
          have hadd := gaussianHeight_add_le (digit m * digit d) (windowCoefficient ms ds)
          have htail := ih ds
          simp only [windowCoefficient, List.length_cons]
          omega

/-- Generic carry budget for a fixed J-digit multiplier. -/
def fixedCarryBound (J : ℕ) : ℕ := 32 * J + 4

/-- One streaming fixed-multiplier step: normalize the current window coefficient plus carry. -/
def fixedMultiplierCarryStep (κ : GaussianInt) (ms ds : List Digit) : GaussianInt :=
  nextCarryFromSum (windowCoefficient ms ds + κ)

/-- The coarse carry box is invariant for every fixed J-digit multiplier. -/
theorem fixedMultiplierCarryStep_height_le
    (ms ds : List Digit) (κ : GaussianInt)
    (hκ : gaussianHeight κ ≤ fixedCarryBound ms.length) :
    gaussianHeight (fixedMultiplierCarryStep κ ms ds) ≤ fixedCarryBound ms.length := by
  let C := 16 * ms.length
  let B := fixedCarryBound ms.length
  have hc : gaussianHeight (windowCoefficient ms ds) ≤ C := by
    simpa [C] using windowCoefficient_height_le ms ds
  have hs : gaussianHeight (windowCoefficient ms ds + κ) ≤ C + B := by
    exact le_trans (gaussianHeight_add_le _ _) (Nat.add_le_add hc hκ)
  have hn := nextCarry_height_bound (windowCoefficient ms ds + κ)
  change 5 * gaussianHeight (fixedMultiplierCarryStep κ ms ds) ≤
      3 * gaussianHeight (windowCoefficient ms ds + κ) + 8 at hn
  have h5 : 5 * gaussianHeight (fixedMultiplierCarryStep κ ms ds) ≤ 5 * B := by
    calc
      5 * gaussianHeight (fixedMultiplierCarryStep κ ms ds)
          ≤ 3 * gaussianHeight (windowCoefficient ms ds + κ) + 8 := hn
      _ ≤ 3 * (C + B) + 8 := by omega
      _ ≤ 5 * B := by
        dsimp [C, B, fixedCarryBound]
        omega
  omega

/-- Gaussian carries inside any fixed max-coordinate box form a finite set. -/
theorem finite_gaussianHeight_le (B : ℕ) :
    Set.Finite {x : GaussianInt | gaussianHeight x ≤ B} := by
  let pairs : Set (ℤ × ℤ) :=
    Set.Icc (-(B : ℤ)) (B : ℤ) ×ˢ Set.Icc (-(B : ℤ)) (B : ℤ)
  let mkGaussian : ℤ × ℤ → GaussianInt := fun p => ⟨p.1, p.2⟩
  have hre : (Set.Icc (-(B : ℤ)) (B : ℤ)).Finite := Set.finite_Icc _ _
  have him : (Set.Icc (-(B : ℤ)) (B : ℤ)).Finite := Set.finite_Icc _ _
  have hpairs : pairs.Finite := by
    simpa [pairs] using hre.prod him
  have himage : (mkGaussian '' pairs).Finite := hpairs.image mkGaussian
  apply himage.subset
  intro x hx
  change gaussianHeight x ≤ B at hx
  have hreabs : x.re.natAbs ≤ B := le_trans (Nat.le_max_left _ _) hx
  have himabs : x.im.natAbs ≤ B := le_trans (Nat.le_max_right _ _) hx
  have hre2 : x.re * x.re ≤ (B : ℤ) * B := by
    apply (Int.natAbs_le_iff_mul_self_le).mp
    simpa using hreabs
  have him2 : x.im * x.im ≤ (B : ℤ) * B := by
    apply (Int.natAbs_le_iff_mul_self_le).mp
    simpa using himabs
  have hrelo : -(B : ℤ) ≤ x.re := by nlinarith
  have hrehi : x.re ≤ (B : ℤ) := by nlinarith
  have himlo : -(B : ℤ) ≤ x.im := by nlinarith
  have himhi : x.im ≤ (B : ℤ) := by nlinarith
  refine ⟨(x.re, x.im), ?_, ?_⟩
  · exact ⟨⟨hrelo, hrehi⟩, ⟨himlo, himhi⟩⟩
  · cases x
    rfl

/-- The carry state set of the generic fixed-multiplier machine is finite. -/
theorem fixedMultiplierCarrySet_finite (ms : List Digit) :
    Set.Finite {κ : GaussianInt | gaussianHeight κ ≤ fixedCarryBound ms.length} :=
  finite_gaussianHeight_le _

/-- P3-style full carry-window state set is finite for every fixed multiplier.
The window is represented as exactly J zero-padded slots, which is equivalent
to keeping the last J input positions with leading/trailing zero padding. -/
theorem fixedMultiplierFullStateSet_finite (ms : List Digit) :
    Set.Finite {s : GaussianInt × (Fin ms.length → Digit) |
      gaussianHeight s.1 ≤ fixedCarryBound ms.length} := by
  have hc := fixedMultiplierCarrySet_finite ms
  have hw : (Set.univ : Set (Fin ms.length → Digit)).Finite := Set.finite_univ
  exact (hc.prod hw).subset (by
    intro s hs
    exact ⟨hs, Set.mem_univ _⟩)

end CNRSArithmetic
