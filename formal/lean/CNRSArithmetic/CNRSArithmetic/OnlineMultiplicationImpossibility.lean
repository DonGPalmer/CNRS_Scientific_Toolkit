/-
CNRSArithmetic Phase F: synchronous two-input multiplication impossibility.

Phase D already proves exact finite convolution followed by normalization for
two arbitrary finite canonical words, and proves finite-state bounds when one
multiplier is fixed.  This module proves the complementary boundary: no one
finite deterministic synchronous LSD-first letter-to-letter Mealy machine can
produce the canonical product stream for every pair of finite inputs.

The result is deliberately limited to this synchronous model.  It makes no
claim about asynchronous or variable-output transducers, multi-pass methods,
unbounded working memory, MSD-first online arithmetic with delay, or redundant
digit alphabets.
-/
import CNRSArithmetic.FixedMultiplier
import Mathlib.Data.Fintype.Pigeonhole
import Mathlib.Tactic

namespace CNRSArithmetic

open Zsqrtd

/-! ## Canonical finite words and zero padding -/

/-- The first digit of a word, with the empty word interpreted as zero. -/
def wordHead : List Digit → Digit
  | [] => 0
  | d :: _ => d

/-- The tail of a word, with the empty word fixed at the empty word. -/
def wordTail : List Digit → List Digit
  | [] => []
  | _ :: ds => ds

/-- Uniform head-tail decomposition, including the empty word. -/
theorem wordValue_head_tail (xs : List Digit) :
    wordValue xs = digit (wordHead xs) + beta * wordValue (wordTail xs) := by
  cases xs <;> simp [wordHead, wordTail, wordValue]

/-- Equal represented values have equal first canonical digits. -/
theorem wordHead_eq_of_wordValue_eq {xs ys : List Digit}
    (h : wordValue xs = wordValue ys) : wordHead xs = wordHead ys := by
  have hdecomp :
      digit (wordHead xs) + beta * wordValue (wordTail xs) =
        digit (wordHead ys) + beta * wordValue (wordTail ys) := by
    rw [← wordValue_head_tail xs, ← wordValue_head_tail ys]
    exact h
  have hphi := congrArg phi hdecomp
  apply digit_bijective.injective
  simpa [phi_add, phi_mul, phi_beta] using hphi

/-- Removing equal first canonical digits preserves equality of the remaining values. -/
theorem wordValue_tail_eq_of_wordValue_eq {xs ys : List Digit}
    (h : wordValue xs = wordValue ys) :
    wordValue (wordTail xs) = wordValue (wordTail ys) := by
  have hhead := wordHead_eq_of_wordValue_eq h
  have hdecomp :
      digit (wordHead xs) + beta * wordValue (wordTail xs) =
        digit (wordHead ys) + beta * wordValue (wordTail ys) := by
    rw [← wordValue_head_tail xs, ← wordValue_head_tail ys]
    exact h
  rw [hhead] at hdecomp
  have hmul : beta * wordValue (wordTail xs) =
      beta * wordValue (wordTail ys) := add_left_cancel hdecomp
  exact mul_left_cancel₀ prime_beta.ne_zero hmul

/-- A finite LSD-first word extended forever by high-order zero digits. -/
def padWord (xs : List Digit) : ℕ → Digit
  | 0 => wordHead xs
  | n + 1 => padWord (wordTail xs) n

/-- Equal finite canonical values have the same zero-padded digit stream. -/
theorem padWord_eq_of_wordValue_eq {xs ys : List Digit}
    (h : wordValue xs = wordValue ys) : padWord xs = padWord ys := by
  funext n
  induction n generalizing xs ys with
  | zero =>
      simpa [padWord] using wordHead_eq_of_wordValue_eq h
  | succ n ih =>
      simp only [padWord]
      exact ih (wordValue_tail_eq_of_wordValue_eq h)

/-- The constructive greedy representative has the original padded stream. -/
theorem padWord_greedyDigits_wordValue (xs : List Digit) :
    padWord (greedyDigits (wordValue xs)) = padWord xs := by
  apply padWord_eq_of_wordValue_eq
  exact greedyDigits_correct _

