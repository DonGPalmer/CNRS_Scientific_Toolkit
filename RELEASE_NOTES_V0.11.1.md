# v0.11.1 — Division Classification Consistency Patch

v0.11.1 is a corrective patch to the v0.11.0 rational-expansion release. It removes a contradiction between the theorem-aligned public division API and a retained v0.8.x compatibility module.

## Fixed

- Corrected `cnrs.cnrs_division_status.classify_division` so powers of five are no longer treated as automatically terminating.
- Made the legacy classifier numerator-aware by delegating to `cnrs.division.classify_denominator`.
- Preserved the legacy API as a deprecated compatibility wrapper rather than removing it.
- Corrected the regression test that previously classified `1/25` as terminating.
- Added cross-API consistency tests covering Gaussian-integer, terminating, periodic, and shifted-periodic cases.
- Clarified that a finite Laurent offset does not itself imply a terminating expansion.

## Mathematical correction

For `beta = -2+i`,

```text
5 = beta * conjugate(beta).
```

A reduced denominator `5**s` produces a terminating Laurent expansion only when the reduced numerator cancels `conjugate(beta)**s`. Therefore:

- `1/5` is shifted eventually periodic;
- `1/25` is shifted eventually periodic;
- `conjugate(beta)/5 = 1/beta` terminates;
- `conjugate(beta)**2/25 = 1/beta**2` terminates.

## Compatibility

`cnrs.cnrs_division_status` remains importable for existing callers. Its `classify_division` function now emits `DeprecationWarning`. New code should use:

```python
from cnrs.division import classify_denominator
```

## Validation

Run the final release candidate with:

```bash
python -m pytest
python -m build
python -m twine check dist/*
```

Record the exact final pass count in `docs/TEST_STATUS.md` and in the GitHub release after the complete v0.11.1 tree is tested. No estimated count is asserted in this patch package.
