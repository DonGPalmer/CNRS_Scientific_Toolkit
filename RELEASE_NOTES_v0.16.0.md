# CNRS Scientific Toolkit v0.16.0

## Exact CNRS-A string multiplication

Version 0.16.0 connects finite CNRS-A strings to the exact Gaussian/Laurent
carrier released in v0.15.0 and routes public string multiplication through
that exact arithmetic spine.

### Added

- exact parsing from the frozen finite CNRS-A grammar into
  `CNRSFiniteSequence`;
- canonical formatting from digit-valued finite carriers back to CNRS-A text;
- public exports `cnrs_string_to_finite_sequence` and
  `finite_sequence_to_cnrs_string`;
- exact `mul_cnrs` routing through `convolve_exact` and
  `normalize_gaussian_laurent`;
- independent rational-pair and historical-parity validation oracles;
- static route and anti-regression guards, including division and duplicate
  arithmetic-loop rejection;
- clean wheel and source-distribution bridge/fractional-product smoke tests.

### Compatibility

The public `mul_cnrs(a, b) -> str` signature is unchanged. Existing valid
finite-input outputs, v0.15.0 convolution and witness interfaces, v0.14.0
streaming-division contracts, and earlier compatible APIs remain unchanged.

### Claim boundary

Production parsing, convolution, carry normalization, and formatting use
integer or Gaussian-integer arithmetic. Validation oracles are not production
dependencies. The release makes no universal elapsed-time, whole-memory,
integer-bit-length, arbitrary-infinite-stream, unrestricted analytic, or
end-to-end Lean-verification claim.

### Validation

- dedicated v0.16 tests: 29 passed;
- executable v0.16 acceptance: 5 passed;
- exhaustive valid strings: 4,490;
- canonical operands: 425;
- exhaustive operand pairs: 180,625;
- randomized long round trips: 5,000;
- randomized exact-value/parity products: 5,000;
- 300-digit all-`4` stress: exact parity and value PASS;
- preserved v0.15 tests: 61 passed;
- preserved v0.14 acceptance: 19 passed;
- full regression: 1,310 passed, 4 skipped, 922 warnings;
- exact-head push and pull-request CI: SUCCESS;
- six-project, 79-file Lean identity: unchanged;
- independent audit: PASS after additive administrative reconciliation.

The audited implementation head was
`ba1f5eda0e359f10926587ced89e6dececb5e87d`, tree
`884b23bc0e775efe4330823d954ad05dca12658c`. PR #8 merged it normally as
`b382209899e97a64249d74291ce1b3268f84c64b` with the identical tree.

The Toolkit concept DOI remains `10.5281/zenodo.20574852`. The v0.16.0
version DOI will be recorded after separately authorized GitHub release
publication and Zenodo processing.
