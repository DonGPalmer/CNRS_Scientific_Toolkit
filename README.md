# CNRS Scientific Toolkit

## v0.6.0: CNRS-native core architecture

v0.6.0 is a consolidation release.  It keeps all established flat imports, but introduces an explicit architecture that distinguishes CNRS-native components from bridge, validation, and workflow layers.

Preferred native imports now include:

```python
from cnrs.core import CVal, BranchState
from cnrs.h import CnrsH, CnrsHJet, verify_jet_chain_rule
from cnrs.validation import CnrsDual   # reference validation layer
```

See `docs/ARCHITECTURE.md` and `docs/CNRS_NATIVE_STATUS.md`.



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
- Addition via 14-state finite-state transducer (`cnrs_add`)
- Multiplication via Cauchy convolution + carry normalization (`cnrs_mul`)
- Division by base, base powers, and Gaussian units (`cnrs_div`)
- High-level arithmetic wrappers (`cnrs_ops`, `cnrs_value`)
- CNRS-H EGF digit-shift calculus (`cnrs_h`)

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
821 passed, 6 xfailed
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