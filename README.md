# cnrs — Complex Numeric Representational System

A Python implementation of the **CNRS** arithmetic and calculus framework.

**Base:** z₀ = −2 + i  (a Gaussian integer, N(z₀) = 5)  
**Digit alphabet:** D = {0, 1, 2, 3, 4}

In CNRS every Gaussian integer has a unique finite digit-string representation.
The system has two interlocking layers:

- **CNRS-A** — arithmetic layer: representation, addition via a 14-state
  finite-state transducer, multiplication via Cauchy convolution and carry
  normalisation, division, and subtraction.
- **CNRS-H** — calculus layer: EGF (exponential generating function)
  digit-string representation in which differentiation and integration are
  exact digit-shift operations with no floating-point approximation.

---

## Implementation maturity

The package is organised into three maturity tiers:

### Stable
Fully implemented, tested, and verified:

- Gaussian integer representation (`cnrs_repr`)
- Addition via 14-state finite-state transducer (`cnrs_add`)
- Multiplication via Cauchy convolution + carry normalisation (`cnrs_mul`)
- Finite Z[i][1/z₀] fractions (denominators that are pure powers of z₀)
- CNRS-H EGF digit-shift calculus (`cnrs_h`): 8 algebraic properties verified

### Experimental
Implemented, tested, and verified for representative cases:

- Gaussian rational expansion (`cnrs_rational`) — all three cases:
  finite Z[i][1/z₀], pure z₀-adic periodic (gcd(q,5)=1), and Laurent-periodic
  (denominator divisible by 5, e.g. 1/5, 1/10, 1/25).
  Use `z0_adic_value_fractions()` for fully exact results (returns `(Fraction, Fraction)`);
  `z0_adic_value_exact()` for high-precision complex; `z0_adic_value()` for fast float.
  Long periods require increasing `max_frac`; exhausting it raises `RuntimeError`.
- CNRS floating-point arithmetic (`cnrs_float`)
- H-streams and operator calculus (`cnrs_hstream`, `cnrs_operator`)
- Layer-2 branch index arithmetic (`cnrs_layer2`)

### Prototype / research sketch
Scaffolding for future work:

- Analytic continuation engine (`cnrs_expansion`, `cnrs_continuation`)
- Layer-3 / Layer-4 global analytic objects (`cnrs_layer3`, `cnrs_layer4`)
- Scale-integration physics bridge (`examples/scale_integration.py`)

---

## Known limitations

### Gaussian rational expansion: all cases now handled

`cnrs_rational.py` handles three cases:

1. **Finite** (Z[i][1/z₀]): values p/z₀ᵏ for p ∈ Z[i]. Expansion terminates.
   Evaluated via `evaluate()`.

2. **Pure z₀-adic periodic** (gcd(q, 5) = 1, e.g. 1/2, 1/3, 1/7):
   An infinite leftward series Σ dₖ z₀ᵏ, analogous to p-adic integers.
   Evaluated via `CnrsRational.z0_adic_value()` using the rational closed form —
   not by summation (the series diverges in ℂ since |z₀| > 1).

3. **Laurent-periodic z₀-adic** (q divisible by 5, e.g. 1/5, 1/10, 1/25):
   Uses the identity p/q = z₀⁻ˢ · p/(z̄₀ˢ r) where q = 5ˢ r, gcd(r,5) = 1.
   The Gaussian denominator Q = z̄₀ˢ r is coprime to z₀, so the z₀-adic
   algorithm applies. Stored with `power_offset = -s < 0`.
   Evaluated via `CnrsRational.z0_adic_value()`.

**Note.** The periodic z₀-adic value is assigned by the rational closed form
S = block + z₀ᵀ S, not by series convergence. Documentation says
"evaluated by its rational closed form," not "converges in ℂ."

Use `CnrsFloat` for approximate floating-point representation of general
complex values.

### InfiniteExpansion analytic continuation

`cnrs_expansion.py` applies the greedy algorithm to non-integer targets. The
algorithm is correct in structure but is only reliable for values already
in Z[i] or Z[i][1/z₀]. For other targets the expansion does not converge
to the intended value.

---

