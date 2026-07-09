# Gaussian-Rational Theorem Support (v0.11.0)

The Toolkit encodes three linked results for base `z0 = -2+i`:

1. Every Gaussian rational has an eventually periodic Laurent expansion.
2. A reduced Gaussian rational terminates exactly when its denominator ideal is a power of `(z0)`.
3. Every admissible eventually periodic Laurent expansion has a unique canonical form with minimal Laurent offset, least preperiod, and primitive period.

## Public API

```python
from cnrs.gaussian_valuation import analyze_termination
from cnrs.canonical_periodic import CanonicalPeriodicExpansion, canonicalize_periodic
```

`analyze_termination((a,b), (c,d))` returns the reduced denominator-ideal generator, beta valuations, residual denominator obstruction, termination status, and exact minimal Laurent offset.

`CanonicalPeriodicExpansion.from_gaussian_fraction((a,b), (c,d))` returns the canonical finite or eventually periodic Laurent representation.

## Status

These are theorem-aligned exact-arithmetic implementations. The remaining open problem is a closed arithmetic formula for minimal period length in terms of finite quotient-ring data.
