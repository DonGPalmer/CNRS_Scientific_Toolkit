/-
CNRSArithmetic Phase C: finite coefficient-string normalization.

This formalizes the P3 carry-normalization stage in a slightly stronger form:
inputs may be arbitrary finite Gaussian-integer coefficient strings, not only the
nonnegative convolution intermediates used by multiplication. The output is a
finite canonical CNRS-A digit word of exactly the same represented value.
-/
import CNRSArithmetic.Finiteness

namespace CNRSArithmetic

open Zsqrtd

/-- Value of an LSD-first finite Gaussian-integer coefficient string. -/
def coeffValue : List GaussianInt → GaussianInt
  | [] => 0
  | c :: cs => c + beta * coeffValue cs

/-- Process every supplied coefficient once, recording canonical digits and the final carry. -/
def normalizePrefix (κ : GaussianInt) : List GaussianInt → List Digit × GaussianInt
  | [] => ([], κ)
  | c :: cs =>
      let s := c + κ
      let r := normalizePrefix (nextCarryFromSum s) cs
      (residueIndex s :: r.1, r.2)

/-- Prefix normalization emits exactly one digit per supplied coefficient. -/
theorem normalizePrefix_output_length (κ : GaussianInt) (cs : List GaussianInt) :
    (normalizePrefix κ cs).1.length = cs.length := by
  induction cs generalizing κ with
  | nil => rfl
  | cons c cs ih =>
      simp [normalizePrefix, ih]

/-- Arithmetic invariant for the finite supplied-coefficient phase. -/
theorem normalizePrefix_invariant (κ : GaussianInt) (cs : List GaussianInt) :
    wordValue (normalizePrefix κ cs).1 +
        beta ^ cs.length * (normalizePrefix κ cs).2 =
      κ + coeffValue cs := by
  induction cs generalizing κ with
  | nil =>
      simp [normalizePrefix, wordValue, coeffValue]
  | cons c cs ih =>
      let s := c + κ
      let q := nextCarryFromSum s
      have hi := ih q
      have hs := selectedDigit_add_beta_mul_nextCarry s
      simp only [selectedDigit] at hs
      change
        digit (residueIndex s) + beta * wordValue (normalizePrefix q cs).1 +
            beta ^ (cs.length + 1) * (normalizePrefix q cs).2 =
          κ + (c + beta * coeffValue cs)
      rw [pow_succ]
      calc
        digit (residueIndex s) + beta * wordValue (normalizePrefix q cs).1 +
              (beta ^ cs.length * beta) * (normalizePrefix q cs).2
            = digit (residueIndex s) +
                beta * (wordValue (normalizePrefix q cs).1 +
                  beta ^ cs.length * (normalizePrefix q cs).2) := by ring
        _ = digit (residueIndex s) + beta * (q + coeffValue cs) := by rw [hi]
        _ = (digit (residueIndex s) + beta * q) + beta * coeffValue cs := by ring
        _ = s + beta * coeffValue cs := by rw [hs]
        _ = κ + (c + beta * coeffValue cs) := by
              dsimp [s]
              ring

/-- Value decomposition across concatenated canonical digit words. -/
theorem wordValue_append (xs ys : List Digit) :
    wordValue (xs ++ ys) = wordValue xs + beta ^ xs.length * wordValue ys := by
  induction xs with
  | nil => simp [wordValue]
  | cons d ds ih =>
      simp [wordValue, ih, pow_succ]
      ring

/-- Normalize an arbitrary finite Gaussian-integer coefficient string. -/
def normalizeCoefficients (cs : List GaussianInt) : List Digit :=
  let r := normalizePrefix 0 cs
  r.1 ++ greedyDigits r.2

/-- Phase C end-to-end theorem: normalization preserves represented value. -/
theorem normalizeCoefficients_correct (cs : List GaussianInt) :
    wordValue (normalizeCoefficients cs) = coeffValue cs := by
  let r := normalizePrefix 0 cs
  have hi := normalizePrefix_invariant 0 cs
  have hl := normalizePrefix_output_length 0 cs
  have hg := greedyDigits_correct r.2
  have ha := wordValue_append r.1 (greedyDigits r.2)
  change wordValue (r.1 ++ greedyDigits r.2) = coeffValue cs
  rw [ha, hg, hl]
  change wordValue r.1 + beta ^ cs.length * r.2 = coeffValue cs
  simpa using hi

/-- The residue selector fixes an already-canonical digit. -/
@[simp] theorem residueIndex_digit (d : Digit) : residueIndex (digit d) = d := by
  fin_cases d <;> native_decide

/-- An already-canonical digit produces zero outgoing carry. -/
@[simp] theorem nextCarryFromSum_digit (d : Digit) : nextCarryFromSum (digit d) = 0 := by
  fin_cases d <;> native_decide

/-- Prefix normalization is the identity on canonical digit words with zero initial carry. -/
theorem normalizePrefix_canonical (xs : List Digit) :
    normalizePrefix 0 (xs.map digit) = (xs, 0) := by
  induction xs with
  | nil => rfl
  | cons d ds ih =>
      simp [normalizePrefix, ih]

/-- Full normalization fixes an already-canonical finite digit word. -/
theorem normalizeCoefficients_canonical (xs : List Digit) :
    normalizeCoefficients (xs.map digit) = xs := by
  simp [normalizeCoefficients, normalizePrefix_canonical, CNRSCore.greedyDigits]

/-- Normalization is idempotent after re-embedding its canonical output as coefficients. -/
theorem normalizeCoefficients_idempotent (cs : List GaussianInt) :
    normalizeCoefficients ((normalizeCoefficients cs).map digit) = normalizeCoefficients cs := by
  exact normalizeCoefficients_canonical (normalizeCoefficients cs)

/-- P3's nonnegative convolution intermediates are a direct specialization. -/
def natCoefficient (n : ℕ) : GaussianInt := ⟨(n : ℤ), 0⟩

def natCoeffValue : List ℕ → GaussianInt
  | [] => 0
  | n :: ns => natCoefficient n + beta * natCoeffValue ns

/-- General coefficient value agrees with the P3 nonnegative specialization. -/
theorem coeffValue_nat_map (ns : List ℕ) :
    coeffValue (ns.map natCoefficient) = natCoeffValue ns := by
  induction ns with
  | nil => rfl
  | cons n ns ih => simp [coeffValue, natCoeffValue, ih]

/-- P3 carry-normalization theorem for finite nonnegative intermediate strings. -/
theorem normalize_nat_coefficients_correct (ns : List ℕ) :
    wordValue (normalizeCoefficients (ns.map natCoefficient)) = natCoeffValue ns := by
  rw [normalizeCoefficients_correct, coeffValue_nat_map]

end CNRSArithmetic
