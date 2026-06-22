# Test Status — v0.4.0

Current validation status for the CNRS Scientific Toolkit v0.4.0 release candidate:

```text
733 passed, 6 xfailed
```

The 6 expected failures document known representational limits, including transcendental numbers and long-period rational cases. They are not regressions.

New in v0.4.0:

- `tests/test_autodiff_chain_rule.py`
- First-order chain-rule autodiff tests over `CnrsComplex` via `CnrsDual`
- Analytic derivative checks for arithmetic, elementary functions, nested composition, scale-law derivatives, and branch-aware logarithm values

Recommended release validation commands:

```bash
python -m pytest -q
python examples/quickstart_cnrs.py
python examples/demo.py
python examples/scale_integration.py
python examples/science_workflows/chain_rule_scale_law.py
for f in examples/science_workflows/*.py; do python "$f"; done
```
