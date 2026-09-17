# CNRS Scientific Toolkit v0.16.0 acceptance packet

Status: DRAFT — PREPARED FOR AUTHOR REVIEW; NOT YET AUTHORIZED FOR EXECUTION

Architecture authority, once separately approved:

- `V016_ARCHITECTURE_FREEZE.md`
- `V016_EXACT_MULTIPLICATION_API_CONTRACT.md`

Verified preparation baseline:

- commit `3d1b8e736395402b1f6c13e4aee225a97902fbaa`
- tree `79ae69643d5060e84ba34e6b00e6562d1ef7d97b`
- formal subtree `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`
- `1281 passed, 4 skipped` on 17 September 2026

## 1. Candidate identity gate

Before implementation begins, verify that the candidate branch was created
directly from the baseline commit and tree above. Before every review, merge,
or release decision, record the exact candidate commit and tree and rerun every
gate against that identity.

If `main` changes before branch creation, stop. Rebase or replacement of the
baseline requires a refreshed preparation packet or an explicit freeze
amendment; do not silently transplant the packet.

## 2. Required implementation artifacts

The candidate must contain:

- `cnrs/finite_string.py`;
- exact `mul_cnrs` routing in `cnrs/cnrs_mul.py`;
- a validation-only copy of the baseline multiplication algorithm under
  `cnrs/validation/`;
- dedicated v0.16 tests;
- an executable acceptance suite under `acceptance/v016/`;
- a static claim/independence guard under `tools/`;
- README quickstart coverage; and
- released wording in `cnrs/__init__.py` for the v0.15 convolution API.

No version bump or release artifact is part of candidate implementation.

## 3. Executable acceptance gates

### A01 — public signatures and exports

Assert the exact bridge and multiplication signatures, public re-exports, and
`__all__` entries. Assert all v0.15 public signatures are unchanged.

### A02 — parser grammar and canonical examples

Cover every example in the API contract, all five digits at integer and
fractional positions, leading/trailing zeros, `"1."`, `".1"`, and canonical
zero. Reject non-string inputs and every specified malformed class with the
specified exception type.

### A03 — formatter domain and exponent padding

Cover zero, positive offsets, negative offsets, internal zeros, subclasses,
and all digit values. Reject non-carriers and every Gaussian coefficient that
is not `(d,0)` for `d in 0..4`.

### A04 — round-trip laws

Exhaustively enumerate every accepted digit string whose total digit count is
at most four, across every legal radix placement, and assert both frozen
round-trip laws. Add deterministic randomized coverage through at least 5,000
longer valid strings.

### A05 — exact multiplication value

For every pair of canonical digit strings of length at most three, including
all radix placements, compare `mul_cnrs` with an independent exact Gaussian
integer/rational value oracle. Add deterministic randomized coverage of at
least 5,000 operand pairs with mixed integer and fractional offsets.

The independent oracle must use direct tuple arithmetic and exact rational
denominators. Floating tolerances are forbidden.

### A06 — historical output parity

Compare new `mul_cnrs` output byte-for-byte with the validation-only baseline
oracle for:

- the same exhaustive domain as A05;
- at least 5,000 deterministic randomized valid operand pairs;
- all existing multiplication regression vectors; and
- long all-`4` stress inputs of 300 digits per operand.

Any mismatch is a release blocker until explained by an author-approved freeze
amendment. Malformed inputs are not in the parity domain.

### A07 — exact-route enforcement

The static guard must fail if production multiplication or bridge code:

- imports `cnrs.validation`;
- uses `complex`, `round`, `.real`, or `.imag`;
- contains a second nested-loop convolution implementation; or
- implements a second carry recurrence instead of calling the v0.15 exact
  primitives.

It must also fail if the legacy or exact acceptance oracles import or call the
production operations prohibited by the architecture freeze.

### A08 — v0.15 preservation

Run the complete v0.15 dedicated suite and claim guard. Witness fixed vectors,
canonical serialization, normalization limits, convolution limits, and public
signatures must remain unchanged.

### A09 — downstream compatibility

Run existing `CVal`, CNRS-H native arithmetic, normalization-scope, Technical
Companion equation, and out-of-normal-range stress tests. No call-site change to
`mul_cnrs` is permitted.

### A10 — complete regression suite

Run the entire test suite. The gate requires zero failures. The final report
must state exact passed/skipped counts rather than copying the preparation
baseline count.

### A11 — clean-distribution verification

Build wheel and source distribution reproducibly, install each in a separate
clean environment, and execute a smoke program that imports both bridge
functions and verifies exact fractional multiplication. Candidate development
retains version `0.15.0`; changing package, runtime, citation, release, or tag
versions requires separate activation authority.

### A12 — formal-source preservation

Verify the candidate `formal/` subtree is exactly
`d3ee7c7fd6648812966f3aaa4f700acbc40e223f`, run
`tools/check_lean_alignment.py`, and preserve the existing Lean source-identity
workflow result. Any formal subtree delta is a stop condition requiring separate
scope and review.

### A13 — documentation truthfulness

Execute the README quickstart verbatim. Check that public text makes no claim of
universal performance, bounded total resources, Lean extraction, or broader
normalization consolidation. Check that no released API is still labeled a
candidate.

## 4. Candidate commands

Names may be adjusted during implementation only where no public contract is
affected; the final candidate must provide an equivalent one-command sequence.

```bash
pytest -q tests/test_v016_exact_multiplication.py
pytest -q acceptance/v016
python tools/check_v016_claims.py
pytest -q tests/test_v015_finite_convolution.py
python tools/check_v015_claims.py
pytest -q acceptance/v014
pytest -q
python tools/check_lean_alignment.py
```

Distribution builds and clean-install smoke tests must also pass in the GitHub
workflow for the exact candidate head.

## 5. Review evidence required

The governed implementation review packet must record:

- candidate commit and tree;
- diffstat and complete changed-path list;
- exact results for A01 through A13;
- complete regression passed/skipped counts;
- exact workflow run and job identities for push and pull-request CI;
- wheel and source-distribution names, sizes, and SHA-256 values;
- source-index/checksum results when those release-engineering artifacts are
  later prepared under separate authority;
- formal subtree identity and Lean source-identity result; and
- every warning, deviation, or waived item.

## 6. Stop conditions

Stop without marking ready, merging, or activating a version if any of these is
true:

- candidate ancestry is not the approved baseline or approved amendment;
- a frozen signature, grammar rule, output, witness vector, or exception class
  changes;
- exact-value or historical-parity validation disagrees;
- production arithmetic reaches a validation oracle or uses floating/complex
  carry logic;
- full tests, dedicated tests, clean installs, distribution builds, or required
  workflows fail or are missing;
- the formal subtree changes or its source-identity check fails;
- the changed-path set includes unrelated work;
- evidence refers to a commit other than the exact candidate head; or
- execution would require authority beyond the separately approved step.

## 7. Authorization boundaries

Approval of this acceptance packet authorizes no action by itself. Candidate
implementation, branch creation, pull-request creation, readiness, merge,
version activation, tagging, GitHub release publication, package publication,
Zenodo action, and branch deletion each remain outside this preparation packet
unless separately and explicitly authorized.

