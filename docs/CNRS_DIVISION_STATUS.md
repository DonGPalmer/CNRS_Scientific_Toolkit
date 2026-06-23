# CNRS-A division status (v0.8.1)

CNRS-A finite digit strings are closed under addition, negation, subtraction, and multiplication. General division is different: it is not finite-string field closure.

The toolkit therefore classifies division results rather than pretending all quotients are finite CNRS-A strings.

## Cases

| Case | Meaning | Toolkit status |
|---|---|---|
| Gaussian integer quotient | reduced denominator is 1 | finite |
| terminating base-power denominator | reduced denominator is a pure power of 5 for ordinary integer denominators | terminating fractional representation |
| periodic coprime denominator | denominator is coprime to 5 | z0-adic periodic representation |
| shifted periodic tail | denominator has a power-of-5 factor and a persistent coprime factor | Laurent-periodic representation |

Use `cnrs.division.classify_denominator` for the denominator classification and `cnrs.division.expand_division` for the classified expansion object.

The exact expansion engine is the existing `gaussian_rational_to_cnrs` implementation. The new v0.8.0 module adds theorem-aligned status language and a structured wrapper.

Sharp minimal carry-state cardinalities remain a mathematical open problem. The toolkit does not claim a universal sharp bound.
