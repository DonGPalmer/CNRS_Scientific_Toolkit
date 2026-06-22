# Release Notes

## v0.4.0 — Chain Rule Automatic Differentiation

This release adds first-order chain-rule capability for CNRS scientific workflows.

### Added

- `cnrs/autodiff.py`: dual-number style automatic differentiation over `CnrsComplex`.
- `CnrsDual`: carries `(value, derivative)` and propagates derivatives through arithmetic.
- Chain-rule elementary functions: `exp`, `log`, `sin`, `cos`, `tan`, `sqrt`, and scalar/dual powers.
- Convenience helpers: `derivative`, `value_and_derivative`, `compose`, `pow_const`.
- `tests/test_autodiff_chain_rule.py`: analytic regression tests for addition, product, quotient, elementary functions, nested composition, branch-aware logarithm, and scale-law derivatives.
- `examples/science_workflows/chain_rule_scale_law.py`: runnable demonstration of nested chain-rule, exponential scale laws, and scale-transform derivatives.

### Changed

- Updated package metadata to `0.4.0`.
- Exported the autodiff layer from `cnrs.__init__` with explicit `autodiff_*` function aliases to avoid name collisions.
- Fixed `examples/scale_integration.py` import path so it runs directly from the repository root.
- Removed generated `__pycache__` files from the release archive.

### Validation

```text
733 passed, 6 xfailed
```

The 6 expected failures remain known representational-limit tests, not regressions.

## v0.3.0 — Multi-Scale Physics Engine (Components 7 and 8)

Two new scientific toolkit components extending CNRS into Scale Space
physics computation and scale-aware regime detection.

### New modules

**`cnrs/cnrs_multiscale.py` — Component 7: Multi-scale SS physics engine**

`ScaleLadder` runs CNRS-H EGF streams across the scale ladder (scale as a
coordinate in the (x,y,z,s) framework), propagating boundary values between
rungs with machine precision via coefficient arithmetic.

- Three constructors:
  - `ScaleLadder.uniform(lam, y0, s_total, n_rungs)` — constant eigenvalue,
    equal-width rungs; the simplest case
  - `ScaleLadder.from_profile(lam_profile, y0, s_edges)` — scale-dependent
    eigenvalue λ(s); models physics where effective coupling changes with scale
  - `ScaleLadder.from_solutions(solutions, s_edges)` — from pre-built
    `OdeSolution` objects; allows mixed rung types (linear, driven, second-order)

- Seven scale-aware observable maps (all using exact digit-shift within each rung):
  `modulus_sq`, `real_part`, `imag_part`, `phase`, `phase_rate`,
  `phase_current`, `scale_derivative`

- `LadderEvalResult` — full evaluation record with rung index, local s,
  and all five observable maps

- `scale_gradient_correction(ladder, s, delta_s)` — Paper 18, Theorem 1:
  effective diffusion ratio d_eff at scale s; validated against exact
  analytical formula exp(Re(λ)·δs)

- `ladder_profile(ladder, s_vals, observable)` — evaluate any observable
  across a numpy array of s values for plotting or fitting

- `ladder_to_scalelaws(ladder)` — convert each rung to a `ScaleLaw` for
  use with the `cnrs_scale` fitting and Turing-threshold machinery

- Placeholder stubs for Thread 5 / items (c)–(e) — await GR specialist:
  `JunctionCondition`, `FieldEquationCheck`, `PsiZeroDeterminer`

65 tests, all passing.

**`cnrs/cnrs_regime.py` — Component 8: Scale-sweep and regime detection**

Lightweight wrapper layer around arbitrary scientific models that makes
parameters explicit functions of logarithmic scale, sweeps across scale
intervals, and detects regime transitions.

Design credit: AI1 proposed the core abstraction (`ScaleParameter`,
`ScaleSweep`, `RegimeTransition`, `detect_transitions`) in the June 2026
multi-scale modelling review. This implementation adapts that design to the
toolkit naming convention and adds an explicit bridge to Component 7.

- `ScaleParameter(base, coefficients)` — parameter as polynomial in s:
  p(s) = base · (1 + c₁s + c₂s² + ...). Optional `enforce_positive` guard.

- `ScaleSweep(model, parameters, s_min, s_max, n, classifier)` — general
  constructor; model is any callable (s, params) → output

