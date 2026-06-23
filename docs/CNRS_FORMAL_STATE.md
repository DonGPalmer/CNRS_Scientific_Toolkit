# CNRS* formal state (v0.8.1)

`CnrsFormalState` provides a compact code-level counterpart to the theoretical CNRS* state tuple:

```text
S = (a, k, h, x0, N, Omega)
```

where:

- `a` is a CNRS-A `CVal` value;
- `k` is branch or winding metadata;
- `h` is a CNRS-H-native coefficient object;
- `x0` is the expansion centre;
- `N` is the truncation order;
- `Omega` is local-domain metadata.

This object is intentionally lightweight. It is intended for theorem-aligned workflows, not as a replacement for the richer `CnrsScientificState` application object.
