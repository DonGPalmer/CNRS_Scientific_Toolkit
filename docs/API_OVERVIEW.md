# API Overview

This document gives a compact map of the CNRS Scientific Toolkit modules. It is not a full API reference; it is intended to help new readers find the relevant part of the codebase.

## Core CNRS-A representation and arithmetic

| Module | Purpose |
|---|---|
| `cnrs.cnrs_repr` | Gaussian-integer representation in base `z0 = -2+i` with digit alphabet `{0,1,2,3,4}`. |
| `cnrs.cnrs_add` | Addition via finite-state carry/transducer machinery. |
| `cnrs.cnrs_mul` | Multiplication via convolution and carry normalization. |
| `cnrs.cnrs_div` | Division by base powers and selected closed cases. |
| `cnrs.cnrs_ops` | High-level arithmetic wrappers. |
| `cnrs.cnrs_value` | Object-oriented wrapper for CNRS values. |

## Rational, approximate, and analytic-continuation components

| Module | Purpose |
|---|---|
| `cnrs.cnrs_rational` | Gaussian-rational expansions, including finite, periodic, and Laurent-periodic cases. |
| `cnrs.cnrs_float` | Experimental approximate CNRS floating-point representation. |
| `cnrs.cnrs_expansion` | Infinite-expansion scaffolding. |
| `cnrs.cnrs_continuation` | Analytic-continuation scaffolding. |
| `cnrs.cnrs_global_constraints` | Global constraint scaffolding. |
| `cnrs.cnrs_global_solver` | Global solver scaffolding. |

## CNRS-H calculus and operator systems

| Module | Purpose |
|---|---|
| `cnrs.cnrs_h` | CNRS-H EGF coefficient representation. Differentiation and integration are digit-shift operations. |
| `cnrs.cnrs_hstream` | H-stream representation. |
| `cnrs.cnrs_hstream_ops` | H-stream operations. |
| `cnrs.cnrs_operator` | Operator-calculus utilities. |
| `cnrs.cnrs_ode` | CNRS-H coefficient-recurrence ODE solvers. |

## Layered and branch-state objects

| Module | Purpose |
|---|---|
| `cnrs.cnrs_layer2` | Branch-index / logarithmic layer support. |
| `cnrs.cnrs_layer2_value` | Layer-2 value object. |
| `cnrs.cnrs_layer3` | Layer-3 analytic object scaffolding. |
| `cnrs.cnrs_layer3_ops` | Layer-3 operations. |
| `cnrs.cnrs_layer3_continuation` | Layer-3 continuation scaffolding. |
| `cnrs.cnrs_layer4` | Layer-4 state/value scaffolding. |

## Scientific toolkit modules

| Module | Purpose |
|---|---|
| `cnrs.cnrs_complex` | Complex-state interface and NumPy conversion helpers. |
| `cnrs.cnrs_scale` | Scale-law construction, fitting, differentiation, allometric analysis, and threshold detection. |
| `cnrs.cnrs_bio` | Gierer-Meinhardt biological scale dynamics and Turing-threshold utilities. |
| `cnrs.cnrs_oscillator` | Stuart-Landau, RLC, driven harmonic, and interference examples. |
| `cnrs.cnrs_interop` | NumPy/SciPy interoperability, comparison, and benchmark helpers. |
| `cnrs.cnrs_physics_check` | Analytic sanity checks for selected standard physics formulae. |

## `cnrs.science` namespace

| Module | Purpose |
|---|---|
| `cnrs.science.branch` | Branch-state workflow helpers. |
| `cnrs.science.observation` | Observation maps and reduction helpers. |
| `cnrs.science.scale_law` | Science-facing scale-law helpers. |
| `cnrs.science.three_workflows` | Three-workflow comparison helpers. |

## Examples

| Path | Purpose |
|---|---|
| `examples/demo.py` | Basic CNRS arithmetic/calculus demonstration. |
| `examples/quickstart_cnrs.py` | Minimal first-run script for new users. |
| `examples/scale_integration.py` | Scale-integration bridge example. |
| `examples/science_workflows/` | Scientific workflow demonstrations and benchmarks. |

## Tests

| Path | Purpose |
|---|---|
| `tests/` | Automated pytest suite. |
| `tests/test_cnrs_interop.py` | NumPy/SciPy interop checks. |
| `tests/test_physics.py` | Analytic formula sanity checks; these are representational checks, not new physical claims. |


## Chain-rule autodiff — v0.4.0

`cnrs.autodiff` adds a first-order automatic differentiation layer over `CnrsComplex`.

Main API:

```python
from cnrs.autodiff import (
    CnrsDual, derivative, value_and_derivative, compose,
    exp, log, sin, cos, tan, sqrt, pow_const,
)
```

Scope: scalar complex-valued functions of one scalar variable; arithmetic, elementary functions, nested composition, and simple branch-aware logarithm/square-root experiments.
