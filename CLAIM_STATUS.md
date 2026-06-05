# Claim Status

This file summarizes the current status of CNRS Scientific Toolkit claims for readers, reviewers, and contributors.

## Tested in the package

The package currently includes tests covering:

```text
CNRS base value and norm
Gaussian-integer representation and round-trip behavior
CNRS-A addition and multiplication semantics
Layer-2 branch-index arithmetic
CNRS-H coefficient-shift differentiation and integration
CNRS-float encode/decode behavior
Gaussian rational arithmetic, including periodic and Laurent-periodic cases
CnrsComplex interface behavior
CNRS-H ODE solvers
Observation-map workflows
Branch / winding workflows
Scale-law fitting and differentiation
Three-workflow comparison examples
```

The current test status is:

```text
260 passed, 6 xfailed
```

The expected failures document known boundaries and limitation cases.

## Practical capabilities

The package currently supports practical experimentation with:

```text
exact finite Gaussian-integer CNRS arithmetic
CNRS-float approximate complex representation
Gaussian rational CNRS representations
CNRS-H coefficient calculus
linear ODE solution through CNRS-H coefficient recurrences
branch-aware complex-state bookkeeping
explicit observation maps: Re, Im, |z|, |z|², phase, and phase-current proxy
scale-law fitting and derivative extraction
three-workflow comparisons:
  A = early real reduction
  B = ordinary complex late reduction
  C = CNRS complex-state late reduction
```

## Scientific use case

The strongest current use case is complex-state preservation.

Many scientific calculations eventually produce real-valued observables, but the working state may be complex-valued. Early reduction to real quantities can discard phase, branch, winding, interference, and observation-map information. CNRS Scientific Toolkit provides tools for keeping the complex state available until the appropriate observation map is chosen.

## Open development areas

Useful next development targets include:

```text
direct CNRS Layer-2 analytic-continuation workflows
more real-data examples
performance and stability comparisons
integration with NumPy/SciPy workflows
more ODE/PDE benchmark systems
expanded scale-law and multiscale modelling examples
clearer contributor documentation
```

## Contributor orientation

This repository is intended to support inspection, testing, extension, and critique. Contributions that add tests, examples, benchmarks, documentation, or clearer mathematical boundaries are especially valuable.
