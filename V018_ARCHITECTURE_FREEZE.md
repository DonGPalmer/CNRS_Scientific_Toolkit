# CNRS Scientific Toolkit v0.18.0 architecture freeze

**Status:** DRAFT — PREPARED FOR AUTHOR REVIEW; NOT YET ADOPTED

**Prepared:** 22 September 2026

## Verified preparation baseline

- Repository: `DonGPalmer/CNRS_Scientific_Toolkit`
- Released version: `v0.17.0`
- `main` commit: `b290f2e3b43dc1830bb1311eb81393475b341a94`
- Tree: `ff732e56a6597d9ec98ce071f41507d7dd9bca21`
- Formal subtree: `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`
- Source index: exact `493`-file inventory
- Fresh regression result: `1,381 passed, 4 skipped, 922 warnings`
- Baseline package/runtime/CFF version: `0.17.0`

This document becomes controlling only after explicit author approval. Approval
of this architecture freeze does not authorize implementation, branch
creation, pull-request creation, readiness, merge, version activation, tagging,
publication, package upload, DOI/Zenodo action, branch deletion, Dropbox
mutation, or unrelated repository mutation.

## 1. Release objective

v0.18.0 completes the exact finite CNRS-A arithmetic path for addition,
negation, and subtraction while preserving the existing public entry points.
It removes floating-complex arithmetic from the claimed finite-string route,
retains the released addition transition relation, and reuses the exact v0.16
multiplication/normalization machinery for negation rather than creating a
second normalization engine.

The normative exact routes are:

```text
two finite CNRS-A strings
  -> released digit alignment
  -> exact integer-pair 14-state addition transition
  -> canonical finite CNRS-A string

one finite CNRS-A string
  -> exact v0.16 multiplication by "144" (the CNRS-A value -1)
  -> canonical finite CNRS-A string

subtraction
  -> exact negation of the right operand
  -> exact addition
```

No new public arithmetic name is introduced. Existing `add_cnrs`, `cnrs_add`,
`cnrs_neg`, and `cnrs_sub` remain the public interfaces.

## 2. Preparation audit and compatibility decision

The preparation audit established all of the following at the exact baseline:

1. `cnrs.cnrs_add` constructs its 350-entry transition table through Python
   `complex`, `/`, `round`, `.real`, and `.imag`, although every mathematical
   state and transition is Gaussian-integral.
2. The released table has 14 carry states and drains every state in at most five
   zero-input transitions. The existing runtime safety guard is 20 and remains
   unchanged for compatibility.
3. The released addition output agreed byte-for-byte with an independent exact
   integer-pair/Laurent normalization route for all 547,600 ordered pairs drawn
   from 740 legal spellings with one to three digits and every legal radix
   placement.
4. `cnrs_ops.cnrs_neg` converts through `cnrs_to_gaussian` and
   `gaussian_to_cnrs_str`. The latter snaps its input to a Gaussian integer.
   Consequently, nonintegral finite Laurent inputs can lose their fractional
   value.
5. `cnrs_ops.cnrs_sub` inherits that defect. In the same 740-spelling domain,
   392 single-operand negations and 290,080 ordered subtraction pairs involving
   radix-point spellings disagreed with the exact value oracle.
6. `CVal.__neg__` already uses exact multiplication by `"144"`, and
   `CVal.__sub__` already composes exact negation with `add_cnrs`.

Examples of the required mathematical correction are:

| Operation | v0.17 output | Exact v0.18 output |
|---|---:|---:|
| `cnrs_neg(".1")` | `"0"` | `"14.4"` |
| `cnrs_sub(".1", ".1")` | `"0.1"` | `"0"` |
| `cnrs_sub("1", ".1")` | `"1"` | `"1320.4"` |
| `cnrs_sub("23.1", "4.3")` | `"32.1"` | `"33.3"` |

It is impossible to preserve these incorrect bytes and simultaneously claim
exact fractional subtraction. This draft therefore interprets “preserve
existing public APIs and behavior” as follows:

- preserve every public name, signature, import path, result type, and correct
  result;
- preserve addition output byte-for-byte throughout the accepted grammar;
- preserve negation and subtraction output byte-for-byte wherever the v0.17
  output equals the exact value;
- correct only the oracle-demonstrated nonintegral negation/subtraction defect;
- record every changed fixed vector in the acceptance evidence; and
- make the correction effective only if this freeze is separately approved.

