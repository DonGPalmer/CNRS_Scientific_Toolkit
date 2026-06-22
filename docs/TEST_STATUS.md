# Test Status — v0.5.1

Current validation status for the CNRS Scientific Toolkit v0.5.1 release candidate:

```text
811 passed, 6 xfailed
```

The 6 expected failures document known representational limits, including transcendental numbers and long-period rational cases. They are not regressions.

New in v0.4.0:

- `tests/test_autodiff_chain_rule.py`
- First-order chain-rule autodiff tests over `CnrsComplex` via `CnrsDual`
- Analytic derivative checks for arithmetic, elementary functions, nested composition, scale-law derivatives, and branch-aware logarithm values

New in v0.5.1:

- CLI polish tests in `tests/test_cli.py` for `cnrs examples` and friendlier missing-variable errors.
- Full-suite regression status: 811 passed, 6 xfailed.

Previously added in v0.4.1/v0.4.2:

- `tests/test_symbolic_diff.py` for minimal symbolic differentiation.
- `tests/test_symbolic_integrate.py` for conservative symbolic integration.

Recommended release validation commands:

```bash
python -m pytest -q
python examples/quickstart_cnrs.py
python examples/demo.py
python examples/scale_integration.py
python examples/science_workflows/chain_rule_scale_law.py
python examples/science_workflows/symbolic_chain_rule_demo.py
for f in examples/science_workflows/*.py; do python "$f"; done
```


New in v0.5.1:

- Direct CNRS-H chain-rule tests: `tests/test_cnrs_h_chain_rule.py`
- Full-suite regression status: 811 passed, 6 xfailed.
