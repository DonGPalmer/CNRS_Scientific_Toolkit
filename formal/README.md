# Formal verification

This directory contains machine-checkable formalizations that support specific mathematical claims used by the CNRS Scientific Toolkit.

## Current formal project

`formal/lean/CnrsQ2/` formalizes the CNRS Q2 beta-adic metric-completion and digit-expansion results for the Gaussian base

`beta = -2 + i`, with `N(beta) = 5` and digit alphabet `{0,1,2,3,4}`.

The project is pinned to Lean 4 `v4.33.0` and Mathlib `v4.33.0`. Its governed programme source is the CNRS Q2 Lean project maintained under the SSC programme archive; this repository copy is the software-distribution and CI copy. The checked-in `CnrsQ2/` tree is the governed v3 source tree rather than a rewritten Python-facing variant.

### Verification boundary

The Lean project machine-checks, among other items:

- `beta` has norm 5 and is prime in the Gaussian integers;
- the five digits give the required residue representatives modulo `beta`;
- an injective dense embedding of the Gaussian integers into `Z_5` carrying `beta` to norm `1/5`;
- the corresponding field-level embedding into `Q_5`;
- unique one-step digit extraction/reduction in `Z_5`;
- existence and uniqueness of the infinite `Fin 5` digit expansion with convergent partial sums.

This does **not** by itself prove that every Toolkit algorithm is a refinement of the Lean construction. The crosswalk in `docs/LEAN_FORMALIZATION_ALIGNMENT.md` records which software components are direct implementation targets, contextual companions, or still require a refinement proof.

### Build

From `formal/lean/CnrsQ2/`:

```bash
lake build
```

The GitHub workflow `.github/workflows/lean.yml` runs this independently of the Python test suite.
