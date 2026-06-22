
# v0.7.0 — CNRS-native scientific state

Added a consolidated `CnrsScientificState` object for science workflows.  The
state object keeps CNRS-H local jets as the primary representation and carries
source expressions, scale units, branch/path metadata, local-domain metadata,
claim-status labels, and observation maps.

Added:

- `cnrs/cnrs_scientific_state.py`
- `cnrs/science/state.py`
- `tests/test_cnrs_scientific_state.py`
- `examples/science_workflows/cnrs_scientific_state_demo.py`
- `docs/CNRS_SCIENTIFIC_STATE.md`

This release marks the start of the v0.7 line: native scientific objects built
on top of the CNRS-H calculus spine.

# Release Notes

## v0.7.0 — CNRS-H Branch-Aware Local Continuation

v0.7.0 adds a conservative branch-aware continuation rebuild layer. In v0.6.2, continuation paths updated branch-state metadata on `CnrsHJet`. In v0.7.0, `continued_jet_from_symbolic(...)` can shift explicit symbolic branches in supported `log`, `sqrt`, and `pow_branch` expressions from path/winding events, then rebuild the finite CNRS-H jet from the continued expression.

Added:

- `cnrs/cnrs_h_continuation.py`
- `cnrs/h/continuation.py`
- `tests/test_cnrs_h_continuation.py`
- `examples/science_workflows/cnrs_h_branch_continuation_demo.py`
- `docs/CNRS_H_BRANCH_CONTINUATION.md`

Claim status: local finite-order coefficient recalculation for supported symbolic expressions; not full global analytic continuation or Riemann-surface lifting.


## v0.6.2 — CNRS-H Path and Winding Tracking

v0.6.2 adds conservative path/winding scaffolding to the CNRS-H branch-aware layer. It introduces piecewise-linear continuation paths, winding-number diagnostics around isolated branch points, branch-state updates for log/sqrt/power metadata, and `CnrsHJet.continue_along(...)` for recording path-induced branch changes.

### Added

- `cnrs/cnrs_h_path.py`
- `cnrs/h/path.py`
- `tests/test_cnrs_h_path.py`
- `examples/science_workflows/cnrs_h_path_winding_demo.py`
- `docs/CNRS_H_PATH_CONTINUATION.md`

### Status

This release does not claim full analytic continuation. It supplies local path/winding bookkeeping for finite CNRS-H jets and prepares the toolkit for later coefficient re-expansion and Riemann-surface work.

## v0.6.2 — CNRS-H Branch-State Propagation

v0.6.2 moves branch-state bookkeeping into the CNRS-H local jet layer. Branch choices from symbolic `log`, `sqrt`, and `pow_branch` expressions now become metadata on finite CNRS-H coefficient jets, and that metadata is preserved through the native local operations.

Added:

- `cnrs.cnrs_h_branch` — branch-state merge and extraction helpers.
- `tests/test_cnrs_h_branch.py` — branch extraction, propagation, composition, and chain-rule metadata tests.
- `examples/science_workflows/cnrs_h_branch_state_demo.py`.
- `docs/CNRS_H_BRANCH_STATE.md`.

Updated:

- `CnrsHJet` now carries `branch_state` and `branch_note`.
- `jet_from_symbolic(...)` extracts local branch state from symbolic expressions.
- Jet differentiation, integration, center shifting, multiplication, composition, and finite chain-rule verification preserve or conservatively merge branch metadata.
- `cnrs.h` and flat imports expose the branch helpers.

Scope: local branch-state bookkeeping inside finite CNRS-H jets. This is not yet path-dependent analytic continuation, Riemann-surface lifting, or monodromy tracking.

Validation: 851 passed, 6 xfailed.

## v0.6.0 — CNRS-Native Core Architecture

v0.6.0 consolidates the CNRS Scientific Toolkit around an explicit native architecture.  The release preserves all historical flat imports, but adds package façades that separate the CNRS-native core from bridge, validation, and workflow layers.

Added:

- `cnrs/core/` — native CNRS-A base, digit, value, arithmetic, and branch-state façade.
- `cnrs/h/` — native CNRS-H series, coefficient calculus, composition, chain rule, jets, domain diagnostics, and Taylor-model metadata.
- `cnrs/validation/` — reference autodiff, complex comparison, and validation helpers.
- `cnrs/workflows/` — scale-law, reaction-diffusion, and oscillator workflow façades.
- `docs/ARCHITECTURE.md` — architectural map and compatibility policy.
- `docs/CNRS_NATIVE_STATUS.md` — native / bridge / validation / workflow classification.
- `tests/test_architecture_v060.py` — compatibility and architecture import tests.

