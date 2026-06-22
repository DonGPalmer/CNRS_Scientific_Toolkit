# Claim Status — v0.4.0

This file separates implemented computational claims from open mathematical or scientific claims.

## Current validation

```text
733 passed, 6 xfailed
```

The expected failures are known representational-limit cases and are not regressions.

## Implemented and tested

- CNRS-A finite digit-string arithmetic over `z0 = -2+i` for Gaussian integers.
- Addition via finite-state transducer, including the v0.3.1 fractional-alignment fix.
- Multiplication by convolution plus carry normalization.
- Gaussian rational expansion for finite, pure periodic, and Laurent-periodic cases.
- CNRS-H coefficient calculus and digit-shift differentiation/integration.
- CNRS-H ODE recurrence examples.
- Scientific workflow helpers for scale laws, biological scale dynamics, oscillators, interoperability, multi-scale SS physics scaffolding, regime detection, and reaction-diffusion scale-exit examples.
- v0.4.0 first-order chain-rule automatic differentiation over `CnrsComplex` via `CnrsDual`.

## New v0.4.0 claim

`cnrs.autodiff` provides a practical first-order automatic differentiation layer for scalar CNRS-compatible complex-valued functions of one scalar variable. It propagates derivatives by the chain rule through arithmetic, elementary functions, nested composition, and scale-law examples.

Status: **implemented and tested for representative numerical cases.**

Boundary: this is a numerical autodiff layer over `CnrsComplex`, not a full symbolic algebra system and not a proof of a complete coefficient-level CNRS-H chain rule. Branch handling is a first explicit integer-branch scaffold for log/sqrt/power experiments, not a final global analytic continuation theory.

## Open / research-level claims

- Full mathematical completeness of CNRS for all complex values.
- Full canonical uniqueness across all branch/global analytic layers.
- Complete symbolic chain-rule calculus at the exact CNRS-H coefficient level.
- Empirical validation of any Scale Space or biological modelling interpretation.
- Production-grade numerical stability guarantees for all scientific workflows.
