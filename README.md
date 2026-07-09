# CNRS Scientific Toolkit

## v0.11.0: Rational Expansion and Scientific Workflow Validation

v0.11.0 is the first capability release after the v0.10.x stabilization line. It deepens exact validation of Gaussian-rational division across terminating, periodic, and Laurent-periodic classes, removes the former Laurent `power_offset` ambiguity in `CnrsRational.evaluate()`, and adds independent reference checks for the principal scientific workflows.

### v0.11.0 validation baseline

- `1167 passed`
- `0 xfailed`
- `0 unexpected failures`

The release preserves the Toolkit's status as an **open research-code package**. Validation establishes that the implementation reproduces its stated arithmetic and workflow equations within documented domains; it does not establish the broader physical interpretation of Scale Space or CNRS.

### Main v0.11.0 changes

- exact `evaluate()` behavior for finite, periodic, and Laurent-periodic rational expansions;
- new `partial_sum()` API for diagnostic formal sums;
- randomized exact division/classification cross-validation;
- Gaussian-rational eventual-periodicity theorem integration and numerator-aware Gaussian-factor termination classification;
- equivalent-fraction invariance and sampled period-minimality checks;
- independent ODE, scale-law, biological-profile, oscillator, and SciPy interoperability checks;
- formal audit records in `docs/audits/`;
- synchronized package, CLI, citation, claim-status, and test-status metadata.

## v0.10.3: Independent Validation and Metadata Synchronization

v0.10.3 incorporates the July 7, 2026 independent audit into the permanent repository record. It adds an exact, independently written Gaussian-integer cross-validation harness, CI regression coverage, CNRS-H eigenfunction constructors, synchronized validation metadata, and normalized release text files. No new completeness claim is introduced.

### v0.10.3 validation baseline

- Release validation: `1167 passed`.
- Current main-branch status: use the GitHub Actions test workflow; the count may increase as tests are added.
- Independent audit: 15/15 checks passed in the supplied Session 72 harness.

See `docs/audits/toolkit_audit_2026-07-07_v1.md`, `tools/toolkit_audit_crossval.py`, and `docs/TEST_STATUS.md`.

## v0.10.2: Verification and Release Engineering

v0.10.2 improves reproducibility and release hygiene while preserving the theorem-to-implementation alignment introduced in v0.10.1.

## v0.10.1: Formal Alignment and Research Release

v0.10.1 aligns the Toolkit more explicitly with the CNRS mathematical
programme. The release establishes a traceable path:

```
CNRS theorem
    |
algorithm
    |
implementation
    |
verification tests
    |
software release
```

The purpose of this release is not to claim completion of CNRS. It documents
the maturity boundary between implemented arithmetic, research workflows, and
open mathematical questions.

### Current capability status

| Capability | Status |
|---|---|
| CNRS-A representation | Stable |
| Canonical normalization | Stable |
| Addition | Theorem-aligned / implemented |
| Subtraction | Theorem-aligned / implemented |
| Multiplication | Closure-theorem aligned / implemented |
| Division | Structured finite/periodic/approximate workflows |
| CNRS-H calculus | Research implementation |
| Branch-aware workflows | Research implementation |
| Metric completeness | Open research question |
| e-base CNS theorem | Open research question |

### Research software principles

The Toolkit distinguishes:

- mathematical theorem statements,
- constructive algorithms,
- software implementations,
- computational verification,
- exploratory scientific workflows.

The Toolkit is the executable implementation layer of the CNRS programme.

---

## v0.10.0: dual-path arithmetic, carry-guard tightening, and Lagrange inversion

v0.10.0 builds on the v0.9.0 theory-aligned core with three additions to the
native CNRS-A / CNRS-H layer.

**Dual-path arithmetic (`CnrsHMode`).** A new adapter automatically selects
`CnrsHNative` (CNRS-A digit-string coefficients) when EGF coefficients are
Gaussian integers, and falls back to `CnrsH` (fast plain-Python path) otherwise.
`ScaleLaw`, `OdeSolution`, and `cnrs_solve_linear` now expose a `native`
parameter and a `.native_mode` property.

**Carry-drain bounds tightened.** The addition transducer drain guard is reduced
from 1000 to 20 (provably correct: carry is always in the 14-state canonical
set). The multiplication normalization drain guard is reduced from 1000 to 100
(empirically ≤ 12 steps for inputs up to ~10³ digits; formal proof is an open
item).

