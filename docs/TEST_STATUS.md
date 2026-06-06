# Test Status

Current package validation status for the v0.2.0 research-code package after merging the AI0 interoperability and example updates.

```text
559 passed, 6 xfailed
```

The 6 expected failures document known representational limits and are not regressions.

## Added in this merge

```text
cnrs/cnrs_interop.py              NumPy/SciPy interoperability bridge
tests/test_cnrs_interop.py        interoperability tests
tests/test_physics.py             standard QM/GR analytic-solution checks
examples/science_workflows/cnrs_vs_scipy_benchmark.py
examples/science_workflows/rlc_three_workflows.py
examples/science_workflows/turing_scale_exit.py
```

## Example smoke checks

The following examples were run successfully:

```text
python examples/science_workflows/turing_scale_exit.py
python examples/science_workflows/rlc_three_workflows.py
python examples/science_workflows/cnrs_vs_scipy_benchmark.py
```

## Notes

The test suite emits warnings when examples intentionally evaluate CNRS-H streams outside conservative reliable-domain estimates. These warnings are expected and document convergence-domain boundaries rather than test failures.
