# CNRS Scientific Toolkit v0.14.0 architecture freeze

Status: FROZEN FOR IMPLEMENTATION  
Freeze date: 2026-09-12  
Baseline: v0.13.1, commit e7f8424a967292a36643bb5fa8206ccb1d3f8fcd

## Release objective

v0.14.0 adds replayable, lazy CNRS division for exact Gaussian-rational inputs and machine-readable witnesses linking runtime results to the established canonical eventually-periodic representation. It does not replace or alter the v0.13.1 materialized division API.

Recommended release title:

> CNRS Scientific Toolkit v0.14.0 — Streaming Division and Formal–Runtime Witness Alignment

## Frozen component boundary

| Component | Responsibility | Dependency rule |
| --- | --- | --- |
| cnrs.streaming_division | Lazy digit production and bounded state resolution | Exact integer/Gaussian arithmetic only |
| cnrs.witnesses | Versioned JSON-safe witness creation and validation | May consume resolution records; no I/O |
| cnrs.division | Existing materialized division API | Preserved without signature changes |
| cnrs.canonical_periodic | Existing canonical value recovery and representation | Oracle for parity, not duplicated |
| CLI and serialization adapters | Optional presentation layer | Must not change mathematical outcomes |

The stream layer owns iteration state. The resolution layer owns the finite certificate obtained when termination or a repeated state is observed. The witness layer owns a stable serialization contract. These layers must not import Lean at runtime.

## Frozen data flow

1. Normalize numerator and nonzero denominator as an exact Gaussian fraction.
2. Remove the denominator's base-power factor and record power_offset.
3. Produce digits lazily from the exact residual-state recurrence.
4. On bounded resolution, stop at zero, a repeated state, or max_steps.
5. For a resolved result, produce a primitive period and an exact cycle witness.
6. Validate exact value equality against cnrs.canonical_periodic.

## Compatibility rules

- No breaking change to expand_division, canonical_expansion, CnrsRational, or existing dataclasses and enums.
- Existing imports continue to work.
- New public names are exported deliberately; wildcard exports are not expanded accidentally.
- Digits are immutable tuples in resolved records and lie in {0, 1, 2, 3, 4}.
- Every stream is replayable: separate iterations begin at digit zero and agree exactly.
- No floating-point conversion is allowed in the mathematical path.
- A bounded search limit is operational uncertainty, never a proof of aperiodicity.

## Dependency and performance policy

The implementation may use the Python standard library and existing cnrs exact-arithmetic modules. It may not add NumPy, SciPy, SymPy, a network call, generated native code, or a Lean runtime dependency. Memory used by taking n digits must be O(n); iteration must not pre-materialize an unbounded expansion.

## Change control

Implementation may optimize internals but must conform to the API contract, claim boundary, and acceptance plan in this freeze package. Any semantic change requires a dated amendment that identifies the changed clause, rationale, compatibility effect, and newly approved acceptance evidence.
