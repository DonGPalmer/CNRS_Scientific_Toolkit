# Exact finite comparison — development candidate

Status: v0.19.0 RELEASE-ACTIVATION CANDIDATE; not released or published.
Implementation merged through PR #20 as
`f04c856064e82fc8e059af693d65392bff9ad843`. Package/runtime metadata is
0.19.0 on this candidate branch; merging activation and publication remain
separate governed actions. The public release remains v0.18.0.

## Additive public interfaces

```python
from cnrs import cnrs_eq_exact, cnrs_string_value_exact, CVal

assert cnrs_eq_exact('.1', '00.100')
value = cnrs_string_value_exact('.1')  # existing GaussianRational type
assert CVal('.1').to_gaussian_exact() == value
assert CVal('.1').equals_exact(CVal('0.1'))
```

`cnrs_string_value_exact(value)` parses with the existing strict finite-string
parser and evaluates the existing finite Laurent carrier at base `(-2, 1)`.
It returns an exact, canonically reduced `GaussianRational` with integer-pair
numerator and denominator. It does not return Python `complex`.
`cnrs_eq_exact(a,b)` compares those exact values. `CVal.to_gaussian_exact()`
and `CVal.equals_exact(other)` expose the same route.

The grammar is digits 0..4 with an optional single radix point and at least
one digit overall. Empty integer parts (`.1`), empty fractional parts (`1.`),
and redundant extreme zeros are accepted. Malformed spellings raise
`ValueError`; non-exact-str objects, including str subclasses, raise `TypeError`.
`CVal.equals_exact` requires a CVal operand or raises `TypeError`.

All four interfaces reuse production exact carriers. They import no validation
oracle and perform no floating-point conversion. They are computationally
verified, not Lean-extracted or end-to-end Lean-verified. There is no universal
runtime, memory or bit-complexity guarantee.

## Compatibility and precision

Legacy `cnrs_eq`, `CVal.__eq__`, `CVal.__hash__`, `to_gaussian`, existing
constructors, arithmetic operations and their out-of-domain compatibility
behavior are unchanged. Use the explicit exact methods for exact finite
comparisons; ordinary `==` on CVal still follows the legacy route.

For example, the spellings `a = '1' + '0'*80` and `b = a[:-1] + '1'` differ
exactly by one. The legacy complex conversion can compare them equal; the new
exact comparison returns False. Similarly, `0.` followed by 1000 zeros and a
final 1 is nonzero, although the legacy complex conversion underflows to zero.

A future migration of equality operators must address hash consistency,
noncanonical direct CVal constructors and malformed legacy inputs together.
This candidate does not silently change that existing contract.

## Verification

`python -m pytest -q tests/test_exact_comparison_candidate.py` covers exact
fractional values against an independent Fraction-pair oracle, large-value
rounding collisions, underflow, overflow-sized values, 115 short spellings
and all 13,225 exact-value pairs, validation errors and public reexports.

`python examples/exact_finite_arithmetic.py` demonstrates finite arithmetic,
exact comparison, exact periodic division and witness validation. These are
software checks, not an empirical claim that CNRS outperforms other systems.

The immutable `formal/` subtree and existing release contracts remain unchanged.
