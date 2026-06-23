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


## v0.6.1 update

Branch-state propagation inside `CnrsHJet` is classified as **CNRS-native local bookkeeping**. It carries branch choices into the CNRS-H coefficient object. It remains distinct from future path-dependent analytic continuation, which is still experimental/open.

## v0.6.2 native-status update

Path/winding tracking is now part of the CNRS-H branch scaffold. It is classified as **native branch bookkeeping / experimental analytic-continuation scaffold**. It is not yet a full global analytic-continuation theorem.

## v0.7.0 native-status update

Branch continuation is now partly coefficient-active: supported symbolic branch changes can rebuild CNRS-H jets rather than only recording branch metadata. This remains local finite-order scaffolding, not full analytic-continuation semantics.


| `CnrsScientificState` | Native scientific integration object | Finite local representation; not global analytic continuation |

## v0.7.1 native-status registry

v0.7.1 adds a programmatic registry in `cnrs.native_status`.  The registry
classifies public components as `native_core`, `native_finite`, `native_local`,
`bridge`, `validation`, `scaffold`, `application`, or `compatibility`.

This is a status map, not a theorem prover. Its purpose is to keep the toolkit
aligned with the theoretical CNRS programme and to prevent bridge/validation
utilities from being mistaken for the native CNRS core.

See `docs/CNRS_NATIVE_STATUS_REGISTER.md` and `tools/audit_native_status.py`.


## v0.8.0 theorem-aligned native additions

v0.8.0 adds native `CVal` negation/subtraction, `CnrsHNative` coefficient calculus, theory-aligned division classification, and a lightweight CNRS* formal state object. These additions are classified in `cnrs.native_status` and documented in `docs/THEOREM_ALIGNMENT.md`.


## v0.8.1 theory-aligned consolidation

v0.8.1 adds scoped normalization, structured division expansion reports, theorem-alignment registry support, and CNRS* state preservation operations. The key architectural distinction is that bounded addition normalization and general finite coefficient normalization are separate native routes.
