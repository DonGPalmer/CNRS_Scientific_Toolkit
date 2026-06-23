# CNRS-A Structured Division Expansions

v0.8.1 expands the division API from status classification to structured
prefix/period reports.

```python
from cnrs.division import expand_division, division_summary

x = expand_division(1, 10)
print(x.status)
print(x.structured_digits())

print(division_summary(1, 2))
```

The division layer deliberately avoids claiming finite-string field closure.
It reports whether a reduced denominator is:

- a Gaussian-integer quotient;
- terminating through a base-power denominator;
- eventually periodic with a persistent coprime denominator;
- shifted-periodic when a base-power factor and persistent denominator both
  occur.

Sharp minimal carry-state counts remain an open/theory-side question.
