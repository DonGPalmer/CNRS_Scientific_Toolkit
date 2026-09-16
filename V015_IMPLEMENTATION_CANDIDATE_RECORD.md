# CNRS Scientific Toolkit v0.15.0 implementation candidate record

Status: **IMPLEMENTED; LOCAL GATES PASS; PUBLIC CI AND INDEPENDENT AUDIT PENDING**

Date: 2026-09-15

## Governed baseline

- Approved freeze PR: `#4`
- Certified freeze head: `29c803e63dff298bf53400a74af70e305a7ab4a4`
- Governed merge commit: `017d9273e0f05d75b2019c623cd91c9615d9571a`
- Governed merge tree: `1e902ff53571161eca480329f25d8733efea6179`
- Implementation branch: `v015-finite-convolution-implementation`
- Measured implementation commit: `467fda628e046545209fb99366802a8b631b9c50`
- Measured implementation tree: `48ec916d092aae3c4547cad7fbc2650072b527c2`

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
| v0.15.0 contract tests | 43 passed |
| Complete regression with optional data dependency | 1,264 passed; 921 warnings |
| Unchanged v0.14 acceptance suite | 19 passed |
| Claim-language guard | PASS |
| Independent-oracle import guard | PASS |
| Benchmark equality prechecks | PASS |

The warnings are the pre-existing numerical-domain and pytest-deprecation notices. No v0.15.0 test failed.

## Boundary

This record does not authorize merge, version activation, tagging or publication. The terminal candidate identity, public CI runs, distribution artifacts and independent audit must be recorded before governed merge consideration.
