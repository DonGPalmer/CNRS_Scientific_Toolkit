# Release Notes

## v0.2.0 — AI0 interoperability/example merge

This update keeps the public version at `0.2.0` and extends the research-code package with interoperability, additional examples, and documentation organization.


### Documentation and quickstart additions

Added contributor and orientation material before the public GitHub update:

```text
CONTRIBUTING.md
docs/RESEARCH_STATUS.md
docs/API_OVERVIEW.md
examples/README.md
examples/quickstart_cnrs.py
```

`README.md` now links to the new documentation map and includes the quickstart script in the first-run commands.

### New module

**`cnrs_interop.py` — NumPy/SciPy interoperability bridge**

Provides:
- `CnrsH` → NumPy array conversion
- NumPy array → `CnrsH` EGF fitting
- `OdeSolution` → SciPy-compatible result bundle
- SciPy `solve_ivp` output → `CnrsH` stream fitting
- Vectorized observation-map arrays: real, imaginary, modulus, modulus squared, phase, phase rate
- Side-by-side CNRS-H vs SciPy comparisons
- Timing benchmark helpers
- Optional pandas DataFrame export

### New examples

```text
examples/science_workflows/cnrs_vs_scipy_benchmark.py
examples/science_workflows/rlc_three_workflows.py
examples/science_workflows/turing_scale_exit.py
```

These are research demonstrations, not claims of completed scientific validation.

### New tests

```text
tests/test_cnrs_interop.py
tests/test_physics.py
```

`test_physics.py` checks standard QM and GR analytic formulae represented as CNRS-H EGF streams. These tests validate representation and digit-shift calculus against known formulae; they are not new physical claims.

### Documentation reorganization

Created `docs/` and moved status files there:

```text
docs/CLAIM_STATUS.md
docs/TEST_STATUS.md
docs/EXAMPLE_SMOKE_STATUS.md
```

`README.md` now explicitly describes the repository as an open research-code package and links to the moved status documents.

### Test count

```text
559 passed, 6 xfailed
```

---


## v0.2.0 — Scale Laws, Biological Dynamics, Complex Oscillators

Three new scientific toolkit components, plus a bug fix in the ODE solver.

### New modules

**`cnrs_scale.py` — Scale-law toolkit**

`ScaleLaw` wraps a CNRS-H EGF stream and provides:
- Construction: `.exponential()`, `.from_coeffs()`, `.from_cnrsh()`
- Exact calculus: `.derivative()` and `.integral()` via digit shift
- Log-derivative `f'(s)/f(s)` (allometric exponent proxy)
- Six observable maps: `modulus`, `modulus_sq`, `real_part`, `imag_part`,
  `phase`, `phase_rate`
- Domain warning when evaluating outside reliable EGF range

Fitting functions:
- `fit_exponential(s, y)` → `FitResult`
- `fit_egf(s, y, degree)` → `ScaleLaw` (polynomial EGF fit)
- `fit_allometric(s, y)` → `AllometricResult` with exponent, amplitude, R²

Threshold detection:
- `turing_threshold(law, threshold, s_lo, s_hi)` → `TuringResult`
  with `s_exit` located by bisection

57 tests, all passing.

**`cnrs_bio.py` — Biological scale dynamics**

Gierer-Meinhardt activator-inhibitor model in the CNRS-H multi-scale
framework (Paper 18):
- `GmParams` dataclass (nondimensional GM parameters, Paper 18 defaults)
- `da_profile()`, `dh_profile()`, `d_ratio()` — diffusion profiles as ScaleLaws
- `gm_steady_state()`, `gm_jacobian()` — kinetics at homogeneous steady state
- `turing_discriminant()` — discriminant roots d_lo, d_hi (recovers Paper 18
  values: d_lo = 0.2154, d_hi = 41.785 for default parameters)
- `find_s_exit()` — Turing extinction scale (recovers s_exit ≈ 0.52 nats)
- `d_eff()` — effective diffusion ratio with first-order scale-gradient
  correction (Paper 18, Theorem 1)
- `turing_profile()` — scale-resolved active/inactive map
- `compare_turing_workflows()` — three-workflow comparison showing how
  scale gradients shift s_exit

57 tests, all passing.

**`cnrs_oscillator.py` — Complex oscillators**

Named oscillator models implemented via CNRS-H coefficient recurrence:
- `StuartLandauParams`, `RlcParams`, `DrivenParams` — parameter dataclasses
- `stuart_landau_linear()` — linear-regime Hopf normal form
- `rlc_free()` — free RLC series circuit
- `rlc_driven()` — driven RLC near resonance
- `driven_harmonic()` — driven harmonic oscillator
- `interference_pair()` — two-oscillator superposition

All return `OscillatorSolution` with observable maps: `modulus`,
`modulus_sq`, `real_part`, `imag_part`, `phase`, `instantaneous_frequency`,
`energy_proxy`, `derivative()`.

Three-workflow comparisons:
- `compare_stuart_landau()` — shows omega invisible in early |z|²
- `compare_rlc()` — shows oscillation invisible in early |q|²
- `compare_interference()` — shows beat frequency lost in incoherent sum

68 tests, all passing.

### Bug fix

`cnrs_ode.py` — `OdeSolution.evaluate()` now correctly handles a complex
argument when comparing `s` against `s_max`. Previously raised `TypeError`
when called from oscillator derivative chains.

### Test count

```text
v0.1.0:  260 passed, 6 xfailed
v0.2.0:  442 passed, 6 xfailed   (+182 new tests)
```

### Files changed

```
cnrs/__init__.py          updated (new exports)
cnrs/cnrs_ode.py          bug fix (complex vs float comparison)
cnrs/cnrs_scale.py        new
cnrs/cnrs_bio.py          new
cnrs/cnrs_oscillator.py   new
tests/test_cnrs_scale.py  new (57 tests)
tests/test_cnrs_bio.py    new (57 tests)
tests/test_cnrs_oscillator.py  new (68 tests)
pyproject.toml            version 0.1.0 → 0.2.0
RELEASE_NOTES.md          updated
TEST_STATUS.md            updated
```

---

## v0.1.0 — Initial CNRS Scientific Toolkit release

First public release. Highlights:

```text
CNRS-A finite complex-base representation over z0 = -2+i
CNRS addition and multiplication
Gaussian rational representation (periodic and Laurent-periodic)
CNRS-float approximate complex representation
CnrsComplex scientific interface
CNRS-H coefficient calculus
CNRS-H linear ODE solvers
Branch-aware complex-state helpers
Observation-map utilities
Scale-law fitting and differentiation
Three-workflow scientific comparison examples
260 passing tests, 6 expected limitation markers
```
