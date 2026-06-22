# CNRS Toolkit Theorem Alignment (v0.8.0)

This note records how the v0.8.0 code aligns with the current CNRS theoretical architecture.  It is a status map, not a proof document.

## Core rule

Use CNRS-native structures where they exist.  Use ordinary Python, symbolic parsing, and reference complex arithmetic only as bridge, validation, or interface layers.

## Alignment table

| Theory component | Toolkit object | Status |
|---|---|---|
| CNRS-A finite canonical value | `cnrs.cnrs_value.CVal` | native core |
| CNRS-A addition | `CVal.__add__`, `add_cnrs` | native bounded-input addition |
| CNRS-A negation | `CVal.__neg__` via `-1 = "144"` | native finite multiplication |
| CNRS-A subtraction | `CVal.__sub__` as `a + (-b)` | native finite arithmetic |
| CNRS-A multiplication | `CVal.__mul__`, `mul_cnrs` | convolution + general CNRS-A normalisation |
| CNRS-A division | `cnrs_division_status`, `cnrs_rational` | classified: finite / shifted / eventually periodic |
| CNRS-H coefficient calculus | `CnrsHNative` | native coefficient calculus over `CVal` |
| CNRS-H differentiation | `CnrsHNative.differentiate()` | exact coefficient drop |
| CNRS-H integration | `CnrsHNative.integrate()` | exact coefficient prepend |
| CNRS-H product | `CnrsHNative.__mul__` | native EGF binomial convolution |
| CNRS-H composition | `compose_native` | finite-order Bell-polynomial / Faà di Bruno algorithm |
| CNRS-H chain rule | `verify_chain_rule_native` | finite-order native verification |
| CNRS* state | `CnrsFormalState` | local theory-aligned state tuple |
| Scientific state | `CnrsScientificState` | science-facing local object |

## Important scope notes

The 14-state addition normalizer is scoped to bounded raw alphabets arising from addition.  Multiplication closure uses convolution followed by general CNRS-A normalisation.  The toolkit should not describe arbitrary multiplication convolution normalisation as the same finite-state result as addition.

CNRS-H composition is algorithmically native through integer Bell-polynomial coefficient arithmetic.  It is not claimed to be a fixed finite-state digit transducer for non-polynomial outer functions.

Division is not finite field closure inside finite CNRS-A strings.  The toolkit exposes a classification into Gaussian-integer, terminating/shifted, and eventually-periodic cases.  Sharp minimal carry-state counts remain theory work.
