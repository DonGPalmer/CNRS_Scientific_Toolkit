# Zenodo new-version metadata — v0.20.0 draft

**Status: COPY PREPARATION ONLY.** DO NOT CREATE/DEPOSIT/PUBLISH A ZENODO RECORD FROM THIS DRAFT. Recheck the live Zenodo account, community and existing concept/version history before the eventual deposit.

## Identity inherited from verified v0.19.0 Zenodo record

- Existing concept DOI: https://doi.org/10.5281/zenodo.20574852
- Previous v0.19.0 version DOI: https://doi.org/10.5281/zenodo.23747938
- Record title: CNRS Scientific Toolkit
- Creator: Palmer, Donald G. — ORCID 0000-0003-4335-5533
- Community: scale-space-cnrs (verify continued acceptance)
- License: Apache-2.0
- Resource type: Software
- Repository: https://github.com/DonGPalmer/CNRS_Scientific_Toolkit
- Proposed version label: v0.20.0

Use **New version** on the existing Zenodo concept record; do not start a different concept record or reuse the previous version DOI.

## Suggested description

CNRS Scientific Toolkit v0.20.0 — Experimental Finite Exact CNRS-H Coefficients and Hurwitz Calculus

This version adds an exact finite CNRS-H coefficient arithmetic implementation over the localization R_A = Z[i][(-2+i)^(-1)] of the Gaussian integers at the complex base -2+i. The implementation provides finite CNRS-A coefficient serialization, exact finite-support divided-power/Hurwitz operations, and restricted truncated inversion where the coefficient is a unit of the localization.

It includes qualified interoperability checks against existing exact CNRS-A digit-string operations, an opt-in facade with explicit resource limits, and Python 3.9 compatibility corrections to the existing toolkit. The previous CNRS public interfaces remain available.

In pre-publication candidate testing, 1,563 Python tests passed with four skipped; finite-operation tests passed under Python 3.9–3.13, existing Lean source identity and six Lean projects built successfully, and reproducible wheel and source-distribution builds with isolated installs passed. The separately approved final publication artifacts must be independently verified against the approved commit and SHA-256 manifest; pre-publication candidate results do not replace final checks.

The Python implementation remains independently authored and is not an end-to-end Lean-extracted or formally verified implementation. The finite coefficient ring is not the full field Q(i). Computational resource budgets are not a security sandbox. The release does not claim analytic infinite-series convergence or performance superiority.

Toolkit concept DOI: https://doi.org/10.5281/zenodo.20574852

## Suggested related identifier

Only after a real GitHub tag exists and is verified:
https://github.com/DonGPalmer/CNRS_Scientific_Toolkit/tree/v0.20.0
Relationship: isSupplementTo; resource: software.

## File and deposit gates

Select exact approved source tag archive, and whether to include the two certified wheel/sdist distributions under an explicit file-inventory approval. Compare all deposited files against the approved source and asset inventory. Zenodo may generate its own archive names: verify actual deposited file checksums, not just names.

Do not set a publication date, GitHub release ID, Zenodo record number, or a new version DOI in advance. Obtain these from published live records after the separately authorized transaction. Record actual DOI and citations in the governed Zenodo index only afterward.
