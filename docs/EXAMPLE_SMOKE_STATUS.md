# Example Smoke Status — v0.5.1

The following examples are expected to run from the repository root.

```bash
python examples/quickstart_cnrs.py
python examples/demo.py
python examples/scale_integration.py
python examples/science_workflows/chain_rule_scale_law.py
python examples/science_workflows/symbolic_chain_rule_demo.py
python examples/science_workflows/symbolic_integration_demo.py
python examples/science_workflows/cnrs_multiscale_turing_window.py
python examples/science_workflows/cnrs_rd_scale_exit_demo.py
python examples/science_workflows/cnrs_vs_scipy_benchmark.py
python examples/science_workflows/complex_scale_law.py
python examples/science_workflows/interference_three_workflows.py
python examples/science_workflows/observation_maps_demo.py
python examples/science_workflows/phase_branch_tracking.py
python examples/science_workflows/rlc_three_workflows.py
python examples/science_workflows/scale_law_fit_demo.py
python examples/science_workflows/turing_scale_exit.py
```

CLI smoke checks:

```bash
python -m cnrs.cli version
python -m cnrs.cli examples
python -m cnrs.cli diff "sin(exp(s/L))" --var s --at s=1.2,L=5
```

`chain_rule_scale_law.py` demonstrates first-order automatic differentiation for composed CNRS-compatible scientific workflows.

`symbolic_chain_rule_demo.py` demonstrates minimal symbolic differentiation plus symbolic-vs-autodiff derivative cross-checks.

`symbolic_integration_demo.py` demonstrates conservative rule-based symbolic integration and unevaluated `Integral` fallback.

- `examples/science_workflows/branch_aware_symbolic_demo.py` — branch-aware symbolic log/sqrt/power demonstration.


## v0.5.1 symbolic-to-CNRS-H bridge

The v0.5.1 release adds `cnrs.cnrs_h_bridge`, a conservative bridge from supported symbolic expressions to finite CNRS-H EGF coefficient representations.  It supports constants, polynomials, simple scale laws such as `A*exp(k*s)`, and `exp`/`sin`/`cos` of affine arguments.  Unsupported expressions raise `UnsupportedBridgeExpression`.


## v0.5.1 direct CNRS-H chain-rule example

Smoke target:

```bash
python examples/science_workflows/cnrs_h_native_chain_rule_demo.py
```

Expected result: the direct CNRS-H chain-rule comparison passes with zero or near-zero coefficient error for the demonstrated finite series.
