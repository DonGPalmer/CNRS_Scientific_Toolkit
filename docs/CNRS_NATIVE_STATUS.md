# CNRS Native Status — v0.6.0

This document classifies major toolkit components by their role in the CNRS
Scientific Toolkit architecture.

| Component | Primary path | Status |
|---|---|---|
| CNRS base and digits | `cnrs.core.base`, `cnrs.core.digits` | Native core |
| CNRS value wrapper | `cnrs.core.value` | Native core |
| CNRS-A arithmetic | `cnrs.core.arithmetic` | Native core |
| Branch state façade | `cnrs.core.branch` | Native direction; currently backed by symbolic branch objects |
| CNRS-H EGF series | `cnrs.h.series` | Native calculus core |
| CNRS-H differentiation/integration | `cnrs.h.series`, `cnrs.h.calculus` | Native coefficient-shift calculus |
| CNRS-H composition and chain rule | `cnrs.h.compose`, `cnrs.h.chain_rule` | Native finite-order structural calculus |
| CNRS-H local jets | `cnrs.h.jet` | Native local analytic object |
| CNRS-H domain diagnostics | `cnrs.h.domain` | Diagnostic support for native jets |
| CNRS-H Taylor-model metadata | `cnrs.h.taylor_model` | Certification scaffold |
| Symbolic expressions | `cnrs.symbolic` | Bridge layer |
| Symbolic-to-CNRS-H conversion | `cnrs.cnrs_h_bridge` | Bridge layer |
| Autodiff / `CnrsDual` | `cnrs.validation.autodiff` | Validation/reference method |
| `CnrsComplex` reference interface | `cnrs.validation.reference_complex` | Validation / interoperability |
| Scientific workflows | `cnrs.workflows` and examples | Application layer |

## Claim discipline

The v0.6.0 claim is architectural, not theorem-completing:

> CNRS-native calculus is now exposed as the primary API spine, with autodiff
> and symbolic methods classified as validation and bridge layers.

The toolkit still needs future work on rigorous remainder propagation,
path/winding tracking, branch-state propagation in CNRS-H jets, and formal
analytic-continuation theorems.
