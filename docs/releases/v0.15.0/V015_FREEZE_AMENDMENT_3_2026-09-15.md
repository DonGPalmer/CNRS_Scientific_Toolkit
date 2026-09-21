# CNRS Scientific Toolkit v0.15.0 third freeze amendment — 2026-09-15

Status: THIRD AUDIT HOLD REPAIRED; INDEPENDENT RE-AUDIT REQUIRED

Audited predecessor: commit `13543667c5ad4339338abb0e7661e1c49be3f203`, tree `cccd9810ce074b5c839d295cd963cd1dd536950d`.

## Binding decisions

1. Canonical normalization uses the unique digit alphabet `{(0,0),(1,0),(2,0),(3,0),(4,0)}`.
2. For total Gaussian carry `t=(x,y)`, the digit is exactly `d=(x+2*y) % 5` in `{0,1,2,3,4}`, and the next carry is the exact Gaussian quotient `(t-(d,0))/(-2,1)`.
3. Every normalized stored coefficient is `(d,0)`; internal zero digits remain, while boundary zeros follow canonical trimming.
4. `normalize_gaussian_laurent` requires a `CNRSFiniteSequence` instance, including subclasses.
5. `max_carry_steps` is validated as `None` or a nonnegative exact `int`: Boolean/non-integer raises `TypeError`, negative raises `ValueError`.
6. `multiply_with_witness` validates `max_carry_steps` even when `normalize=False`; after validation the value is unused in that mode.
7. When `normalize=True` and the drain limit is insufficient, `NormalizationLimitError` propagates. No `MultiplicationResult`, normalized value, or witness is returned or created.
8. Product-count exhaustion remains the only condition represented by `ConvolutionStatus.LIMIT_REACHED`.

This third amendment and the synchronized contract documents control any conflicting earlier language. Runtime implementation remains prohibited until an independent re-audit returns GREEN.
