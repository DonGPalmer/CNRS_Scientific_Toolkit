# v0.14.0 acceptance test plan

Status: FROZEN FOR IMPLEMENTATION  
Preimplementation expectation: RED  
Release expectation: GREEN

The executable contract is acceptance/v014/test_streaming_division_contract.py. It is intentionally outside the default tests directory so the released v0.13.1 suite remains untouched while v0.14.0 is under development.

Run:

~~~bash
python -m pytest -q acceptance/v014
~~~

## Acceptance matrix

| ID | Requirement | Required evidence |
| --- | --- | --- |
| A01 | Public surface | Imports, signatures, constants, frozen dataclasses |
| A02 | Input discipline | Integer/Gaussian inputs accepted; ambiguous types rejected |
| A03 | Laziness and replay | Finite take; two iterators agree; no eager resolution |
| A04 | Digit contract | Every emitted digit is in {0,1,2,3,4} |
| A05 | Termination | 0/1, 1/1, and (-2-i)/5 resolve with empty period |
| A06 | Periodicity | 1/2 resolves with a primitive nonempty period |
| A07 | Shifted tail | 1/5 has negative power offset and eventual period |
| A08 | Gaussian denominator | (3+2i)/(1-2i) resolves exactly |
| A09 | Sign normalization | Equal quotients serialize identically |
| A10 | Search limit | LIMIT_REACHED is explicit and cannot become a witness |
| A11 | Canonical parity | Offset, prefix, period, and exact value match canonical API |
| A12 | Witness integrity | JSON round trip validates; tampering is rejected |
| A13 | Determinism | Repeated executions produce byte-identical canonical JSON |
| A14 | Regression | Existing Python suite and six Lean jobs stay GREEN |
| A15 | Hygiene | No float path, prohibited proof marker, network, or new dependency |
| A16 | Documentation | README, API status, claim status, theorem registry, provenance, release notes updated consistently |
| A17 | Performance evidence | Frozen protocol completes; JSON/CSV retained; exact parity passes |

## Required parity corpus

The release suite must include at least 100 deterministic nonzero-denominator cases covering:

- integer numerators from -12 through 12;
- denominators containing both base factors and coprime residual factors;
- Gaussian denominators in every quadrant;
- zero numerator, units, associates, reducible fractions, and sign-equivalent inputs;
- terminating, purely periodic, and shifted eventually-periodic outcomes.

Every resolved case must satisfy canonical parity and exact quotient recovery. The corpus must have a fixed source definition or seed recorded in the test.

## Release gates

1. The executable v0.14.0 acceptance suite is GREEN.
2. The complete pre-existing Python regression suite is GREEN with updated truthful counts.
3. All six Lean matrix jobs are GREEN.
4. Source/checksum alignment remains GREEN.
5. Claim-boundary and theorem-alignment documentation is audited.
6. Wheel and source distribution install in clean environments and rerun smoke tests.
7. An independent audit records candidate commit, tree, artifacts, test counts, and CI run identities.
8. The performance harness completes under the frozen protocol, retains raw results, and receives anomaly review.

No merge, tag, GitHub release, or Zenodo publication should precede these gates.
