# CNRS Toolkit theorem alignment (v0.8.1)

This release aligns the Python implementation more tightly with the current CNRS theoretical architecture.

The guiding rule is: use CNRS internally wherever CNRS has a native structure; retain Python complex arithmetic, symbolic parsing, and dual-number methods as bridge, validation, or interface layers.

## Theory-to-code map

| Theory component | Toolkit component | Status |
|---|---|---|
| CNRS-A canonical value | `cnrs.cnrs_value.CVal` | native core |
| Native negation | `-CVal`, using `-1 = "144"` | native core |
| Native subtraction | `a + (-b)` | native core |
| CNRS-A multiplication | `CVal.__mul__`, `mul_cnrs` | native core; convolution + general normalization |
| CNRS-A division classification | `cnrs.division` | native finite/periodic classification |
| CNRS-H native coefficients | `CnrsHNative` | native core |
| CNRS-H differentiation | `CnrsHNative.differentiate()` | exact coefficient drop |
| CNRS-H integration | `CnrsHNative.integrate()` | exact coefficient prepend |
| CNRS-H product | `CnrsHNative.__mul__` | EGF binomial convolution using `CVal` coefficients |
| CNRS-H composition | `compose_native` | algorithmic-native finite-order coefficient calculus |
| CNRS-H chain rule | `verify_chain_rule_native` | finite-order native verification |
| CNRS* state | `CnrsFormalState` | finite local theory-aligned state |

## Scope discipline

The 14-state normalizer is scoped to bounded addition inputs. Multiplication closure is implemented by convolution followed by general CNRS-A normalization, not by reusing the addition transducer as if arbitrary convolution coefficients were bounded.

Division is not presented as finite-string field closure. It is classified into terminating and periodic cases. Persistent denominators are represented by periodic structures.

EGF composition is not treated as a finite-state CNRS-A transducer. It is an algorithmic-native CNRS-H coefficient-calculus operation using Bell polynomials / Faà di Bruno recurrence.
