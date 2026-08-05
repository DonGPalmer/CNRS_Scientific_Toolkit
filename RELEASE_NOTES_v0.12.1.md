# CNRS Scientific Toolkit v0.12.1

**Release date:** 2026-08-04 documentation-synchronized rebuild  
**Theme:** Algebraic-curve intake, finite branch-point detection, and Problem 4 record synchronization.

## Added: algebraic-curve branch detection

- `cnrs.algebraic_curve.AlgebraicCurve` for accepting and validating polynomial relations `P(z,w)=0`.
- Exact construction of `P_w`, the resultant `Res_w(P,P_w)`, and the polynomial discriminant where available.
- Detection of candidate finite branch values from resultant roots.
- Recovery of ramification points satisfying `P=0` and `P_w=0` over each candidate value.
- Exact root handling when SymPy supplies complete roots, with explicit numerical fallback using `nroots`.
- Ramification multiplicity, exact/numerical status, residual, and warning metadata.
- Convenience functions `algebraic_curve(...)` and `finite_branch_points(...)`.
- Seven focused tests covering exact, numerical, unbranched, and repeated-component cases.

Install the optional algebraic dependency with:

```bash
pip install cnrs[algebraic]
```

## Problem 4 documentation synchronization

The full package now identifies the canonical Problem 4 record:

> Donald G. Palmer, *Partial Operational Completeness of a Positional Number System for Complex Numbers*, Version 12, Zenodo, 2026. DOI: `10.5281/zenodo.21791909`.

Updated current-status files:

- `README.md`
- `CITATION.cff`
- `RELEASE_NOTES.md`
- `docs/CLAIM_STATUS.md`
- `docs/THEOREM_ALIGNMENT.md`
- `docs/API_STATUS.md`
- `docs/TEST_STATUS.md`
- `docs/GAUSSIAN_RATIONAL_THEOREMS.md`
- `docs/CNRS_TOPOLOGY_AND_HYBRID.md`
- `docs/RESEARCH_STATUS.md`
- `docs/CNRS_P4_REFERENCE_STATUS.md` (new)

The documentation now distinguishes the resolved natural beta-adic completeness result from the separate open question of ordinary complex analytic convergence.

## Validation

```text
1206 passed, 0 failed
```

The suite reports 917 retained reliable-domain warnings from pre-existing scientific-workflow tests.

## Scope boundary

The algebraic-curve detector computes finite critical values of the projection `(z,w) -> z`. It does not yet:

- analyze branch behavior at infinity;
- normalize singular or reducible curves;
- infer monodromy permutations automatically;
- build Puiseux charts;
- certify numerical roots or continuation paths.

The bundled P4 records establish results only in their explicitly stated algebraic, beta-adic, coefficientwise, or formal domains. They do not identify the beta-adic completion with the ordinary complex plane and do not prove unrestricted analytic convergence of all CNRS-H series.
