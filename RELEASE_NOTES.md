# CNRS Scientific Toolkit v0.8.0

Theme: **CNRS-A Native Values and CNRS-H Native Coefficient Calculus**.

This release moves the toolkit from native-status classification toward theory-aligned native implementation. It incorporates the AI0 native arithmetic work and updates it to match the current CNRS theoretical direction.

## Added

- `cnrs/cnrs_value.py` with `CVal`, a canonical CNRS-A value wrapper.
- Native negation using the finite CNRS-A representation `-1 = "144"`.
- Native subtraction as `a + (-b)`.
- `cnrs/cnrs_h_native.py` with `CnrsHNative`, a CNRS-H EGF object whose coefficients are `CVal` instances.
- Native CNRS-H EGF product through binomial convolution over `CVal` coefficients.
- Native finite-order composition by Faà di Bruno / Bell-polynomial recurrence.
- Native finite-order chain-rule and Leibniz verification helpers.
- Theory-aligned division classification.
- Lightweight CNRS* formal state support.
- Documentation for theorem alignment, division status, native coefficient calculus, and formal-state structure.
- Tests for `CVal` arithmetic, CNRS-H native coefficient calculus, native composition, chain rule, division classification/status, and formal state behavior.

## Corrected framing

- The 14-state normalizer is scoped to bounded addition input.
- Multiplication is described as convolution followed by general CNRS-A normalization.
- CNRS-H composition is algorithmically native, not finite-state-native for non-polynomial outer functions.
- Division is classified as finite, shifted, or eventually periodic; finite-string field closure is not claimed.
- Python complex arithmetic remains a validation, bridge, or evaluation interface where used; it is not presented as the CNRS-native layer.

## Validation

```text
1003 passed, 6 xfailed
```

The 6 expected failures remain known representational-limit tests, not regressions.

---

## Public release context

This release supersedes the internal v0.7.1 native-status cleanup and extends the v0.7.0 CNRS scientific-state direction with native CNRS-A coefficient arithmetic and theory-aligned CNRS-H operations.

Relevant prior milestones:

- **v0.7.1** — native-status and internal-consistency register.
- **v0.7.0** — CNRS scientific state object for local scientific workflows.
- **v0.6.0** — CNRS-native core architecture with separated native, bridge, validation, scaffold, and workflow layers.
- **v0.5.x** — CNRS-H jets, domains, Taylor-style metadata, and finite-order chain-rule support.
- **v0.4.x** — symbolic calculus and chain-rule/autodiff bridge infrastructure.