Adoption of this freeze is also explicit approval of that narrow semantic
correction. Without such approval, implementation must not begin.

## 3. Frozen scope

The implementation scope is limited to:

1. exact integer-pair construction of the existing 14-state addition table;
2. preservation of the exact released transition relation and carry ordering;
3. exact finite-string `add_cnrs` behavior on the accepted grammar;
4. exact `cnrs_neg` through the released v0.16 multiplication and
   normalization route;
5. exact `cnrs_sub` as addition after exact negation;
6. unchanged forwarding behavior for `cnrs_add`;
7. independent exact value and baseline-parity oracles under
   `cnrs.validation`;
8. dedicated unit, acceptance, static-guard, and downstream compatibility
   tests; and
9. truthful README, API-status, claim-status, and release-note preparation.

No version metadata change is part of implementation scope.

## 4. Addition architecture

### 4.1 Frozen public surface

The following remain available at their existing import paths:

```python
def add_cnrs(a: str, b: str) -> str: ...
def cnrs_add(a: str, b: str) -> str: ...
```

`cnrs_add` remains a direct semantic wrapper over `add_cnrs`.

The existing module-level `CARRY_SET_PAIRS`, `CARRY_SET`, and
`ADDITION_TABLE` objects remain available with equal values and compatible
container behavior. `CARRY_SET` may remain a compatibility representation, but
production transition construction and execution must not depend on its
floating-complex values.

### 4.2 Exact transition construction

For a carry pair `(x, y)` and input digits `a, b` in `{0,1,2,3,4}`, let

```text
raw_real = x + a + b
raw_imag = y
digit = (raw_real + 2*raw_imag) mod 5
u = raw_real - digit
next_real = (-2*u + raw_imag) / 5
next_imag = (-u - 2*raw_imag) / 5
```

Both divisions must be exact integer divisions. The resulting pair must be in
the frozen carry set, and the emitted transition is:

```text
(carry_index, a, b) -> (digit, next_carry_index)
```

No Python `complex`, `float`, tolerance comparison, `round`, `.real`, or
`.imag` may participate in table construction or addition execution.

### 4.3 Frozen transition identity

The carry order is exactly:

```text
(0,0), (1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1),
(-2,0), (2,1), (-2,-1), (-2,-2), (2,2), (-3,-1), (-3,-2)
```

The table contains exactly 350 entries. Its preparation checksum is:

```text
b68818cdb0766aead9993639ca2f1b96351371154c94453e730bf9a67a0746ee
```

The checksum is SHA-256 over UTF-8 minified JSON produced by Python
`json.dumps(payload, separators=(",", ":"))`, where `payload` is inserted in
this order:

```python
{
    "carry_set_pairs": CARRY_SET_PAIRS,
    "transitions": [
        (carry_index, digit_a, digit_b, output_digit, next_carry_index)
        for (carry_index, digit_a, digit_b),
            (output_digit, next_carry_index)
        in sorted(ADDITION_TABLE.items())
    ],
}
```

The candidate must reproduce both the table and this checksum exactly.

### 4.4 Alignment and formatting

Released operand alignment, fractional zero-padding, integer zero-padding,
right-to-left transition execution, radix reinsertion, and canonical
normalization remain observationally unchanged. The runtime drain guard remains
20. Reducing it to the observed maximum of five is outside scope.

## 5. Exact negation and subtraction

The public signatures remain:

```python
def cnrs_neg(a: str) -> str: ...
def cnrs_sub(a: str, b: str) -> str: ...
```

For every operand in the frozen finite grammar:

```python
cnrs_neg(a) == mul_cnrs("144", a)
cnrs_sub(a, b) == add_cnrs(a, cnrs_neg(b))
```

`"144"` is the canonical CNRS-A representation of `-1`. The implementation
must reuse released exact multiplication and normalization; it must not add a
second greedy encoder, Gaussian/Laurent normalizer, or floating-complex value
round-trip.

Existing `CVal.__neg__` and `CVal.__sub__` behavior is already consistent with
this route and must remain unchanged. Refactoring shared private constants is
permitted only if it does not change public or downstream behavior.

## 6. Input and compatibility boundary

The exactness claim covers the frozen finite-string grammar:

```text
( [0-4]+ ( "." [0-4]* )? ) | ( "." [0-4]+ )
```

