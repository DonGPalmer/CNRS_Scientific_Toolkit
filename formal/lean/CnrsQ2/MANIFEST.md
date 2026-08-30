# CnrsQ2 Lean project — manifest

Snapshot: `CnrsQ2_lean_aug_30_2026_v3.zip` (August 30, 2026)
Live project: `/_SSC/20_Program/80_Strategy/30_Lean4/CnrsQ2/`
Supersedes: `CnrsQ2_lean_aug_18_2026_v2`
Toolchain: `leanprover/lean4:v4.33.0` | Mathlib: `v4.33.0`

## Build and proof state

- The theorem/proof code is the same code previously recorded as a full clean `lake build`, zero sorries.
- v3 changes are governance/documentation only: the obsolete `Step 3 (OPEN)` commentary was removed from `DigitExpansion.lean`; the README live-path/versioning text was normalized; this manifest was regenerated; and the live project folder is normalized to `CnrsQ2/`.
- No theorem statement, definition, import, tactic block, or proof term was changed for v3.
- A source scan of the v3 `.lean` tree found no `sorry` or `sorryAx` tokens.
- Lean was not re-run in the present ChatGPT execution environment; the clean-build claim above refers to the already-recorded build of the unchanged proof code.

## Contents and SHA-256

| File | Bytes | SHA-256 (first 16) |
|---|---:|---|
| `README.md` | 6,485 | `af38e6cc876dbf96…` |
| `lakefile.toml` | 177 | `9a7871914e10bb6b…` |
| `lean-toolchain` | 25 | `302cd63c54178885…` |
| `CnrsQ2.lean` | 1,087 | `2168216ff6cd4d79…` |
| `CnrsQ2/Basic.lean` | 1,824 | `f8c23159944b12dc…` |
| `CnrsQ2/DigitAlphabet.lean` | 2,085 | `67b8dcec516be649…` |
| `CnrsQ2/HenselRoot.lean` | 1,855 | `9a4e582e52ded681…` |
| `CnrsQ2/Embedding.lean` | 2,753 | `c64027228065fe6a…` |
| `CnrsQ2/Density.lean` | 1,745 | `e3014aa7c5a49aa9…` |
| `CnrsQ2/FieldLevel.lean` | 3,223 | `0de71a6c56368937…` |
| `CnrsQ2/DigitExpansion.lean` | 14,845 | `2f2c916d9a5f4905…` |

## Project structure convention

Lean/Lake requires fixed internal filenames (`lakefile.toml`, `lean-toolchain`, module-path-matching `.lean` files). The live project therefore uses the stable folder name `CnrsQ2/`; immutable dated/versioned snapshots carry programme versioning in the ZIP filename and are stored in `30_Lean4/99_Archive/`.
