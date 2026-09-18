# CNRS Scientific Toolkit v0.17.0 acceptance packet

**Status:** DRAFT — PREPARED FOR AUTHOR REVIEW; NOT YET AUTHORIZED FOR EXECUTION

Architecture authority, once separately approved:

- `V017_ARCHITECTURE_FREEZE.md`
- `V017_EXACT_DIVISION_API_CONTRACT.md`

## Verified preparation baseline

- Tag: `v0.16.0`
- Commit: `1b817fca30e061854e6bc62823e5c5ff28b92f9a`
- Tree: `006d27f65e301a6239a5362cbb988f6afb983bf4`
- Formal subtree: `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`
- Regression: `1,310 passed, 4 skipped, 922 warnings`

## 1. Candidate identity gate

Before implementation, verify that the candidate branch was created directly
from the exact baseline commit and tree above. Before review, readiness, merge,
or activation, record the exact candidate commit and tree and rerun all gates
against that identity.

If `main` changes before branch creation, stop. A new baseline requires a
refreshed preparation packet or explicit freeze amendment; do not silently
transplant the packet.

## 2. Required implementation artifacts

The candidate must contain:

- `cnrs/exact_division.py`;
- public export updates in `cnrs/__init__.py`;
- a validation-only exact rational-pair oracle under `cnrs/validation/`;
- dedicated v0.17 tests;
- an executable suite under `acceptance/v017/`;
- a static v0.17 claim/independence guard under `tools/`;
- README exact-division examples; and
- a narrowly documented `div_cnrs` deprecation-on-call boundary.

No package version bump, citation change, release note, tag, or publication
artifact belongs to implementation scope.

## 3. Executable acceptance gates

### A01 — baseline and changed-path identity

Verify the exact baseline ancestry, candidate commit and tree, diffstat, and
complete changed-path list. Reject formal-source changes, version activation,
release metadata, or unrelated paths.

### A02 — public signature, exports, and type identity

Assert the exact `divide_cnrs_exact` signature, re-export, and `__all__` entry.
Assert that the returned object is the existing v0.14 `DivisionResolution`, not
a duplicate or wrapper type. Assert all v0.14–v0.16 public signatures are
unchanged.

### A03 — parser and error inheritance

Exercise every accepted and rejected grammar class from v0.16 for both operand
positions. Verify exact exception classes. Verify that every canonical and
noncanonical zero divisor spelling raises `ZeroDivisionError`. Verify
`max_steps` type and positivity behavior.

### A04 — finite-carrier exact-value conversion

For every accepted digit string with total digit count at most four and every
legal radix position, compare the production converter's mathematical value
through the public result with an independent rational-pair evaluation. Include
at least 5,000 deterministic randomized longer strings and offsets.

The acceptance oracle uses only integer and `Fraction` pair arithmetic. It may
not call production conversion, streaming division, canonical periodic
construction, or witness code.

### A05 — exact quotient construction

For every ordered pair of canonical operands with total digit count at most
three and nonzero divisor, verify the normalized quotient numerator and
denominator against the independent conjugate formula. This gate may inspect
the resulting stream identity without resolving every quotient.

Add at least 5,000 deterministic randomized mixed-offset pairs. Include values
whose inputs contain negative offsets on one side, both sides, and neither
side.

### A06 — terminating resolution

Execute every terminating fixed vector from the API contract. Exhaustively
resolve all nonzero-divisor operand pairs with total digit count at most two
whose independent denominator analysis predicts termination. Verify status,
offset, digits, exact value, terminal state, and deterministic witness.

### A07 — eventually-periodic resolution

Execute every periodic and shifted-periodic fixed vector. Exhaustively resolve
all nonzero-divisor operand pairs with total digit count at most two whose
independent analysis predicts a persistent denominator. Verify primitive
period, repeated-state cycle, exact value, canonical parity, and deterministic
witness.

### A08 — limit behavior

Use deliberately small positive limits on known periodic examples. Verify
`LIMIT_REACHED`, exact step accounting, replayable observed digits, absence of a
mathematical witness, resolved-only exception behavior, and documentation that
the result is not evidence of aperiodicity.

### A09 — canonical-equivalence invariance

For equivalent spellings such as leading integer zeros, trailing fractional
zeros, `"1"`/`"1."`, and `".1"`/`"0.1"`, verify byte-identical
`DivisionResolution.to_dict()` output at the same limit. Add at least 2,000
deterministic randomized equivalent-spelling pairs.

### A10 — v0.14 canonical and witness parity

For every resolved acceptance case:

- compare power offset, prefix, and period with
  `CanonicalPeriodicExpansion.from_gaussian_fraction`;
- compare exact values byte-for-byte as reduced rational pairs;
- round-trip `to_witness()` through `validate_division_witness`; and
- preserve the frozen schema `cnrs-division-witness-v1` and algorithm
  `cnrs-gaussian-rational-stream-v1`.

The parity comparison is acceptance evidence, not permission to call the
canonical constructor inside the production bridge.

