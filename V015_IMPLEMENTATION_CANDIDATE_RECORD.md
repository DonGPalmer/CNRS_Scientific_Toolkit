# CNRS Scientific Toolkit v0.15.0 implementation candidate record

Status: **AMBER REPAIR IMPLEMENTED; LOCAL GATES PASS; TERMINAL CI/RE-AUDIT PENDING**

Date: 2026-09-15

## Governed baseline

- Approved freeze PR: `#4`
- Certified freeze head: `29c803e63dff298bf53400a74af70e305a7ab4a4`
- Governed merge commit: `017d9273e0f05d75b2019c623cd91c9615d9571a`
- Governed merge tree: `1e902ff53571161eca480329f25d8733efea6179`
- Implementation branch: `v015-finite-convolution-implementation`
- Initial public candidate head: `0bde37323cc9ef8c307fdcf0122d8d671157e7f6`
- Initial public candidate tree: `b3524233a5dac784ea6617346f8ad7893c5759f1`
- Initial push CI: `35117475678` — SUCCESS
- Initial PR CI: `35120250186` — SUCCESS
- Initial distribution artifact: `10456659344`
- Initial artifact digest: `sha256:acd7360737c8f233d4db20d80850d8671a5900b31f5c4cf5c2a6fc357d779942`
- Audited implementation commit: `2adf691b3ad25dd2db9a7be6d9aae92175a71db8`
- Audited implementation tree: `8e05246d477237bd96b6d3cb51c82a1f17404e9d`

## Implemented scope

- strict Gaussian-integer coercion and canonical Gaussian rationals;
- immutable finite Gaussian-coefficient Laurent sequences;
- exact raw finite convolution with deterministic traversal and product limits;
- deterministic chunked progress records;
- exact canonical base `-2+i` normalization;
- complete canonical convolution witnesses;
- independent nested-loop verification that does not import production convolution;
- equality-gated comparison and benchmark harness;
- public package exports and dedicated CI gates.

No existing arithmetic signature was changed. Package, runtime and citation metadata remain `0.14.1` during candidate validation.

## Local validation

| Gate | Result |
|---|---:|
| v0.15.0 contract tests | 61 passed |
| v0.15.0 plus unchanged v0.14 acceptance | 80 passed |
| Complete regression with optional data dependency | 1,282 passed; 921 warnings |
| Unchanged v0.14 acceptance suite | 19 passed |
| Claim-language guard | PASS |
| Independent-oracle import guard | PASS |
| Benchmark equality prechecks | PASS |
| Governed checksum inventory | 16/16 PASS |
| Source index | 472/472 exact |

The warnings are the pre-existing numerical-domain and pytest-deprecation notices. No v0.15.0 test failed.

## Boundary

The audit of public head `0bde373...` returned HOLD solely for evidence and
acceptance coverage. This repair adds committed exhaustive-small cases, the
complete frozen signature/limit/parser/witness-mutation matrices, negative
claim-guard cases, a restricted exact Lean theorem map, and benchmark evidence
tied to the accessible audited implementation commit above.

This record does not authorize merge, version activation, tagging or
publication. Because a tracked file cannot contain the identity of the commit
that contains it, the terminal repair head/tree, exact-head Python and Lean CI,
artifact identity, and re-audit disposition must be bound in PR #5 and the
independent re-audit record.