- `ScaleSweep.from_ladder(ladder, classifier, n)` — bridge constructor;
  model is a `ScaleLadder`; classifier operates on `LadderEvalResult` objects,
  giving the full chain from CNRS-H exact physics to regime classification

- `ScaleSweepResult` — `.scales`, `.outputs`, `.regime`, `.transitions`,
  `.active_intervals()` for identifying pattern-forming windows

- `RegimeTransition` — detected boolean state change with `.midpoint`

- `detect_transitions(scales, states)` — detect regime changes across a
  scale sequence

- Coordinate utilities: `logarithmic_scale(L, L_ref)` and
  `length_from_scale(s, L_ref)` for conversion between physical length
  and scale coordinate (nats)

67 tests, all passing.

### New example

**`examples/science_workflows/cnrs_multiscale_turing_window.py`**

Three-part demonstration:

- Part A: `ScaleLadder` + `ScaleSweep.from_ladder()` — the CNRS-H exact
  physics path; identifies the Turing-active window (|Ψ|² above threshold)
  from the decaying-oscillatory activator mode
- Part B: `ScaleParameter` + `ScaleSweep` — the AI1 scalar parameter path;
  same Turing window via scale-dependent diffusion ratios
- Part C: `logarithmic_scale` / `length_from_scale` roundtrip table

### Architecture note

Components 7 and 8 form a two-layer stack:

```
cnrs_multiscale.ScaleLadder   (exact CNRS-H physics; scale ladder)
         ↓
cnrs_regime.ScaleSweep        (scale sweep + regime classification)
         ↓
RegimeTransition / active_intervals  (transition detection)
```

`ScaleSweep.from_ladder()` connects the two layers directly.

### Connection to Scale Space programme

Component 7 implements items (a) and (b) of the proposed SS physics engine:

- (a) Scale-indexed solution container — `ScaleLadder` ✓
- (b) Scale-aware observable maps with exact s-derivatives — ✓
- (c) Junction conditions at scale boundaries — scoped; awaits Thread 5
- (d) 5D field equation and FLRW verification — scoped; awaits Thread 5
- (e) Ψ₀ determination (Paper 22) — scoped; awaits Thread 5

The junction-condition mathematics (item c) is the same problem as the
Thread 5 GR specialist work blocking Papers 21 and 22, approached from
the computational rather than analytical direction.

### Test count

```text
v0.2.2:  624 passed, 6 xfailed
v0.3.0:  719 passed, 6 xfailed   (+95 new tests)
```

### New module (AI1 contribution)

**`cnrs/cnrs_rd_scale_exit.py` — Reaction-diffusion scale-exit analysis**

A focused diagnostic layer for two-species reaction-diffusion systems
with scale-dependent diffusion coefficients. Does not solve the full PDE;
answers the narrow question: at which scales is the homogeneous state
linearly Turing-unstable?

- `RDLinearKinetics` — 2×2 linearized reaction matrix with `trace`,
  `determinant`, and `homogeneous_stable()` properties
- `ExponentialDiffusionLaw` — D(s) = D₀·exp(λ_s·s)
- `turing_thresholds(kinetics)` — discriminant roots d_low, d_high
  (recovers Paper 18 values: d_low=0.2154, d_high=41.785)
- `turing_diagnostic(kinetics, d_u, d_v, s)` — full Turing point
  evaluation at one scale: ratio, active flag, q*, margin
- `scan_scale_exit(kinetics, d_u, d_v, s_min, s_max, n)` — sweeps scale
  interval with bisection-refined transition detection (48 steps)
- `exponential_gm_scale_exit(...)` — convenience wrapper for exponential
  diffusion laws; recovers s_exit ≈ 0.5236 nats for GM default parameters
- `gm_default_kinetics()` — lazy import of GM default from `cnrs_bio`
  (avoids circular import)

6 tests, all passing. Reproduces Paper 18 scale-exit value exactly.

Design note: `cnrs_rd_scale_exit` sits at the boundary of Components 7 and 8 —
it is a specialised multi-scale diagnostic that could in future be connected
to `ScaleLadder` (for exact CNRS-H field propagation) and `ScaleSweep`
(for regime classification). Currently it operates as a standalone layer.

### Files added or changed

