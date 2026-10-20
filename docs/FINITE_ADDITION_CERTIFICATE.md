# Finite-addition correspondence certificate — development candidate

The permanent check compares the production `ADDITION_TABLE` and ordered carry
inventory with data captured in the installed E2 Lean candidate. It also checks
each column equation independently, complete carry reachability, and every
zero-input drain path. This is an executable drift check against pinned,
Lean-checked data. It does not run Lean or certify Python parsing, formatting,
normalization, or arbitrary Python execution.

## Evidence and reproduction

The authoritative installed-source run is
[39331704917](https://github.com/DonGPalmer/SSC_Formal_Methods_CI/actions/runs/39331704917),
private checker commit `03e40d19348694b470897b6c6434e38ccc841250`.
Its evidence artifact is `12224872876`, SHA-256
`4cecf1ae810503c8b9fb11bc723cbf1ab9fcab17c13f13956dc20afa253f8fe0`.
The installed E2 candidate passed authoritative checking; final governed
adoption and freeze remain pending. The certified public capstone and Toolkit
`formal/` subtree are unchanged.

`verification/finite_addition_certificate.json` records the artifact, nested
source archive, Lean table and runner module hashes, the captured Python source
hash, theorem names, 14 carries, 350 rows, and drain lengths. The historical
Python file hash identifies the captured version; the current gate compares
the relation itself, allowing comment repairs without executable changes.
Fixture SHA-256:
`9b30818368ae814bd373c195ee7c7d8ba59bb0c525a0d7bc23e12b69487ea875`.

With the retained authoritative evidence ZIP, regenerate it using:

```sh
python tools/export_addition_certificate.py --evidence /path/to/E2-authoritative-evidence.zip --output /tmp/finite_addition_certificate.json
cmp verification/finite_addition_certificate.json /tmp/finite_addition_certificate.json
```

The exporter requires the pinned artifact and source hashes before extracting
literal data; it never derives the fixture from production Python. Updating
the pins requires review against a new authoritative Lean evidence package.
The normal gate needs no private repository access or network:

```sh
python tools/check_addition_certificate.py
python -m pytest -q tests/test_addition_certificate.py
```

## Checked contract

For beta = -2+i, carry c=(x,y), successor c'=(u,v), and input digits a,b,
every production row must match the pinned row and satisfy
`(digit - 2*u - v, u - 2*v) == (x + a + b, y)`.
Keys, carries and outputs must be exact integers within their domains; Boolean
and floating-point aliases are rejected. All 14 carries must be reachable.

Zero-input drain lengths, in production carry order, are:
`0, 1, 3, 2, 3, 2, 3, 3, 2, 3, 5, 4, 3, 5`.
Thus five steps suffice and four do not. State zero is absorbing and emits
zero on zero input. The runtime's existing guard of 20 remains unchanged.
Finite state-set membership alone would not rule out a nonzero cycle.

Tests include changed/missing/extra rows, carry-order drift, invalid numeric
types and fixture edits. Public addition is exercised with witnesses reaching
all 14 carries and fractional shifts 0, 1 and 7, using an independent rational
Horner oracle. The integer witnesses reach each carry immediately before the
drain; high zero padding in fractional cases can begin draining earlier.

## Formal boundary and next step

The installed candidate proves the literal table agrees with certified
`addStep`; its typed arbitrary-length runner refines `runAddition` and gives
correct values after five zero columns. See the
[candidate theorem crosswalk](FINITE_ARITHMETIC_LEAN_EXTENSION_CANDIDATE.md).
The Python gate ties today's table contents to those literals computationally.
It is not a theorem connecting today's entire Python function to the typed
runner. The fixture and checker pins are review controls, not a signature or a
defence against coordinated malicious changes.

The next small formal obligation is a variable-length early-stop refinement:
prove that stopping at the first zero carry, then padding to five zero columns,
preserves the emitted value. Follow it with the actual finite-string
parse/align/format contract. Keep both additions outside the frozen certified
source until governed review; neither requires reopening completed capstone
certification. General multiplication-normalizer correspondence remains a
separate requirement for the Python negation/subtraction pipeline.
