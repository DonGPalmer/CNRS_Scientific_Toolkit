# CnrsQ2 Lean project — manifest

State: **Phase-5 Q2b(iii) compile candidate** (August 30, 2026)
Base governed snapshot: `CnrsQ2_lean_aug_30_2026_v3.zip`
Toolchain: `leanprover/lean4:v4.33.0` | Mathlib: `v4.33.0`

## Build and proof state

- Phases 1–4 are the previously governed v3 source, recorded as a clean `lake build` with zero sorries.
- This candidate adds `CnrsQ2/FieldDigitExpansion.lean` and imports it from `CnrsQ2.lean`.
- The new theorem target is Q2b(iii): every nonzero `x : ℚ_[5]` has a unique normalized beta-adic expansion starting at `Padic.valuation x`, with nonzero leading digit.
- The new Phase-5 source contains no `sorry` or `sorryAx` tokens.
- This candidate is **not yet a governed v4 snapshot**. Its new Lean code requires the pinned GitHub Actions `lake build` before promotion to Dropbox.
- The stronger global evaluation-map isometry and the finite-support `= R_A` converse are not asserted in this candidate.

## Contents and SHA-256

| File | Bytes | SHA-256 (first 16) |
|---|---:|---|
| `README.md` | 6,485 | `af38e6cc876dbf96…` |
| `lakefile.toml` | 177 | `9a7871914e10bb6b…` |
| `lean-toolchain` | 25 | `302cd63c54178885…` |
| `CnrsQ2.lean` | 1,159 | `be3f7ad8f946e332…` |
| `CnrsQ2/Basic.lean` | 1,824 | `f8c23159944b12dc…` |
| `CnrsQ2/DigitAlphabet.lean` | 2,085 | `67b8dcec516be649…` |
| `CnrsQ2/HenselRoot.lean` | 1,855 | `9a4e582e52ded681…` |
| `CnrsQ2/Embedding.lean` | 2,753 | `c64027228065fe6a…` |
| `CnrsQ2/Density.lean` | 1,745 | `e3014aa7c5a49aa9…` |
| `CnrsQ2/FieldLevel.lean` | 3,223 | `0de71a6c56368937…` |
| `CnrsQ2/DigitExpansion.lean` | 14,845 | `2f2c916d9a5f4905…` |
| `CnrsQ2/FieldDigitExpansion.lean` | 8,761 | `0518ad6e9d97b490…` |

## Project structure convention

Lean/Lake requires fixed internal filenames (`lakefile.toml`, `lean-toolchain`, module-path-matching `.lean` files). The governed live project uses the stable folder name `CnrsQ2/`; immutable dated/versioned snapshots carry programme versioning in their ZIP filename.
