# v0.14.0 freeze amendment — equal-output benchmark and finite bound

Status: APPROVED TECHNICAL REPAIR WITHIN FROZEN SCOPE  
Date: 2026-09-12

## Amendment 1: equal-output performance comparison

The preimplementation benchmark compared stream.take(n) with
expand_division(..., max_frac=n). The traditional call returns a compact
eventually-periodic object and does not necessarily materialize n logical
digits. That was not an equal-output timing comparison.

The repaired benchmark first obtains the traditional canonical compact
expansion and then materializes exactly n logical digits from its prefix and
period. Both measured paths now return the same number and sequence of digits.
The architecture, public API, and claim boundary are unchanged.

## Amendment 2: bounded terminating resolution

The acceptance suite now explicitly requires max_steps to bound terminating
integer expansions as well as periodic state searches. If a terminating
expansion needs more than the supplied number of steps, resolve returns
LIMIT_REACHED with the observed prefix. It does not precompute the remaining
digits or issue a mathematical conclusion.

This closes an ambiguity in the original bounded-resolution contract without
changing a public signature or broadening a claim.

## Required evidence

- v0.14.0 acceptance suite GREEN;
- exact parity with CanonicalPeriodicExpansion;
- benchmark JSON and CSV produced by the equal-output harness;
- independent audit of this amendment with the candidate.
