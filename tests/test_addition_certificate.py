"""Evidence drift controls and all-state drain/finite-addition checks."""
from collections import deque
from fractions import Fraction
import importlib.util
from pathlib import Path
import pytest

from cnrs.cnrs_add import ADDITION_TABLE, CARRY_SET_PAIRS, add_cnrs
_SPEC = importlib.util.spec_from_file_location(
    "addition_certificate_checker",
    Path(__file__).resolve().parents[1] / "tools" / "check_addition_certificate.py",
)
assert _SPEC is not None and _SPEC.loader is not None
_CHECKER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_CHECKER)
CertificateError = _CHECKER.CertificateError
FIXTURE = _CHECKER.FIXTURE
check_addition_certificate = _CHECKER.check_addition_certificate


def test_complete_pinned_relation_and_sharp_bound():
    result = check_addition_certificate()
    assert result["states"] == 14
    assert result["transitions"] == 350
    assert result["maximum_drain"] == 5
    assert result["drain_lengths"] == [0, 1, 3, 2, 3, 2, 3, 3, 2, 3, 5, 4, 3, 5]


@pytest.mark.parametrize("mutation", ["row", "missing", "extra", "boolean_output", "boolean_key", "float_output"])
def test_relation_drift_is_rejected(mutation):
    table = dict(ADDITION_TABLE)
    if mutation == "row": table[0, 0, 0] = (1, 0)
    elif mutation == "missing": del table[0, 0, 0]
    elif mutation == "extra": table[14, 0, 0] = (0, 0)
    elif mutation == "boolean_output": table[0, 0, 0] = (False, 0)
    elif mutation == "float_output": table[0, 0, 0] = (0.0, 0)
    else:
        del table[0, 0, 0]
        table[False, 0, 0] = (0, 0)
    with pytest.raises(CertificateError):
        check_addition_certificate(table, CARRY_SET_PAIRS)


def test_carry_order_drift_is_rejected():
    carries = list(CARRY_SET_PAIRS)
    carries[1], carries[2] = carries[2], carries[1]
    with pytest.raises(CertificateError, match="carry order"):
        check_addition_certificate(ADDITION_TABLE, carries)


def test_noninteger_carry_is_rejected():
    carries = list(CARRY_SET_PAIRS)
    carries[0] = (False, 0)
    with pytest.raises(CertificateError, match="exact integer pairs"):
        check_addition_certificate(ADDITION_TABLE, carries)


def test_fixture_edit_is_rejected(tmp_path):
    path = tmp_path / "fixture.json"
    path.write_bytes(FIXTURE.read_bytes() + b" ")
    with pytest.raises(CertificateError, match="fixture digest"):
        check_addition_certificate(fixture=path)


def exact_value(s):
    """Independent rational Horner evaluator, without Toolkit value carriers."""
    left, sep, right = s.partition(".")
    real = imag = Fraction(0)
    for digit in left + right:
        real, imag = -2*real-imag+int(digit), real-2*imag
    for _ in right:
        real, imag = (-2*real+imag)/5, (-real-2*imag)/5
    return real, imag


def reach_witnesses():
    witnesses, pending = {0: []}, deque([0])
    while pending:
        q = pending.popleft()
        for a in range(5):
            for b in range(5):
                successor = ADDITION_TABLE[q, a, b][1]
                if successor not in witnesses:
                    witnesses[successor] = witnesses[q] + [(a, b)]
                    pending.append(successor)
    assert set(witnesses) == set(range(14))
    return witnesses


@pytest.mark.parametrize("state", range(14))
@pytest.mark.parametrize("fractional_digits", [0, 1, 7])
def test_public_addition_after_reaching_every_carry(state, fractional_digits):
    pairs = reach_witnesses()[state]
    # Prefix high zeros to cover long fractional shifts without changing the
    # state reached by the witness's significant input columns.
    width = max(1, len(pairs), fractional_digits + 1)
    a = "".join(str(x) for x, _ in reversed(pairs)).zfill(width)
    b = "".join(str(y) for _, y in reversed(pairs)).zfill(width)
    if fractional_digits:
        a = a[:-fractional_digits] + "." + a[-fractional_digits:]
        b = b[:-fractional_digits] + "." + b[-fractional_digits:]
    x, y = exact_value(a), exact_value(b)
    value = exact_value(add_cnrs(a, b))
    assert value == (x[0]+y[0], x[1]+y[1])
