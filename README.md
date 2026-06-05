# CNRS Scientific Toolkit

CNRS Scientific Toolkit is an open research-code package for exploring the Complex Numeric Representational System (CNRS): complex-base representation, CNRS-float, branch-aware complex-state workflows, CNRS-H scale-law calculus, and CNRS-H coefficient-based ODE methods.

The package is designed to interoperate with ordinary scientific workflows:

```text
standard real/complex input
    -> CNRS exact / float / rational / branch / H-calculus representation
    -> complex-state-preserving workflow
    -> standard real/complex/decimal output
```

## What is included

```text
cnrs/                  Core CNRS implementation and scientific modules
tests/                 Pytest test suite
examples/              Runnable scientific workflow examples
README.md              Project overview and quick start
CLAIM_STATUS.md        Current tested/practical/open claim status
TEST_STATUS.md         Captured test output
RELEASE_NOTES.md       Current release summary
```

Core capabilities include:

```text
CNRS-A finite complex-base representation over z0 = -2+i
CNRS addition and multiplication
Gaussian rational representation, including periodic and Laurent-periodic cases
CNRS-float approximate complex representation
CnrsComplex scientific interface
CNRS-H coefficient calculus
CNRS-H linear ODE solvers
Branch-aware complex-state helpers
Explicit observation maps
Scale-law fitting and differentiation
Three-workflow comparison examples
```

Additional documentation can be added later as the public repository develops.

## Scientific purpose

The toolkit is meant to make CNRS inspectable, testable, and extensible. It provides working code, tests, and examples for evaluating where CNRS may be useful in scientific computation, especially where complex-valued state should be preserved before choosing a real-valued observation map.

A recurring workflow in the examples is:

```text
A. early real reduction
B. ordinary complex late reduction
C. CNRS complex-state late reduction
```

This helps test what information is lost when calculations are projected to real-valued observables too early.

## Project documentation

CNRS Scientific Toolkit is part of the broader Scale Space / CNRS research programme.

Project index and reading guide:

https://www.nul1.com/

The project index connects the book-level synthesis, Scale Space papers, CNRS mathematical documents, software-related records, open problems, and Zenodo concept DOI records. For technical background and citation routes, start there.

## Quick start

From the repository root:

```bash
python -m pytest -q
python examples/science_workflows/interference_three_workflows.py
python examples/science_workflows/complex_scale_law.py
python examples/science_workflows/phase_branch_tracking.py
python examples/science_workflows/scale_law_fit_demo.py
python examples/science_workflows/observation_maps_demo.py
```

## Example: complex scale law

```python
from cnrs.science.three_workflows import compare_complex_scale_law

result = compare_complex_scale_law(alpha=-0.14, omega=4.25, omega2=1.75)
print(result.metrics)
```

This compares early modulus-squared reduction with complex-state-preserving workflows and shows how the oscillatory scale frequency is retained in the complex state.

## Claim status

See [`CLAIM_STATUS.md`](CLAIM_STATUS.md) for a concise summary of what is tested, what is currently practical, and what remains open.

## Test status

The current package test suite passed in this environment:

```text
260 passed, 6 xfailed
```

See [`TEST_STATUS.md`](TEST_STATUS.md) for the captured test output.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
