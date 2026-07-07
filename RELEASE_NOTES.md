# v0.10.1 — Formal Alignment and Reproducibility Release

v0.10.1 is a documentation and release-engineering update following the
CNRS-A arithmetic closure work. It aligns the software repository with the
mathematical record and improves reproducibility.

## Added

- theorem-to-implementation alignment documentation
- explicit capability/status table
- release verification guidance
- clean research-release packaging
- GitHub Actions test workflow

## Changed

- removed development cache artifacts from release package
- clarified the distinction between proved operations, implemented algorithms,
  computational validation, and open research questions

# v0.10.0 — Dual-Path Arithmetic, Carry-Guard Tightening, and Lagrange Inversion

v0.10.0 extends the v0.9.0 native core with three interconnected improvements:
tighter, proven carry-drain bounds in the CNRS-A arithmetic layer; a dual-path
architecture that automatically selects CNRS-A native or fast-path arithmetic
for `ScaleLaw` and `OdeSolution`; and native Lagrange series inversion in
coefficient space.

## Added

### `cnrs/cnrs_h_mode.py` — dual-path CNRS-H adapter (new module)

`CnrsHMode` wraps either `CnrsH` (fast, plain Python complex coefficients) or
`CnrsHNative` (CNRS-A digit-string coefficients) and exposes a uniform
interface. Path selection is automatic:

- **Auto (default):** uses `CnrsHNative` when all EGF coefficients are
  Gaussian integers representable in CNRS-A; falls back to `CnrsH` silently
  for float coefficients or Gaussian integers too large for exact CNRS-A
  floating-point expansion.
- **`native=True`:** forces `CnrsHNative`; raises `NonGaussianCoefficientError`
  if any coefficient is not a Gaussian integer.
- **`native=False`:** always uses the fast `CnrsH` path.

The active path is readable via `.native`.

### `ScaleLaw` and `OdeSolution` — dual-path integration

Both classes now accept an optional `native` parameter and expose a
`.native_mode` property. `ScaleLaw.derivative()` and `.integral()` propagate
the path. `cnrs_solve_linear` also accepts `native`.

`numpy_to_cnrsh` in `cnrs_interop.py` is fixed to return a plain `CnrsH`
stream for backward compatibility when the fitted coefficients are Gaussian
integers.

### `invert_native` — native Lagrange series inversion

`invert_native(f, order)` computes the compositional inverse g of a
`CnrsHNative` series f (i.e., f(g(s)) = s) using the Lagrange inversion
recurrence derived from Faà di Bruno's formula. All arithmetic routes through
CVal (add_cnrs / mul_cnrs); no Python arithmetic touches the EGF coefficients.

The recurrence:

```
g_1 = 1 / f_1
g_n = -(1/f_1) * Σ_{k=2}^n  f_k · B_{n,k}(g_1, …, g_{n-k+1})
```

where B_{n,k} are partial Bell polynomials built incrementally. Because
k ≥ 2 implies the Bell argument index n−k+1 ≤ n−1, each g_n is determined
solely from already-computed coefficients — the entire computation is a single
forward pass.

Requirements: f(0) = 0, f′(0) ∈ {1, −1, i, −i} (Gaussian integer units;
non-unit f′(0) produces non-integer inverse coefficients not storable in CVal).

`verify_inversion(f, order)` checks f(g(s)) = s at the digit-string level
(strictest standard: `strings_match=True`, `max_error=0.0`).

### `InversionError`

New exception raised by `invert_native` when f(0) ≠ 0 or f′(0) is not a
Gaussian unit. Exported from `cnrs` top-level.

## Fixed

### Native integration constants in `CnrsHMode.integrate()`

Fixed a native-mode bug where Gaussian-integer complex integration constants
such as `3+0j` or `1+2j` were incorrectly passed through `int()`, raising a
`TypeError`. Native mode now rounds valid Gaussian-integer complex constants to
complex Gaussian integers and rejects non-Gaussian constants with
`NonGaussianCoefficientError`. Regression coverage added in
`tests/test_cnrs_h_mode_integrate_v010.py`.

