# CNRS Scientific Toolkit v0.17.0 architecture freeze

**Status:** DRAFT — PREPARED FOR AUTHOR REVIEW; NOT YET ADOPTED

**Prepared:** 18 September 2026

## Verified preparation baseline

- Repository: `DonGPalmer/CNRS_Scientific_Toolkit`
- Released tag: `v0.16.0`
- Commit: `1b817fca30e061854e6bc62823e5c5ff28b92f9a`
- Tree: `006d27f65e301a6239a5362cbb988f6afb983bf4`
- Formal subtree: `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`
- Released regression result: `1,310 passed, 4 skipped, 922 warnings`

This document becomes controlling only after explicit author approval. Approval of
this architecture freeze does not authorize implementation, branch creation,
version activation, pull-request creation, readiness, merge, tagging, publication,
Zenodo action, branch deletion, or unrelated repository mutation.

## 1. Release objective

v0.17.0 connects finite CNRS-A strings to the exact Gaussian-rational streaming
division machinery released in v0.14.0. It adds an authoritative structured
string-division entry point without representing a nonterminating quotient by a
silently truncated finite string.

The normative exact route is:

```text
two finite CNRS-A strings
  -> v0.16 finite-string parser
  -> exact Gaussian-fraction values
  -> exact quotient fraction
  -> v0.14 stream_division
  -> bounded exact resolution
```

The new route uses integer, Gaussian-integer, and `Fraction` arithmetic only. It
does not use Python `complex`, binary floating point, tolerance comparison,
`round`, `.real`, or `.imag`.

## 2. Frozen scope

The implementation scope is limited to:

1. one exact finite-carrier-to-Gaussian-fraction conversion used by the new route;
2. one public string bridge, `divide_cnrs_exact`;
3. reuse of the v0.14 `CnrsDivisionStream`, `DivisionResolution`, status, cycle,
   and witness contracts without duplication;
4. exact terminating, eventually-periodic, and search-limit outcomes;
5. an independent exact rational-pair oracle;
6. static independence and anti-regression enforcement;
7. one executable README example; and
8. explicit documentation of the legacy `div_cnrs` boundary.

No version metadata change is part of implementation scope.

## 3. Component architecture

### 3.1 New exact string-division module

Add `cnrs.exact_division` with exactly this public function:

```python
def divide_cnrs_exact(
    dividend: str,
    divisor: str,
    *,
    max_steps: int = 100_000,
) -> DivisionResolution: ...
```

`divide_cnrs_exact` is re-exported from `cnrs` and added to `cnrs.__all__`.
The existing v0.14 public `DivisionResolution`, `DivisionStreamStatus`,
`DivisionSearchLimitError`, `stream_division`, and witness APIs remain the
authoritative result and evidence types; v0.17 must not create parallel result,
status, or witness schemas.

### 3.2 Exact finite-value conversion

Each parsed `CNRSFiniteSequence` represents

```text
sum(coefficients[k] * beta ** (offset + k)), beta = -2 + i.
```

The conversion must recover that value as a reduced Gaussian fraction
`(numerator, denominator)`, where both are two-integer Gaussian pairs and the
denominator is nonzero. Negative exponents are handled by exact powers of
`beta`; no complex conversion is permitted.

The conversion may be a private helper. It must reuse existing exact Gaussian
arithmetic primitives where available and must not implement a second division
stream, cycle detector, canonical-periodic normalizer, or witness validator.

### 3.3 Exact quotient construction

If the parsed values are `A/B` and `C/D`, the exact quotient supplied to
`stream_division` is:

```text
(A * D) / (B * C).
```

The divisor is zero exactly when `C == (0, 0)`; this raises
`ZeroDivisionError` before stream construction. The quotient fraction is reduced
by the existing exact Gaussian-fraction normalization used by v0.14.

### 3.4 Resolution delegation

The public call is normatively equivalent to:

```python
left = cnrs_string_to_finite_sequence(dividend)
right = cnrs_string_to_finite_sequence(divisor)
numerator, denominator = exact_quotient_fraction(left, right)
return stream_division(numerator, denominator).resolve(max_steps)
```

Factoring into private helpers is permitted. Reimplementing the v0.14 digit
recurrence, state-cycle detection, canonical-periodic normalization, exact-value
recovery, or witness validation is not permitted.

### 3.5 Independent validation oracle

Add a validation-only oracle under `cnrs.validation`. It must:

- parse the frozen v0.16 grammar independently of the production bridge or use a
  frozen copy installed before production changes;
- evaluate powers of `(-2, 1)` by direct rational-pair arithmetic;
- compute the exact complex-rational quotient directly; and
- compare exact real and imaginary `Fraction` pairs.

The oracle must not import or call `divide_cnrs_exact`, the production
finite-value converter, `stream_division`, `CanonicalPeriodicExpansion`, or
production witness generation.

## 4. Frozen input and error contract

`dividend` and `divisor` use the exact v0.16 finite-string grammar:

```text
( [0-4]+ ( "." [0-4]* )? ) | ( "." [0-4]+ )
```

Thus `"1."` and `".1"` are accepted and normalized through the existing bridge.
The parser's existing exact-type and malformed-input exceptions remain
authoritative:

- a non-`str` operand raises `TypeError`;
- an empty string, bare point, sign, whitespace, exponent notation, invalid
  digit, or repeated point raises `ValueError`;
