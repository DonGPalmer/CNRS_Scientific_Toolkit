# CNRS-H Domain and Convergence Diagnostics — v0.5.3

v0.5.3 adds lightweight domain metadata for CNRS-H local jets.  A jet is still a finite local coefficient object,

```text
f(s) ~= sum_n d_n (s-s0)^n / n!
```

but it can now carry conservative information about where that local expansion should be trusted.

## Main objects

```python
from cnrs.cnrs_h_domain import CnrsHDomain, infer_symbolic_domain
from cnrs.cnrs_h_jet import jet_from_symbolic
from cnrs.symbolic import Var, log, exp
```

`CnrsHDomain` records:

- `radius`: distance from the expansion center to the nearest known singularity, or `inf` for known-entire supported expressions;
- `singularities`: known singular or branch points in the expansion variable plane;
- `note`: short explanation of the inference;
- `confidence`: `known`, `hint`, or `unknown`.

## Example

```python
s = Var("s")
j = jet_from_symbolic(log(1 + s), s, center=0, order=8)

print(j.domain.radius)          # 1.0
print(j.domain.singularities)   # (-1+0j,)
print(j.valid_for(0.25))        # True
print(j.valid_for(1.25))        # False
```

For entire supported functions:

```python
j = jet_from_symbolic(exp(0.1*s), s, center=-12, order=8)
print(j.domain.is_entire)       # True
```

## Truncation indicator

The method

```python
j.estimate_truncation_error(point)
```

returns the magnitude of the last retained EGF term at the requested point.  This is not a rigorous bound; it is a diagnostic signal for whether increasing the order materially changes the local expansion.

## Scope

This layer is intentionally conservative.  It provides local radius/singularity metadata for supported expression classes.  It does not yet provide:

- rigorous interval or ball-arithmetic bounds;
- automatic proof of convergence for arbitrary expressions;
- global analytic continuation;
- path-dependent branch/winding tracking;
- certified error envelopes.

Those are later milestones.  v0.5.3's role is to stop finite local jets from looking global by default.
