# CNRS Scientific Toolkit v0.17.0 exact-division API contract

**Status:** DRAFT — PREPARED FOR AUTHOR REVIEW; NOT YET ADOPTED

This contract is subordinate to `V017_ARCHITECTURE_FREEZE.md` and states the
frozen behavior in implementation-oriented form.

## 1. Public API

```python
from cnrs.streaming_division import DivisionResolution

def divide_cnrs_exact(
    dividend: str,
    divisor: str,
    *,
    max_steps: int = 100_000,
) -> DivisionResolution: ...
```

The name is exported from `cnrs.exact_division`, re-exported from `cnrs`, and
listed in `cnrs.__all__`.

No new result class, status enum, cycle class, witness class, schema identifier,
or algorithm identifier is introduced.

## 2. Normative composition

```python
left = cnrs_string_to_finite_sequence(dividend)
right = cnrs_string_to_finite_sequence(divisor)

left_num, left_den = finite_value_fraction(left)
right_num, right_den = finite_value_fraction(right)

if right_num == (0, 0):
    raise ZeroDivisionError("CNRS division by zero")

quotient_num = gaussian_multiply(left_num, right_den)
quotient_den = gaussian_multiply(left_den, right_num)

return stream_division(quotient_num, quotient_den).resolve(max_steps)
```

Names for private helpers may differ. Observable behavior and delegation may
not differ.

## 3. Operand examples

| Input | Exact value |
|---|---:|
| `"0"` | `0` |
| `"1"` | `1` |
| `"10"` | `beta` |
| `".1"` | `beta^-1` |
| `"1."` | `1` |
| `"001"` | `1` |
| `"0.010"` | `beta^-2` |

`beta = -2 + i`. Values are mathematical Gaussian fractions, not Python
floating or complex approximations.

## 4. Required fixed quotient vectors

| Dividend | Divisor | Required outcome |
|---|---|---|
| `"0"` | `"1"` | terminating exact zero |
| `"1"` | `"1"` | terminating exact one |
| `"1"` | `"10"` | terminating exact `beta^-1` |
| `".1"` | `"1"` | terminating exact `beta^-1` |
| `".1"` | `".1"` | terminating exact one |
| `"23.1"` | `"1."` | terminating exact value of `"23.1"` |
| `"1"` | `"2"` | resolved eventually periodic |
| `"1"` | `"3"` | resolved eventually periodic |
| `"1"` | `"4"` | resolved eventually periodic |
| `"1"` | `"11"` | resolved eventually periodic |
| `"1"` | `"20"` | resolved eventually periodic with a negative power offset |

The exact prefix, primitive period, power offset, step count, and cycle witness
for these vectors must be generated from the unmodified v0.14 engine and frozen
as implementation-candidate fixtures before review. They may not be guessed in
this preparation contract.

For every vector:

```python
result.exact_value_fractions() == independent_exact_quotient(dividend, divisor)
```

## 5. Status behavior

### `TERMINATING`

```python
result.resolved is True
result.terminates is True
result.period_digits == ()
result.witness is None
validate_division_witness(result.to_witness()) == result.to_witness()
```

The exact terminal-state invariant remains the v0.14 invariant.

### `EVENTUALLY_PERIODIC`

```python
result.resolved is True
result.terminates is False
len(result.period_digits) > 0
primitive_period(result.period_digits) == result.period_digits
result.witness is not None
validate_division_witness(result.to_witness()) == result.to_witness()
```

### `LIMIT_REACHED`

```python
result.resolved is False
result.terminates is False
result.status is DivisionStreamStatus.LIMIT_REACHED
```

`to_witness()` and resolved-only exact-value recovery retain the v0.14
exceptions. The outcome makes no claim that the quotient is aperiodic.

## 6. Canonical-equivalence law

For all accepted spellings `a1`, `a2`, `b1`, and `b2` satisfying

```python
normalize_cnrs(a1) == normalize_cnrs(a2)
normalize_cnrs(b1) == normalize_cnrs(b2)
```

and nonzero divisor value:

```python
divide_cnrs_exact(a1, b1, max_steps=n).to_dict() \
    == divide_cnrs_exact(a2, b2, max_steps=n).to_dict()
```

for the same positive integer `n`.

## 7. Exact-value law

If the two finite input values are

```text
dividend = x + yi
divisor  = u + vi
```

with rational components, the returned resolved exact value must equal

```text
real      = (xu + yv) / (u^2 + v^2)
imaginary = (yu - xv) / (u^2 + v^2)
```

using `Fraction` throughout. This formula is an acceptance oracle formula, not
permission to implement production with a second independent route.

## 8. Errors

| Condition | Required exception |
|---|---|
| either operand is not exact `str` | `TypeError` |
| malformed operand under the v0.16 grammar | `ValueError` |
| divisor has exact value zero, including noncanonical zero spellings | `ZeroDivisionError` |
| `max_steps` is `bool` or not an `int` | `TypeError` |
| `max_steps <= 0` | `ValueError` |

Malformed-input validation must not be bypassed by early zero or equality
shortcuts.

## 9. Resource statement

`max_steps` bounds counted streaming recurrence steps for resolution. It does
not bound wall-clock time, total memory, integer bit length, input size, output
size, Python runtime overhead, or witness serialization cost. A limit outcome
is reproducible operational evidence only.

## 10. Legacy compatibility API

```python
def div_cnrs(a: str, b: str) -> str: ...
```

The signature and baseline behavior remain unchanged in v0.17. It is explicitly
legacy, outside the exactness claim, and deprecated on call. No README example,
new production code, or new acceptance code may use it as an exact oracle.

## 11. Independence requirements

The production module may import the v0.16 finite-string bridge, exact Gaussian
arithmetic helpers, and v0.14 streaming APIs. It may not import:

- `cnrs.validation`;
- `cnrs.cnrs_div`;
- an acceptance oracle; or
- a second periodic-expansion implementation.

The validation oracle may import immutable data types such as `Fraction`, but
may not call the production bridge under test, streaming engine, canonical
periodic constructor, or witness generator.