This release does not remove the useful bridge and validation tools.  It makes their role explicit: `CnrsDual` autodiff is a reference validation layer, while the direct CNRS-H coefficient chain rule is the primary CNRS-native chain-rule implementation.

Validation: 842 passed, 6 xfailed.

## v0.5.4 — CNRS-H Taylor-Model Remainder Metadata

- Added `cnrs.cnrs_h_taylor_model`, a lightweight Taylor-model-style wrapper for CNRS-H local jets.
- Added `CnrsHTaylorModel`, `taylor_model_from_jet`, `taylor_model_from_symbolic`, and `verify_taylor_model_chain_rule`.
- Added explicit optional `remainder_bound` metadata and disk-style `enclosure(point)` diagnostics.
- Added last-retained-term indicator construction from an existing `CnrsHJet` sample point.
- Added conservative propagation through addition, subtraction, and scalar multiplication, with local center diagnostics for products.
- Differentiation, integration, composition, and center shifting keep the finite jet operation but mark propagated bounds as unknown unless supplied by the caller.
- Added `tests/test_cnrs_h_taylor_model.py`.
- Added `examples/science_workflows/cnrs_h_taylor_model_demo.py`.
- Added `docs/CNRS_H_TAYLOR_MODELS.md`.
- Scope: finite local Taylor-model-style metadata; not interval arithmetic, rigorous global bounds, or full analytic continuation.

Validation: 837 passed, 6 xfailed.

## v0.5.3 — CNRS-H Domain and Convergence Diagnostics

- Added `cnrs.cnrs_h_domain`, a lightweight local-domain metadata layer for CNRS-H jets.
- Added `CnrsHDomain`, `infer_symbolic_domain`, `domain_from_radius`, and `estimate_next_term_error`.
- Added radius/singularity hints for supported symbolic expressions, including polynomials, `exp`, `sin`, `cos`, affine denominators, `log(1+s)`, and `sqrt(1+s)`.
- Extended `CnrsHJet` with structured `domain`, `truncation_error`, `valid_for()`, `distance_to_boundary()`, `estimate_truncation_error()`, and `with_domain()`.
- Added `tests/test_cnrs_h_domain.py`.
- Added `examples/science_workflows/cnrs_h_domain_diagnostics_demo.py`.
- Added `docs/CNRS_H_DOMAIN_DIAGNOSTICS.md`.
- Scope: conservative local radius/singularity diagnostics and last-term indicators; not rigorous global analytic continuation or certified interval bounds.

Validation: 830 passed, 6 xfailed.

## v0.5.2 — CNRS-H Jets and Expansion Points

- Added `cnrs.cnrs_h_jet`, a finite local CNRS-H jet object with explicit expansion point metadata.
- Added `CnrsHJet`, representing `f(s) ~= sum d_n (s-s0)^n/n!`.
- Added structural local-jet differentiation, integration, multiplication, center shifting, composition, and chain-rule verification.
- Added `jet_from_symbolic(expr, var, center=s0, order=N)` for derivative-coefficient construction around nonzero centers.
- Added `tests/test_cnrs_h_jet.py`.
- Added `examples/science_workflows/cnrs_h_local_scale_expansion_demo.py`.
- Added `docs/CNRS_H_CHAIN_RULE_THEORY.md`.
- Scope: finite local jets, not full convergence/domain or analytic-continuation tracking.

Validation: 821 passed, 6 xfailed.

## v0.5.1 — Direct CNRS-H Chain Rule

- Added `cnrs.cnrs_h_chain`, a finite-order CNRS-H coefficient-space chain-rule layer.
- Added EGF-series composition `compose_series(f, g, order=N)`.
- Added direct chain-rule checks `D(f ∘ g)` versus `(Df ∘ g) * Dg` without using `CnrsDual`.
- Added `tests/test_cnrs_h_chain_rule.py`.
- Added `examples/science_workflows/cnrs_h_native_chain_rule_demo.py`.
- Scope: finite truncated CNRS-H series; this is a structural coefficient-calculus implementation, not a full analytic-continuation theorem.

Validation: 811 passed, 6 xfailed.

## v0.5.0 — Symbolic-to-CNRS-H Bridge

Introduces the first tested bridge between the symbolic calculus layer and CNRS-H coefficient calculus.  Supported symbolic expressions can now be converted into finite CNRS-H exponential-generating-function representations, differentiated or integrated structurally, and compared against symbolic differentiation/integration paths.

### Added

