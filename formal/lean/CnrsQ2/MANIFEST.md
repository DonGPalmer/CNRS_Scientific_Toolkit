# CnrsQ2 Lean project — manifest

State: **Phase-5D raw finite-left carrier compile candidate** (August 30, 2026)
Base verified state: Phases 1–5B have pinned GitHub Actions `cnrs-q2` PASS; Phase 5C repository guards are green and its source remains in the working tree.
Toolchain: `leanprover/lean4:v4.33.0` | Mathlib: `v4.33.0`

## Build and proof state

- Phases 1–4 are the governed v3 source.
- Phase 5A (`FieldDigitExpansion.lean`) passed the pinned GitHub Actions `lake build`; it proves the nonzero field-level finite-negative-index expansion Q2b(iii).
- Phase 5B (`DigitIsometry.lean`) passed the pinned GitHub Actions `lake build`; it proves the first-differing-digit norm theorem and integer-shifted field formula, the metric core of Q2b(iv).
- Phase 5C (`FiniteLeftCarrier.lean`) packages a certified normalized finite-left carrier and a bijective evaluation map; its Python/formal-tree guards are green in the current repository state.
- This Phase-5D candidate adds `CnrsQ2/RawFiniteLeftCarrier.lean` and imports it from `CnrsQ2.lean`.
- Phase 5D proves convergence for every raw `ℕ → Fin 5` stream from the existing uniform tail bound and completeness of `ℤ_[5]`; it then removes convergence/normalization certificates from finite-left syntax.
- The Phase-5D targets are: raw evaluation bijective onto `ℚ_[5]`; exact nonzero norm from the integer shift; same-shift first-difference norm; and unequal-shift ultrametric max formula.
- The new source contains no proof placeholders.
- This Phase-5D candidate is **not yet a governed v4 snapshot**. Its new Lean code requires the pinned GitHub Actions `lake build` before promotion.
- The finite-support `= R_A` converse remains separate because it still requires a formal finite CNS expansion theorem for Gaussian integers.

## Contents and SHA-256

| File | Bytes | SHA-256 (first 16) |
|---|---:|---|
| `README.md` | 6,485 | `af38e6cc876dbf96…` |
| `lakefile.toml` | 177 | `9a7871914e10bb6b…` |
| `lean-toolchain` | 25 | `302cd63c54178885…` |
| `CnrsQ2.lean` | 1,857 | `407b63e43a57decf…` |
| `CnrsQ2/Basic.lean` | 1,824 | `f8c23159944b12dc…` |
| `CnrsQ2/DigitAlphabet.lean` | 2,085 | `67b8dcec516be649…` |
| `CnrsQ2/HenselRoot.lean` | 1,855 | `9a4e582e52ded681…` |
| `CnrsQ2/Embedding.lean` | 2,753 | `c64027228065fe6a…` |
| `CnrsQ2/Density.lean` | 1,745 | `e3014aa7c5a49aa9…` |
| `CnrsQ2/FieldLevel.lean` | 3,223 | `0de71a6c56368937…` |
| `CnrsQ2/DigitExpansion.lean` | 14,845 | `2f2c916d9a5f4905…` |
| `CnrsQ2/FieldDigitExpansion.lean` | 8,761 | `0518ad6e9d97b490…` |
| `CnrsQ2/DigitIsometry.lean` | 5,052 | `92201078a61f23bb…` |
| `CnrsQ2/FiniteLeftCarrier.lean` | 7,562 | `9d9487e842532912…` |
| `CnrsQ2/RawFiniteLeftCarrier.lean` | 13,539 | `907963bb5914d3b3…` |

## Project structure convention

Lean/Lake requires fixed internal filenames (`lakefile.toml`, `lean-toolchain`, module-path-matching `.lean` files). The governed live project uses the stable folder name `CnrsQ2/`; immutable dated/versioned snapshots carry programme versioning in their ZIP filename.