## Changed

### Carry-drain guards tightened

- `cnrs_add.py`: drain guard `1000 → 20`. Justified: the addition carry is
  always an element of the 14-state canonical set, so it drains in ≤ 14 steps.
  Guard of 20 provides a formal safety margin with explanatory comment.

- `cnrs_mul.py`: drain guard `1000 → 100`. The multiplication normalization
  carry is a general Gaussian integer (not bounded to the 14-state set);
  empirically drains in ≤ 12 steps for inputs up to ~10³ digits. Guard of 100
  is a well-motivated reduction from 1000 with a comment explaining why the
  bound differs from `add_cnrs`. A formal proof of the carry bound remains an
  open item (see Research Status).

## Exports added to `cnrs` top level

- `InversionError`
- `invert_native`
- `verify_inversion`
- `CnrsHMode`
- `native_eligible`

## Tests

```text
1121 passed, 6 xfailed
```

New test files:

- `tests/test_stress_outside_normal.py` (31 tests) — drain guard stress
  (`TestDrainGuardStress`, 6 tests: large/alternating coefficient injection,
  drain step bounds across 2 000 random trials, 300-digit string multiplication,
  2 000 random Gaussian-integer correctness checks) and dual-path architecture
  (`TestDualPathArchitecture`, 25 tests: auto-selection, large-Gaussian fallback,
  forced overrides, value agreement, path propagation, `ScaleLaw` and
  `OdeSolution` integration).

- `tests/test_cnrs_h_mode_integrate_v010.py` (6 tests) — regression coverage
  for native `CnrsHMode.integrate()` with real-complex and full Gaussian
  complex constants, rejection of non-Gaussian constants, fast-path
  preservation, and propagation through `ScaleLaw` / `OdeSolution`.

- `tests/test_lagrange_inversion.py` (57 tests) — Lagrange inversion across
  seven test classes: identity, log-from-exp closed form (coefficients and digit
  strings verified against (−1)^{n−1}·(n−1)!), quadratic shift (double-factorial
  coefficients), Gaussian unit f′(0) = i, negation self-inverse, round-trip
  composition across six series including double-inversion, and all error
  conditions.

---

# v0.9.0 — Native Rational Values and CNRS Scientific Workflows

v0.9.0 extends the v0.8.x theory-aligned core with enhanced capabilities that remain status-aware. It adds a value-facing CNRS rational layer for finite and periodic division outputs, and a small scientific workflow layer for measuring complex-state preservation before applying real-valued observation maps.

## Added

- `cnrs/rational_value.py` with `CnrsRationalValue`, `rational_value(...)`, and `rational_batch(...)`.
- Explicit finite / terminating / periodic / shifted-periodic rational-value reports.
- `cnrs/science/workflow.py` with observation-preservation reports and projection-loss diagnostics.
- `docs/CNRS_RATIONAL_VALUES.md`.
- `docs/CNRS_SCIENTIFIC_WORKFLOWS_V090.md`.
- `tests/test_rational_value_v090.py`.
- `tests/test_scientific_workflow_v090.py`.
- `examples/science_workflows/cnrs_v090_preservation_workflow_demo.py`.

## Corrected / clarified framing

- General rational division is represented through structured finite or periodic expansions, not finite-string field closure.
- `CVal` remains the finite Gaussian-integer CNRS-A value wrapper; terminating base-power fractions are finite CNRS expansions but not Gaussian-integer `CVal` objects.
- Scientific workflows preserve complex/CNRS state first and apply observation maps explicitly.
- Projection diagnostics are workflow measurements, not new physical claims.

## Validation

```text
1026 passed, 6 xfailed
```

The 6 expected failures remain known representational-limit tests, not regressions.

---

# v0.8.1 — Theory-Aligned Normalization, Division, and Formal-State Preservation

v0.8.1 consolidates the v0.8.0 native core and includes the v0.8.2-style cleanup work discussed for the theory-aligned line. The release focuses on internal consistency rather than adding workaround capability.

