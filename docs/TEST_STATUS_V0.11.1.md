# Test Status — v0.11.1

v0.11.1 adds regression coverage for the corrected numerator-aware division classification.

## Required release checks

- full `pytest` suite;
- no unexpected failures;
- corrected `1/5` and `1/25` shifted-periodic classifications;
- terminating cancellation cases `conjugate(beta)/5` and `conjugate(beta)**2/25`;
- agreement between the legacy compatibility API and `cnrs.division`;
- wheel and source-distribution build;
- `twine check` for all built artifacts;
- clean-environment import smoke test.

The final numeric pass count must be inserted only after running the complete v0.11.1 repository. The earlier v0.11.0 release-page count of 1167 and the later audit count of 1172 refer to different repository states and should not be copied into this file without a fresh run.
