# v0.9.0 Claim Status Addendum

`CnrsRationalValue` is a status-preserving representation layer for finite and periodic division outputs. It does not claim finite-string field closure for general division. Scientific workflow diagnostics quantify projection effects; they are diagnostic tools, not standalone physical claims.

# Claim Status — v0.8.1

This file separates implemented computational claims from open mathematical or scientific claims.

## Current validation

```text
1015 passed, 6 xfailed
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
- v0.4.1 minimal symbolic differentiation through expression trees, conservative simplification, and symbolic-vs-autodiff consistency checks.
- v0.4.2 conservative rule-based symbolic integration with unevaluated `Integral` fallback.
- v0.4.3/v0.4.4 lightweight CLI access, example discovery, and documentation polish.
- v0.5.1 explicit branch-state scaffolding for symbolic `log`, `sqrt`, and branch-aware powers.
- v0.5.1 symbolic-to-CNRS-H bridge and direct finite CNRS-H chain-rule checks.
- v0.6.0 CNRS-H local jets with explicit expansion points and nonzero-center chain-rule checks.

- v0.8.0 native `CVal` arithmetic, `CnrsHNative` coefficient calculus, division classification, and CNRS* formal-state tuple.
- v0.8.1 scoped normalization routes, structured division reports, theorem-alignment registry, and CNRS* state-preservation operations.

## v0.4.0 claim

`cnrs.autodiff` provides a practical first-order automatic differentiation layer for scalar CNRS-compatible complex-valued functions of one scalar variable. It propagates derivatives by the chain rule through arithmetic, elementary functions, nested composition, and scale-law examples.

Status: **implemented and tested for representative numerical cases.**

Boundary: this is a numerical autodiff layer over `CnrsComplex`, not a full symbolic algebra system and not a proof of a complete coefficient-level CNRS-H chain rule. Branch handling is a first explicit integer-branch scaffold for log/sqrt/power experiments, not a final global analytic continuation theory.


## v0.4.1/v0.4.2 symbolic calculus claim

`cnrs.symbolic` provides a minimal symbolic calculus layer for scalar CNRS-compatible expressions. It supports expression trees, symbolic chain-rule differentiation, conservative simplification, numeric evaluation, conservative rule-based symbolic integration, unevaluated `Integral` fallback for unsupported forms, and cross-checking against `CnrsDual` automatic differentiation.

Status: **implemented and tested for representative symbolic and numerical cases.**

Boundary: this is not a full computer algebra system, not a general symbolic integration engine, and not a complete exact CNRS-H coefficient-level symbolic calculus. Branch support is currently a simple integer-tag scaffold for log/sqrt/power expressions.

## v0.5.1 branch-aware symbolic-calculus claim

`cnrs.symbolic` preserves explicit local branch choices for logarithms, square roots, and branch-aware powers through expression construction, substitution, differentiation, conservative integration where relevant, evaluation, and CLI parsing.

Status: **implemented and tested for representative symbolic, parser, CLI, and numerical branch cases.**

Boundary: this is a local branch-state scaffold. It is not a full Riemann-surface representation, not a global analytic-continuation engine, and not a proof of complete CNRS branch calculus.

## v0.4.4 usability claim

The toolkit provides a lightweight CLI with conversion, symbolic evaluation, differentiation, integration, demo, and example-discovery commands. It is intended as a demonstration and convenience interface for the Python API, not as a full graphical interface or computer algebra shell.

Status: **implemented and tested for basic command workflows and friendly error handling.**


## v0.6.0 CNRS-H local-jet claim

`cnrs.cnrs_h_jet` provides finite local CNRS-H jets around explicit expansion points. A jet represents `f(s) ~= sum d_n (s-s0)^n/n!`, supports center-preserving differentiation/integration, finite multiplication/composition, center shifting for finite jets, and local-jet chain-rule checks.

Status: **implemented and regression-tested for representative finite local jets, including nonzero expansion centers.**

Boundary: this is a finite local coefficient object. It does not yet prove convergence domains, Taylor remainder bounds, branch-path transport, or global analytic continuation.

## Open / research-level claims

- Full mathematical completeness of CNRS for all complex values.
- Full canonical uniqueness across all branch/global analytic layers.
- Complete symbolic chain-rule calculus at the exact CNRS-H coefficient level.
- Empirical validation of any Scale Space or biological modelling interpretation.
- Production-grade numerical stability guarantees for all scientific workflows.


## v0.5.1 symbolic-to-CNRS-H bridge

The v0.5.1 release adds `cnrs.cnrs_h_bridge`, a conservative bridge from supported symbolic expressions to finite CNRS-H EGF coefficient representations.  It supports constants, polynomials, simple scale laws such as `A*exp(k*s)`, and `exp`/`sin`/`cos` of affine arguments.  Unsupported expressions raise `UnsupportedBridgeExpression`.


## v0.5.1 direct CNRS-H chain-rule claim

Status: implemented and regression-tested for finite truncated CNRS-H EGF coefficient series.

The toolkit now supports direct coefficient-space composition and verification of `D(f ∘ g) = (Df ∘ g) * Dg` without relying on the `CnrsDual` autodiff wrapper.  The claim is finite-order and computational: it applies to the represented truncated series and does not yet constitute a complete analytic theorem for arbitrary CNRS-H functions, branch paths, or singular functions.


## v0.6.0 domain diagnostics

`cnrs.cnrs_h_domain` provides conservative local radius/singularity metadata and last-term truncation indicators for supported CNRS-H jets.  These are diagnostics, not rigorous global convergence proofs or analytic-continuation theorems.