## Added

- `cnrs/normalization.py` with scoped normalization routes:
  - bounded addition-transducer normalization;
  - general finite coefficient normalization;
  - multiplication-convolution normalization as a separate scope.
- `cnrs/theorem_alignment.py`, a registry mapping implementation features to theorem-backed, computationally verified, conditional, bridge, validation, scaffold, or open status.
- Expanded `cnrs/division.py` structured reports:
  - `structured_digits()`;
  - `division_summary()`;
  - explicit tail kind, persistent denominator, preperiod, and period metadata.
- Expanded `cnrs/formal_state.py` with CNRS* preservation operations:
  - differentiation;
  - integration;
  - addition;
  - multiplication;
  - preservation reports.
- Documentation:
  - `docs/CNRS_NORMALIZATION_STATUS.md`;
  - `docs/CNRS_DIVISION_STRUCTURED_EXPANSIONS.md`;
  - `docs/CNRS_THEOREM_ALIGNMENT_REGISTRY.md`;
  - `docs/CNRS_FORMAL_STATE_PRESERVATION.md`.
- Tests:
  - `tests/test_normalization_v081.py`;
  - `tests/test_division_structured_v081.py`;
  - `tests/test_formal_state_preservation_v081.py`;
  - `tests/test_theorem_alignment_v081.py`.

## Corrected framing

- The 14-state normalizer is explicitly scoped to bounded addition inputs.
- Multiplication is described as convolution followed by general CNRS-A normalization.
- General finite coefficient normalization is treated as a distinct native core route.
- Division returns structured prefix/period data and does not claim finite-string field closure.
- CNRS* state preservation is implemented as finite local state preservation; full branch-composition semantics remains scope-qualified.

## Validation

```text
1015 passed, 6 xfailed
```

---

# v0.8.0 — CNRS-A Native Values and CNRS-H Native Coefficient Calculus

v0.8.0 was a theorem-alignment release. It incorporated the AI0 native-arithmetic work into the CNRS-native architecture and added division/status tooling consistent with the current theoretical work.

## Added

- `cnrs/cnrs_value.py` updated with native negation and subtraction using `-1 = "144"`.
- `cnrs/cnrs_h_native.py` for CNRS-H coefficient calculus with `CVal` coefficients.
- `cnrs/division.py` for theory-aligned division classification and structured expansion wrappers.
- `cnrs/formal_state.py` for a lightweight CNRS* state tuple.
- `docs/THEOREM_ALIGNMENT.md`.
- `docs/CNRS_DIVISION_STATUS.md`.
- `docs/CNRS_H_NATIVE.md`.
- `docs/CNRS_FORMAL_STATE.md`.
- Native tests for CVal arithmetic, CNRS-H native coefficient calculus, native composition, chain rule, division status, and formal state behavior.

## Corrected framing

- The 14-state normalizer is scoped to bounded addition inputs.
- Multiplication remains native, but is described as convolution followed by general CNRS-A normalization.
- CNRS-H composition is classified as algorithmic-native finite-order coefficient calculus, not as a finite-state CNRS-A transducer.
- Division is classified as finite, shifted, or eventually periodic; finite-string field closure is not claimed.

## Validation

```text
1003 passed, 6 xfailed
```

---

# Earlier public milestones

- **v0.7.1** — Native-status and internal-consistency registry.
- **v0.7.0** — CNRS-native scientific state / branch-aware local continuation line.
- **v0.6.0** — CNRS-native core architecture with `cnrs.core`, `cnrs.h`, `cnrs.validation`, and `cnrs.workflows` façades.
- **v0.5.x** — CNRS-H bridge, direct chain rule, jets, domain diagnostics, and Taylor-model metadata.
- **v0.4.x** — Chain-rule autodiff, symbolic differentiation/integration, and CLI.
- **v0.3.0** — Multi-scale physics engine and scale-regime detection.
- **v0.2.x** — Interoperability, examples, Zenodo metadata, and public project packaging.
- **v0.1.0** — Initial CNRS Scientific Toolkit release.
