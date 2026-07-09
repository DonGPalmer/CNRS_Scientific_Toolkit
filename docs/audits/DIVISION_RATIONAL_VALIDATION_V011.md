# Division and Rational-Expansion Validation — v0.11.0

This release validates the Gaussian-rational layer across terminating, periodic, and Laurent-periodic classes using exact `Fraction` arithmetic and an independently written classifier. The final v0.11.0 classifier is numerator-aware in `Z[i]`: because `5=z0*conjugate(z0)`, ordinary denominator factorization alone is insufficient to decide termination.

## Validated properties

- reduced-denominator classification;
- exact reconstruction of real and imaginary rational components;
- invariance under equivalent numerator/denominator scaling;
- finite, periodic, and shifted-periodic behavior;
- sampled minimality of detected periods;
- long-period reconstruction, including `1/23` with period 528;
- zero-denominator handling;
- consistency of `evaluate()`, `z0_adic_value_exact()`, and exact fraction output.

## API correction

In earlier releases, `CnrsRational.evaluate()` treated z0-adic data as an ordinary fractional CNRS string and therefore ignored `power_offset` for Laurent-periodic values. v0.11.0 changes the default behavior:

- `evaluate()` returns the exact represented rational value for all expansion classes;
- `partial_sum(n)` returns a diagnostic finite formal sum and respects `power_offset`;
- `evaluate(n)` remains as a compatibility route to the diagnostic partial sum.

Periodic z0-adic expansions do not converge in the ordinary complex norm because `|z0| > 1`; exact value assignment uses the rational periodic closed form.

## Theorem integration correction

The Gaussian-rational periodicity theorem establishes that every element of `Q(i)` has an eventually periodic Laurent base-`z0` expansion, and conversely. Its exact termination criterion is `x in Z[i][z0^{-1}]`. For reduced integer denominator `5^s`, this requires cancellation of `conjugate(z0)^s` by the numerator. The prior denominator-only shortcut incorrectly labelled `1/5` as terminating; v0.11.0 now labels it shifted-periodic and includes regression coverage for the corrected criterion.