## Mathematical background

The base z₀ = −2 + i satisfies:

```
N(z₀) = (-2)² + 1² = 5
```

Every Gaussian integer z ∈ ℤ[i] has a unique representation

```
z = d₀ + d₁·z₀ + d₂·z₀² + … + dₙ·z₀ⁿ,    dₖ ∈ {0,1,2,3,4}
```

obtained by the greedy remainder algorithm. The 14-state addition transducer
is derived from the finite symbolic cover of the toral automorphism associated
with the characteristic polynomial h(u) = u² + 4u + 5.

The CNRS-H layer uses factorial-weighted place values

```
f(ρ) = Σ dₙ · ρⁿ / n!
```

so that differentiation corresponds exactly to dropping the leading digit,
and integration to prepending a constant digit. Eight algebraic properties
are verified in the test suite (Leibniz rule, fundamental theorem of calculus,
linearity, EGF multiplication, scale input, etc.).

---

## Installation

No external dependencies are required for the core package. Python ≥ 3.9.

```bash
git clone https://github.com/<username>/cnrs-python.git
cd cnrs-python
pip install -e ".[dev]"
```

---

## Quick start

```python
import cnrs

# Represent a Gaussian integer
s = cnrs.gaussian_to_cnrs_str(3 + 2j)   # -> '1332'
z = cnrs.cnrs_to_gaussian(s)             # -> (3+2j)

# Addition via 14-state transducer
a = cnrs.gaussian_to_cnrs_str(3 + 2j)   # '1332'
b = cnrs.gaussian_to_cnrs_str(1 + 1j)   # '13'
c = cnrs.cnrs_add(a, b)                  # '1200' (represents 4+3j)

# Multiplication via convolution + carry normalisation
c = cnrs.cnrs_mul(a, b)                  # represents (3+2j)*(1+1j) = 1+5j

# CNRS-H calculus: exact digit-shift differentiation
f  = cnrs.CnrsH((1, 1, 1, 1))           # truncated e^ρ (4 terms)
df = f.differentiate()                   # exact: drop leading digit
print(df.coeffs)                         # (1, 1, 1)

# Euler's formula to 20 terms
import math
coeffs = tuple(1j**k for k in range(20))
exp_i  = cnrs.CnrsH(coeffs)
print(exp_i.evaluate(math.pi) + 1)      # ≈ 0 to ~1e-14
```

---

## Running the demo

```bash
python examples/demo.py
```

The demo walks through representation, addition, multiplication, and CNRS-H
digit-shift calculus including Euler's formula.

---

## Running the tests

```bash
pytest
```

**79 tests, 0 failures.** All Gaussian rational cases pass including
Laurent-periodic denominators divisible by 5, long-period cases (1/23,
period 528), and RuntimeError on insufficient max_frac.

| Test file | Coverage |
|---|---|
| `tests/test_arithmetic.py` | Representation round-trip, addition (14-state transducer), multiplication (convolution + normalisation), Layer-2 branch arithmetic |
| `tests/test_cnrs_h.py` | 8 algebraic properties: exact differentiation, integration, FTC, Leibniz rule, linearity, nth derivative, EGF multiplication, scale input |
| `tests/test_expansion.py` | InfiniteExpansion (E1–E5 for Gaussian integers), CnrsRational (R1–R7 for exact finite cases) |
| `tests/test_rational_all_cases.py` | Pure z₀-adic and Laurent-periodic Gaussian rationals; exact `Fraction` equality; long-period 1/23 (period 528); `RuntimeError` on insufficient `max_frac` |

Additional rational tests are in `tests/test_rational_all_cases.py`. These cover
pure z₀-adic rationals, Laurent-periodic denominators divisible by 5, exact
`Fraction` evaluation, long-period cases such as 1/23 (period 528), and
`RuntimeError` behavior when `max_frac` is too small.

---

## Package structure

