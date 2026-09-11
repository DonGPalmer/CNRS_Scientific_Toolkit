# CNRS Scientific Toolkit — Formal Verification

Status date: 2026-09-11  
Coverage boundary: governed CNRS-LEAN-CAPSTONE

The Toolkit vendors the exact six-project Lean source snapshot certified by
CNRS-LEAN-CAPSTONE. The evidence chain remains:

`CNRS claim → Lean statement → proof → software contract → Python implementation → tests`

Lean verifies the mathematical statements encoded in the vendored projects.
It does not automatically verify the independently written Python runtime.

## Vendored projects

- `CNRSCore` — finite Gaussian foundation;
- `CnrsQ2` — beta-adic completion and digit expansion;
- `CNRSArithmetic` — E1–E11 and Phase F;
- `CNRSIntegration` — Addition Bridge;
- `CNRSProblem1` — P1-L1 through P1-L7;
- `CNRSProblem2` — P2-L1 through P2-L10.

Each project is directly buildable from `formal/lean/<project>/` with its
certified `lakefile.toml`, `lake-manifest.json`, and `lean-toolchain`.

## Certified identity

See `PROVENANCE.json` and `capstone/SHA256SUMS.txt`. The consolidated source
is commit `07e776b4e1d7d09513394a4b676516eb51e4c597`, artifact
`10175389923`, SHA-256
`840ffee8a9a1183292ef8c952fe81199b1d916ea0fd0e688602f19559a375c21`.

The certification records 79 Lean files, 14,341 source lines, all six normal
and clean network-disabled builds passing (CNRSCore 3,015; CnrsQ2 3,037;
CNRSArithmetic 3,043; CNRSIntegration 3,046; CNRSProblem1 8,723;
CNRSProblem2 3,052; total 23,916), byte-stable source, and no `sorry`,
`sorryAx`, `admit`, added axiom, or unsafe declaration.

In the Toolkit layout, the supported checksum and proof-hygiene verification
command is:

```bash
python tools/check_lean_alignment.py
```

The upstream checksum inventory retains its original `./release/...` paths;
the Toolkit verifier maps those paths to the vendored `formal/lean/...` tree.

## Scope

The verified boundary is the finite CNRS kernel. It excludes arbitrary
infinite-series serialization, analytic continuation or path reconstruction,
unequal-branch arithmetic, unrestricted streaming multiplication or division,
and a general representation theorem for all complex numbers.

Do not describe the complete Toolkit as formally verified. Use
**Lean-verified mathematical theorem** and **separately tested,
theorem-aligned Python implementation** where appropriate.
