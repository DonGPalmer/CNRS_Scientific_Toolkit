# CNRS Native Status Register — v0.7.1

v0.7.1 introduces a lightweight native-status registry in `cnrs.native_status`.
The purpose is to keep the Python toolkit aligned with the CNRS theoretical
programme: CNRS-native structures should be distinguished from bridge,
validation, scaffold, compatibility, and application layers.

The guiding rule is:

> Use CNRS internally wherever CNRS has a native structure; use external
> methods only as validation, comparison, bridge tooling, or temporary
> scaffolding.

## Status categories

| Status | Meaning |
|---|---|
| `native_core` | Foundational CNRS representation or operation. |
| `native_finite` | CNRS-native finite-order operation, usually truncated/local. |
| `native_local` | CNRS-native local object carrying finite analytic/branch/scale metadata. |
| `bridge` | Converts ordinary notation or expressions into CNRS objects. |
| `validation` | Reference method for checking CNRS results against standard approaches. |
| `scaffold` | Transitional support toward a more native or rigorous construction. |
| `application` | Science-facing workflow or observation interface. |
| `compatibility` | Historical import/API path retained for users. |

## Current interpretation

The native spine is:

```text
cnrs.core  -> CNRS-A base, digits, values, arithmetic, branch-state façade
cnrs.h     -> CNRS-H coefficient calculus, finite composition, chain rule,
              jets, branch/path metadata, local analytic objects
cnrs.science.state -> CNRS-H-centered scientific state object
```

Bridge and validation layers remain useful, but they do not constitute the core
CNRS conjecture.  `CnrsDual` autodiff is a validation/reference method.
`cnrs.symbolic` and the symbolic-to-CNRS-H bridge are access tools for building
and checking CNRS-H objects.

## Programmatic access

```python
from cnrs.native_status import get_component, native_components, status_table

print(get_component("CNRS-H chain rule"))
print(status_table(native_components()))
```

The command-line audit helper is:

```bash
PYTHONPATH=. python tools/audit_native_status.py
```

## Claim discipline

The registry is not a proof system. It is a status map. It records which parts
of the implementation are intended to be CNRS-native and which remain bridge,
validation, or scaffold. Formal support still belongs in CNRS papers/proof
notes, especially for finite CNRS-A normalization/arithmetic, Layer-2 branch
representation, and CNRS-H coefficient calculus.