**Native Lagrange inversion (`invert_native`).** Computes the compositional
inverse g of a `CnrsHNative` series f (f(g(s)) = s) using the Lagrange
inversion recurrence in CNRS-A coefficient space. All arithmetic routes through
`CVal` (add_cnrs / mul_cnrs). Verification via `verify_inversion` confirms
f(g(s)) = s at the digit-string level (`strings_match=True`, `max_error=0.0`).

```python
from cnrs.cnrs_h_native import CnrsHNative, invert_native, verify_inversion

# f(s) = exp(s) - 1  →  g(s) = log(1+s)
# g_n = (-1)^{n-1} * (n-1)!   (all integer, all verifiable at digit level)
f = CnrsHNative.from_gaussian_list([0, 1, 1, 1, 1, 1, 1, 1])
result = verify_inversion(f, order=8)
print(result["strings_match"])   # True
print(result["max_error"])       # 0.0
print([c.to_gaussian() for c in result["g"].coeffs])
# [0, 1, -1, 2, -6, 24, -120, 720]

# Dual-path: auto-selects native for Gaussian-integer coefficients
from cnrs.cnrs_scale import ScaleLaw
law = ScaleLaw.from_coeffs([1, 2, -1, 3])
print(law.native_mode)           # True  (Gaussian integers → CnrsHNative)

law2 = ScaleLaw.exponential(lam=1.5)
print(law2.native_mode)          # False (float coefficients → CnrsH)
```

Validation: `1121 passed, 6 xfailed`.

Patch note: this build fixes native `CnrsHMode.integrate()` so Gaussian-integer
complex integration constants such as `3+0j` and `1+2j` are accepted correctly
in native mode, with regression tests.

## v0.9.0: native rational values and complex-state preservation workflows

v0.9.0 builds on the v0.8.x theory-aligned core. It adds value-facing support for finite and periodic CNRS rational divisions, plus lightweight scientific workflow helpers for measuring what is preserved by complex-state workflows and what is lost by early projection to real-valued observables.

```python
from cnrs import rational_value, build_preservation_report
from cnrs.cnrs_h_native import CnrsHNative, compose_native

# Structured rational value: finite/periodic status is explicit.
x = rational_value(1, 2)
print(x.status)
print(x.structured_report())

# Native CNRS-H composition can feed a state-preserving workflow.
f = CnrsHNative.from_gaussian_list([1] * 8)   # exp
g = CnrsHNative.from_gaussian_list([0, 2])    # 2s
h = compose_native(f, g, order=6)
report = build_preservation_report(h, [0, 0.1, 0.2], name="native_exp_2s")
print(report.summary())
```

See `docs/CNRS_RATIONAL_VALUES.md`, `docs/CNRS_SCIENTIFIC_WORKFLOWS_V090.md`, `docs/CNRS_NORMALIZATION_STATUS.md`, `docs/CNRS_DIVISION_STRUCTURED_EXPANSIONS.md`, and `docs/CNRS_THEOREM_ALIGNMENT_REGISTRY.md`.

Validation: `1026 passed, 6 xfailed`.

## v0.8.1: theory-aligned normalization, division, and formal-state preservation

v0.8.1 consolidates the v0.8.0 native core. It makes the normalization status explicit, expands division into structured prefix/period reports, adds a theorem-alignment registry, and gives the lightweight CNRS* formal state preservation operations for differentiation, integration, addition, and multiplication.

```python
from cnrs import (
    CVal, CnrsHNative, CnrsFormalState,
    normalize_addition, normalize_general_coefficients,
    normalize_multiplication_convolution,
    expand_division, division_summary,
    get_theorem_record,
)

x = CVal.from_gaussian(3+2j)
y = -x                  # native negation using -1 = "144"

# Addition has a bounded normalisation route; multiplication convolution uses
# general CNRS-A normalisation.
add_norm = normalize_addition("4", "4")
mul_norm = normalize_multiplication_convolution("444444", "444444")

# Division is reported as structured prefix/period data, not finite-string field closure.
report = division_summary(1, 10)

state = CnrsFormalState.from_gaussian_coefficients(1, [1, 2, 3])
d_state = state.differentiate()

print(get_theorem_record("CNRS-A multiplication closure").status)
```

See `docs/CNRS_NORMALIZATION_STATUS.md`, `docs/CNRS_DIVISION_STRUCTURED_EXPANSIONS.md`, `docs/CNRS_THEOREM_ALIGNMENT_REGISTRY.md`, `docs/CNRS_FORMAL_STATE_PRESERVATION.md`, `docs/THEOREM_ALIGNMENT.md`, `docs/CNRS_H_NATIVE.md`, `docs/CNRS_DIVISION_STATUS.md`, and `docs/CNRS_FORMAL_STATE.md`.

