# Research Status

CNRS Scientific Toolkit is an **open research-code package** supporting the development and evaluation of the Complex Numeric Representational System (CNRS) and related multi-scale modeling concepts.

The repository contains reference implementations, experimental algorithms, validation tests, and demonstration models. It is intended to support investigation, reproducibility, criticism, and extension by other researchers.

## What this package is

The toolkit is:

- a reference implementation of current CNRS research;
- a platform for experimentation and reproducibility;
- a computational companion to associated papers and technical notes;
- a place to test arithmetic, calculus, normalization, transducer, and scientific-workflow ideas;
- an invitation for independent analysis and extension.

## What this package is not

The toolkit is not presented as:

- a completed mathematical theory;
- a production numerical-analysis library;
- a validated biological or physical model suite;
- proof that any broader scientific interpretation is established.

Inclusion of a module, example, or algorithm does **not** imply that the associated scientific hypothesis has been experimentally validated.

## Current maturity levels

The package contains several maturity levels.

### Reference / tested implementation

Core arithmetic and calculus routines with automated regression tests, including CNRS-A arithmetic and CNRS-H coefficient calculus.

### Experimental but tested utilities

Modules that implement research ideas with representative tests, including rational expansion, CNRS-float, branch-state helpers, scale-law tools, ODE solvers, interop utilities, biological-scale examples, and oscillator examples.

### Demonstrations and examples

Runnable scripts that show how CNRS structures can be used in scientific workflows. These examples are intended to be inspectable and modifiable, not final scientific validation.

### Open research scaffolding

Partial or exploratory components for analytic continuation, global constraints, global solvers, and broader layered architectures.

## Related status documents

- `docs/CLAIM_STATUS.md` summarizes claim status.
- `docs/TEST_STATUS.md` summarizes automated-test status.
- `docs/EXAMPLE_SMOKE_STATUS.md` summarizes example smoke-test status.
- `docs/API_OVERVIEW.md` summarizes the module layout.
