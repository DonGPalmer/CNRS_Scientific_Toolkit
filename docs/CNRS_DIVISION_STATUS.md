# CNRS-A Division Status (v0.8.0)

CNRS-A has exact finite representation for Gaussian integers and exact native addition, subtraction, negation, and multiplication over finite canonical strings.  Division is different: general division does not remain a finite CNRS-A string.

The toolkit therefore classifies division rather than presenting it as ordinary field closure.

## Implemented categories

`cnrs.cnrs_division_status.classify_division(numerator, denominator)` returns one of:

| Category | Meaning |
|---|---|
| `gaussian_integer` | reduced denominator is 1 |
| `terminating_z0_power` | denominator contributes only a finite base-shift / power-of-5 effect under the existing rational layer |
| `eventually_periodic` | reduced denominator is coprime to 5; z0-adic tail is eventually periodic |
| `shifted_eventually_periodic` | finite shift followed by a periodic tail |

`division_expansion(...)` combines this classification with the existing exact `CnrsRational` expansion object.

## What is established in code

The code computes exact rational expansion data using the existing `cnrs_rational` machinery.  It records prefix, period, period length, and string-with-period display where applicable.

## What remains open theoretically

The toolkit does not claim a sharp formula for minimal carry-state cardinalities.  It also does not claim finite-string field closure for all division.  Those remain mathematical questions for the theory track.