## v0.8.0: CNRS-A native values and CNRS-H native coefficient calculus

v0.8.0 moved the toolkit closer to the formal CNRS architecture. It added native `CVal` arithmetic with CNRS-A negation/subtraction, a `CnrsHNative` coefficient-calculus layer where coefficients are themselves CNRS-A values, theory-aligned division classification, and a lightweight CNRS* formal state object.

## v0.7.1: CNRS native-status and internal consistency

v0.7.1 adds a programmatic native-status registry so the toolkit can distinguish CNRS-native structures from bridge, validation, scaffold, application, and compatibility layers.  This release does not add another workaround layer; it clarifies which modules express CNRS internally and which modules support conversion, validation, comparison, or scientific applications.

```python
from cnrs.native_status import get_component, native_components, status_table

print(get_component("CNRS-H chain rule").status)
print(status_table(native_components()))
```

See `docs/CNRS_NATIVE_STATUS_REGISTER.md`, `docs/CNRS_NATIVE_STATUS.md`, and `docs/ARCHITECTURE.md`.

## v0.7.0: CNRS-H branch-aware local continuation

v0.7.0 continues the move toward a full CNRS-native toolkit by making path-induced branch changes affect finite CNRS-H local coefficients when a supported symbolic source expression is available. It adds a branch-continuation rebuild layer for `log`, `sqrt`, and `pow_branch` expressions: winding events shift explicit symbolic branch labels, then the CNRS-H jet is rebuilt from the continued expression. This is still local finite-order continuation scaffolding, not a full Riemann-surface analytic-continuation theorem.


## v0.6.2: CNRS-H path/winding tracking

v0.6.2 extends the CNRS-native branch architecture with piecewise-linear continuation paths, winding-number diagnostics, conservative branch-state updates for log/sqrt/power scaffolding, and path-history metadata on CNRS-H local jets. This is still local path/winding bookkeeping, not full analytic continuation or Riemann-surface lifting.

## v0.6.1: CNRS-H branch-state propagation

v0.6.2 extends the CNRS-native architecture by carrying branch-state metadata into CNRS-H local jets. Branch choices from symbolic `log`, `sqrt`, and `pow_branch` expressions now survive conversion into finite coefficient jets and are preserved through local differentiation, integration, center shifting, multiplication, composition, and chain-rule verification. The feature remains local branch bookkeeping, not full path-dependent analytic continuation.

Preferred native imports now include:

```python
from cnrs.core import CVal, BranchState
from cnrs.h import CnrsH, CnrsHJet, verify_jet_chain_rule, branch_state_from_symbolic
from cnrs.validation import CnrsDual   # reference validation layer
```

See `docs/ARCHITECTURE.md`, `docs/CNRS_NATIVE_STATUS.md`, and `docs/CNRS_H_BRANCH_STATE.md`.



CNRS Scientific Toolkit is an open research-code package for exploring the Complex Numeric Representational System (CNRS): complex-base representation, CNRS-float, branch-aware complex-state workflows, first-order chain-rule automatic differentiation, minimal symbolic differentiation and conservative symbolic integration, CNRS-H scale-law calculus, CNRS-H coefficient-based ODE methods, and NumPy/SciPy interoperability.

**Base:** `z0 = -2 + i`  (a Gaussian integer, `N(z0) = 5`)  
**Digit alphabet:** `D = {0, 1, 2, 3, 4}`

The package is designed to interoperate with ordinary scientific workflows:

```text
standard real/complex input
    -> CNRS exact / float / rational / branch / H-calculus representation
    -> complex-state-preserving workflow
    -> standard real/complex/decimal output
```

### v0.6.0: CNRS-native core architecture

v0.6.0 introduced the explicit `cnrs.core`, `cnrs.h`, `cnrs.validation`, and `cnrs.workflows` façades while preserving flat imports.

### v0.5.4: CNRS-H Taylor-model remainder metadata

The v0.5.4 release adds a lightweight Taylor-model-style wrapper around finite CNRS-H local jets. A jet still represents a local expansion around an explicit center:

```text
f(s) ~= sum_n d_n * (s - s0)^n / n!
```

`CnrsHTaylorModel` pairs that finite jet with optional remainder/error metadata. This makes finite-truncation uncertainty explicit while preserving the structural CNRS-H operations introduced in v0.5.1–v0.5.3.

