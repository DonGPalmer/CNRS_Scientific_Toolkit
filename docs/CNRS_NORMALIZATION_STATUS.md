# CNRS-A Normalization Status

v0.8.1 separates two normalization routes that should not be conflated.

## Bounded addition normalization

Addition of two canonical CNRS-A digit strings has bounded raw digit sums. This
is the scope of the compact addition-transducer route.

Use:

```python
from cnrs.normalization import normalize_addition

result = normalize_addition("4", "4")
assert result.scope.value == "addition_bounded"
```

## General finite coefficient normalization

Multiplication convolution and other finite coefficient constructions can
produce raw coefficients that grow with input length. These are not bounded by
the addition alphabet and must be routed through the general CNRS-A carry
normalization algorithm.

Use:

```python
from cnrs.normalization import normalize_general_coefficients

result = normalize_general_coefficients([40, 37, 12])
assert result.scope.value == "general_finite_coefficients"
```

## Multiplication status

CNRS-A multiplication remains native and theorem-aligned, but its status is:

```text
convolution followed by general CNRS-A normalization
```

not:

```text
arbitrary multiplication normalized by the bounded 14-state addition transducer
```

This distinction is part of the v0.8.1 theory-aligned core cleanup.