- `cnrs/cnrs_h_bridge.py` with conservative symbolic-to-CNRS-H conversion.
- `cnrs_h_from_symbolic(expr, var, order, env)` for supported expressions around the expansion point `var = 0`.
- Commutation checks for symbolic differentiation vs. CNRS-H digit-shift differentiation.
- Commutation checks for conservative symbolic integration vs. CNRS-H digit-shift integration, with integration constants handled explicitly.
- `tests/test_cnrs_h_bridge.py` covering polynomials, scale laws, exponentials, sine/cosine, symbolic parameters, unsupported cases, and bridge comparison helpers.
- `examples/science_workflows/symbolic_to_cnrs_h_demo.py`.

### Supported bridge subset

- Constants and the expansion variable.
- Polynomials built from `+`, `-`, `*`, and non-negative integer powers.
- Division by expressions independent of the expansion variable.
- `exp`, `sin`, and `cos` of affine arguments such as `k*s`, `s/L`, or `k*s+b`.
- Scale laws such as `A*exp(k*s)` with numeric parameter values supplied through `env`.

### Scope note

This is a minimal bridge, not a full symbolic series engine.  Unsupported expressions raise `UnsupportedBridgeExpression` rather than silently producing unreliable expansions.

### Validation

```text
811 passed, 6 xfailed
```

The 6 expected failures remain known representational-limit tests, not regressions. Existing reliable-domain warnings from scale-law and oscillator tests remain expected.

## v0.4.4 — CLI Usability and Documentation Polish

This release stabilizes the user-facing command-line surface added in v0.4.3 and adds quickstart documentation for command-line and symbolic-calculus workflows.

### Added

- `cnrs examples`: lists packaged examples and their intended use.
- `docs/CLI_QUICKSTART.md`: command-line examples, expression syntax, and common workflows.
- `docs/SYMBOLIC_CALCULUS_QUICKSTART.md`: symbolic differentiation/integration quickstart and autodiff cross-check pattern.
- Additional CLI regression tests for example discovery and friendly missing-variable errors.

### Improved

- Clearer top-level CLI help epilog with runnable examples.
- Friendlier CLI error handling for missing symbolic variables and unevaluated symbolic cases.
- README and documentation links now surface CLI and symbolic-calculus quickstarts.

### Validation

```text
772 passed, 6 xfailed
```

The 6 expected failures remain known representational-limit tests, not regressions. Existing reliable-domain warnings from scale-law and oscillator tests remain expected.

## v0.4.3 — Lightweight Command-Line Interface

Adds a small command-line interface for common workflows.

### Added

- `cnrs/cli.py`
- `tests/test_cli.py`
- Project script entry point: `cnrs = "cnrs.cli:main"`
- Commands: `version`, `convert`, `eval`, `diff`, `integrate`, and `demo`

### Validation

```text
770 passed, 6 xfailed
```

## v0.4.2 — Conservative Symbolic Integration

Adds a conservative rule-based symbolic integrator to the minimal symbolic calculus layer.

### Added

- `integrate(expr, var)` for constants, linearity, constant-factor extraction, powers, reciprocal/log, and affine exp/sin/cos forms.
- `Integral(expr, var)` fallback for unsupported cases rather than overclaiming symbolic integration.
- `tests/test_symbolic_integrate.py`
- `examples/science_workflows/symbolic_integration_demo.py`

### Validation

```text
760 passed, 6 xfailed
```

## v0.4.1 — Minimal Symbolic Differentiation

Adds a small expression-tree symbolic calculus layer on top of the v0.4.0 chain-rule autodiff layer.

### Added

- `cnrs/symbolic.py`: minimal symbolic expression trees for constants, variables, arithmetic, powers, and elementary functions.
- Symbolic differentiation rules for sums, products, quotients, powers, `exp`, `log`, `sin`, `cos`, `tan`, and `sqrt`.
- Conservative simplification rules for zero/one identities and constant folding.
- Simple branch tags for `log`, `sqrt`, and branch-aware powers.
- Symbolic evaluation through ordinary CNRS-compatible values or through `CnrsDual` for autodiff cross-checks.
- `tests/test_symbolic_diff.py`
- `examples/science_workflows/symbolic_chain_rule_demo.py`

### Validation

```text
748 passed, 6 xfailed
```

## v0.4.0 — Chain Rule Automatic Differentiation

This release adds first-order chain-rule capability for CNRS scientific workflows.

### Added

- `cnrs/autodiff.py`: dual-number style automatic differentiation over `CnrsComplex`.
- `CnrsDual`: carries `(value, derivative)` and propagates derivatives through arithmetic.
- Chain-rule elementary functions: `exp`, `log`, `sin`, `cos`, `tan`, `sqrt`, and scalar/dual powers.
- Convenience helpers: `derivative`, `value_and_derivative`, `compose`, `pow_const`.
- `tests/test_autodiff_chain_rule.py`.
- `examples/science_workflows/chain_rule_scale_law.py`.

### Validation

```text
733 passed, 6 xfailed
```

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