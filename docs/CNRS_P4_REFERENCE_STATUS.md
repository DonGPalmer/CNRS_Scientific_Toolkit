# Current CNRS Problem 4 Reference Status — Toolkit v0.12.1

## Canonical programme reference

Donald G. Palmer, *Partial Operational Completeness of a Positional Number System for Complex Numbers*, Version 12, Zenodo, 2026. DOI: [10.5281/zenodo.21791909](https://doi.org/10.5281/zenodo.21791909).

This is the canonical Problem 4 citation for the present Toolkit release. The bundled working theorem records below provide the detailed mathematical basis and executable verification material used by the implementation.

## Bundled supporting theorem records

| Record | Toolkit location | Current role |
|---|---|---|
| Gaussian-rational eventual periodicity | `docs/theory/GAUSSIAN_RATIONAL_PERIODICITY_THEOREM_V1.md` | Establishes eventual periodicity for Gaussian rationals in base `-2+i` within the stated algebraic orientation. |
| Denominator-ideal termination | `docs/theory/TERMINATION_DENOMINATOR_IDEALS_V1.tex` / `.pdf` | Gives the exact finite-Laurent termination criterion and minimal offset through Gaussian ideals and valuations. |
| Canonical periodic normalization | `docs/theory/CANONICAL_PERIODIC_NORMALIZATION_V1.tex` / `.pdf` | Selects a value-preserving, idempotent canonical finite/eventually-periodic Laurent record. |
| Formal CNRS-H algebra | `docs/theory/FORMAL_CNRS_H_ALGEBRA_V1.tex` / `.pdf` | Establishes the Hurwitz-series differential-algebra structure and finite-truncation implementation interface. |
| Metric and topological completeness | `docs/theory/METRIC_TOPOLOGICAL_COMPLETENESS_V1.tex` / `.pdf` | Resolves the natural CNRS-A prefix/beta-adic completeness question; the completion is the local valuation ring/field (`Z_5`/`Q_5` topologically), not the ordinary complex plane. |
| Hybrid CNRS-A/CNRS-H representation | `docs/theory/HYBRID_CNRS_A_CNRS_H_REPRESENTATION_THEOREM_V1.tex` / `.pdf` | Transports canonical CNRS-A coefficient representations into the CNRS-H Hurwitz-series carrier. |

Independent verification scripts are bundled under `docs/audits/scripts/`.

## Current status represented in the Toolkit

Established within the present formal model and stated coefficient domains:

- finite CNRS-A Gaussian-integer arithmetic;
- exact Gaussian-rational finite/eventually-periodic classification and reconstruction;
- denominator-ideal termination and minimal Laurent offset;
- canonical periodic normalization;
- formal CNRS-H differential algebra;
- completeness of the natural symbolic/beta-adic CNRS-A representation space;
- coefficientwise completeness of CNRS-H over a complete coefficient ring;
- the conditional hybrid representation theorem for coefficient domains with a canonical codec.

Still separate or open:

- ordinary complex analytic convergence for arbitrary CNRS-H objects;
- a canonical CNRS-A representation of every value in the ordinary complex plane under one selected global convention;
- efficient arithmetic on arbitrary infinite fractional streams;
- a closed arithmetic formula for all minimal period lengths;
- certified automatic construction of compact algebraic Riemann surfaces, including infinity, singular normalization, Puiseux charts, and certified continuation;
- empirical or physical necessity of CNRS representations.

## Citation discipline

Cite the Toolkit concept DOI for software use: [10.5281/zenodo.20574852](https://doi.org/10.5281/zenodo.20574852).

When relying on Problem 4 completeness or operational-closure claims, also cite the canonical Problem 4 Version 12 record above. The bundled theorem papers are working records and should be cited separately only when their specific theorem statements or derivations are used.
