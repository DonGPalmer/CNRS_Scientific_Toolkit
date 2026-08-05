# Gaussian-Rational Theorem Support — v0.12.1

The Toolkit encodes three linked results for base `beta = -2+i`:

1. Every Gaussian rational has an eventually periodic Laurent expansion in the stated beta-adic orientation.
2. A reduced Gaussian rational terminates exactly when its denominator ideal is a power of `(beta)`; the beta valuation gives the minimal Laurent offset.
3. Every admissible eventually periodic Laurent expansion has a unique canonical record with minimal offset, least preperiod, and primitive period.

## Public API

```python
from cnrs.gaussian_valuation import analyze_termination
from cnrs.canonical_periodic import CanonicalPeriodicExpansion, canonicalize_periodic
```

`analyze_termination((a,b), (c,d))` returns the reduced denominator-ideal generator, beta valuations, residual denominator obstruction, termination status, and exact minimal Laurent offset.

`CanonicalPeriodicExpansion.from_gaussian_fraction((a,b), (c,d))` returns the canonical finite or eventually periodic Laurent representation.

## Theorem records

- `theory/GAUSSIAN_RATIONAL_PERIODICITY_THEOREM_V1.md`
- `theory/TERMINATION_DENOMINATOR_IDEALS_V1.tex` / `.pdf`
- `theory/CANONICAL_PERIODIC_NORMALIZATION_V1.tex` / `.pdf`

The canonical programme citation is the Problem 4 Version 12 record listed in `CNRS_P4_REFERENCE_STATUS.md`, DOI `10.5281/zenodo.21791909`.

## Status and remaining boundary

These are theorem-aligned exact-arithmetic implementations within the stated Gaussian-rational and beta-adic domains. Still open are a closed arithmetic formula for every minimal period length and general efficient arithmetic on arbitrary infinite fractional streams. Ordinary complex convergence is a separate topology question.
