# CNRS v6.1 / Scientific Toolkit Merge Review

## Summary

AI0's `cnrs-python_v6.1` is a substantive update over v6.

Compared with v6:

```text
added files:   6
changed files: 3
removed files: 0
```

Added files:

```text
cnrs/cnrs_complex.py
cnrs/cnrs_ode.py
tests/test_cnrs_complex.py
tests/test_cnrs_ode.py
tests/test_evaluate_limitations.py
tests/test_rational_arithmetic.py
```

Changed files:

```text
cnrs/__init__.py
cnrs/cnrs_rational.py
pyproject.toml
```

## Key v6.1 additions

1. `cnrs_rational.py` now extends rational handling to **Laurent-periodic z0-adic** cases where denominators are divisible by 5.
2. `cnrs_complex.py` introduces `CnrsComplex`, a clean scientific complex interface wrapping CNRS-float.
3. `cnrs_ode.py` introduces CNRS-H coefficient recurrence solvers for linear ODEs.
4. New tests cover CNRS complex interface, ODEs, rational arithmetic, and limitation cases.

## v6.1 test status

```text
253 passed, 6 xfailed
```

The expected failures are limitation markers.

## Merge strategy used

The merged package starts from AI0's v6.1 as the base, then adds the v0.1 Scientific Toolkit layer:

```text
cnrs/science/
tests/test_science_toolkit.py
examples/science_workflows/
```

This avoids conflicts because the two toolkit directions are complementary:

- AI0's toolkit direction adds core scientific interfaces (`CnrsComplex`) and ODE solvers.
- The v0.1 layer adds workflow tools: branch objects, observation maps, scale-law helpers, and three-workflow comparisons.

## Resulting package

Output package:

```text
cnrs_scientific_toolkit_v0_2_v61_merged.zip
```
