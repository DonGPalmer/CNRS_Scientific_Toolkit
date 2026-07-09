# Scientific Workflow Audit — v0.11.0

The scientific layer was reviewed against independent closed-form and symbolic/numerical reference calculations.

## Audited modules

- `cnrs_ode.py`: first- and second-order linear ODE coefficient recurrences;
- `cnrs_scale.py`: exponential scale laws and domain diagnostics;
- `cnrs_bio.py`: diffusion profiles, Gierer–Meinhardt steady state, Jacobian, and Turing diagnostics;
- `cnrs_oscillator.py`: damped complex oscillator and interference workflows;
- `cnrs_interop.py`: early-real, late-complex, and CNRS complex-state comparison infrastructure;
- `cnrs_multiscale.py`: surveyed for parameter propagation and scale-rung consistency.

## Findings

1. The core ODE recurrences reproduce closed-form exponential and oscillator solutions within their stated truncated-EGF domains.
2. Biological diffusion profiles reproduce their declared exponential laws; the steady state and Jacobian tests agree with the implemented Gierer–Meinhardt equations.
3. Oscillator workflows preserve complex amplitude and phase until the selected observation map is applied.
4. Existing domain warnings are appropriate, but examples evaluated outside the stated domain should not be interpreted quantitatively without increasing terms or using step-and-shift continuation.
5. The scientific modules are reference and exploratory workflows. Validation shows that the implementations reproduce their stated equations; it does not independently establish the physical interpretation of those equations.

## Status

- numerical implementation of stated equations: **Established within current model**;
- physical applicability to Scale Space or biological systems: **Derived, conditional** or **Speculative**, depending on the workflow;
- claim that CNRS necessarily changes a physical prediction rather than its representation: **Open and workflow-dependent**.
