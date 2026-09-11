/-
CNRS Q2 formalization — finite Gaussian CNS theorem for beta = -2+i.
Promoted from private CI after pinned/no-network verification.
-/
import CnrsQ2.DigitAlphabet
import CNRSCore.QuotientStep
import CNRSCore.FiniteWords
import Mathlib.Tactic

open Zsqrtd

namespace CnrsQ2

abbrev gaussianDigit : GaussianInt -> Fin 5 := CNRSCore.residueIndex

lemma phi_digit_gaussianDigit (z : GaussianInt) :
    phi (digit (gaussianDigit z)) = phi z := by
  simpa [gaussianDigit, digit, phi, CNRSCore.selectedDigit] using CNRSCore.phi_selectedDigit z

lemma phi_sub (x y : GaussianInt) : phi (x - y) = phi x - phi y := by
  simp only [phi, CNRSCore.phi, Zsqrtd.re_sub, Zsqrtd.im_sub]
  push_cast
  ring

def betaQuotient (w : GaussianInt) : GaussianInt :=
  let t : ℤ := (w.re + 2 * w.im) / 5
  ⟨w.im - 2 * t, -t⟩

theorem beta_mul_betaQuotient_of_phi_eq_zero
    (w : GaussianInt) (hphi : phi w = 0) :
    beta * betaQuotient w = w := by
  have hmod : (((w.re + 2 * w.im : ℤ) : ZMod 5)) = 0 := by
    simpa [phi, CNRSCore.phi] using hphi
  have h5 : (5 : ℤ) ∣ w.re + 2 * w.im := by
    exact (ZMod.intCast_zmod_eq_zero_iff_dvd (w.re + 2 * w.im) 5).mp hmod
  have ht : 5 * ((w.re + 2 * w.im) / 5) = w.re + 2 * w.im := by
    simpa [mul_comm] using (Int.ediv_mul_cancel h5)
  ext <;> simp [beta, betaQuotient] <;> nlinarith [ht]

theorem beta_dvd_iff_phi_eq_zero (w : GaussianInt) : beta ∣ w ↔ phi w = 0 := by
  constructor
  · rintro ⟨q, rfl⟩
    rw [phi_mul, phi_beta, zero_mul]
  · intro hphi
    refine ⟨betaQuotient w, ?_⟩
    exact (beta_mul_betaQuotient_of_phi_eq_zero w hphi).symm

theorem beta_dvd_sub_digit_gaussianDigit (z : GaussianInt) :
    beta ∣ z - digit (gaussianDigit z) := by
  apply (beta_dvd_iff_phi_eq_zero (z - digit (gaussianDigit z))).2
  rw [phi_sub, phi_digit_gaussianDigit, sub_self]

abbrev gaussianNext : GaussianInt -> GaussianInt := CNRSCore.nextQuotient

theorem gaussian_step_sub_spec (z : GaussianInt) :
    z - digit (gaussianDigit z) = beta * gaussianNext z := by
  change z - CNRSCore.selectedDigit z = CNRSCore.beta * CNRSCore.nextQuotient z
  have h := CNRSCore.selectedDigit_add_beta_mul_nextQuotient z
  calc
    z - CNRSCore.selectedDigit z =
        (CNRSCore.selectedDigit z + CNRSCore.beta * CNRSCore.nextQuotient z) - CNRSCore.selectedDigit z := by rw [h]
    _ = CNRSCore.beta * CNRSCore.nextQuotient z := by abel

theorem gaussian_step_spec (z : GaussianInt) :
    z = digit (gaussianDigit z) + beta * gaussianNext z := by
  change z = CNRSCore.selectedDigit z + CNRSCore.beta * CNRSCore.nextQuotient z
  exact (CNRSCore.selectedDigit_add_beta_mul_nextQuotient z).symm

