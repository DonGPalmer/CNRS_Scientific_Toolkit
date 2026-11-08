# Draft GitHub Release description — CNRS Scientific Toolkit v0.20.0

**DRAFT ONLY — NOT YET PUBLISHED.** This text is for an author-approved future GitHub release. Add final commit SHA, verified asset hashes and publication date only after that evidence exists.

## Finite exact CNRS-H coefficients and divided-power arithmetic

This version adds an experimental exact arithmetic pathway over the localized Gaussian-integer coefficient ring R_A = Z[i][(-2+i)^(-1)] while retaining the existing CNRS-A and CNRS-H interfaces.

New qualified modules:
- cnrs.cnrs_h_finite_exact: canonical finite CNRS-A coefficient encoding/decoding, exact finite Hurwitz jets, binomial convolution, derivative/antiderivative, and truncated formal reciprocals when the constant coefficient is a unit of R_A.
- cnrs.cnrs_h_toolkit_interop: checked comparison with selected existing exact native CNRS-A digit addition and multiplication operations.
- cnrs.cnrs_h_limits: opt-in BoundedFiniteOps with explicit limits for digit size, numerator bits, localized denominator power, jet degree and convolution work.

The two pre-existing runtime type-alias declarations incompatible with Python 3.9 were corrected without changing numerical formulas. The implementation keeps the previous package-root exports and existing CnrsHNative / CnrsHJet APIs.

## Verification from pre-publication candidate

The post-publication-control source candidate passed 1,575 Python tests with 4 skipped on GitHub Actions; an independent reviewer reproduced 1,575 passed and 4 skipped on Python 3.9 through 3.13. Historical acceptance contracts and isolated wheel/source-distribution installations also passed. Final release-source tests and hashes remain subject to verification after the last approved commit. Five Python 3.9–3.13 CNRS-H jobs and all six existing Lean project builds passed on the candidate. The publication gate requires fresh independent verification of the exact final release commit/tree and bytes before asset upload.

## Scientific and formal boundaries

The exact finite coefficient domain is the localization R_A, not all Gaussian rationals Q(i). Raw research algebra remains unbounded. The opt-in bounded facade is not a hardened untrusted-input sandbox. The new Python modules have not been extracted from Lean or formally verified end to end; the existing Lean checks do not prove them. No claim is made of infinite-series convergence, physical prediction or performance superiority.

## Publication provenance (to be completed only from verified records)

- Final approved commit and tree: PENDING FINAL RELEASE AUDIT
- Certified wheel and sdist SHA-256: PENDING FINAL RELEASE AUDIT
- GitHub publication date: PENDING ACTUAL PUBLICATION
- Existing Toolkit concept DOI: https://doi.org/10.5281/zenodo.20574852

Do not publish this draft or replace the already published v0.19.0 assets as part of preparation.
