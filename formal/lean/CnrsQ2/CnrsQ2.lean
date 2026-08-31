/-
CNRS Q2 formalization — umbrella file.
  Basic:      β = -2+i prime in ℤ[i], N(β) = 5
  HenselRoot: √(-1) ∈ ℤ_[5] via Hensel's lemma, ≡ 2 mod 5
  Embedding:  φ : ℤ[i] →+* ℤ_[5] injective, ‖φ(β)‖ = 1/5
  Density:    dense β-place embedding into ℤ_[5]
  FieldLevel: ψ : Frac(ℤ[i]) →+* ℚ_[5] injective, dense, ‖ψ(β)‖ = 1/5
  DigitExpansion: valuation-ring Q2b(ii): every x : ℤ_[5] has a unique
              canonical β-adic digit sequence converging to x.
  FieldDigitExpansion: Q2b(iii) extension: every nonzero x : ℚ_[5] is
              normalized at its exact p-adic valuation, expanded uniquely
              in the same digits, then scaled back; the leading digit is
              nonzero, so only finitely many negative-index digits occur.
  DigitIsometry: Q2b(iv) metric core: the norm is determined exactly by the
              first differing canonical digit, with the corresponding
              integer-shifted field formula.
  FiniteLeftCarrier: certified normalized finite-left carrier, bijective
              evaluation map onto ℚ_[5], and fixed-valuation-stratum
              first-difference isometry.

Removing convergence certificates from the raw syntax and the finite-support
= R_A converse remain separate later targets.
-/
import CnrsQ2.Basic
import CnrsQ2.DigitAlphabet
import CnrsQ2.HenselRoot
import CnrsQ2.Embedding
import CnrsQ2.Density
import CnrsQ2.FieldLevel
import CnrsQ2.DigitExpansion
import CnrsQ2.FieldDigitExpansion

import CnrsQ2.DigitIsometry
import CnrsQ2.FiniteLeftCarrier
