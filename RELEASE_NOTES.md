# v0.10.1 — Formal Alignment and Research Release

## Summary

v0.10.1 aligns the CNRS Scientific Toolkit with the CNRS mathematical record.
The release focuses on traceability, reproducibility, and clearer separation
between established implementation capability and open research questions.

## Added

### Theorem-to-Implementation Alignment

Added documentation describing the relationship:

- mathematical theorem,
- constructive algorithm,
- implementation,
- verification tests,
- software release.

### Research Status Documentation

Added:

- `docs/THEOREM_ALIGNMENT.md`
- `docs/API_STATUS.md`

These documents define stable, research, and experimental capability areas.

### Continuous Integration

Added GitHub Actions testing workflow:

- automated installation,
- pytest execution,
- regression checking.

## Changed

### Release Packaging

- Removed development cache artifacts.
- Updated ignore rules for Python development files.
- Improved reproducibility of release archives.

### Documentation

Updated README to clarify:

- CNRS-A maturity,
- CNRS-H research status,
- open completeness questions,
- distinction between software and mathematical claims.

## Validation

Full test suite:

- 1121 passed
- 6 expected failures
- 0 unexpected failures

Warnings produced by tests relate to intentional domain-validity diagnostics.

## Known Open Research Areas

The Toolkit does not claim completion of:

- CNRS metric completeness,
- the e-base CNS theorem,
- full analytic closure,
- physical interpretation of all CNRS states.

