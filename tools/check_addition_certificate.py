"""Check production addition against pinned Lean-checked data; no Lean invocation."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "verification" / "finite_addition_certificate.json"
EXPECTED_SHA256 = "9b30818368ae814bd373c195ee7c7d8ba59bb0c525a0d7bc23e12b69487ea875"


class CertificateError(ValueError):
    """The production relation or its pinned evidence drifted."""


def check_addition_certificate(table=None, carry_pairs=None, fixture=FIXTURE):
    data = Path(fixture).read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        raise CertificateError("pinned Lean-checked fixture digest mismatch")
    certificate = json.loads(data)
    if table is None or carry_pairs is None:
        sys.path.insert(0, str(ROOT))
        from cnrs.cnrs_add import ADDITION_TABLE, CARRY_SET_PAIRS
        if table is None:
            table = ADDITION_TABLE
        if carry_pairs is None:
            carry_pairs = CARRY_SET_PAIRS
    carries = list(carry_pairs)
    if (len(carries) != 14 or
            any(type(p) is not tuple or len(p) != 2 or
                any(type(x) is not int for x in p) for p in carries)):
        raise CertificateError("carry inventory must contain 14 exact integer pairs")
    if [list(p) for p in carries] != certificate["carry_pairs"]:
        raise CertificateError("carry order differs from the Lean-checked inventory")
    expected_keys = {(q, a, b) for q in range(14) for a in range(5) for b in range(5)}
    if set(table) != expected_keys or len(table) != 350:
        raise CertificateError("production transition keys differ from the 350-row domain")
    # Reject Boolean/float key aliases even though Python compares them equal to ints.
    if any(type(k) is not tuple or len(k) != 3 or
           any(type(n) is not int for n in k) for k in table):
        raise CertificateError("transition keys must be exact integer triples")
    for q, a, b, digit, successor in certificate["rows"]:
        actual = table[q, a, b]
        if (type(actual) is not tuple or len(actual) != 2 or
                any(type(n) is not int for n in actual)):
            raise CertificateError("transition outputs must be exact integer pairs")
        if actual != (digit, successor):
            raise CertificateError(f"transition {(q, a, b)} differs from the Lean-checked row")
        if not (0 <= digit < 5 and 0 <= successor < 14):
            raise CertificateError("output digit or successor outside the finite domain")
        x, y = carries[q]
        u, v = carries[successor]
        # Independently reconstruct beta*(u+iv)+digit; no production quotient logic.
        if (digit - 2*u - v, u - 2*v) != (x + a + b, y):
            raise CertificateError(f"arithmetic reconstruction failed at {(q, a, b)}")
    reachable = {0}
    while True:
        successors = {table[q, a, b][1] for q in reachable for a in range(5) for b in range(5)}
        enlarged = reachable | successors
        if enlarged == reachable:
            break
        reachable = enlarged
    if reachable != set(range(14)):
        raise CertificateError("not all declared carries are reachable from zero")
    if table[0, 0, 0] != (0, 0):
        raise CertificateError("zero carry is not absorbing on zero input")
    lengths = []
    for q in range(14):
        state, seen = q, set()
        while state != 0:
            if state in seen or len(seen) >= 5:
                raise CertificateError(f"carry {q} does not drain within five steps")
            seen.add(state)
            state = table[state, 0, 0][1]
        lengths.append(len(seen))
    if lengths != certificate["zero_input_drain_lengths"] or max(lengths) != 5:
        raise CertificateError("sharp drain-bound evidence differs")
    return {"states": 14, "transitions": 350, "maximum_drain": 5,
            "drain_lengths": lengths}


if __name__ == "__main__":
    try:
        result = check_addition_certificate()
    except (CertificateError, OSError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"FAIL addition certificate: {exc}")
    print("PASS addition certificate: 14 states, 350 pinned transitions, "
          "exact column equations, complete reachability, sharp drain bound 5")
