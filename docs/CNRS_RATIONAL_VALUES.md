# CNRS Rational Values (v0.9.0)

`cnrs.rational_value` promotes structured division expansions into a value-facing object while preserving the CNRS-A division status.

The module does **not** claim that general division closes inside finite CNRS-A digit strings. It records whether a division is:

- a Gaussian-integer finite value;
- a terminating base-power fractional expansion;
- an eventually periodic coprime-denominator expansion;
- a shifted eventually periodic expansion.

## Main API

```python
from cnrs import rational_value

x = rational_value(1, 2)
print(x.status)
print(x.structured_report())
```

`CnrsRationalValue.finite_cval()` is intentionally restricted to Gaussian-integer quotients. A terminating negative-power value such as `(-2-i)/5 = z0^{-1}` is finite in the Laurent sense but is not a Gaussian integer and therefore cannot be collapsed into the finite-integer `CVal` wrapper. By contrast, `1/5` is shifted-periodic because `5=z0*conjugate(z0)` and the numerator does not cancel the conjugate-base factor.

## Status

This is a theory-aligned representation layer. It carries finite/periodic status explicitly and uses the exact rational expansion machinery already present in the toolkit.
