# Test Status — v0.11.0

Release validation on 2026-07-08:

- `1167 passed`
- `0 xfailed`
- `0 unexpected failures`

## New validation groups

- exact division and Gaussian-rational reconstruction;
- denominator classification and equivalent-fraction invariance;
- periodic and Laurent-periodic evaluation;
- sampled period minimality;
- ODE, scale-law, biological, oscillator, and interoperability cross-validation.

The warning stream consists primarily of documented domain warnings for truncated EGF evaluations outside estimated reliable intervals. Warnings are not silently suppressed because they are part of the scientific-domain safety behavior.

- Includes 11 theorem-specific tests for ideal/valuation termination and canonical periodic normalization.


## v0.11.0 topology and hybrid additions

- Symbolic prefix space and beta-adic valuation-ring completeness: **established within current model**.
- Finite-Laurent completion as the local field at `beta=-2+i`: **established within current model**.
- Identification with ordinary complex topology: **disproved**; the topologies are incompatible.
- CNRS-H coefficientwise completeness over a complete coefficient ring: **established within current model**.
- Hybrid CNRS-A/CNRS-H differential-algebra representation theorem: **established within current model**, conditional on a canonical coefficient codec for the selected ring.
- Ordinary complex analytic convergence: separate and dependent on coefficient embedding and growth bounds.