```python
from cnrs.symbolic import Var, exp
from cnrs.cnrs_h_taylor_model import taylor_model_from_symbolic

s = Var("s")
model = taylor_model_from_symbolic(exp(s), s, center=0, order=8, sample_point=0.1)
value, radius = model.enclosure(0.1)

print(value)   # finite jet value
print(radius)  # last-retained-term diagnostic unless caller supplied a bound
```

The release propagates known bounds through addition, subtraction, scalar multiplication, and local center-product diagnostics. Differentiation, integration, composition, and center shifting keep the finite jet operation but mark propagated bounds as unknown unless a trusted bound is supplied. This is not interval arithmetic or a rigorous global convergence proof.


## Research Status

CNRS Scientific Toolkit is an open research-code package supporting the development and evaluation of CNRS and related multi-scale modeling concepts.

The toolkit contains:

- Reference implementations of CNRS arithmetic, calculus, normalization, and transducer systems.
- Experimental algorithms and prototype representations.
- Validation and regression tests.
- Demonstration models for scale-aware, biological, oscillator, and related scientific applications.
- Reproducible examples used in ongoing research and publication development.

### Scope

This repository is intended to support:

- Reproducibility of published and pre-publication results.
- Exploration of alternative representational and computational frameworks.
- Investigation of cross-scale mathematical structures.
- Development of new numerical, symbolic, and dynamical methods.
- Independent verification and extension by other researchers.

### Research Nature of the Software

This repository is released as an **open research-code package**.

Many components are active research implementations rather than finalized production software. The inclusion of a module, algorithm, example, or demonstration does **not** imply that any associated scientific hypothesis, interpretation, or theoretical framework has been fully established or experimentally validated.

Users should therefore regard the toolkit as:

- A reference implementation of current CNRS research.
- A platform for experimentation and exploration.
- A reproducible computational companion to the associated papers and technical notes.
- An invitation for independent analysis, testing, criticism, and extension.

### Project Philosophy

The long-term goal of the project is not to provide a finished theory, but to develop and evaluate mathematical structures, computational tools, and multi-scale representations that may prove useful across scientific disciplines.

As with many research programs, future work may modify, replace, or extend individual components while preserving useful mathematical or computational ideas that emerge from the investigation.

## Repository

**GitHub:** https://github.com/DonGPalmer/CNRS_Scientific_Toolkit  
**Programme landing page:** https://www.nul1.com  
**Zenodo:** https://doi.org/10.5281/zenodo.19797882  
**ORCID:** https://orcid.org/0000-0003-4335-5533

## What is included

```text
cnrs/                  Core CNRS implementation and scientific modules
cnrs/science/          Scientific workflow helpers and observation maps
examples/              Runnable CNRS and scientific workflow examples
tests/                 Pytest test suite
docs/                  Research status, API overview, claim/test status, and example-smoke status
README.md              Project overview and quick start
RELEASE_NOTES.md       Release history
CITATION.cff           Citation metadata
CONTRIBUTING.md         Contributor guidance for research-code additions
```

Core capabilities:

```text
CNRS-A finite complex-base representation over z0 = -2+i
CNRS addition and multiplication
Gaussian rational representation, including periodic and Laurent-periodic cases
CNRS-float approximate complex representation
CnrsComplex scientific interface
CNRS-H coefficient calculus
CNRS-H linear ODE solvers
Branch-aware complex-state helpers
Explicit observation maps
Scale-law fitting and differentiation
Biological scale dynamics and Turing-threshold examples
Complex oscillator and three-workflow examples
NumPy/SciPy interoperability bridge
First-order chain-rule automatic differentiation (`cnrs.autodiff`)
Minimal symbolic differentiation and conservative symbolic integration (`cnrs.symbolic`)
Symbolic-to-CNRS-H bridge, local jets, and domain diagnostics (`cnrs.cnrs_h_bridge`, `cnrs.cnrs_h_jet`, `cnrs.cnrs_h_domain`)
```

Scientific toolkit modules include:

```text
cnrs_scale      ScaleLaw: fitting, allometric, derivative, threshold tools
cnrs_bio        Gierer-Meinhardt biological scale dynamics
cnrs_oscillator Stuart-Landau, RLC, driven harmonic, interference examples
cnrs_interop    NumPy/SciPy bridge and benchmark utilities
autodiff       First-order dual-number chain-rule layer over CnrsComplex
symbolic       Minimal expression-tree symbolic differentiation, integration, and evaluation
```

## Implementation maturity

### Stable

Fully implemented, tested, and verified:

