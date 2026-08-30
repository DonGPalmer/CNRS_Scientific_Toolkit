/-
CNRS Q2 formalization — umbrella file. ALL PHASES COMPLETE, zero sorries.
  Basic:      β = -2+i prime in ℤ[i], N(β) = 5
  HenselRoot: √(-1) ∈ ℤ_[5] via Hensel's lemma, ≡ 2 mod 5
  Embedding:  φ : ℤ[i] →+* ℤ_[5] injective, ‖φ(β)‖ = 1/5
  Density:    φ dense; capstone: ℤ_[5] is the β-adic completion of ℤ[i]
  FieldLevel: ψ : Frac(ℤ[i]) →+* ℚ_[5] injective, dense, ‖ψ(β)‖ = 1/5
              — K_β ≅ ℚ_5 in concrete form (Q2a)
  DigitExpansion: Phase 4, COMPLETE. Milestones 4a/4b (one-step digit
              residue/reduction) plus the full infinite-expansion assembly
              (exists_unique_digit_expansion): every x : ℤ_[5] has a UNIQUE
              digit sequence whose partial sums converge to it
              (thm:q2_digit_carrier(ii)/(iii)). Zero sorries, verified via
              #print axioms and a full clean rebuild from scratch.
-/
import CnrsQ2.Basic
import CnrsQ2.DigitAlphabet
import CnrsQ2.HenselRoot
import CnrsQ2.Embedding
import CnrsQ2.Density
import CnrsQ2.FieldLevel
import CnrsQ2.DigitExpansion
