/-
Private-CI integration candidate: connect the governed v4 finite-left carrier
to the finite Laurent characterization of R_A proved in FiniteSupportRA.
SSC v4 remains authoritative and unchanged.
-/
import CnrsQ2.FiniteLeftIsometry
import CnrsQ2.FiniteSupportRA

open Zsqrtd

namespace CnrsQ2

def EventuallyZeroDigits (d : ℕ → Fin 5) : Prop :=
  ∃ N : ℕ, ∀ n : ℕ, N ≤ n → d n = 0

def FiniteLeftHasFiniteSupport : FiniteLeftDigitCarrier → Prop
  | .zero => True
  | .nonzero s => EventuallyZeroDigits s.digits

theorem partialSum_eq_of_eventually_zero
    {d : ℕ → Fin 5} {N : ℕ}
    (hzero : ∀ n : ℕ, N ≤ n → d n = 0) :
    ∀ M : ℕ, N ≤ M → partialSum d M = partialSum d N := by
  intro M hNM
  induction M, hNM using Nat.le_induction with
  | base => rfl
  | succ M hNM ih =>
      rw [partialSum, Finset.sum_range_succ, ← partialSum, ih, hzero M hNM]
      simp [digitP]

theorem digitStreamLimit_eq_partialSum_of_eventually_zero
    {d : ℕ → Fin 5} {N : ℕ}
    (hzero : ∀ n : ℕ, N ≤ n → d n = 0) :
    digitStreamLimit d = partialSum d N := by
  have heq : (fun M => partialSum d M) =ᶠ[Filter.atTop]
      (fun _ : ℕ => partialSum d N) := by
    exact Filter.eventually_atTop.2 ⟨N, fun M hNM =>
      partialSum_eq_of_eventually_zero hzero M hNM⟩
  have ht : Filter.Tendsto (partialSum d) Filter.atTop
      (nhds (partialSum d N)) :=
    tendsto_const_nhds.congr' heq.symm
  exact tendsto_nhds_unique (tendsto_partialSum_digitStreamLimit d) ht

def gaussianPartialSum (d : ℕ → Fin 5) (N : ℕ) : GaussianInt :=
  ∑ n ∈ Finset.range N, digit (d n) * beta ^ n

theorem toPadic_gaussianPartialSum (d : ℕ → Fin 5) (N : ℕ) :
    toPadic (gaussianPartialSum d N) = partialSum d N := by
  simp only [gaussianPartialSum, partialSum, map_sum, map_mul, map_pow,
    toPadic_digit, pi5]

theorem finiteLeft_finiteSupport_mem_fracToPadic_RA
    (c : FiniteLeftDigitCarrier) (hc : FiniteLeftHasFiniteSupport c) :
    ∃ x : GaussianFrac, x ∈ RAFrac ∧ finiteLeftEval c = fracToPadic x := by
  cases c with
  | zero =>
      refine ⟨0, ?_, ?_⟩
      · refine ⟨0, 0, ?_⟩
        simp [betaFrac]
      · simp [finiteLeftEval]
  | nonzero s =>
      rcases hc with ⟨N, hzero⟩
      let z : GaussianInt := gaussianPartialSum s.digits N
      have hlim : digitStreamLimit s.digits = toPadic z := by
        rw [digitStreamLimit_eq_partialSum_of_eventually_zero hzero]
        exact (toPadic_gaussianPartialSum s.digits N).symm
      by_cases hs : 0 ≤ s.shift
      · let n : ℕ := s.shift.toNat
        have hshift : s.shift = (n : ℤ) := by
          simpa [n] using (Int.toNat_of_nonneg hs).symm
        let x : GaussianFrac :=
          algebraMap GaussianInt GaussianFrac (beta ^ n * z)
        refine ⟨x, ?_, ?_⟩
        · refine ⟨beta ^ n * z, 0, ?_⟩
          simp [x, betaFrac]
        · rw [finiteLeftEval, hlim, hshift]
          simp [x, fracToPadic_algebraMap, toPadicField, pi5Q, pi5,
            map_mul, map_pow]
          rfl
      · have hsneg : s.shift < 0 := lt_of_not_ge hs
        let m : ℕ := (-s.shift).toNat
        have hm : s.shift = -(m : ℤ) := by
          have hnonneg : 0 ≤ -s.shift := le_of_lt (neg_pos.mpr hsneg)
          have hnat : ((-s.shift).toNat : ℤ) = -s.shift := Int.toNat_of_nonneg hnonneg
          simpa [m] using (congrArg Neg.neg hnat).symm
        let x : GaussianFrac :=
          algebraMap GaussianInt GaussianFrac z / betaFrac ^ m
        refine ⟨x, ?_, ?_⟩
        · exact ⟨z, m, rfl⟩
        · rw [finiteLeftEval, hlim, hm]
          simp [x, fracToPadic_algebraMap, toPadicField,
            betaFrac, pi5Q, pi5, zpow_neg, div_eq_mul_inv, mul_comm]
          rfl