- Gaussian integer representation (`cnrs_repr`)
- Addition via 14-state finite-state transducer (`cnrs_add`) — carry drain bound provably ≤ 14 steps
- Multiplication via Cauchy convolution + carry normalization (`cnrs_mul`) — drain bound empirically ≤ 12 steps
- Division by base, base powers, and Gaussian units (`cnrs_div`)
- High-level arithmetic wrappers (`cnrs_ops`, `cnrs_value`)
- CNRS-H EGF digit-shift calculus (`cnrs_h`)
- CNRS-H native coefficient calculus with CVal coefficients (`cnrs_h_native`):
  - differentiation, integration, multiplication, composition (Faà di Bruno)
  - chain-rule verification, Leibniz verification
  - **Lagrange series inversion** (`invert_native`, `verify_inversion`) — v0.10.0
- Dual-path CNRS-H adapter (`cnrs_h_mode`) — v0.10.0

### Experimental

Implemented and tested for representative cases:

- Gaussian rational expansion (`cnrs_rational`): finite, pure z0-adic periodic, and Laurent-periodic cases
- CNRS floating-point arithmetic (`cnrs_float`)
- H-streams and operator calculus (`cnrs_hstream`, `cnrs_hstream_ops`, `cnrs_operator`)
- Layer-2 branch index arithmetic (`cnrs_layer2`, `cnrs_layer2_value`)
- Scientific workflow helpers (`cnrs.science`)
- First-order chain-rule automatic differentiation (`cnrs.autodiff`)
- Minimal symbolic differentiation, conservative symbolic integration, and explicit branch-state scaffolding (`cnrs.symbolic`)
- CNRS-H linear ODE solvers (`cnrs_ode`)
- Scale-law, biological-scale, oscillator, and interop utilities

### Prototype / research sketch

Scaffolding for future work:

- Analytic continuation engine (`cnrs_expansion`, `cnrs_continuation`)
- Layer-3 / Layer-4 global analytic objects (`cnrs_layer3`, `cnrs_layer4`)
- Global constraint and solver scaffolding (`cnrs_global_constraints`, `cnrs_global_solver`)
- Scale-integration bridge example (`examples/scale_integration.py`)


## Command-line interface

The toolkit includes a lightweight CLI for common workflows. The v0.4.5 release adds explicit branch-aware symbolic expressions for `log`, `sqrt`, and `pow_branch`, including CLI parsing for branch choices.

```bash
cnrs version
cnrs convert "1+2j" --to cnrs
cnrs convert "104" --from cnrs
cnrs eval "sin(exp(s/L))" --at s=1.2,L=5
cnrs eval "log(z, branch=2)" --at z=-1
cnrs eval "sqrt(z, branch=1)" --at z=-1
cnrs diff "sin(exp(s/L))" --var s
cnrs diff "sin(exp(s/L))" --var s --at s=1.2,L=5
cnrs integrate "A*exp(k*s)" --var s
cnrs examples
cnrs demo
```

The CLI is deliberately small: it exposes conversion, symbolic evaluation, differentiation, conservative integration, explicit branch examples, example discovery, and a short demo without turning the toolkit into a full computer-algebra system or graphical application. See [`docs/CLI_QUICKSTART.md`](docs/CLI_QUICKSTART.md) and [`docs/SYMBOLIC_CALCULUS_QUICKSTART.md`](docs/SYMBOLIC_CALCULUS_QUICKSTART.md).

## Branch-aware symbolic calculus

v0.4.5 makes local branch choices explicit for symbolic complex functions:

```python
from cnrs.symbolic import Var, log, sqrt, pow_branch, BranchState

z = Var("z")
expr = log(z, branch=2)
root = sqrt(z, branch=1)
power = pow_branch(z, 0.5, branch=1)
```

Branch metadata is preserved through expression construction, substitution, differentiation, conservative integration when relevant, evaluation, and CLI parsing. This is a branch-state scaffold, not a complete path-dependent analytic-continuation or Riemann-surface engine.

## Test status

Current validation status:

```text
1121 passed, 6 xfailed
```

The 6 expected failures document known representational limits, including transcendental numbers and long-period rationals. They are not regressions.

See [`docs/RESEARCH_STATUS.md`](docs/RESEARCH_STATUS.md), [`docs/API_OVERVIEW.md`](docs/API_OVERVIEW.md), [`docs/TEST_STATUS.md`](docs/TEST_STATUS.md), [`docs/CLAIM_STATUS.md`](docs/CLAIM_STATUS.md), [`docs/EXAMPLE_SMOKE_STATUS.md`](docs/EXAMPLE_SMOKE_STATUS.md), [`docs/CLI_QUICKSTART.md`](docs/CLI_QUICKSTART.md), and [`docs/SYMBOLIC_CALCULUS_QUICKSTART.md`](docs/SYMBOLIC_CALCULUS_QUICKSTART.md) for details.