```
cnrs/
├── cnrs_repr.py               # base, digits, greedy representation       [stable]
├── cnrs_add.py                # 14-state addition transducer               [stable]
├── cnrs_mul.py                # Cauchy convolution + carry normalisation   [stable]
├── cnrs_div.py                # division by base, base powers, units       [stable]
├── cnrs_ops.py                # high-level arithmetic (add/sub/mul/neg/eq) [stable]
├── cnrs_value.py              # CVal convenience wrapper                   [stable]
├── cnrs_h.py                  # CNRS-H calculus layer (CnrsH class)        [stable]
├── cnrs_hstream.py            # H-streams (extendable digit prefixes)      [experimental]
├── cnrs_hstream_ops.py        # arithmetic on H-streams                    [experimental]
├── cnrs_operator.py           # shift operators, discrete Δ and Σ          [experimental]
├── cnrs_expansion.py          # InfiniteExpansion (prototype)              [prototype]
├── cnrs_continuation.py       # analytic continuation rules/engine         [prototype]
├── cnrs_rational.py           # CnrsRational: all Gaussian rationals               [experimental]
│                              #   finite / pure z0-adic / Laurent-periodic; exact via Fraction
├── cnrs_float.py              # CnrsFloat (floating-point in base z₀)      [experimental]
├── cnrs_layer2.py             # (digit string, branch index) pairs         [experimental]
├── cnrs_layer2_value.py       # L2Val wrapper                              [experimental]
├── cnrs_layer3.py             # unified analytic object (L3Value)          [prototype]
├── cnrs_layer3_continuation.py                                             [prototype]
├── cnrs_layer3_ops.py                                                      [prototype]
├── cnrs_layer4.py             # global analytic object (L4Value, L4State)  [prototype]
├── cnrs_global_constraints.py # reusable analytic constraints              [prototype]
└── cnrs_global_solver.py      # global solver for L4 objects               [prototype]
```

---

## Relationship to published papers

This implementation accompanies the CNRS research programme by Donald G. Palmer
(ORCID: [0000-0003-4335-5533](https://orcid.org/0000-0003-4335-5533)).
Preprints are deposited to Zenodo (CERN):

| Module | Paper / result | Status |
|---|---|---|
| `cnrs_repr`, `cnrs_add` | CNRS Problem 3: arithmetic closure; 14-state transducer | Stable |
| `cnrs_h` | CNRS Problem 4 Q3c: digit-shift = d/dρ (EGF sense) | Stable |
| `cnrs_rational` | Finite, pure z₀-adic, and Laurent-periodic Gaussian rational representation | Experimental |
| `cnrs_float` | CNRS floating-point extension | Experimental |

---

## Citation

```bibtex
@software{palmer2026cnrs,
  author  = {Palmer, Donald G.},
  title   = {cnrs: Complex Numeric Representational System (Python implementation)},
  year    = {2026},
  orcid   = {0000-0003-4335-5533},
  url     = {https://github.com/<username>/cnrs-python}
}
```

---

## Licence

MIT — see `LICENSE`.
---

# CNRS Scientific Toolkit Layer

This merged package includes AI0's CNRS v6.1 base plus the `cnrs.science`
workflow layer from CNRS Scientific Toolkit v0.1.

## Added science-layer modules

```text
cnrs/science/branch.py
cnrs/science/observation.py
cnrs/science/scale_law.py
cnrs/science/three_workflows.py
```

## Purpose

The science layer supports complex-state-preserving workflows:

```text
ordinary scientific input
  -> CNRS exact / float / complex / ODE / branch / H-calculus representation
  -> explicit observation maps
  -> ordinary real/complex/decimal output
```

## Example commands

```bash
python -m pytest -q
python examples/science_workflows/interference_three_workflows.py
python examples/science_workflows/complex_scale_law.py
python examples/science_workflows/phase_branch_tracking.py
```

## Relationship to v6.1

v6.1 adds:
- Laurent-periodic rational support in `cnrs_rational.py`;
- `CnrsComplex` as a clean scientific interface over CNRS-float;
- CNRS-H based linear ODE solvers in `cnrs_ode.py`;
- a much larger pytest suite including rational, complex, ODE, and limitation tests.

The merged science layer adds:
- branch-aware value objects;
- observation maps;
- CNRS-H scale-law utilities;
- three-workflow comparison harnesses;
- examples aimed at complex-state preservation.
