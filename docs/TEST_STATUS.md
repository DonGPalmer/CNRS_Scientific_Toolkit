# Test Status — v0.6.0

Current validation status for the CNRS Scientific Toolkit v0.6.0 release candidate:

```text
842 passed, 6 xfailed
```

The 6 expected failures document known representational limits, including transcendental numbers and long-period rational cases. They are not regressions.

## v0.6.0 additions

- `tests/test_architecture_v060.py` checks the new package façades:
  - `cnrs.core`
  - `cnrs.h`
  - `cnrs.validation`
  - `cnrs.workflows`
- Confirms that flat historical imports still work.
- Confirms that `CnrsDual` is available through `cnrs.validation` as a reference layer.
- Confirms that the CNRS-H jet chain-rule path is available through the native `cnrs.h` façade.

## Recent regression totals

- v0.5.1: 811 passed, 6 xfailed.
- v0.5.2: 821 passed, 6 xfailed.
- v0.5.3: 830 passed, 6 xfailed.
- v0.5.4: 837 passed, 6 xfailed.
- v0.6.0: 842 passed, 6 xfailed.

## Recommended validation commands

```bash
python -m pytest -q
python examples/quickstart_cnrs.py
python examples/demo.py
python examples/scale_integration.py
python examples/science_workflows/chain_rule_scale_law.py
python examples/science_workflows/symbolic_chain_rule_demo.py
python examples/science_workflows/cnrs_h_native_chain_rule_demo.py
python examples/science_workflows/cnrs_h_local_scale_expansion_demo.py
python examples/science_workflows/cnrs_h_domain_diagnostics_demo.py
python examples/science_workflows/cnrs_h_taylor_model_demo.py
python -m cnrs.cli version
python -m compileall -q cnrs examples tests
```
