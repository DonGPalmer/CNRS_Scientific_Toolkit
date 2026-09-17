# CNRS Scientific Toolkit v0.16.0 exact-multiplication API contract

Status: DRAFT — PREPARED FOR AUTHOR REVIEW; NOT YET ADOPTED

This contract is subordinate to `V016_ARCHITECTURE_FREEZE.md` and states the
frozen behavior in implementation-oriented form.

## Public bridge API

```python
def cnrs_string_to_finite_sequence(value: str) -> CNRSFiniteSequence: ...

def finite_sequence_to_cnrs_string(value: CNRSFiniteSequence) -> str: ...
```

### Parsing examples

| Input | Coefficients | Offset | Canonical formatted value |
|---|---:|---:|---|
| `"0"` | `()` | `0` | `"0"` |
| `"0012"` | `((2,0),(1,0))` | `0` | `"12"` |
| `"23.1"` | `((1,0),(3,0),(2,0))` | `-1` | `"23.1"` |
| `".1"` | `((1,0),)` | `-1` | `"0.1"` |
| `"1."` | `((1,0),)` | `0` | `"1"` |
| `"0.010"` | `((1,0),)` | `-2` | `"0.01"` |

The coefficients in the table are least-significant exponent first.

### Formatting examples

| Sequence | Output |
|---|---|
| `CNRSFiniteSequence(())` | `"0"` |
| `CNRSFiniteSequence((1,), 2)` | `"100"` |
| `CNRSFiniteSequence((1,), -3)` | `"0.001"` |
| `CNRSFiniteSequence((1,0,2), -1)` | `"20.1"` |

### Errors

| Condition | Required exception |
|---|---|
| parser input is not exact `str` | `TypeError` |
| empty, bare point, invalid digit, sign, whitespace, exponent, or repeated point | `ValueError` |
| formatter input is not a `CNRSFiniteSequence` instance | `TypeError` |
| formatter sees a non-digit Gaussian coefficient | `ValueError` |

## Public multiplication API

```python
def mul_cnrs(a: str, b: str) -> str: ...
```

Normative composition:

```python
left = cnrs_string_to_finite_sequence(a)
right = cnrs_string_to_finite_sequence(b)
raw = convolve_exact(left, right)
normalized = normalize_gaussian_laurent(raw)
return finite_sequence_to_cnrs_string(normalized)
```

An implementation may factor this composition into private helpers but may not
replace any step with floating-point, Python-complex, or duplicated arithmetic.

## Canonicality

Every successful public multiplication result:

- contains only `0` through `4` and at most one radix point;
- has at least one integer digit;
- has no redundant leading integer zero;
- has no trailing fractional zero;
- has no radix point when the fractional part is empty; and
- parses back to the exact normalized product carrier.

## Resource statement

`mul_cnrs` has no explicit resource-limit parameters. Its finite inputs imply a
finite stored-position convolution and finite exact carry drain, but this API
does not claim bounded elapsed time, memory, integer bit length, product count,
or output size. Callers needing explicit product and carry-drain accounting use
the v0.15 APIs directly.

## Validation-only legacy oracle

The validation oracle preserves the pre-v0.16 algorithm and accepts only the
same grammar used by the new bridge during parity tests. It is not a supported
end-user API. Any parity mismatch is a stop condition; it must be investigated,
not normalized away by changing both implementations together.

