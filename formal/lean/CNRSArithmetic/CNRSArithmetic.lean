/-
CNRSArithmetic — Phase F candidate: synchronous two-input multiplication impossibility.

Phases A--D and E2--E11 remain unchanged.  Phase D already proves exact
finite convolution plus normalization for arbitrary pairs of finite canonical
words, and finite-state realizability when the multiplier is fixed.

Phase F proves the complementary quantifier boundary: no single finite
deterministic synchronous LSD-first letter-to-letter Mealy machine computes the
canonical product stream for all pairs of finite inputs.  It does not extend
that impossibility result to asynchronous or variable-output machines,
multi-pass algorithms, unbounded memory, MSD-first online arithmetic with
delay, or redundant digit alphabets.

This project is independent of CnrsQ2, CNRSProblem1, and CNRSProblem2.
-/
import CNRSArithmetic.Base
import CNRSArithmetic.Digits
import CNRSArithmetic.AdditionStep
import CNRSArithmetic.AdditionCarrySet
import CNRSArithmetic.AdditionTransducer
import CNRSArithmetic.AdditionCorrectness
import CNRSArithmetic.Finiteness
import CNRSArithmetic.Normalization
import CNRSArithmetic.FixedMultiplier
import CNRSArithmetic.FixedMultiplierTransducer
import CNRSArithmetic.FixedMultiplierStep
import CNRSArithmetic.FixedMultiplierK2
import CNRSArithmetic.FixedMultiplierKi
import CNRSArithmetic.FixedMultiplierK3
import CNRSArithmetic.FixedMultiplierK4

import CNRSArithmetic.ExactDivisionRecurrence
import CNRSArithmetic.DivisionStateBounds
import CNRSArithmetic.DivisionOrbitPeriodicity
import CNRSArithmetic.DivisionTermination
import CNRSArithmetic.DivisionCycleClassification
import CNRSArithmetic.DivisionCycleEnumeration
import CNRSArithmetic.DivisionDecisionWitness
import CNRSArithmetic.DivisionMinimalPeriod
import CNRSArithmetic.DivisionCycleCatalogue
import CNRSArithmetic.DivisionOutcomeMachine
import CNRSArithmetic.DivisionOutcomeRepresentativeIntegrity

import CNRSArithmetic.OnlineMultiplicationImpossibility
