# CNRS Scientific Toolkit v0.17.0

## Exact CNRS-A string division

Version 0.17.0 connects finite CNRS-A strings to the exact streaming-division
engine released in v0.14.0. The public exact API returns a structured result
that explicitly distinguishes terminating, eventually-periodic, and
limit-reached outcomes.

### Added

- `divide_cnrs_exact` for exact division of two finite CNRS-A strings;
- `ExactDivisionResult` and `DivisionStreamStatus` outcomes for terminating,
  eventually-periodic, and limit-reached computations;
- exact Gaussian-rational value reconstruction for resolved results;
- deterministic division witnesses and independent witness revalidation;
- strict finite-string parsing and zero-divisor rejection;
- explicit counted-step limits whose exhaustion returns `LIMIT_REACHED`;
- static route, dependency, and legacy-complex-arithmetic isolation guards;
- clean wheel and source-distribution exact-division smoke tests.

### Compatibility

The historical `div_cnrs(a, b) -> str` API remains available for compatibility
and emits `DeprecationWarning` on call. It retains legacy Python-complex
behavior and is not part of the v0.17 exactness claim. Existing v0.16 exact
multiplication, v0.15 finite convolution, v0.14 streaming division, and earlier
compatible APIs remain unchanged.

### Outcome semantics

- `TERMINATING` identifies a finite exact quotient.
- `EVENTUALLY_PERIODIC` identifies an exact quotient represented by a
  deterministic preperiod and primitive cycle.
- `LIMIT_REACHED` is a reproducible operational outcome. It is not evidence
  that the quotient is aperiodic and does not expose a resolved witness.

The step limit bounds counted streaming recurrence steps only. It does not
bound wall-clock time, total memory, integer bit length, input or output size,
or witness-serialization cost.

### Claim boundary

Production exact division uses integer, Gaussian-integer, and rational-pair
arithmetic. Validation oracles are not production dependencies. The release
makes no universal elapsed-time, whole-memory, integer-bit-length,
arbitrary-infinite-stream, unrestricted analytic, or end-to-end Lean-
verification claim.

### Validation

- dedicated v0.17 tests: 65 passed;
- executable v0.17 acceptance: 6 passed;
- preserved v0.16 tests: 29 passed;
- preserved v0.16 acceptance: 5 passed;
- preserved v0.15 tests: 61 passed;
- preserved v0.14 acceptance: 19 passed;
- full regression: 1,378 passed, 4 skipped, 922 warnings;
- exact-head push and pull-request CI: SUCCESS;
- post-merge Python/distribution CI: SUCCESS;
- six-project, 79-file Lean identity: unchanged;
- independent implementation audit and two-file repair delta audit: PASS.

The audited implementation head was
`7840b51db1b7a3b9955aa20bd2b67fb99344335f`, tree
`924b8af717e17183e8bf9375adcb9fb35ca4093f`. PR #10 merged it normally as
`9965eb3bb2a1389469a4a99b90a03f6671fe76c8` with the identical tree.

The Toolkit concept DOI remains `10.5281/zenodo.20574852`. The v0.17.0
version DOI will be recorded after separately authorized GitHub release
publication and Zenodo processing.
