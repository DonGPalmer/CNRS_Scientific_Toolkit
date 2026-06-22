# Examples

This folder contains runnable examples for the CNRS Scientific Toolkit.

The examples are intended to be clear, inspectable research-code demonstrations. They are not presented as validated scientific models unless explicitly stated.

## Quickstart

```bash
python examples/quickstart_cnrs.py
```

This script demonstrates a minimal path through:

1. CNRS-A representation and arithmetic;
2. CNRS-H digit-shift calculus;
3. scale-law evaluation;
4. NumPy/SciPy interoperability.

## Basic examples

| File | Purpose |
|---|---|
| `demo.py` | Basic CNRS arithmetic and calculus demonstration. |
| `scale_integration.py` | Scale-integration bridge example. |
| `quickstart_cnrs.py` | Minimal first-run workflow. |

## Science workflow examples

Located in `examples/science_workflows/`.

| File | Type | Purpose |
|---|---|---|
| `cnrs_vs_scipy_benchmark.py` | Benchmark / interop example | Compares CNRS-H workflow with SciPy-style workflow. |
| `rlc_three_workflows.py` | Demonstration | Shows three workflow styles for an RLC system. |
| `turing_scale_exit.py` | Paper-linked demonstration | Demonstrates scale-dependent Turing exit behavior. |
| `complex_scale_law.py` | Demonstration | Complex scale-law example. |
| `interference_three_workflows.py` | Demonstration | Interference/beat-frequency workflow comparison. |
| `observation_maps_demo.py` | Demonstration | Observation map examples. |
| `phase_branch_tracking.py` | Demonstration | Phase and branch tracking. |
| `scale_law_fit_demo.py` | Demonstration | Scale-law fitting example. |
| `chain_rule_scale_law.py` | v0.4.0 demonstration | First-order automatic differentiation and chain-rule workflows. |
| `symbolic_chain_rule_demo.py` | v0.5.1 demonstration | Minimal symbolic differentiation and symbolic-vs-autodiff cross-checks. |
| `symbolic_integration_demo.py` | v0.4.4 demonstration | Conservative symbolic integration with differentiate-the-antiderivative checks. |
| `branch_aware_symbolic_demo.py` | v0.5.1 demonstration | Explicit branch-aware symbolic log/sqrt/power workflows. |

## Smoke testing examples

From the repository root:

```bash
python examples/quickstart_cnrs.py
python examples/science_workflows/turing_scale_exit.py
python examples/science_workflows/rlc_three_workflows.py
python examples/science_workflows/cnrs_vs_scipy_benchmark.py
python examples/science_workflows/chain_rule_scale_law.py
python examples/science_workflows/symbolic_chain_rule_demo.py
```

See `docs/EXAMPLE_SMOKE_STATUS.md` for the currently recorded smoke-test status.


## Chain-rule example — v0.4.0

Run from the repository root:

```bash
python examples/science_workflows/chain_rule_scale_law.py
```

This demonstrates first-order automatic differentiation over CNRS-compatible complex values for `exp(s^2)`, an exponential scale law, and a nested scale transformation `sin(exp(s/L))`.


## Symbolic differentiation example — v0.4.1+

Run from the repository root:

```bash
python examples/science_workflows/symbolic_chain_rule_demo.py
```

This demonstrates the minimal `cnrs.symbolic` expression-tree layer for symbolic differentiation, conservative simplification, numerical evaluation, and cross-checking the symbolic derivative against the `CnrsDual` autodiff backend.

CLI quick check:

```bash
cnrs demo
cnrs examples
cnrs diff "sin(exp(s/L))" --var s
cnrs integrate "A*exp(k*s)" --var s
```

## Branch-aware symbolic example — v0.5.1+

```bash
python examples/science_workflows/branch_aware_symbolic_demo.py
```

Demonstrates explicit local branch tags for logarithms, square roots, and branch-aware powers, plus conservative simplification and symbolic/autodiff cross-checking.

- `science_workflows/symbolic_to_cnrs_h_demo.py` — symbolic calculus to CNRS-H coefficient bridge.

| `cnrs_h_native_chain_rule_demo.py` | v0.5.1 demonstration | Direct CNRS-H finite-series chain-rule verification. |