### A11 — exact-route and independence guard

The static guard must fail if new production code:

- imports validation or the legacy `cnrs_div` module;
- uses `complex`, `float`, numeric `/`, `round`, `.real`, `.imag`, or a floating
  tolerance;
- duplicates the v0.14 digit recurrence, state-cycle loop, canonical-periodic
  implementation, or witness validator; or
- returns a finite approximation for periodic or unresolved results.

It must fail if the validation oracle calls the production converter,
`divide_cnrs_exact`, `stream_division`, the canonical constructor, or witness
generation. Mutation probes must demonstrate rejection of every prohibited
class.

### A12 — legacy compatibility and deprecation boundary

Run all existing `div_cnrs` tests and a frozen baseline vector set. Verify its
signature and outputs are unchanged, its warning occurs only when called, and
no new code or documentation uses it as an exact route. Do not compare new exact
periodic results to approximate legacy output.

### A13 — v0.14–v0.16 preservation

Run the complete dedicated suites and claim guards for:

- v0.14 streaming division and witnesses;
- v0.15 finite convolution, normalization, and witnesses; and
- v0.16 finite strings and exact multiplication.

All fixed identities, signatures, exception classes, limits, serialized
witnesses, multiplication outputs, and bridge grammar must remain unchanged.

### A14 — downstream and full regression

Run downstream `CVal`, CNRS-H, normalization-scope, analytic-continuation,
scientific, Technical Companion, and stress tests, then the complete test
suite. Zero failures are required. Report exact passed, skipped, and warning
counts from the candidate rather than copying the baseline.

### A15 — clean-distribution verification

Build wheel and sdist reproducibly. Install each in a separate clean
environment and execute a smoke program that:

1. imports `divide_cnrs_exact`, `DivisionStreamStatus`, and witness validation;
2. verifies `"1" / "10"` terminates with the exact value;
3. verifies `"1" / "2"` resolves eventually periodically;
4. validates both witnesses; and
5. verifies a small limit yields `LIMIT_REACHED` without a witness.

Candidate development retains version `0.16.0`. Any package, runtime,
citation, release, or tag version change requires separate activation authority.

### A16 — formal-source preservation and documentation truth

Verify the candidate `formal/` subtree is exactly
`d3ee7c7fd6648812966f3aaa4f700acbc40e223f`, run the Lean alignment guard, and
preserve the existing six-project/79-file source-identity result.

Execute the README example verbatim. Reject claims of universal performance,
bounded total resources, mathematical meaning for `LIMIT_REACHED`, exactness of
legacy `div_cnrs`, Lean extraction, or broader arithmetic consolidation.

## 4. Candidate command surface

Exact filenames may be adjusted only where no frozen public contract is
affected. The candidate must provide an equivalent one-command sequence:

```bash
pytest -q tests/test_v017_exact_division.py
pytest -q acceptance/v017
python tools/check_v017_claims.py
pytest -q acceptance/v014
pytest -q tests/test_v015_finite_convolution.py
python tools/check_v015_claims.py
pytest -q tests/test_v016_exact_multiplication.py
pytest -q acceptance/v016
python tools/check_v016_claims.py
pytest -q
python tools/check_lean_alignment.py
```

Distribution builds and both clean-install smoke tests must pass in GitHub CI
for the exact candidate head.

## 5. Required review evidence

The governed implementation-review packet must record:

- candidate commit and tree;
- baseline ancestry and merge base;
- diffstat and complete changed-path list;
- exact A01–A16 results;
- exhaustive and randomized domain counts and seeds;
- every frozen fixed-vector output;
- full regression passed/skipped/warning counts;
- exact push and pull-request workflow and job identities;
- wheel and sdist filenames, byte sizes, and SHA-256 values;
- formal subtree identity and Lean source-identity result;
- source-index/checksum results when prepared under separate authority; and
- every warning, deviation, or waived item.

## 6. Stop conditions

Stop without marking ready, merging, activating, tagging, or publishing if:

- ancestry is not the approved baseline or an approved amendment;
- a frozen signature, grammar, result type, status, witness identity, exception
  class, or legacy output changes;
- exact-value, canonical-periodic, or witness validation disagrees;
- production reaches validation code, legacy complex division, duplicated
  recurrence, or floating/complex arithmetic;
- a periodic or unresolved quotient is presented as a finite exact string;
- a limit outcome is described as proof of aperiodicity;
- any dedicated, regression, clean-install, distribution, or required workflow
  gate fails or is absent;
- the formal subtree changes or source-identity certification fails;
- changed paths include unrelated work;
- evidence refers to a commit other than the exact candidate head; or
- execution would require authority beyond the separately approved step.

## 7. Authorization boundaries

Approval of this draft packet authorizes no repository action by itself.
Implementation, branch creation, pull-request creation, readiness, merge,
version activation, tagging, GitHub release or package publication, Zenodo
action, branch deletion, and unrelated mutation each require separate explicit
authorization.

