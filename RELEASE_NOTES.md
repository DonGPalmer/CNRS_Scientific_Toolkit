# v0.12.1 — Algebraic-Curve Branch Detection and P4 Documentation Synchronization

See `RELEASE_NOTES_v0.12.1.md`. Adds polynomial algebraic-curve intake and finite branch-point detection, synchronizes current documentation with the canonical Problem 4 Version 12 record, updates citation metadata to v0.12.1, and records the validated baseline of `1206 passed, 0 failed`.

# v0.12.0 — Finite Global Riemann-Surface Layer

See `RELEASE_NOTES_v0.12.0.md`. Adds finite sheets, ordered path words, noncommuting monodromy permutations, lifted transport, and atlas overlap checks.

# v0.11.1 — Division Classification Consistency Patch

v0.11.1 is a corrective patch to the v0.11.0 rational-expansion release. It aligns the retained v0.8.x compatibility classifier with the theorem-aligned public division API and adds cross-API regression protection.

## Fixed

- Added a corrected, deprecated compatibility module at `cnrs.cnrs_division_status`.
- Made `classify_division()` numerator-aware by delegating to `cnrs.division.classify_denominator()`.
- Ensured powers of five are not treated as automatically terminating.
- Added regression tests for `1/5`, `1/25`, `conjugate(beta)/5`, and `conjugate(beta)^2/25`.
- Added cross-API consistency tests covering Gaussian-integer, terminating, periodic, shifted-periodic, negative-denominator, and equivalent-fraction cases.
- Clarified that a finite Laurent offset does not by itself imply a terminating expansion.

## Mathematical correction retained

For `beta = -2+i`,

```text
5 = beta * conjugate(beta).
```

A reduced denominator `5**s` produces a terminating Laurent expansion only when the reduced numerator cancels `conjugate(beta)**s`. Therefore:

- `1/5` is shifted eventually periodic;
- `1/25` is shifted eventually periodic;
- `conjugate(beta)/5 = 1/beta` terminates;
- `conjugate(beta)**2/25 = 1/beta**2` terminates.

## Compatibility

`cnrs.cnrs_division_status` is retained only for compatibility and emits `DeprecationWarning`. New code should use:

```python
from cnrs.division import classify_denominator
```

## Validation

Final validation: `1182 passed`, `0 failed`. Build and distribution metadata checks completed successfully.

---

# v0.11.0 — Rational Expansion and Scientific Workflow Validation

**Release date:** 2026-07-08

This release advances the Toolkit from the v0.10.x verification line to a substantive validation release. It introduces no claim of full CNRS completeness.

## Division and rational expansion

- Corrected `CnrsRational.evaluate()` so its default returns the exact represented value for finite, periodic, and Laurent-periodic classes.
- Added `CnrsRational.partial_sum(n_digits)` for diagnostic finite formal sums that respect `power_offset`.
- Removed six expected-failure markers associated with the former Laurent-periodic evaluation limitation.
- Added randomized exact reconstruction tests using `fractions.Fraction`.
- Added reduced-denominator classification checks, equivalent-fraction invariance, sampled period-minimality checks, long-period validation, and invalid-input tests.
- Integrated the Gaussian-rational eventual-periodicity theorem for base `z0=-2+i`.
- Corrected integer-denominator classification using Gaussian factorization: `5=z0*conjugate(z0)`. In particular, `1/5` is shifted-periodic, not terminating; a denominator `5**s` terminates only when the numerator cancels `conjugate(z0)**s`.
- Added `docs/theory/GAUSSIAN_RATIONAL_PERIODICITY_THEOREM_V1.md` and theorem-specific regression tests.

## Scientific workflow audit

- Cross-validated first- and second-order CNRS-H ODE solutions against closed forms.
- Cross-validated exponential scale laws.
- Rechecked biological diffusion profiles, steady state, Jacobian, and Turing prerequisites.
- Cross-validated linear complex oscillator behavior.
- Compared the interoperability workflow with closed-form and SciPy reference solutions.
- Added `docs/audits/SCIENTIFIC_WORKFLOW_AUDIT_V011.md`.

## Validation

- `1167 passed`
- `0 xfailed`
- `0 unexpected failures`

Warnings remain intentional domain diagnostics when existing tests deliberately evaluate truncated EGF models outside their estimated reliable range.

## Claim boundary

The release establishes implementation agreement with the equations represented in the Toolkit. It does not prove metric completeness, the e-base theorem, or the physical applicability of exploratory Scale Space and biological workflows.

## Final theorem-alignment additions

The final v0.11.0 package now includes the full Gaussian denominator-ideal and valuation API and canonical periodic normalization:

- arbitrary Gaussian numerator and denominator support;
- exact Gaussian gcd, divisibility, unit normalization, and beta valuation;
- intrinsic denominator-ideal generator;
- exact termination analysis and minimal Laurent offset;
- canonical eventually periodic Laurent expansion;
- least-preperiod cycle detection and primitive-period normalization;
- exact semantic equality and deterministic serialization;
- theorem papers and independent verification script.

The special `1/5` behavior is now a corollary of the general Gaussian-ideal implementation rather than a standalone special case.


## Branch-index and formal CNRS-H theorem alignment

- Added `LiftedComplex` with the exact branch-wrap cocycle for multiplication on the universal cover of `C*`.
- Added a single-valued lifted logarithm satisfying an exact product law.
- Added formal Hurwitz-series coefficient operations for CNRS-H and exact theorem tests for Leibniz, integration, inversion, and exponential eigenfunctions.
- Included both theorem papers and independent verification scripts under `docs/theory/` and `docs/audits/scripts/`.

## Metric/topological completeness and hybrid theorem integration

- Added `cnrs.topology` with exact symbolic-prefix and beta-adic distance utilities, finite-digit evaluation, the first-difference isometry check, and CNRS-H coefficientwise product distance.
- Recorded the theorem that right-infinite CNRS-A strings complete to the valuation ring at `beta=-2+i` (`Z_5` topologically), while finite Laurent shifts give the corresponding local field (`Q_5` topologically).
- Explicitly separated beta-adic convergence from ordinary complex convergence.
- Added `cnrs.hybrid` with `CoefficientCodec` and `HybridSeries`, transporting canonical CNRS-A coefficient representations into the CNRS-H Hurwitz-series carrier.
- Added theorem-aligned tests for ultrametricity, first-difference isometry, coefficientwise convergence, Hurwitz-product transport, Leibniz, integration, exponential eigenfunctions, and deterministic serialization.
- Included both theorem papers and independent verification scripts under `docs/theory/` and `docs/audits/scripts/`.
