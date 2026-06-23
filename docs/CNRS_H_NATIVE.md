# CNRS-H native coefficient calculus (v0.10.0)

`CnrsHNative` is the native-coefficient CNRS-H object. Unlike `CnrsH`, which stores Python numeric coefficients, `CnrsHNative` stores each coefficient as a `CVal` CNRS-A digit string. All coefficient operations route through `add_cnrs` / `mul_cnrs`.

## Native operations

- **differentiation:** drop the constant coefficient (exact digit shift)
- **integration:** prepend the integration constant (exact digit shift)
- **coefficient addition:** CNRS-A addition through `CVal` (14-state FST)
- **coefficient negation:** multiplication by CNRS-A `−1 = "144"`
- **coefficient subtraction:** native addition after native negation
- **coefficient multiplication:** CNRS-A multiplication through `CVal`
- **EGF product:** binomial convolution in CNRS-A coefficient space
- **EGF composition:** finite-order Faà di Bruno / Bell-polynomial recurrence in CNRS-A coefficient space
- **EGF inversion:** Lagrange inversion recurrence in CNRS-A coefficient space (v0.10.0)

Evaluation at an ordinary real or complex point remains a bridge operation because the input point is not itself a CNRS-A value (EGF term denominators n! are periodic in base z₀ for n ≥ 2, so exact native evaluation would require infinite CNRS-A series).

## Lagrange inversion (v0.10.0)

`invert_native(f, order)` computes the compositional inverse g such that f(g(s)) = s. The recurrence is derived from Faà di Bruno's formula applied to f(g(s)) = identity:

```
g_1 = 1 / f_1
g_n = −(1/f_1) · Σ_{k=2}^n  f_k · B_{n,k}(g_1, …, g_{n-k+1})
```

where B_{n,k} are partial Bell polynomials. For k ≥ 2, B_{n,k} depends only on g_1,…,g_{n−k+1} ≤ g_{n−1}, so the entire computation is a single forward pass with no look-ahead. The Bell table is built incrementally alongside the g coefficients.

**Preconditions:** f(0) = 0 (necessary for a power-series inverse to exist) and f′(0) ∈ {1, −1, i, −i} (Gaussian integer units — non-unit f′(0) produces non-integer inverse coefficients not storable in `CVal`).

**Verification:** `verify_inversion(f, order)` composes f(g(s)) and checks the result equals the identity series at the digit-string level. The canonical test case — f(s) = exp(s)−1, g(s) = log(1+s) with g_n = (−1)^{n−1}·(n−1)! — gives `strings_match=True` and `max_error=0.0` to order 8.

## Dual-path adapter (v0.10.0)

`CnrsHMode` in `cnrs_h_mode.py` wraps either `CnrsH` (fast) or `CnrsHNative` and presents a uniform interface. Auto-selection uses `CnrsHNative` when all coefficients are Gaussian integers representable in CNRS-A, falling back to `CnrsH` silently otherwise. `ScaleLaw` and `OdeSolution` use `CnrsHMode` internally and expose `.native_mode`.

## Status

`CnrsHNative` supports the theoretical interpretation of CNRS-H as an internal coefficient-calculus layer. Composition and inversion are algorithmic-native (not finite-state-native). Evaluation remains a projection step, consistent with the architecture position that the coefficient layer is the native layer.

### Open items

- Formal proof of the carry-drain bound for `_normalize_coeffs` in multiplication (currently empirical: ≤ 12 steps for inputs up to ~10³ digits).
- Carry-set characterization for multiplication (analogue of the 14-state addition carry set).
- `CnrsFormalState.compose` for the general case g(0) ≠ 0 (shift-compose-shift).
