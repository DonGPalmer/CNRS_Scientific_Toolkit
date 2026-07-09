# CNRS-A division status (v0.8.1)

CNRS-A finite digit strings are closed under addition, negation, subtraction, and multiplication. General division is different: it is not finite-string field closure.

The toolkit therefore classifies division results rather than pretending all quotients are finite CNRS-A strings.

## Cases

| Case | Meaning | Toolkit status |
|---|---|---|
| Gaussian integer quotient | reduced denominator is 1 | finite |
| terminating base-power denominator | after reduction, denominator is `5^s` and numerator is divisible by `conjugate(z0)^s` in `Z[i]` | terminating fractional representation |
| periodic coprime denominator | denominator is coprime to 5 | z0-adic periodic representation |
| shifted periodic tail | denominator contains a `z0` factor but the numerator does not cancel the full conjugate-base factor, with or without a further coprime factor | Laurent-periodic representation |

Use `cnrs.division.classify_denominator` for the denominator classification and `cnrs.division.expand_division` for the classified expansion object.

The exact expansion engine is the existing `gaussian_rational_to_cnrs` implementation. The new v0.8.0 module adds theorem-aligned status language and a structured wrapper.

Sharp minimal carry-state cardinalities remain a mathematical open problem. The toolkit does not claim a universal sharp bound.

## Gaussian-factor correction in v0.11.0

For `z0=-2+i`,

```text
5 = z0 * conjugate(z0).
```

Therefore a pure rational-integer power of five is not sufficient for termination. For a reduced fraction `(A+Bi)/5^s`, termination occurs exactly when `conjugate(z0)^s` divides `A+Bi` in `Z[i]`. Thus `1/5` is shifted-periodic, while `(-2-i)/5 = z0^{-1}` terminates. See `docs/theory/GAUSSIAN_RATIONAL_PERIODICITY_THEOREM_V1.md`.
