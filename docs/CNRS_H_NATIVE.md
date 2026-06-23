# CNRS-H native coefficient calculus (v0.8.1)

`CnrsHNative` is the native-coefficient CNRS-H object. Unlike `CnrsH`, which stores Python numeric coefficients, `CnrsHNative` stores each coefficient as a `CVal` CNRS-A digit string.

## Native operations

- differentiation: drop the constant coefficient;
- integration: prepend the integration constant;
- coefficient addition: CNRS-A addition through `CVal`;
- coefficient negation: multiplication by CNRS-A `-1 = "144"`;
- coefficient subtraction: native addition after native negation;
- coefficient multiplication: CNRS-A multiplication through `CVal`;
- EGF product: binomial convolution in CNRS-A coefficient space;
- EGF composition: finite-order Faà di Bruno / Bell-polynomial recurrence in CNRS-A coefficient space.

Evaluation at an ordinary real or complex point remains a bridge operation because the input point is not itself a CNRS-A value.

## Status

`CnrsHNative` supports the theoretical interpretation of CNRS-H as an internal coefficient-calculus layer. Composition is algorithmic-native, not finite-state-native.
