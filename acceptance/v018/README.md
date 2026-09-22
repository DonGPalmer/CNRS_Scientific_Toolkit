# CNRS Scientific Toolkit v0.18.0 acceptance packet

**Status:** DRAFT — PREPARED FOR AUTHOR REVIEW; NOT YET AUTHORIZED FOR EXECUTION

**Prepared:** 22 September 2026

Architecture authority, if separately adopted:

- `V018_ARCHITECTURE_FREEZE.md`
- `V018_EXACT_ADDITION_SUBTRACTION_API_CONTRACT.md`

Verified preparation baseline:

- commit `b290f2e3b43dc1830bb1311eb81393475b341a94`
- tree `ff732e56a6597d9ec98ce071f41507d7dd9bca21`
- formal subtree `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`
- exact `493`-file source inventory
- `1,381 passed, 4 skipped, 922 warnings` on 22 September 2026

## 1. Candidate identity gate

Before implementation begins, verify that any candidate branch was created
directly from the approved baseline commit and tree. Before each review, merge,
or release decision, record the exact candidate commit and tree and rerun every
gate against that identity.

If `main` changes before authorized branch creation, stop. Rebase or replacement
of the baseline requires a refreshed preparation packet or an explicit freeze
amendment. The preparation documents may not be silently transplanted.

## 2. Required implementation artifacts

An authorized candidate must contain:

- exact integer-pair transition construction in `cnrs/cnrs_add.py`;
- exact finite-string negation/subtraction routing in `cnrs/cnrs_ops.py`;
- an independent exact v0.18 oracle under `cnrs/validation/`;
- a validation-only frozen v0.17 parity oracle or equivalent immutable fixture;
- dedicated v0.18 unit tests;
- executable acceptance tests under `acceptance/v018/`;
- a static claim/independence guard under `tools/`;
- a machine-readable fractional-correction ledger or an exact equivalent in
  the acceptance evidence; and
- narrowly scoped documentation updates.

No version bump or release artifact is part of candidate implementation.

## 3. Executable acceptance gates

### A01 — baseline identity and ancestry

Assert the authorized base commit, base tree, candidate ancestry, complete
changed-path list, and absence of unrelated changes. A candidate based on a
different tree stops unless an approved amendment records the new baseline.

### A02 — public signatures, exports, and constants

Assert unchanged signatures and import paths for `add_cnrs`, `cnrs_add`,
`cnrs_neg`, and `cnrs_sub`. Assert unchanged return type `str`, public
re-exports, core façade exports, `CARRY_SET_PAIRS`, compatible `CARRY_SET`, and
the shape and container type of `ADDITION_TABLE`.

### A03 — exact transition identity

Generate the 350 transitions using exact integer-pair arithmetic. Assert:

- the 14 carry pairs and their order;
- exact equality with the frozen v0.17 table;
- SHA-256
  `b68818cdb0766aead9993639ca2f1b96351371154c94453e730bf9a67a0746ee`
  under the architecture serialization;
- exact divisibility at every transition;
- membership of every next carry in the carry set;
- full state drain under zero input; and
- observed maximum drain length five while retaining the runtime guard 20.

### A04 — accepted grammar and canonical spellings

Cover all five digits at integer and fractional positions, leading and trailing
zeros, `"1."`, `".1"`, internal zeros, and canonical zero. Assert canonical
equivalence for the examples in the API contract.

Out-of-contract behavior is tested separately for parity and must not be used
to broaden the exactness claim.

### A05 — exact addition value

Exhaustively enumerate every accepted spelling with one to three digits and
every legal radix placement. For all ordered operand pairs, compare the result
with the independent exact `Fraction`-pair sum oracle.

The preparation domain contains 740 spellings and 547,600 ordered pairs and
produced zero mismatches. The candidate must reproduce that result. Add at
least 10,000 deterministic randomized pairs with mixed offsets and at least 100
long-input pairs up to 1,000 digits per operand.

### A06 — addition historical-output parity

Compare candidate `add_cnrs` and `cnrs_add` byte-for-byte with the frozen v0.17
baseline for:

- the complete A05 exhaustive domain;
- at least 10,000 deterministic randomized accepted operand pairs;
- every existing addition regression vector;
- long all-`4`, alternating, leading-zero, and mixed-radix inputs; and
- the agreed out-of-contract compatibility fixture.

Any accepted-domain output mismatch is a release blocker.

### A07 — exact negation value

For every A05 spelling, compare `cnrs_neg` with an independent exact
`Fraction`-pair negation and with exact multiplication by `"144"`. Add at least
10,000 deterministic randomized inputs and long mixed-offset inputs.

Assert involution, additive inverse, canonical output, and all fixed vectors in
the API contract.

### A08 — exact subtraction value

For all ordered pairs in the A05 domain, compare `cnrs_sub` with the independent
exact difference oracle. Add at least 10,000 deterministic randomized pairs.

Assert self-subtraction, zero identity, antisymmetry, canonical equivalence, and
all fixed vectors in the API contract.

### A09 — correction ledger and correct-behavior parity

For each negation and subtraction result in the exhaustive domain:

- if the frozen v0.17 output equals the exact oracle, require byte parity;
- otherwise require the unique canonical exact result and record the change;
- reject every result that is neither baseline-correct parity nor the exact
  correction; and
- report mismatch counts and representative vectors.

The preparation audit found 392 negation mismatches among 740 spellings and
290,080 subtraction mismatches among the 547,600 ordered pairs involving
radix-point spellings. Candidate evidence must recompute, not copy, these
counts.

