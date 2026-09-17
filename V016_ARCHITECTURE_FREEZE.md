# CNRS Scientific Toolkit v0.16.0 architecture freeze

Status: DRAFT — PREPARED FOR AUTHOR REVIEW; NOT YET ADOPTED

Prepared: 17 September 2026

Verified baseline:

- repository: `DonGPalmer/CNRS_Scientific_Toolkit`
- branch: `main`
- commit: `3d1b8e736395402b1f6c13e4aee225a97902fbaa`
- tree: `79ae69643d5060e84ba34e6b00e6562d1ef7d97b`
- formal subtree: `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`
- baseline regression result: `1281 passed, 4 skipped`

This document becomes controlling only after explicit author approval. Approval of
the architecture freeze does not authorize implementation, branch creation,
version activation, merge, tagging, publication, Zenodo action, or branch
deletion.

## 1. Release objective

v0.16.0 consolidates finite CNRS-A string multiplication onto the exact
Gaussian/Laurent machinery released in v0.15.0. The public
`mul_cnrs(a: str, b: str) -> str` interface remains intact, but its production
path no longer uses Python `complex`, floating-point division, or `round()` for
convolution carry normalization.

The release also adds a small, explicit bridge between finite CNRS-A digit
strings and `CNRSFiniteSequence`, so the conversion boundary is public,
testable, and documented rather than embedded in `cnrs_mul.py`.

## 2. Frozen scope

The implementation scope is limited to:

1. a finite-string/carrier bridge module;
2. exact `mul_cnrs` routing through the v0.15 exact convolution and
   Gaussian/Laurent normalization primitives;
3. compatibility tests against the pre-v0.16 multiplication implementation;
4. an independent exact value oracle for acceptance testing;
5. a practical README example for exact finite multiplication; and
6. removal of the stale `v0.15.0 candidate` label in `cnrs/__init__.py`.

No other arithmetic route is silently redefined by this freeze.

## 3. Component architecture

### 3.1 New bridge module

Add `cnrs.finite_string` with exactly these public functions:

```python
def cnrs_string_to_finite_sequence(value: str) -> CNRSFiniteSequence: ...

def finite_sequence_to_cnrs_string(value: CNRSFiniteSequence) -> str: ...
```

Both names are re-exported from `cnrs` and added to `cnrs.__all__`.

### 3.2 Production multiplication path

`cnrs.cnrs_mul.mul_cnrs` becomes a thin composition:

```text
CNRS-A string
  -> CNRSFiniteSequence
  -> exact stored-position convolution
  -> exact Gaussian/Laurent normalization
  -> canonical CNRS-A string
```

The production route must call the existing public v0.15 primitives
`convolve_exact` and `normalize_gaussian_laurent`, or a single existing public
wrapper that provably invokes those same primitives without changing their
contracts. It must not copy a second production convolution or carry algorithm.

### 3.3 Legacy parity oracle

The pre-v0.16 string multiplication algorithm is retained only under
`cnrs.validation` as a test oracle. It is not exported from `cnrs`, is not called
by production code, and carries an explicit warning that its Python-complex and
rounding route is historical validation evidence rather than the authoritative
implementation.

The oracle must be copied from the verified baseline before production changes.
Its arithmetic is not repaired or modernized, because changing it would weaken
its independence as a parity comparator.

### 3.4 Existing diagnostic normalization API

`cnrs.normalization` remains outside this release's production-route change.
Its structured diagnostic functions retain their current signatures and
semantics. v0.16 does not claim that every historical diagnostic helper has
been converted to the new exact carrier. The authoritative public string
multiplication route after v0.16 is `mul_cnrs`.

## 4. Frozen conversion contract

### 4.1 Accepted string grammar

`cnrs_string_to_finite_sequence` accepts `type(value) is str` and the grammar:

```text
( [0-4]+ ( "." [0-4]* )? ) | ( "." [0-4]+ )
```

Thus ordinary integer and fractional strings are accepted, including `"1."`
and `".1"`. At least one digit is required. Whitespace, signs, exponent
notation, empty strings, a bare radix point, digits outside `0..4`, and multiple
radix points are rejected with `ValueError`. A non-string raises `TypeError`.

Digits are mapped least-significant first. If the fractional part has length
`f`, the untrimmed carrier offset is `-f`. Construction then applies the
existing `CNRSFiniteSequence` canonical boundary-zero trimming rules.

### 4.2 Formatting contract

`finite_sequence_to_cnrs_string` accepts a `CNRSFiniteSequence` instance,
including subclasses; any other value raises `TypeError`.

