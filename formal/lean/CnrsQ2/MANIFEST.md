# CnrsQ2 Lean project — manifest

State: **Phase-5C certified finite-left carrier compile candidate** (August 30, 2026)
Base verified state: Phase-5B Q2b(iv) metric core, GitHub Actions `cnrs-q2` PASS (`Upload 5B`)
Toolchain: `leanprover/lean4:v4.33.0` | Mathlib: `v4.33.0`

## Build and proof state

- Phases 1–4 are the governed v3 source.
- Phase 5A (`FieldDigitExpansion.lean`) passed the pinned GitHub Actions `lake build`; it proves the nonzero field-level finite-negative-index expansion Q2b(iii).
- Phase 5B (`DigitIsometry.lean`) passed the pinned GitHub Actions `lake build`; it proves the first-differing-digit norm theorem and integer-shifted field formula, the metric core of Q2b(iv).
- This candidate adds `CnrsQ2/FiniteLeftCarrier.lean` and imports it from `CnrsQ2.lean`.
- The Phase-5C target is a certified normalized finite-left carrier with a bijective evaluation map onto `ℚ_[5]`, plus the manuscript-style first-difference isometry on each fixed valuation stratum.
- The new source contains no `sorry` or `sorryAx` tokens.
- This Phase-5C candidate is **not yet a governed v4 snapshot**. Its new Lean code requires the pinned GitHub Actions `lake build` before promotion.
- Removing convergence/normalization certificates from the raw carrier syntax and proving the finite-support `= R_A` converse remain later targets.

## Contents and SHA-256

| File | Bytes | SHA-256 (first 16) |
|---|---:|---|
| `README.md` | 6,485 | `af38e6cc876dbf96…` |
| `lakefile.toml` | 177 | `9a7871914e10bb6b…` |
| `lean-toolchain` | 25 | `302cd63c54178885…` |
| `CnrsQ2.lean` | 1,567 | `45bb97eeca541d54…` |
| `CnrsQ2/Basic.lean` | 1,824 | `f8c23159944b12dc…` |
| `CnrsQ2/DigitAlphabet.lean` | 2,085 | `67b8dcec516be649…` |
| `CnrsQ2/HenselRoot.lean` | 1,855 | `9a4e582e52ded681…` |
| `CnrsQ2/Embedding.lean` | 2,753 | `c64027228065fe6a…` |
| `CnrsQ2/Density.lean` | 1,745 | `e3014aa7c5a49aa9…` |
| `CnrsQ2/FieldLevel.lean` | 3,223 | `0de71a6c56368937…` |
| `CnrsQ2/DigitExpansion.lean` | 14,845 | `2f2c916d9a5f4905…` |
| `CnrsQ2/FieldDigitExpansion.lean` | 8,761 | `0518ad6e9d97b490…` |
| `CnrsQ2/DigitIsometry.lean` | 5,052 | `92201078a61f23bb…` |
| `CnrsQ2/FiniteLeftCarrier.lean` | 7,643 | `53372c46d5ffb798…` |

## Project structure convention

Lean/Lake requires fixed internal filenames (`lakefile.toml`, `lean-toolchain`, module-path-matching `.lean` files). The governed live project uses the stable folder name `CnrsQ2/`; immutable dated/versioned snapshots carry programme versioning in their ZIP filename.
