# CNRS-H Native Coefficient Calculus (v0.8.0)

`CnrsHNative` stores each CNRS-H EGF coefficient as a `CVal`, a CNRS-A canonical digit string.  This is the main v0.8.0 step toward using CNRS internally rather than using Python complex coefficients inside CNRS-H.

## Native operations

| Operation | Implementation |
|---|---|
| differentiation | coefficient drop |
| integration | coefficient prepend |
| coefficient addition | `CVal.__add__` |
| coefficient negation | `CVal.__neg__`, using `-1 = "144"` |
| coefficient subtraction | `a + (-b)` |
| EGF product | binomial convolution using `CVal` arithmetic |
| EGF composition | Bell-polynomial / Faà di Bruno recurrence using `CVal` arithmetic |
| finite chain rule | `verify_chain_rule_native` |

## Boundary

Evaluation at an ordinary real or complex point is still an interface/bridge operation, because the external point is not itself currently a CNRS-A or CNRS-H object.