theorem norm_sub_digit_lt_five_mul_norm_of_norm_ge_eleven
    (z : GaussianInt) (k : Fin 5) (h : (11 : ℤ) ≤ z.norm) :
    (z - digit k).norm < 5 * z.norm := by
  fin_cases k <;>
    simp [Zsqrtd.norm, digit, CNRSCore.digit] at h ⊢ <;>
    nlinarith [sq_nonneg (z.re + 1), sq_nonneg (z.re + 2),
      sq_nonneg z.re, sq_nonneg z.im]

theorem gaussianNext_norm_lt_of_norm_ge_eleven
    (z : GaussianInt) (h : (11 : ℤ) ≤ z.norm) :
    (gaussianNext z).norm < z.norm := by
  have hd := norm_sub_digit_lt_five_mul_norm_of_norm_ge_eleven
    z (gaussianDigit z) h
  rw [gaussian_step_sub_spec, Zsqrtd.norm_mul, norm_beta] at hd
  nlinarith

def gaussianIterate : ℕ → GaussianInt → GaussianInt
  | 0, z => z
  | n + 1, z => gaussianIterate n (gaussianNext z)

theorem gaussianIterate_five_eq_zero_of_norm_lt_eleven
    (z : GaussianInt) (h : z.norm < 11) :
    gaussianIterate 5 z = 0 := by
  rcases z with ⟨a, b⟩
  simp [Zsqrtd.norm] at h
  have ha_lo : -4 < a := by nlinarith [sq_nonneg b]
  have ha_hi : a < 4 := by nlinarith [sq_nonneg b]
  have hb_lo : -4 < b := by nlinarith [sq_nonneg a]
  have hb_hi : b < 4 := by nlinarith [sq_nonneg a]
  interval_cases a <;> interval_cases b <;> norm_num at h
  all_goals native_decide

theorem gaussian_eventually_zero (z : GaussianInt) :
    ∃ n : ℕ, gaussianIterate n z = 0 := by
  apply (measure (Int.natAbs ∘ Zsqrtd.norm)).wf.induction z
  intro z ih
  by_cases hs : z.norm < 11
  · exact ⟨5, gaussianIterate_five_eq_zero_of_norm_lt_eleven z hs⟩
  · have hge : (11 : ℤ) ≤ z.norm := by omega
    have hlt := gaussianNext_norm_lt_of_norm_ge_eleven z hge
    have hnat : (gaussianNext z).norm.natAbs < z.norm.natAbs := by
      exact Int.ofNat_lt.1 <| by simp [hlt]
    obtain ⟨n, hn⟩ := ih (gaussianNext z) hnat
    refine ⟨n + 1, ?_⟩
    simpa [gaussianIterate] using hn

abbrev evalGaussianDigits : List (Fin 5) -> GaussianInt := CNRSCore.wordValue

def gaussianDigitsN : ℕ → GaussianInt → List (Fin 5)
  | 0, _ => []
  | n + 1, z => gaussianDigit z :: gaussianDigitsN n (gaussianNext z)

theorem eval_gaussianDigitsN_of_iterate_eq_zero
    (n : ℕ) (z : GaussianInt) (h : gaussianIterate n z = 0) :
    evalGaussianDigits (gaussianDigitsN n z) = z := by
  induction n generalizing z with
  | zero =>
      simpa [gaussianIterate, gaussianDigitsN, evalGaussianDigits, CNRSCore.wordValue] using h.symm
  | succ n ih =>
      have htail : gaussianIterate n (gaussianNext z) = 0 := by
        simpa [gaussianIterate] using h
      have heval := ih (gaussianNext z) htail
      simpa [gaussianDigitsN, evalGaussianDigits, CNRSCore.wordValue, heval] using (gaussian_step_spec z).symm

theorem gaussian_finite_expansion (z : GaussianInt) :
    ∃ ds : List (Fin 5), evalGaussianDigits ds = z := by
  obtain ⟨n, hn⟩ := gaussian_eventually_zero z
  exact ⟨gaussianDigitsN n z, eval_gaussianDigitsN_of_iterate_eq_zero n z hn⟩

end CnrsQ2