## Quick start

From the repository root:

```bash
pip install numpy scipy          # runtime dependencies for scientific examples
pip install pytest               # for running tests
python -m pytest -q
```

Run selected examples:

```bash
python examples/quickstart_cnrs.py
python examples/demo.py
python examples/scale_integration.py

# Science workflow examples
python examples/science_workflows/interference_three_workflows.py
python examples/science_workflows/complex_scale_law.py
python examples/science_workflows/phase_branch_tracking.py
python examples/science_workflows/scale_law_fit_demo.py
python examples/science_workflows/observation_maps_demo.py

# v0.4.0 chain-rule example
python examples/science_workflows/chain_rule_scale_law.py

# v0.4.1+ symbolic differentiation example
python examples/science_workflows/symbolic_chain_rule_demo.py

# v0.4.2+ symbolic integration example
python examples/science_workflows/symbolic_integration_demo.py

# v0.4.5+ branch-aware symbolic example
python examples/science_workflows/branch_aware_symbolic_demo.py

# Additional science examples
python examples/science_workflows/turing_scale_exit.py
python examples/science_workflows/rlc_three_workflows.py
python examples/science_workflows/cnrs_vs_scipy_benchmark.py
```

See [`examples/README.md`](examples/README.md) for example categories and smoke-test guidance.


### Reaction-diffusion scale-exit prototype

The development version includes a reusable reaction-diffusion scale-exit layer:

```text
cnrs/rd_scale_exit.py
examples/science_workflows/reaction_diffusion_scale_exit.py
docs/RD_SCALE_EXIT.md
```

It detects Turing entry/exit transitions for two-species reaction-diffusion
systems with scale-dependent diffusion laws. The default Gierer-Meinhardt
example reproduces a scale exit near `s ≈ 0.524` nats.


## Example: chain-rule automatic differentiation

```python
from cnrs.autodiff import exp, sin, derivative, value_and_derivative

# d/ds exp(s^2) at s = 2
d = derivative(lambda s: exp(s * s), 2.0, L=18)

# value and derivative for a scale law y = A exp(k s)
A = 2.0
k = 0.3
value, deriv = value_and_derivative(lambda s: A * exp(k * s), 4.0, L=18)

# nested chain rule: y = sin(exp(s/L))
Lscale = 5.0
value, deriv = value_and_derivative(lambda s: sin(exp(s / Lscale)), 1.2, L=18)
```

The autodiff layer is a first-order numerical chain-rule layer over `CnrsComplex`. The `cnrs.symbolic` layer adds minimal expression-tree symbolic differentiation and can cross-check symbolic derivatives against the autodiff backend; it is still not a full computer algebra system and does not replace the exact coefficient-shift calculus in `CnrsH`.


## Example: minimal symbolic differentiation

```python
from cnrs.symbolic import Var, exp, sin, log, diff
from cnrs.autodiff import CnrsDual

s = Var("s")
L = Var("L")
expr = sin(exp(s / L)) + log(s * s + 2)
dexpr = diff(expr, s).simplify()

value = expr.eval({"s": 1.2, "L": 5.0}, L=20)
deriv = dexpr.eval({"s": 1.2, "L": 5.0}, L=20)

# Cross-check through the autodiff backend.
dual_value = expr.eval({"s": CnrsDual.variable(1.2, L=20), "L": 5.0}, L=20)
assert abs(complex(deriv) - complex(dual_value.deriv)) < 1e-3
```

The symbolic layer currently supports `+`, `-`, `*`, `/`, powers, `exp`, `log`, `sin`, `cos`, `tan`, and `sqrt`, with conservative simplification and simple branch tags for `log`, `sqrt`, and powers.

## Documentation map

- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contributor guidance and testing expectations.
- [`docs/RESEARCH_STATUS.md`](docs/RESEARCH_STATUS.md) — research-code status and maturity levels.
- [`docs/API_OVERVIEW.md`](docs/API_OVERVIEW.md) — compact module map.
- [`docs/CLAIM_STATUS.md`](docs/CLAIM_STATUS.md) — tested/practical/open claim boundaries.
- [`docs/TEST_STATUS.md`](docs/TEST_STATUS.md) — test-suite status.
- [`docs/EXAMPLE_SMOKE_STATUS.md`](docs/EXAMPLE_SMOKE_STATUS.md) — runnable example status.