### A10 — algebraic laws and cross-operation consistency

Over exhaustive short domains and deterministic randomized longer domains,
assert:

- commutativity and associativity of addition;
- zero identity and additive inverses;
- negation involution;
- subtraction identities and antisymmetry;
- distributivity against released exact multiplication;
- equality of `cnrs_add` and `add_cnrs`; and
- equality of `cnrs_sub(a,b)` and `add_cnrs(a,cnrs_neg(b))`.

Every value comparison uses the independent oracle.

### A11 — exact-route and independence enforcement

The static guard must fail if claimed production paths:

- import `cnrs.validation`;
- use `complex`, `float`, tolerance comparison, `round`, `.real`, or `.imag`;
- call general value-map encoders/decoders;
- duplicate convolution or Gaussian/Laurent normalization;
- create a second addition transition relation; or
- route accepted operands through a compatibility fallback.

The guard must also fail if an independent oracle imports or calls prohibited
production operations. A compatibility lane, if needed, must be statically and
dynamically shown unreachable for the accepted grammar.

### A12 — v0.14–v0.17 preservation

Run all dedicated and executable acceptance suites and claim guards for
v0.14, v0.15, v0.16, and v0.17. Preserve signatures, witnesses, fixed vectors,
limits, normalization behavior, exact multiplication, exact division, and
legacy-division deprecation behavior.

### A13 — downstream compatibility

Run existing `CVal`, CNRS-H native arithmetic, normalization-scope, Technical
Companion equation, symbolic, ODE, and stress tests. Add fractional `CVal`
parity checks demonstrating that direct `cnrs_neg`/`cnrs_sub` now agree with
the already-exact `CVal` route.

No downstream call-site change is permitted solely to accommodate v0.18.

### A14 — complete regression suite

Run the complete suite with zero failures. The final evidence must state exact
passed, skipped, and warning counts for the candidate head rather than copying
the preparation baseline.

### A15 — reproducible builds and clean installations

Build wheel and source distributions reproducibly. Install each in separate
clean environments and execute smoke programs covering:

- integer and fractional addition;
- fractional negation and subtraction;
- unchanged exact multiplication and division;
- public and core-façade imports; and
- the fixed correction-ledger vectors.

Candidate development retains version `0.17.0`. Version activation requires
separate authority.

### A16 — formal and source preservation

Verify the formal subtree is exactly
`d3ee7c7fd6648812966f3aaa4f700acbc40e223f`, run the existing Lean-alignment
and source-identity checks, and preserve all formal sources byte-for-byte.

Regenerate `SOURCE_INDEX.txt` only if separately authorized for a later
candidate or activation step. Candidate review must nevertheless verify the
complete Git path inventory and explain any expected count delta.

### A17 — documentation and claim truthfulness

Execute every new README example verbatim. Check that public text:

- distinguishes exact finite strings from arbitrary infinite streams;
- identifies the narrow fractional correction;
- makes no universal resource or performance claim;
- makes no Lean-extraction or end-to-end formal-verification claim;
- preserves v0.14–v0.17 claims; and
- does not describe an unactivated candidate as released.

## 4. Candidate command set

Exact filenames may be adjusted during implementation only where the frozen
public contract is unaffected. The candidate must provide an equivalent
one-command sequence:

```bash
pytest -q tests/test_v018_exact_addition_subtraction.py
pytest -q acceptance/v018
python tools/check_v018_claims.py
pytest -q acceptance/v014 acceptance/v015 acceptance/v016 acceptance/v017
python tools/check_v015_claims.py
python tools/check_v016_claims.py
python tools/check_v017_claims.py
pytest -q
python tools/check_lean_alignment.py
```

If a historical acceptance directory has a different released layout, invoke
its authoritative released command instead of inventing a new path.
Distribution, clean-install, and GitHub workflow gates are additional.

## 5. Required review evidence

The implementation review packet must record:

- exact candidate commit, tree, base, ancestry, and changed paths;
- results for A01 through A17;
- transition checksum and carry-drain distribution;
- exhaustive and randomized sample counts;
- historical parity and fractional-correction counts;
- fixed correction-ledger vectors;
- full regression passed/skipped/warning counts;
- workflow run and job identities for push and pull-request CI;
- wheel and source-distribution names, sizes, and SHA-256 values;
- formal subtree and Lean source-identity results;
- source-index/inventory result; and
- every warning, deviation, compatibility fallback, or waived item.

## 6. Stop conditions

Stop without marking ready, merging, or activating if:

- candidate identity or ancestry is not authorized;
- a public API, correct result, transition, or table checksum changes;
- an output change is absent from the independently proved correction ledger;
- exact-value, parity, or algebraic-law validation disagrees;
- claimed production arithmetic reaches floating/complex or validation code;
- a compatibility fallback is reachable on an accepted input;
- any earlier acceptance or claim gate regresses;
- full tests, builds, clean installations, or required workflows fail or are
  missing;
- the formal subtree changes;
- the changed-path set contains unrelated work; or
- execution would require authority beyond the separately approved step.

## 7. Authorization boundary

Approval of this acceptance packet authorizes no action by itself. Architecture
adoption, API-contract adoption, implementation, branch creation, pull-request
creation, readiness, merge, version activation, tagging, release publication,
package publication, Dropbox mutation, DOI/Zenodo action, and branch deletion
all require separate and explicit authority.
