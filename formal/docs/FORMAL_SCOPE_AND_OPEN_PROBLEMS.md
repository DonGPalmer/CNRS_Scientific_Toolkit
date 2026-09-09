# Formal Scope and Open Problems

Status date: 2026-09-09

## Lean-verified scope

The governed Lean programme verifies selected exact statements concerning:

- Gaussian integers and the base `-2+i`;
- the five-digit residue system;
- beta-adic completion and unique digit expansion;
- finite exact arithmetic and division recurrences;
- bounded-state periodicity and cycle/representative results;
- finite-state multiplication boundaries;
- finite representations, termination, periodicity, and stated special bases;
- lifted logarithmic coordinates and explicit integer branch metadata;
- canonical and fail-closed serialization;
- finite Laurent coefficients over `ℤ[i][(-2+i)⁻¹]`;
- finite-support Hurwitz algebra and differentiation;
- branch-labelled, equal-branch partial arithmetic;
- branch transport, relative-branch invariance, and pair-orbit normal forms.

## Conditional or deliberately restricted results

- Quadratic-lattice periodicity uses explicit boundedness and algebraic hypotheses.
- Hurwitz algebra results concern finite support, not arbitrary infinite streams.
- P2 arithmetic is deliberately partial on branch-labelled states.
- P2 transport changes explicit branch metadata; it does not reconstruct a winding path.
- The finite Laurent carrier is a specific subring of the Gaussian fraction field, not all complex numbers.
- Q2 convergence is beta-adic, not ordinary complex analytic convergence.

## Computationally tested but not end-to-end formally verified

- the independent Python implementations of CNRS arithmetic and normalization;
- CNRS-float and interoperability layers;
- finite numerical or symbolic CNRS-H routines beyond the exact Lean overlap;
- ODE, PDE, oscillator, biological-profile, and other scientific examples;
- finite-cover and algebraic-curve helpers outside the precise P2 pair-state theorems.

## Open mathematical and formalization work

### Bounded completion programme

- P2 compatibility bridge to `BranchPoint` and canonical lifted coordinates;
- integrated P2 codec/API capstone;
- cross-problem compatibility theorems;
- consolidated Lean workspace and release certification.

### Research-risk extensions

- arbitrary infinite CNRS-H series and their algebra;
- ordinary complex analytic realization, convergence, and error control;
- analytic continuation and reconstruction of path/winding information;
- general streaming division;
- executable digit-by-digit or finite-state Hurwitz convolution;
- a complete concrete codec for every intended CNRS-A value string;
- a canonical representation of every ordinary complex value under one global convention;
- the bounded-digit complex-base-`e` theorem;
- automatic compact Riemann-surface construction, singular normalization, and certified continuation;
- first-principles derivation of the CNRS–Scale Space bridge;
- empirical necessity or scientific advantage over standard complex representations.

## Completion criterion

The bounded Lean campaign can be declared complete when the compatibility bridge, integrated capstone, cross-problem agreement, consolidated build, frozen declaration inventory, and reproducible authoritative artifact all pass independent audit. Research-risk extensions should remain separately labelled and should not block that bounded completion.
