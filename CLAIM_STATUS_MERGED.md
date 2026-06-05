# Merged Claim Status — CNRS Scientific Toolkit v0.2 / CNRS v6.1

## Base package

This merged package uses AI0's CNRS v6.1 as the base.

v6.1 contributes:

- Laurent-periodic Gaussian rational representation for denominators divisible by 5.
- `CnrsComplex`, a clean scientific interface around CNRS-float.
- `cnrs_ode.py`, CNRS-H coefficient-recurrence solvers for linear ODEs.
- Expanded tests for rational arithmetic, complex interface, ODEs, TC equations, and known limitations.

## Science layer

The merged package adds the v0.1 `cnrs.science` layer:

- branch-aware complex values;
- explicit observation maps;
- CNRS-H scale-law utilities and fitting;
- three-workflow comparisons:
  - A: early real reduction,
  - B: ordinary complex late reduction,
  - C: CNRS complex-state late reduction.

## Current research-use claim

The package is now stronger as a scientific workbench because the AI0 layer and the v0.1 science layer are complementary:

- `CnrsComplex` gives a user-facing complex numeric wrapper.
- `cnrs_ode` gives CNRS-H coefficient-level ODE solutions.
- `cnrs.science.observation` gives explicit real/complex observation maps.
- `cnrs.science.three_workflows` gives reproducible comparisons showing what early real reduction loses.
- `cnrs_rational` now handles finite, pure periodic, and Laurent-periodic rational cases.

## Known boundaries

The package contains expected-failure tests documenting some limitations. These are useful markers for future work rather than accidental failures.
