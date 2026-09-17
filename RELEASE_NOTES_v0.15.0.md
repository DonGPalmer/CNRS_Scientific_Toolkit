# CNRS Scientific Toolkit v0.15.0

## Exact finite convolution and canonical witnesses

Version 0.15.0 implements the independently audited 42-gate finite-convolution
contract for exact Gaussian-coefficient Laurent sequences.

### Added

- strict Gaussian-integer coercion and canonical Gaussian-rational values;
- immutable finite Laurent sequences with exact evaluation;
- deterministic raw and chunked finite convolution;
- product-count limit states and deterministic progress records;
- exact canonical base-`(-2+i)` normalization;
- canonical JSON convolution witnesses with SHA-256 identities;
- independent nested-loop convolution and witness verification;
- equality-gated timing and peak-memory benchmark evidence;
- public exports, acceptance tests, claim guards, and CI integration.

### Compatibility

Existing v0.14 streaming-division and witness interfaces remain unchanged. No
existing public arithmetic signature was removed or modified.

### Claim boundary

The release covers exact finite arithmetic over the frozen carrier.
`max_products` bounds the counted coefficient products only.
`max_carry_steps` bounds post-input carry-drain steps only. These controls do
not bound coefficient bit length, Python-integer work, total allocation,
elapsed time, or total memory. No universal performance superiority,
arbitrary-infinite-stream multiplication, unrestricted analytic convergence,
or end-to-end Lean verification of the Python runtime is claimed.

### Validation

- dedicated v0.15 contract suite: 61 passed;
- unchanged v0.14 acceptance suite: 19 passed;
- standard full suite: 1,278 passed, 4 skipped, 922 warnings;
- full suite with optional pandas: 1,282 passed, 921 warnings;
- candidate checksum inventory: 16/16 PASS;
- implementation source index: 472/472 exact;
- exact-head Python/distribution runs: SUCCESS;
- exact-head Lean source identity plus six project builds: 7/7 SUCCESS;
- independent audit: PASS after one PR-body-only administrative correction.

The audited implementation head was
`0740c1e8ace7af98ac3ed4c76d6ba74610bada56`, tree
`88a545bbf359e2e5fe2b0d29111b915e08963e08`. PR #5 merged it normally as
`fa93a8307905961808321e19d7020dc7806e4e5f` with the identical tree.

The published v0.15.0 Zenodo version DOI is
`10.5281/zenodo.22812232`. The Toolkit concept DOI remains
`10.5281/zenodo.20574852`.