```
cnrs/__init__.py                              updated (new exports)
cnrs/cnrs_multiscale.py                       new (Component 7)
cnrs/cnrs_regime.py                           new (Component 8)
cnrs/cnrs_rd_scale_exit.py                         new (AI1; RD scale-exit)
tests/test_cnrs_multiscale.py                 new (65 tests)
tests/test_cnrs_regime.py                     new (67 tests)
tests/test_cnrs_rd_scale_exit.py                   new (6 tests; AI1)
examples/science_workflows/cnrs_multiscale_turing_window.py  new
examples/science_workflows/cnrs_rd_scale_exit_demo.py  new (AI1)
docs/RD_SCALE_EXIT.md                         new (AI1)
pyproject.toml                                version → 0.3.0
RELEASE_NOTES.md                              updated
SOURCE_INDEX.txt                              updated
```

---

## v0.2.2 — Zenodo integration and metadata correction

GitHub–Zenodo integration enabled. Future tagged releases auto-deposit
to Zenodo.

- Concept DOI: `10.5281/zenodo.20574852`
- Version DOI (v0.2.2): `10.5281/zenodo.20574853`
- `pyproject.toml` Zenodo URL corrected to concept DOI
- `README.md` Zenodo badge updated to concept DOI
- CNRS User Guide (zenodo.19797882) retired; toolkit is now the canonical
  software reference for the CNRS programme

No code changes from v0.2.0.

---

## v0.2.0 — AI0 interoperability/example merge

This update keeps the public version at `0.2.0` and extends the research-code
package with interoperability, additional examples, and documentation
organization.

### Documentation and quickstart additions

Added contributor and orientation material before the public GitHub update:

```text
CONTRIBUTING.md
docs/RESEARCH_STATUS.md
docs/API_OVERVIEW.md
examples/README.md
examples/quickstart_cnrs.py
```

`README.md` now links to the new documentation map and includes the quickstart
script in the first-run commands.

### New module

**`cnrs_interop.py` — NumPy/SciPy interoperability bridge**

Provides:
- `CnrsH` → NumPy array conversion
- NumPy array → `CnrsH` EGF fitting
- `OdeSolution` → SciPy-compatible result bundle
- SciPy `solve_ivp` output → `CnrsH` stream fitting
- Vectorized observation-map arrays: real, imaginary, modulus, modulus
  squared, phase, phase rate
- Side-by-side CNRS-H vs SciPy comparisons
- Timing benchmark helpers
- Optional pandas DataFrame export

### New examples

```text
examples/science_workflows/cnrs_vs_scipy_benchmark.py
examples/science_workflows/rlc_three_workflows.py
examples/science_workflows/turing_scale_exit.py
```

These are research demonstrations, not claims of completed scientific
validation.

### New tests

```text
tests/test_cnrs_interop.py
tests/test_physics.py
```

`test_physics.py` checks standard QM and GR analytic formulae represented as
CNRS-H EGF streams. These tests validate representation and digit-shift
calculus against known formulae; they are not new physical claims.

### Documentation reorganization

Created `docs/` and moved status files there:

```text
docs/CLAIM_STATUS.md
docs/TEST_STATUS.md
docs/EXAMPLE_SMOKE_STATUS.md
```

`README.md` now explicitly describes the repository as an open research-code
package and links to the moved status documents.

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
- `compare_turing_workflows()` — three-workflow comparison

57 tests, all passing.

**`cnrs_oscillator.py` — Complex oscillators**

Named oscillator models implemented via CNRS-H coefficient recurrence:
- `StuartLandauParams`, `RlcParams`, `DrivenParams` — parameter dataclasses
- `stuart_landau_linear()`, `rlc_free()`, `rlc_driven()`,
  `driven_harmonic()`, `interference_pair()`

All return `OscillatorSolution` with observable maps: `modulus`,
`modulus_sq`, `real_part`, `imag_part`, `phase`, `instantaneous_frequency`,
`energy_proxy`, `derivative()`.

Three-workflow comparisons showing what early real reduction loses vs.
full complex-state preservation.

68 tests, all passing.

### Bug fix

`cnrs_ode.py` — `OdeSolution.evaluate()` now correctly handles a complex
argument when comparing `s` against `s_max`.

### Test count

```text
v0.1.0:  260 passed, 6 xfailed
v0.2.0:  442 passed, 6 xfailed   (+182 new tests)
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
