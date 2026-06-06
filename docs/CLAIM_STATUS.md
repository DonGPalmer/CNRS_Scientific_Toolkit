# Claim Status

This file summarizes the current status of CNRS Scientific Toolkit claims
for readers, reviewers, and contributors.

## Tested in the package

The package currently includes tests covering:

```text
CNRS base value and norm
Gaussian-integer representation and round-trip behaviour
CNRS-A addition and multiplication semantics
Layer-2 branch-index arithmetic
CNRS-H coefficient-shift differentiation and integration
CNRS-float encode/decode behaviour
Gaussian rational arithmetic (periodic and Laurent-periodic)
CnrsComplex interface behaviour
CNRS-H ODE solvers
Observation-map workflows
Branch / winding workflows
ScaleLaw: construction, fitting, derivative, allometric, Turing threshold
Biological scale dynamics: Gierer-Meinhardt, d_ratio, s_exit, d_eff
Complex oscillators: Stuart-Landau, RLC, driven harmonic, interference
NumPy/SciPy interoperability bridge and benchmarks
Standard QM and GR solutions as CNRS-H EGF streams (hydrogen, QHO, Schwarzschild)
Three-workflow comparison examples
```

The current test status is:

```text
559 passed, 6 xfailed
```

Breakdown by module:

```text
test_arithmetic.py             existing
test_cnrs_complex.py           63 tests
test_cnrs_h.py                 existing
test_cnrs_ode.py               36 tests
test_expansion.py              existing
test_evaluate_limitations.py   6 xfailed + 18 passing
test_rational_all_cases.py     existing
test_rational_arithmetic.py    38 tests
test_science_toolkit.py        existing
test_tc_equations.py           19 tests
test_cnrs_scale.py             57 tests  (v0.2.0)
test_cnrs_bio.py               57 tests  (v0.2.0)
test_cnrs_oscillator.py        68 tests  (v0.2.0)
test_cnrs_interop.py           51 tests  (v0.2.0)
test_physics.py                66 tests  (v0.2.0)
```

The expected failures document known boundaries and limitation cases.

## Practical capabilities

The package currently supports practical experimentation with:

```text
Exact finite Gaussian-integer CNRS arithmetic
CNRS-float approximate complex representation
Gaussian rational CNRS representations
CNRS-H coefficient calculus (differentiation and integration as digit shift)
Linear ODE solution through CNRS-H coefficient recurrences
Second-order ODE and driven ODE solvers
Branch-aware complex-state bookkeeping
Observation maps: Re, Im, |z|, |z|², phase, phase-current proxy

Scale-law toolkit (ScaleLaw):
  - Construction from exponential, EGF coefficients, or CnrsH stream
  - Exact digit-shift derivative and integral
  - Log-derivative (allometric exponent proxy)
  - Fitting: exponential, EGF polynomial, allometric (power-law)
  - Turing threshold detection via bisection

Biological scale dynamics (GmParams, da_profile, d_ratio, ...):
  - Scale-dependent Gierer-Meinhardt diffusion profiles as ScaleLaws
  - Turing discriminant roots d_lo, d_hi (Paper 18 parameters verified)
  - s_exit detection (≈ 0.52 nats for default parameters)
  - Scale-gradient correction d_eff (Paper 18, Theorem 1)
  - Three-workflow comparison for Turing threshold

Complex oscillators (StuartLandauParams, RlcParams, DrivenParams, ...):
  - Stuart-Landau linear regime (exact CNRS-H)
  - RLC free and driven
  - Driven harmonic oscillator
  - Two-oscillator interference (beat frequency preserved)
  - Three-workflow comparison showing information loss in early reduction

NumPy/SciPy interoperability (cnrs_interop):
  - CnrsH ↔ numpy round-trip (evaluate and fit)
  - OdeSolution → scipy-compatible Bunch
  - scipy solve_ivp output → CnrsH stream
  - Vectorised observation-map extractors
  - Side-by-side CNRS-H vs scipy.integrate.solve_ivp benchmark
  - Optional pandas DataFrame export

Standard physics verification (test_physics):
  - QHO ψ_0, ψ_1 values and derivatives via CNRS-H
  - QHO energy eigenvalues encoded as EGF phase rates
  - Hydrogen 1s and 2s radial wavefunctions and derivatives
  - Schwarzschild g_tt and g_rr^{-1} values and derivatives
  - Effective potential V_eff and circular orbit condition
  - Weak-field EGF coefficient correspondence to Newtonian potential

Three-workflow comparisons:
  A = early real reduction
  B = ordinary complex late reduction
  C = CNRS complex-state late reduction
```

## Scientific use case

The strongest current use case is **complex-state preservation**.

Many scientific calculations eventually produce real-valued observables,
but the working state may be complex-valued. Early reduction to real
quantities can discard phase, branch, winding, interference, and
observation-map information. The CNRS Scientific Toolkit provides tools
for keeping the complex state available until the appropriate observation
map is chosen.

The scipy interoperability bridge (v0.2.0) makes this practical: CNRS-H
results can be passed directly to numpy/scipy functions, or scipy results
can be imported into CNRS-H streams for exact digit-shift differentiation.

## Open development areas

Useful next development targets include:

```text
Direct CNRS Layer-2 analytic-continuation workflows
Performance and stability comparisons at larger term counts
Expanded PDE benchmark systems (reaction-diffusion, wave equation)
CNRS-H convergence radius estimation improvements
Contributor documentation
```

## Contributor orientation

This repository is intended to support inspection, testing, extension,
and critique. Contributions that add tests, examples, benchmarks,
documentation, or clearer mathematical boundaries are especially valuable.

The GitHub repository is at: https://github.com/DonGPalmer/CNRS_Scientific_Toolkit
Programme landing page: https://www.nul1.com