/-- Canonical evaluation is injective when the word length is fixed. -/
theorem wordValue_injective_of_length_eq {xs ys : List Digit}
    (hlen : xs.length = ys.length) (hval : wordValue xs = wordValue ys) : xs = ys := by
  induction xs generalizing ys with
  | nil =>
      symm
      exact List.eq_nil_of_length_eq_zero hlen.symm
  | cons x xs ih =>
      cases ys with
      | nil => simp at hlen
      | cons y ys =>
          have hxy : x = y := by
            have hphi := congrArg phi hval
            apply digit_bijective.injective
            simpa [wordValue, phi_add, phi_mul, phi_beta] using hphi
          subst y
          have htail : wordValue xs = wordValue ys := by
            have hmul : beta * wordValue xs = beta * wordValue ys :=
              add_left_cancel hval
            exact mul_left_cancel₀ prime_beta.ne_zero hmul
          have hlen' : xs.length = ys.length := by simpa using hlen
          exact congrArg (List.cons x) (ih hlen' htail)

/-- A finite string of zero digits represents zero. -/
@[simp] theorem wordValue_replicate_zero (N : ℕ) :
    wordValue (List.replicate N (0 : Digit)) = 0 := by
  induction N with
  | zero => rfl
  | succ N ih => simp [List.replicate_succ, wordValue, ih]

/-- Prefixing `N` LSD-first zeros multiplies the represented value by `beta^N`. -/
theorem shiftWordValue (N : ℕ) (xs : List Digit) :
    wordValue (List.replicate N (0 : Digit) ++ xs) = beta ^ N * wordValue xs := by
  rw [wordValue_append]
  simp [wordValue]

/-- Length-`N` canonical words, represented without list-padding ambiguity. -/
abbrev FixedWord (N : ℕ) := Fin N → Digit

/-- There are exactly `5^N` canonical words of length `N`. -/
theorem fixedWord_card (N : ℕ) : Fintype.card (FixedWord N) = 5 ^ N := by
  simp [FixedWord, Digit]

/-- Convert a fixed-length word to its LSD-first list. -/
def fixedWordList {N : ℕ} (A : FixedWord N) : List Digit := List.ofFn A

@[simp] theorem fixedWordList_length {N : ℕ} (A : FixedWord N) :
    (fixedWordList A).length = N := by
  simp [fixedWordList]

/-- Past the end of a finite word, its padded stream is zero. -/
theorem padWord_eq_zero_of_length_le (xs : List Digit) {n : ℕ}
    (h : xs.length ≤ n) : padWord xs n = 0 := by
  induction xs generalizing n with
  | nil =>
      induction n with
      | zero => rfl
      | succ n ih => simpa [padWord, wordTail] using ih
  | cons d ds ih =>
      cases n with
      | zero => simp at h
      | succ n =>
          simp only [padWord, wordTail]
          apply ih
          simpa using h

/-- Padding commutes with moving across a finite prefix. -/
theorem padWord_append_length (xs ys : List Digit) (n : ℕ) :
    padWord (xs ++ ys) (xs.length + n) = padWord ys n := by
  induction xs with
  | nil => simp
  | cons d ds ih =>
      rw [List.length_cons, Nat.succ_add]
      simp only [List.cons_append, padWord, wordTail]
      exact ih

/-- Reading a fixed word inside its range returns the corresponding digit. -/
theorem padWord_fixedWordList {N : ℕ} (A : FixedWord N) (j : Fin N) :
    padWord (fixedWordList A) j = A j := by
  change padWord (List.ofFn A) j.val = A j
  induction N with
  | zero => exact Fin.elim0 j
  | succ N ih =>
      rw [List.ofFn_succ]
      cases j using Fin.cases with
      | zero => rfl
      | succ j =>
          simpa [padWord, wordTail] using ih (fun k => A k.succ) j

/-! ## The synchronous deterministic machine -/

/-- Deterministic synchronous letter-to-letter two-input Mealy machine. -/
structure SynchronousMealy (State : Type) where
  step : State → (Digit × Digit) → State × Digit

namespace SynchronousMealy

variable {State : Type} (M : SynchronousMealy State)

/-- Final state after a finite list of paired input letters. -/
def runState : State → List (Digit × Digit) → State
  | q, [] => q
  | q, a :: as => runState (M.step q a).1 as

/-- Output word from a finite list of paired input letters. -/
def runOutput : State → List (Digit × Digit) → List Digit
  | _, [] => []
  | q, a :: as => (M.step q a).2 :: runOutput (M.step q a).1 as

/-- Combined finite run interface. -/
def run (q : State) (input : List (Digit × Digit)) : State × List Digit :=
  (M.runState q input, M.runOutput q input)

/-- Finite execution splits across concatenated inputs. -/
theorem runState_append (q : State) (xs ys : List (Digit × Digit)) :
    M.runState q (xs ++ ys) = M.runState (M.runState q xs) ys := by
  induction xs generalizing q with
  | nil => rfl
  | cons a as ih => simp [runState, ih]

/-- Finite output splits across concatenated inputs. -/
theorem runOutput_append (q : State) (xs ys : List (Digit × Digit)) :
    M.runOutput q (xs ++ ys) =
      M.runOutput q xs ++ M.runOutput (M.runState q xs) ys := by
  induction xs generalizing q with
  | nil => rfl
  | cons a as ih => simp [runOutput, runState, ih]

/-- Finite execution splits across concatenated inputs. -/
theorem run_append (q : State) (xs ys : List (Digit × Digit)) :
    M.run q (xs ++ ys) =
      (M.runState (M.runState q xs) ys,
        M.runOutput q xs ++ M.runOutput (M.runState q xs) ys) := by
  simp [run, runState_append, runOutput_append]

/-- A letter-to-letter run emits exactly one output per input pair. -/
theorem runOutput_length (q : State) (xs : List (Digit × Digit)) :
    (M.runOutput q xs).length = xs.length := by
  induction xs generalizing q with
  | nil => rfl
  | cons a as ih => simp [runOutput, ih]

/-- Machine state before the input letter at position `n`. -/
def stateStream (q : State) (xs ys : ℕ → Digit) : ℕ → State
  | 0 => q
  | n + 1 => (M.step (stateStream q xs ys n) (xs n, ys n)).1

/-- The unique synchronous output digit at each position. -/
def outputStream (q : State) (xs ys : ℕ → Digit) (n : ℕ) : Digit :=
  (M.step (M.stateStream q xs ys n) (xs n, ys n)).2

/-- A streamed run at `N+j` is the suffix run started from the state at `N`. -/
theorem stateStream_add (q : State) (xs ys : ℕ → Digit) (N j : ℕ) :
    M.stateStream q xs ys (N + j) =
      M.stateStream (M.stateStream q xs ys N)
        (fun k => xs (N + k)) (fun k => ys (N + k)) j := by
  induction j with
  | zero => simp [stateStream]
  | succ j ih =>
      rw [Nat.add_succ]
      simp only [stateStream]
      convert congrArg (fun s => (M.step s (xs (N + j), ys (N + j))).1) ih using 1

/-- The corresponding suffix law for streamed outputs. -/
theorem outputStream_add (q : State) (xs ys : ℕ → Digit) (N j : ℕ) :
    M.outputStream q xs ys (N + j) =
      M.outputStream (M.stateStream q xs ys N)
        (fun k => xs (N + k)) (fun k => ys (N + k)) j := by
  simp [outputStream, stateStream_add]

/-- Equal intermediate states and equal suffix inputs force equal suffix outputs. -/
theorem same_suffix_of_same_state
    (q : State) (xs ys xs' ys' : ℕ → Digit) (N : ℕ)
    (hq : M.stateStream q xs ys N = M.stateStream q xs' ys' N)
    (hx : ∀ j, xs (N + j) = xs' (N + j))
    (hy : ∀ j, ys (N + j) = ys' (N + j)) :
    ∀ j, M.outputStream q xs ys (N + j) =
      M.outputStream q xs' ys' (N + j) := by
  intro j
  rw [M.outputStream_add, M.outputStream_add, hq]
  congr 2 <;> funext k
  · exact hx k
  · exact hy k

/-! ## The collision family -/

/-- One at position `N`, with zeros at every other position. -/
def shiftInputStream (N : ℕ) : ℕ → Digit :=
  padWord (List.replicate N (0 : Digit) ++ [1])

/-- A fixed word shifted upward by exactly `N` digit positions. -/
def shiftedWordStream {N : ℕ} (A : FixedWord N) : ℕ → Digit :=
  padWord (List.replicate N (0 : Digit) ++ fixedWordList A)

/-- The input stream associated to a fixed-length word. -/
def fixedWordStream {N : ℕ} (A : FixedWord N) : ℕ → Digit :=
  padWord (fixedWordList A)

/-- At offset `j<N`, the shifted output stream contains digit `A j`. -/
theorem shiftedWordStream_at {N : ℕ} (A : FixedWord N) (j : Fin N) :
    shiftedWordStream A (N + j) = A j := by
  calc
    shiftedWordStream A (N + j) = padWord (fixedWordList A) j := by
      simpa [shiftedWordStream] using
        padWord_append_length (List.replicate N (0 : Digit))
          (fixedWordList A) (j : ℕ)
    _ = A j := padWord_fixedWordList A j

/-- After its first `N` positions, a fixed word supplies only zero padding. -/
theorem fixedWordStream_suffix_zero {N : ℕ} (A : FixedWord N) (j : ℕ) :
    fixedWordStream A (N + j) = 0 := by
  apply padWord_eq_zero_of_length_le
  simp

/-- State reached after the common-length prefix used in the collision proof. -/
def shiftPrefixState (q : State) {N : ℕ} (A : FixedWord N) : State :=
  M.stateStream q (fixedWordStream A) (shiftInputStream N) N

/-- Correctness merely on the shift-product family used by the lower bound. -/
def ComputesShiftProducts (q : State) : Prop :=
  ∀ (N : ℕ), 1 ≤ N → ∀ A : FixedWord N,
    M.outputStream q (fixedWordStream A) (shiftInputStream N) = shiftedWordStream A

/-- The canonical zero-padded product stream for two finite inputs. -/
def canonicalProductStream (xs ys : List Digit) : ℕ → Digit :=
  padWord (greedyDigits (wordValue xs * wordValue ys))

/-- Full synchronous correctness for all finite input words. -/
def ComputesAllFiniteProducts (q : State) : Prop :=
  ∀ xs ys : List Digit,
    M.outputStream q (padWord xs) (padWord ys) = canonicalProductStream xs ys

/-- Every pointed finite state type admits a word length with more words than states. -/
theorem exists_word_length_exceeding_state_card [Fintype State] (q : State) :
    ∃ N : ℕ, 1 ≤ N ∧ Fintype.card State < 5 ^ N := by
  refine ⟨Fintype.card State, Fintype.card_pos_iff.mpr ⟨q⟩, ?_⟩
  exact Nat.lt_pow_self (by norm_num : 1 < 5)

/-- More fixed words than states force two distinct common-length prefixes to collide. -/
theorem shift_prefix_state_collision [Fintype State]
    (q : State) (N : ℕ) (hcard : Fintype.card State < 5 ^ N) :
    ∃ A B : FixedWord N, A ≠ B ∧ M.shiftPrefixState q A = M.shiftPrefixState q B := by
  apply Fintype.exists_ne_map_eq_of_card_lt (fun A : FixedWord N => M.shiftPrefixState q A)
  simpa [fixedWord_card] using hcard

/-- No finite deterministic synchronous machine computes even all shift products. -/
theorem no_synchronousMealy_computesShiftProducts [Fintype State]
    (q : State) : ¬ M.ComputesShiftProducts q := by
  intro hcompute
  obtain ⟨N, hN, hcard⟩ := exists_word_length_exceeding_state_card (State := State) q
  obtain ⟨A, B, hAB, hstate⟩ := M.shift_prefix_state_collision q N hcard
  have hsuffix : ∀ j,
      M.outputStream q (fixedWordStream A) (shiftInputStream N) (N + j) =
      M.outputStream q (fixedWordStream B) (shiftInputStream N) (N + j) := by
    apply M.same_suffix_of_same_state q
        (fixedWordStream A) (shiftInputStream N)
        (fixedWordStream B) (shiftInputStream N) N hstate
    · intro j
      rw [fixedWordStream_suffix_zero, fixedWordStream_suffix_zero]
    · intro j
      rfl
  have hfun : A = B := by
    funext j
    have ha := congrFun (hcompute N hN A) (N + (j : ℕ))
    have hb := congrFun (hcompute N hN B) (N + (j : ℕ))
    have hs := hsuffix (j : ℕ)
    rw [shiftedWordStream_at] at ha hb
    exact ha.symm.trans (hs.trans hb)
  exact hAB hfun

/-! ## From full product correctness to the collision family -/

/-- The shift input word represents exactly `beta^N`. -/
theorem wordValue_shift_input (N : ℕ) :
    wordValue (List.replicate N (0 : Digit) ++ [1]) = beta ^ N := by
  rw [shiftWordValue]
  simp [wordValue]

/-- Multiplying a fixed word by the shift word has the shifted-word value. -/
theorem wordValue_fixed_mul_shift {N : ℕ} (A : FixedWord N) :
    wordValue (fixedWordList A) *
        wordValue (List.replicate N (0 : Digit) ++ [1]) =
      wordValue (List.replicate N (0 : Digit) ++ fixedWordList A) := by
  rw [wordValue_shift_input, shiftWordValue]
  ring

/-- Full finite-product stream correctness includes the special collision family. -/
theorem computesAllFiniteProducts_implies_computesShiftProducts
    (q : State) (h : M.ComputesAllFiniteProducts q) : M.ComputesShiftProducts q := by
  intro N hN A
  rw [fixedWordStream, shiftInputStream, shiftedWordStream]
  rw [h (fixedWordList A) (List.replicate N (0 : Digit) ++ [1])]
  unfold canonicalProductStream
  apply padWord_eq_of_wordValue_eq
  rw [greedyDigits_correct]
  exact wordValue_fixed_mul_shift A

/-- No finite synchronous letter-to-letter machine computes every finite product stream. -/
theorem no_synchronousMealy_computesAllFiniteProducts [Fintype State]
    (q : State) : ¬ M.ComputesAllFiniteProducts q := by
  intro h
  exact M.no_synchronousMealy_computesShiftProducts q
    (M.computesAllFiniteProducts_implies_computesShiftProducts q h)

end SynchronousMealy

end CNRSArithmetic
