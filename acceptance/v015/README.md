# CNRS Scientific Toolkit v0.15.0 candidate acceptance

The executable 42-gate contract is represented by:

- `tests/test_v015_finite_convolution.py` for the frozen public API, exact arithmetic, limits, canonical normalization, witnesses and independent verification;
- `acceptance/v014/test_streaming_division_contract.py` for unchanged v0.14 behavior;
- `tools/check_v015_claims.py` for claim-language and verifier-independence guards;
- `benchmarks/benchmark_finite_convolution.py` for equality-gated timing and peak-memory evidence;
- the complete regression suite and existing Lean source-identity workflow.

Candidate command:

```bash
pytest -q tests/test_v015_finite_convolution.py
pytest -q acceptance/v014
python tools/check_v015_claims.py
python benchmarks/benchmark_finite_convolution.py --output-dir benchmark-results/v015
```

Package, runtime and citation versions remain `0.14.1` during candidate development.
