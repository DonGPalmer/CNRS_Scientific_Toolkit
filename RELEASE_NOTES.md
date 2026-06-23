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

Validation in the build environment:

```text
1015 passed, 6 xfailed
```

The 6 expected failures remain known representational-limit tests, not regressions.

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
