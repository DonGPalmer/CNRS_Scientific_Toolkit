# v0.9.0 Test Status

Validation in the build environment: `1026 passed, 6 xfailed`. The expected failures remain known representational-limit tests, not regressions.

# Test Status — v0.8.1

Current validation status for the CNRS Scientific Toolkit v0.8.1 build:

```text
1015 passed, 6 xfailed
```

The 6 expected failures document known representational limits, including
transcendental numbers and long-period rational cases. They are not regressions.

## v0.8.1 additions

- `tests/test_normalization_v081.py` checks scoped CNRS-A normalization:
  bounded addition, general finite coefficients, and multiplication convolution.
- `tests/test_division_structured_v081.py` checks structured prefix/period
  division reports.
- `tests/test_formal_state_preservation_v081.py` checks CNRS* state
  preservation operations.
- `tests/test_theorem_alignment_v081.py` checks the theorem-alignment registry.

## Recent regression totals

- v0.8.0: 1003 passed, 6 xfailed.
- v0.8.1: 1015 passed, 6 xfailed.

## Recommended validation commands

```bash
python -m pytest -q
python -m cnrs.cli version
PYTHONPATH=. python tools/audit_native_status.py
python -m compileall -q cnrs examples tests tools
```
