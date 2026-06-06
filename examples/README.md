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

## Smoke testing examples

From the repository root:

```bash
python examples/quickstart_cnrs.py
python examples/science_workflows/turing_scale_exit.py
python examples/science_workflows/rlc_three_workflows.py
python examples/science_workflows/cnrs_vs_scipy_benchmark.py
```

See `docs/EXAMPLE_SMOKE_STATUS.md` for the currently recorded smoke-test status.