## Core CNRS examples

```python
import cnrs

# Represent a Gaussian integer
s = cnrs.gaussian_to_cnrs_str(3 + 2j)   # -> '1332'
z = cnrs.cnrs_to_gaussian(s)            # -> (3+2j)

# Addition via finite-state transducer
a = cnrs.gaussian_to_cnrs_str(3 + 2j)
b = cnrs.gaussian_to_cnrs_str(1 + 1j)
c = cnrs.cnrs_add(a, b)

# Multiplication via convolution + carry normalization
m = cnrs.cnrs_mul(a, b)
```

## Example: interference and beat frequency

```python
from cnrs.cnrs_oscillator import interference_pair, compare_interference
import numpy as np

# Two oscillators at omega1=1.0, omega2=1.5
sol = interference_pair(omega1=1.0, omega2=1.5)

# Workflow A: incoherent sum loses the beat
A_intensity = 1.0 + 1.0   # |amp1|² + |amp2|² — constant

# Workflow C: CNRS-H stream preserves the beat at omega2-omega1 = 0.5
t_vals = np.linspace(0.0, 2*np.pi/0.5, 200)
mod2 = sol.modulus_sq(t_vals)   # oscillates at beat frequency

result = compare_interference(omega1=1.0, omega2=1.5)
print(result.metrics["B_beat_frequency"])      # 0.5
print(result.metrics["A_intensity_constant"])  # True
print(result.interpretation)
```

## Example: Turing instability exit scale

```python
from cnrs.cnrs_bio import GmParams, find_s_exit, turing_profile

p = GmParams()   # Paper 18 default parameters

# Find the scale at which Turing instability becomes extinct
s_exit = find_s_exit(p)
print(f"s_exit ≈ {s_exit:.3f} nats")   # ≈ 0.520 nats

# Full profile across scale
prof = turing_profile(p)
print(f"d_hi = {prof.d_hi:.3f}")
print(f"Active scales: s < {prof.s_exit:.3f} nats")
```

## Example: CNRS-H vs SciPy comparison

```python
from cnrs.cnrs_interop import solve_and_compare, benchmark_linear
import numpy as np

# Side-by-side comparison for y' = lam*y
result = solve_and_compare(
    lam=complex(-0.3, 2.0),
    y0=complex(1.0),
    s_vals=np.linspace(0.0, 0.5, 100),
    terms=30,
)
print(result.summary())

# Timing benchmark
bench = benchmark_linear(n_repeat=20)
print(bench.summary())
```

## Example: complex scale law

```python
from cnrs.cnrs_scale import fit_allometric
import numpy as np

# Allometric power law: y ~ A * exp(b * s) = A * ell^b
s = np.linspace(0.0, 5.0, 60)
y = 1.5 * np.exp(0.75 * s)

result = fit_allometric(s, y)
print(f"Allometric exponent b = {result.exponent:.4f}")
print(f"Amplitude A = {result.amplitude:.4f}")
print(f"R² = {result.r_squared:.6f}")

# Exact digit-shift derivative of the fitted law
print(f"Log-derivative at s=1: {result.law.log_derivative(1.0).real:.4f}")
```

## The three-workflow pattern

A recurring design in the toolkit:

```text
Workflow A — early real reduction
    Convert to |z|² or Re(z) immediately.
    Fast; loses phase, branch, and interference information.

Workflow B — late complex reduction
    Propagate in ordinary Python complex; measure at the end.
    Retains phase; no digit-shift calculus.

Workflow C — CNRS complex-state preservation
    Propagate via CNRS-H EGF stream; exact digit-shift derivative;
    choose observation map only at the final step.
    Retains all complex structure; supports exact differentiation.
```

The toolkit's `compare_*` functions demonstrate these workflows side-by-side, showing what early reduction loses relative to full complex-state preservation.

## Scientific purpose

The toolkit is meant to make CNRS inspectable, testable, and extensible. It provides working code, tests, and examples for evaluating where CNRS may be useful in scientific computation, especially where complex-valued state should be preserved before choosing a real-valued observation map.

The digit-shift identity for CNRS-H differentiation is proved within the EGF convention. ODE solutions are tested computationally against SciPy and exact analytical formulae. Standard QM and GR exact solutions are verified as CNRS-H streams. See [`docs/CLAIM_STATUS.md`](docs/CLAIM_STATUS.md) for the precise status of each claim.

