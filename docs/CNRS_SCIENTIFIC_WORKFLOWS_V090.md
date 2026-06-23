# CNRS Scientific Workflows (v0.9.0)

v0.9.0 adds small workflow helpers that make complex-state preservation measurable.

The workflow rule is:

> keep the complex/CNRS state intact first; apply real-valued observation maps only when the workflow explicitly asks for them.

## Main API

```python
from cnrs import build_preservation_report

report = build_preservation_report(state, points, name="example")
print(report.summary())
```

The report samples a state, stores the complex values, applies standard observation maps, and returns projection diagnostics such as:

- real-projection relative error;
- modulus-projection relative error;
- squared-modulus projection relative error;
- phase span;
- mean phase rate;
- modulus and intensity variation.

## Purpose

The purpose is not to introduce a new physical claim. It is to provide a reusable diagnostic harness for the CNRS programme question: what information is preserved by a complex-state workflow and what is lost by early projection to real-valued observables?
