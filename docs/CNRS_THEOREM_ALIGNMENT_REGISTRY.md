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

## Lean formal-verification metadata

The registry can additionally record machine-checked proof evidence without treating the independently implemented Python routine as extracted or refinement-proved software. The optional `TheoremRecord` fields are:

- `formal_system` — proof assistant/toolchain identity;
- `formal_source` — maintained repository source path;
- `formal_status` — evidence wording for the encoded theorem.

Current Q2 records:

| Result | Formal status | Formal source | Python relationship |
|---|---|---|---|
| CNRS Q2 beta-adic completion | Lean-verified mathematical theorem | `formal/lean/CnrsQ2/` (`Density.lean`, `FieldLevel.lean`) | `cnrs.topology` supplies finite theorem-aligned witnesses; no runtime `Z_5`/`Q_5` object is claimed |
| CNRS Q2 unique beta-adic digit expansion | Lean-verified mathematical theorem | `formal/lean/CnrsQ2/CnrsQ2/DigitExpansion.lean` | formal foundation for canonical completion-level digits; no end-to-end Python refinement proof is claimed |
| `beta=-2+i` base/primality and residue-digit foundation | Lean-verified mathematical theorem | `Basic.lean`, `DigitAlphabet.lean` | supports the mathematical contract used by finite CNRS-A base/digit code; it is not by itself a proof of every finite-encoding routine |

Use **Lean-verified mathematical theorem** only for claims actually encoded in the maintained Lean project. Keep implementation status separate as theorem-aligned and/or computationally tested unless a refinement proof connects executable Python to Lean. See `LEAN_FORMALIZATION_ALIGNMENT.md` for the theorem-level crosswalk.