Every stored coefficient must be a canonical CNRS digit `(d, 0)` with
`d in {0,1,2,3,4}`. A non-digit Gaussian coefficient raises `ValueError`.
The function pads missing exponents with zero digits, inserts the radix point at
exponent zero, and returns canonical formatting:

- canonical zero is `"0"`;
- the integer part is never empty;
- leading integer zeros are removed except for the single zero before a radix
  point;
- trailing fractional zeros are removed; and
- a radix point with no remaining fractional digits is removed.

The bridge itself never performs arithmetic normalization. Callers must invoke
`normalize_gaussian_laurent` before formatting a carrier whose coefficients are
not already CNRS digits.

### 4.3 Round-trip laws

For every accepted string `s`:

```python
finite_sequence_to_cnrs_string(cnrs_string_to_finite_sequence(s)) \
    == normalize_cnrs(s)
```

For every canonical finite sequence `x` containing only CNRS digits:

```python
cnrs_string_to_finite_sequence(finite_sequence_to_cnrs_string(x)) == x
```

## 5. Frozen `mul_cnrs` contract

The public signature remains exactly:

```python
def mul_cnrs(a: str, b: str) -> str: ...
```

For inputs in the accepted grammar:

- the result is a canonical finite CNRS-A digit string;
- it represents the exact product at base `(-2, 1)`;
- output agrees exactly with the verified pre-v0.16 implementation throughout
  the frozen parity domain in the acceptance packet;
- zero, fractional offsets, and noncanonical boundary zeros are handled by the
  public bridge contract; and
- no Python floating-point or complex arithmetic participates in the
  production multiplication path.

Malformed-input behavior outside the accepted grammar is governed by §4.1,
not by accidental behavior of the historical implementation.

`mul_cnrs` retains no public product-count or carry-step limit. The existing
bounded v0.15 APIs remain available to callers that require explicit limits.

## 6. Independence and anti-regression boundary

Acceptance tooling must enforce all of the following:

- production `cnrs_mul.py` and `finite_string.py` do not import
  `cnrs.validation`;
- neither production file uses `complex`, `/` on Gaussian carry values,
  `.real`, `.imag`, or `round`;
- the legacy parity oracle does not import or call `convolve_exact`,
  `normalize_gaussian_laurent`, `multiply_with_witness`, or the bridge module;
- the independent exact value oracle does not call the production convolution,
  production normalizer, `mul_cnrs`, or the legacy parity oracle; and
- acceptance compares values with exact Gaussian-integer/rational arithmetic,
  never with a floating tolerance.

## 7. Compatibility boundary

All v0.15.0 public signatures and witness serialization remain unchanged.
Existing valid CNRS-A multiplication outputs remain unchanged. Existing CNRS-H
and `CVal` callers continue to use `mul_cnrs` without call-site changes.

Private helpers in `cnrs.cnrs_mul` are not public compatibility commitments.
Tests that intentionally exercise the historical helpers move to the validation
oracle module and are relabeled accordingly.

## 8. Documentation boundary

README documentation must include one executable example showing:

1. conversion from two finite CNRS-A strings to `CNRSFiniteSequence`;
2. exact convolution and normalization;
3. conversion back to a canonical string; and
4. equality with `mul_cnrs`.

The comment `Exact finite convolution and witnesses (v0.15.0 candidate)` in
`cnrs/__init__.py` is corrected to released wording. No broader historical
rewriting is authorized by this item.

## 9. Formal-method boundary

This release introduces no new Lean theorem, proof, extraction claim, or
formal-to-runtime equivalence claim. Unless a separately approved correction is
required, the entire `formal/` subtree must remain byte-identical to baseline
tree `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`.

The existing exact-tree Lean source-identity certification must remain valid.

## 10. Explicit non-goals

The following are excluded:

- infinite or eventually periodic multiplication;
- approximate or FFT convolution;
- performance superiority claims;
- changes to addition, division, CNRS-H branch state, or analytic continuation;
- redesign of `CNRSFiniteSequence`, witness schemas, or v0.15 limits;
- conversion of every legacy diagnostic normalizer;
- new formal proofs or Lean extraction;
- version activation, release metadata, tags, publication, or Zenodo action;
  and
- unrelated cleanup or refactoring.

## 11. Freeze-change rule

After adoption, any change to a public signature, accepted grammar, conversion
law, multiplication route, compatibility domain, formal boundary, or acceptance
gate requires an explicit written freeze amendment and renewed author approval.