Thus `"1."`, `".1"`, leading zeros, and trailing fractional zeros remain
accepted. Canonically equivalent spellings must produce identical canonical
results.

The v0.17 implementation has incidental behavior outside this grammar,
including treating `""` and `"."` as zero in addition and accepting some
nonalphabet digits in value-map-based negation. These are not part of the
exactness claim. The candidate must not deliberately broaden, remove, or
reinterpret such behavior without a compatibility ledger and explicit review.
If exact routing cannot preserve a successful out-of-contract behavior, a
narrow compatibility lane may retain it, provided:

- it is unreachable for every input in the frozen grammar;
- it is tested against a frozen baseline oracle;
- it is excluded from the exactness claim; and
- its presence is stated in the review evidence.

No new strict-parser exception policy is authorized by this freeze.

## 7. Independent validation architecture

Validation must extend or accompany `cnrs.validation.exact_string_oracle` with
direct `Fraction`-pair operations for addition, negation, and subtraction.
The oracle must not import or call:

- `add_cnrs`, `cnrs_add`, `cnrs_neg`, or `cnrs_sub`;
- `mul_cnrs`, convolution, production normalization, or the addition table;
- `cnrs_to_gaussian`, `gaussian_to_cnrs_str`, or Python `complex`; or
- a production helper introduced by v0.18.

A separate validation-only baseline oracle may preserve the exact v0.17
addition/negation/subtraction algorithms for output-parity and correction-ledger
testing. Production code must never import `cnrs.validation`.

## 8. Compatibility and preservation boundary

The candidate must preserve:

- all v0.14 streaming-division APIs, witnesses, fixed vectors, and limits;
- all v0.15 convolution, normalization, witness, and limit contracts;
- all v0.16 finite-string bridge and exact-multiplication contracts;
- all v0.17 exact-division contracts and deprecation boundaries;
- `CVal` arithmetic semantics and public behavior;
- CNRS-H native coefficient arithmetic and downstream workflows;
- the formal subtree identity; and
- all released version metadata until separately authorized activation.

`cnrs_eq`, general Gaussian encoding/decoding, arbitrary infinite streams,
analytic continuation, global remainder bounds, and formal verification of the
Python runtime are outside the v0.18 claim.

## 9. Claim boundary

The permitted claim is:

> For operands in the frozen finite CNRS-A grammar, the released addition,
> negation, and subtraction entry points return canonical finite strings whose
> values exactly equal the corresponding Gaussian-rational sum, additive
> inverse, or difference; production arithmetic on the claimed route uses
> integer/Gaussian-integer exact operations and reuses the released exact
> multiplication/normalization machinery.

No claim is made of universal elapsed-time, total-memory, integer-bit-length,
arbitrary infinite-stream, unrestricted analytic, Lean-extracted, or end-to-end
formally verified behavior.

## 10. Implementation changed-path boundary

The expected changed paths are limited to:

- `cnrs/cnrs_add.py`;
- `cnrs/cnrs_ops.py`;
- a validation-only v0.18 oracle or extension under `cnrs/validation/`;
- dedicated v0.18 tests;
- `acceptance/v018/`;
- a v0.18 static claim guard under `tools/`; and
- narrowly necessary README, API-status, claim-status, and release-note files.

Changes to multiplication, convolution, normalization, streaming division,
exact division, formal sources, package version, citation version, release
assets, or unrelated scientific modules are stop conditions unless separately
approved by freeze amendment.

## 11. Stop conditions

Stop without marking a candidate ready if:

- baseline ancestry or tree identity differs without approved amendment;
- a public name, signature, import path, return type, or correct frozen output
  changes;
- addition-table value or checksum changes;
- a fractional negation/subtraction change is not in the correction ledger;
- claimed production arithmetic uses floating/complex value conversion;
- production imports validation code or duplicates frozen exact machinery;
- any v0.14–v0.17 acceptance or claim gate regresses;
- downstream `CVal` or CNRS-H behavior regresses;
- the formal subtree changes;
- tests, builds, clean installations, or required CI are missing or fail;
- the changed-path set exceeds the approved scope; or
- any action requires authority beyond the separately approved step.

## 12. Authorization boundary

This is a preparation artifact only. Adoption of it requires a separate,
explicit author instruction identifying the exact file and SHA-256. Adoption
alone does not authorize implementation or any repository, GitHub, Dropbox,
release, publication, or DOI/Zenodo mutation.