def listDigits : List (Fin 5) → ℕ → Fin 5
  | [], _ => 0
  | d :: _, 0 => d
  | _ :: ds, n + 1 => listDigits ds n

theorem listDigits_zero_of_length_le (ds : List (Fin 5)) :
    ∀ n : ℕ, ds.length ≤ n → listDigits ds n = 0 := by
  induction ds with
  | nil => intro n hn; simp [listDigits]
  | cons d ds ih =>
      intro n hn
      cases n with
      | zero => simp at hn
      | succ n =>
          simp [listDigits]
          apply ih n
          have hs : Nat.succ ds.length ≤ Nat.succ n := by simpa using hn
          exact Nat.succ_le_succ_iff.mp hs

theorem listDigits_eventually_zero (ds : List (Fin 5)) :
    EventuallyZeroDigits (listDigits ds) :=
  ⟨ds.length, listDigits_zero_of_length_le ds⟩

noncomputable def evalPadicDigits : List (Fin 5) → ℤ_[5]
  | [] => 0
  | d :: ds => digitP d + pi5 * evalPadicDigits ds

theorem toPadic_evalGaussianDigits (ds : List (Fin 5)) :
    toPadic (evalGaussianDigits ds) = evalPadicDigits ds := by
  induction ds with
  | nil => simp [evalGaussianDigits, evalPadicDigits]
  | cons d ds ih =>
      simp [evalGaussianDigits, evalPadicDigits, toPadic_digit, pi5, ih]

