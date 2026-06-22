# CNRS-H Taylor-model-style remainder metadata

v0.5.4 adds `CnrsHTaylorModel`, a lightweight wrapper around a finite `CnrsHJet` plus an explicit remainder/error indicator.

A model represents a local finite expansion

```text
f(s) ~= sum_n d_n (s-s0)^n / n!
```

with optional metadata saying how much finite-truncation error should be allowed.

## What this is

This is a practical Taylor-model-style scaffold:

- finite CNRS-H local jet;
- explicit expansion center inherited from the jet;
- optional remainder bound or last-retained-term indicator;
- basic propagation through addition, subtraction, and scalar multiplication;
- local diagnostic propagation for products;
- chain-rule comparison on the finite jet parts.

## What this is not

This is not interval arithmetic, a rigorous global convergence theorem, or a full analytic-continuation engine. Differentiation, integration, composition, and center shifting preserve the jet operation but mark the propagated bound as unknown unless a caller supplies a trusted bound.

## Example

```python
from cnrs.symbolic import Var, exp
from cnrs.cnrs_h_taylor_model import taylor_model_from_symbolic

s = Var("s")
model = taylor_model_from_symbolic(exp(s), s, center=0, order=8, sample_point=0.1)
value, radius = model.enclosure(0.1)
```

The `radius` returned here is a diagnostic error radius, normally derived from the last retained term unless explicitly supplied by the caller.