## Disclosure

AI collaboration is disclosed throughout this programme and in associated papers, in accordance with the policies of the target journals.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
## v0.7.0 — CNRS-native scientific state

This release adds `CnrsScientificState`, the first consolidated science-facing
CNRS object.  It keeps the CNRS-H local jet as the primary representation while
carrying source expression, expansion center, scale unit, branch state, path
history, domain metadata, claim status, and observation maps in one object.

```python
from cnrs.symbolic import Var, exp
from cnrs.cnrs_scientific_state import CnrsScientificState

s = Var("s")
state = CnrsScientificState.from_symbolic(exp(0.08*s), s, center=-12, order=8)
print(state.evaluate(-12))
print(state.diff().evaluate(-12))
```

This is still a finite local representation, but it makes the native CNRS-H
spine explicit rather than presenting scientific workflows as wrappers around
standard external methods.

## v0.7.1 — Native-status and internal-consistency release

v0.7.1 adds a programmatic native-status registry so the toolkit can distinguish
CNRS-native structures from bridge, validation, scaffold, application, and
compatibility layers.

```python
from cnrs.native_status import get_component, native_components, status_table

print(get_component("CNRS-H chain rule").status)
print(status_table(native_components()))
```

The release does not add another mathematical workaround layer.  It clarifies
which modules are intended to express CNRS internally and which modules support
conversion, validation, comparison, or applications.  This keeps the Python
research toolkit aligned with the formal CNRS proof-ladder work.


## v0.10.1: Theorem-to-Implementation Alignment Release

This release aligns the Toolkit more explicitly with the CNRS mathematical record.

### Mathematical-to-software traceability

The Toolkit now documents the path:

```
CNRS theorem
    |
algorithm
    |
implementation
    |
verification tests
    |
release
```

Core CNRS-A status:

| Capability | Status |
|---|---|
| Canonical representation | Stable |
| Addition | Theorem-aligned / implemented |
| Subtraction | Theorem-aligned / implemented |
| Multiplication | Closure-theorem aligned / implemented |
| Division | Structured finite-periodic-approximate workflows |
| CNRS-H calculus | Research implementation |
| Metric completeness | Open research question |
| e-base CNS theorem | Open research question |

The Toolkit distinguishes mathematical results, constructive algorithms, computational verification, and experimental workflows.

### Gaussian-rational theorem support

v0.11.0 includes exact ideal/valuation analysis and canonical periodic normalization for Gaussian rationals in base `-2+i`:

```python
from cnrs import analyze_termination, CanonicalPeriodicExpansion

a = analyze_termination((1, 0), (5, 0))
assert not a.terminates

c = CanonicalPeriodicExpansion.from_gaussian_fraction((1, 0), (5, 0))
print(c)  # canonical shifted eventually-periodic form
```

The implementation supports arbitrary Gaussian denominators, not only ordinary integer denominators.


### Branch-index and formal CNRS-H algebra

The v0.11.0 release includes an exact universal-cover multiplication API (`LiftedComplex`) with branch-wrap correction and a single-valued lifted logarithm. It also includes a formal Hurwitz-series coefficient algebra for CNRS-H. These are algebraic/formal results; analytic convergence is a separate question.

### Metric/topological completeness and hybrid representation

v0.11.0 now distinguishes symbolic, `beta`-adic, Laurent, coefficientwise, and ordinary complex topologies. The natural prefix metric on right-infinite CNRS-A digit strings is the metric induced by the `beta=-2+i` valuation; the corresponding completion is the local valuation ring at `(beta)`, topologically isomorphic to `Z_5`. Allowing finite negative offsets gives the associated local field, topologically isomorphic to `Q_5`. This is not the ordinary complex topology.

```python
from cnrs import symbolic_distance, beta_adic_distance, first_difference_isometry

assert first_difference_isometry((1, 2, 3), (1, 2, 4))
```

The hybrid CNRS-A/CNRS-H layer transports the Hurwitz-series differential algebra through a canonical coefficient codec:

```python
from fractions import Fraction
from cnrs import CoefficientCodec, HybridSeries

codec = CoefficientCodec(
    encode=lambda x: (x.numerator, x.denominator),
    decode=lambda p: Fraction(*p),
    zero=Fraction(0),
    one=Fraction(1),
)
f = HybridSeries.from_values([Fraction(1), Fraction(2), Fraction(3)], codec)
df = f.derivative()
```

Formal coefficientwise completeness is distinct from analytic convergence of the associated EGF in the ordinary complex norm.