theorem partialSum_listDigits_length (ds : List (Fin 5)) :
    partialSum (listDigits ds) ds.length = evalPadicDigits ds := by
  induction ds with
  | nil => simp [partialSum, evalPadicDigits, listDigits]
  | cons d ds ih =>
      rw [show (d :: ds).length = ds.length + 1 by simp]
      rw [partialSum, Finset.sum_range_succ']
      simp only [listDigits, pow_zero, mul_one]
      have htail :
          (∑ x ∈ Finset.range ds.length,
            digitP (listDigits ds x) * pi5 ^ (x + 1)) =
          pi5 * partialSum (listDigits ds) ds.length := by
        rw [partialSum, Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro x hx
        rw [pow_succ]
        ring
      rw [htail, ih]
      simp [evalPadicDigits, add_comm]

theorem digitStreamLimit_listDigits (ds : List (Fin 5)) :
    digitStreamLimit (listDigits ds) = toPadic (evalGaussianDigits ds) := by
  calc
    digitStreamLimit (listDigits ds)
        = partialSum (listDigits ds) ds.length :=
          digitStreamLimit_eq_partialSum_of_eventually_zero
            (listDigits_zero_of_length_le ds)
    _ = evalPadicDigits ds := partialSum_listDigits_length ds
    _ = toPadic (evalGaussianDigits ds) := (toPadic_evalGaussianDigits ds).symm

def finiteListCarrier : ℤ → List (Fin 5) → FiniteLeftDigitCarrier
  | _, [] => .zero
  | shift, d :: ds =>
      if h : d = 0 then
        finiteListCarrier (shift + 1) ds
      else
        .nonzero
          { shift := shift
            digits := listDigits (d :: ds)
            leading_ne_zero := by simpa [listDigits] using h }

theorem finiteListCarrier_finiteSupport (shift : ℤ) (ds : List (Fin 5)) :
    FiniteLeftHasFiniteSupport (finiteListCarrier shift ds) := by
  induction ds generalizing shift with
  | nil => simp [finiteListCarrier, FiniteLeftHasFiniteSupport]
  | cons d ds ih =>
      by_cases hd : d = 0
      · simpa [finiteListCarrier, hd] using ih (shift + 1)
      · simp only [finiteListCarrier, hd, dite_false]
        change EventuallyZeroDigits (listDigits (d :: ds))
        exact listDigits_eventually_zero (d :: ds)

theorem finiteLeftEval_finiteListCarrier (shift : ℤ) (ds : List (Fin 5)) :
    finiteLeftEval (finiteListCarrier shift ds) =
      pi5Q ^ shift * (toPadic (evalGaussianDigits ds) : ℚ_[5]) := by
  induction ds generalizing shift with
  | nil => simp [finiteListCarrier, finiteLeftEval, evalGaussianDigits]
  | cons d ds ih =>
      by_cases hd : d = 0
      · subst d
        have hcarrier : finiteListCarrier shift (0 :: ds) =
            finiteListCarrier (shift + 1) ds := by
          simp [finiteListCarrier]
        rw [hcarrier, ih (shift + 1)]
        change pi5Q ^ (shift + 1) * (toPadic (evalGaussianDigits ds) : ℚ_[5]) =
          pi5Q ^ shift * (toPadic (digit (0 : Fin 5) + beta * evalGaussianDigits ds) : ℚ_[5])
        have hd0 : digit (0 : Fin 5) = 0 := rfl
        rw [hd0, zero_add, map_mul]
        change pi5Q ^ (shift + 1) * (toPadic (evalGaussianDigits ds) : ℚ_[5]) =
          pi5Q ^ shift * (pi5Q * (toPadic (evalGaussianDigits ds) : ℚ_[5]))
        rw [zpow_add₀ pi5Q_ne_zero]
        simp [mul_assoc]
      · simp [finiteListCarrier, hd, finiteLeftEval,
          digitStreamLimit_listDigits]

theorem mem_RA_has_finiteLeft_finiteSupport
    {x : GaussianFrac} (hx : x ∈ RAFrac) :
    ∃ c : FiniteLeftDigitCarrier,
      FiniteLeftHasFiniteSupport c ∧ finiteLeftEval c = fracToPadic x := by
  obtain ⟨m, ds, hxrep⟩ := mem_RAFrac_has_finite_digits hx
  let c := finiteListCarrier (-(m : ℤ)) ds
  refine ⟨c, finiteListCarrier_finiteSupport (-(m : ℤ)) ds, ?_⟩
  rw [finiteLeftEval_finiteListCarrier]
  rw [hxrep]
  simp [evalFiniteLaurent, fracToPadic_algebraMap, toPadicField,
    betaFrac, pi5Q, pi5, zpow_neg, div_eq_mul_inv, mul_comm]
  rfl

theorem finiteLeft_finiteSupport_iff_fracToPadic_RA
    (c : FiniteLeftDigitCarrier) :
    FiniteLeftHasFiniteSupport c ↔
      ∃ x : GaussianFrac, x ∈ RAFrac ∧ finiteLeftEval c = fracToPadic x := by
  constructor
  · exact finiteLeft_finiteSupport_mem_fracToPadic_RA c
  · rintro ⟨x, hx, heval⟩
    obtain ⟨c', hc', heval'⟩ := mem_RA_has_finiteLeft_finiteSupport hx
    have hcc : c = c' := finiteLeftEval_injective (heval.trans heval'.symm)
    rw [hcc]
    exact hc'

end CnrsQ2