- an exact zero divisor raises `ZeroDivisionError`; and
- `max_steps <= 0`, `bool`, or a non-`int` value raises `ValueError` or
  `TypeError` consistently with the frozen v0.14 `resolve` contract.

Exact exception prose is not frozen, but it must identify the rejected operand
or parameter.

## 5. Frozen result contract

`divide_cnrs_exact` always returns the existing v0.14 `DivisionResolution`.

### 5.1 Terminating

- `status is DivisionStreamStatus.TERMINATING`;
- `period_digits == ()`;
- the terminal state is zero;
- `resolved is True` and `terminates is True`;
- `exact_value_fractions()` equals the input quotient exactly; and
- `to_witness()` produces a valid deterministic v0.14 witness.

### 5.2 Eventually periodic

- `status is DivisionStreamStatus.EVENTUALLY_PERIODIC`;
- `period_digits` is nonempty and primitive;
- the cycle witness records an exact repeated Gaussian state;
- `resolved is True` and `terminates is False`;
- `exact_value_fractions()` equals the input quotient exactly; and
- `to_witness()` produces a valid deterministic v0.14 witness.

### 5.3 Search limit reached

- `status is DivisionStreamStatus.LIMIT_REACHED`;
- `resolved is False`;
- the result preserves only digits and states observed within `max_steps`;
- it is an operational result, never evidence of aperiodicity; and
- exact-value and mathematical-witness requests retain the v0.14 exception
  behavior.

Equivalent noncanonical spellings of the same two operands must produce
identical `DivisionResolution.to_dict()` values.

## 6. Legacy `div_cnrs` compatibility boundary

The existing `div_cnrs(a: str, b: str) -> str` function is a legacy compatibility
API whose baseline implementation passes through Python `complex`. v0.17 does
not silently redefine its return grammar or make it the authoritative exact
division route.

For v0.17:

- its public signature and baseline outputs remain unchanged;
- it receives a runtime and documentation deprecation notice directing new code
  to `divide_cnrs_exact`;
- no new production or example code may call it; and
- no exactness claim may be attached to it.

Removal or semantic replacement of `div_cnrs`, including a new periodic string
grammar, requires a separately approved future freeze. Deprecation warnings must
not be emitted during import; they may be emitted only when `div_cnrs` is called.

## 7. Independence and anti-regression boundary

Acceptance tooling must fail if the new production route:

- imports `cnrs.validation` or `cnrs.cnrs_div`;
- uses `complex`, `float`, `/` on Python numeric values, `round`, `.real`,
  `.imag`, or tolerance comparison;
- duplicates the streaming digit recurrence, cycle-detection loop,
  canonical-periodic algorithm, or witness validator;
- returns an approximate finite string for a periodic or unresolved quotient;
- mutates or trusts supplied witness fields instead of using v0.14 validation; or
- changes any v0.14 witness schema or algorithm identifier.

The guard must also fail if the independent oracle imports any prohibited
production operation listed in §3.5.

Exact integer floor or remainder operations already present inside the frozen
v0.14 engine are outside the prohibition. The prohibition applies to new v0.17
code and to any modified legacy division route.

## 8. Compatibility boundary

The release must preserve:

- all v0.14 streaming-division signatures, statuses, witnesses, fixed vectors,
  canonical parity, and exception classes;
- all v0.15 finite convolution, normalization, limits, and witness contracts;
- all v0.16 finite-string and exact-multiplication signatures and outputs;
- package import compatibility and clean wheel/sdist behavior; and
- existing downstream CNRS-H, `CVal`, scientific, and formal-alignment tests.

No existing public class is widened or narrowed by v0.17.

## 9. Documentation boundary

README documentation must include one executable example covering:

1. exact terminating string division, such as `"1" / "10"`;
2. exact eventually-periodic string division, such as `"1" / "2"`;
3. status inspection;
4. exact `Fraction`-pair recovery; and
5. witness creation only after resolution.

Documentation must say that `LIMIT_REACHED` is operational, not mathematical
evidence of nonperiodicity. It must identify `div_cnrs` as legacy and must not
claim universal performance, bounded total resources, arbitrary infinite-stream
completion, or end-to-end Lean verification.

## 10. Formal-method boundary

This release introduces no new Lean theorem, proof, extraction, or
formal-to-runtime equivalence claim. Unless a separately approved amendment is
adopted, the entire `formal/` subtree must remain byte-identical to
`d3ee7c7fd6648812966f3aaa4f700acbc40e223f` and the exact-tree Lean
source-identity certification must remain valid.

## 11. Explicit non-goals

The following are excluded:

- a new periodic string serialization grammar;
- removal or semantic replacement of `div_cnrs`;
- Gaussian Euclidean `divmod` or quotient/remainder tie-breaking;
- changes to addition, subtraction, multiplication, convolution, or carry
  normalization;
- changes to CNRS-H, analytic continuation, ODE, biology, physics, or branch
  APIs;
- unrestricted symbolic division or arbitrary analytic-function division;
- performance-superiority claims or FFT/GPU work;
- a new witness schema or duplicate periodicity engine;
- new formal proofs or Lean extraction;
- version activation, release metadata, tags, publication, or Zenodo action; and
- unrelated cleanup, formatting, or refactoring.

## 12. Freeze-change rule

After adoption, any change to the public signature, parser domain, quotient
construction, result type, status semantics, legacy boundary, witness identity,
formal boundary, or acceptance gate requires a written freeze amendment and
renewed author approval.

