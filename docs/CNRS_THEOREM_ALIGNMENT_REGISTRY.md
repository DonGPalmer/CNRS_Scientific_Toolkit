# CNRS Theorem-Alignment Registry

`cnrs.theorem_alignment` records the proof/status role of core toolkit
features. It complements `cnrs.native_status`:

- `native_status` says whether a module is native, bridge, validation,
  scaffold, application, or compatibility.
- `theorem_alignment` says whether a result is theorem-backed,
  computationally verified, conditional, scaffold, bridge, validation, or open.

Example:

```python
from cnrs.theorem_alignment import get_theorem_record, theorem_alignment_table

record = get_theorem_record("CNRS-A multiplication closure")
print(record.status)
print(theorem_alignment_table())
```

The registry is not a theorem prover. It is a discipline layer so the codebase
continues to distinguish implemented operations from theorem-backed results,
conditional results, and support layers.
