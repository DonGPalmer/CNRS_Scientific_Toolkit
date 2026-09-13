"""Frozen v0.14.0 acceptance contract.

Expected state on the v0.13.1 baseline: collection RED because the two new
public modules do not exist. Expected state before v0.14.0 release: GREEN.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass
from fractions import Fraction
import inspect
import json

import pytest

from cnrs.canonical_periodic import CanonicalPeriodicExpansion, primitive_period
from cnrs.streaming_division import (
    CnrsDivisionStream,
    DivisionResolution,
    DivisionSearchLimitError,
    DivisionStreamStatus,
    stream_division,
)
from cnrs.witnesses import (
    DIVISION_ALGORITHM,
    DIVISION_WITNESS_SCHEMA,
    CycleWitness,
    DivisionWitness,
    WitnessValidationError,
    division_witness,
    validate_division_witness,
)


def canonical_json(value: object) -> str:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def assert_exact(result: DivisionResolution, p: tuple[int, int], q: tuple[int, int]) -> None:
    re, im = result.exact_value_fractions()
    den = q[0] * q[0] + q[1] * q[1]
    expected_re = Fraction(p[0] * q[0] + p[1] * q[1], den)
    expected_im = Fraction(p[1] * q[0] - p[0] * q[1], den)
    assert (re, im) == (expected_re, expected_im)


def assert_canonical_parity(p: tuple[int, int], q: tuple[int, int]) -> None:
    result = stream_division(p, q).resolve()
    canonical = CanonicalPeriodicExpansion.from_gaussian_fraction(p, q)
    assert result.resolved
    assert result.power_offset == canonical.power_offset
    assert result.prefix_digits == canonical.prefix
    assert result.period_digits == canonical.period
    assert result.exact_value_fractions() == canonical.exact_value_fractions()


def test_public_surface_and_frozen_records() -> None:
    assert DIVISION_WITNESS_SCHEMA == "cnrs-division-witness-v1"
    assert DIVISION_ALGORITHM == "cnrs-gaussian-rational-stream-v1"
    assert list(inspect.signature(stream_division).parameters) == ["numerator", "denominator"]
    assert inspect.signature(stream_division).parameters["denominator"].default == 1
    for cls in (CnrsDivisionStream, DivisionResolution, CycleWitness, DivisionWitness):
        assert is_dataclass(cls)
    stream = stream_division(1)
    with pytest.raises(FrozenInstanceError):
        stream.power_offset = 7


@pytest.mark.parametrize("bad", [True, 1.0, 1 + 0j, (1,), (1, 2, 3), (1, 2.0), "1"])
def test_ambiguous_inputs_are_rejected(bad: object) -> None:
    with pytest.raises(TypeError):
        stream_division(bad)
    with pytest.raises(TypeError):
        stream_division(1, bad)


def test_zero_denominator_and_bounds() -> None:
    with pytest.raises(ZeroDivisionError):
        stream_division(1, 0)
    stream = stream_division(1, 2)
    with pytest.raises(ValueError):
        stream.digit(-1)
    with pytest.raises(ValueError):
        stream.take(-1)
    with pytest.raises(ValueError):
        stream.resolve(max_steps=0)


def test_stream_is_lazy_replayable_and_digit_bounded() -> None:
    stream = stream_division(1, 2)
    assert stream.take(0) == ()
    first = stream.take(64)
    second = tuple(next(it) for it in [iter(stream)] for _ in range(0))
    assert second == ()
    assert tuple(x for _, x in zip(range(64), iter(stream))) == first
    assert tuple(x for _, x in zip(range(64), iter(stream))) == first
    assert all(type(d) is int and 0 <= d <= 4 for d in first)
    assert stream.digit(17) == first[17]


@pytest.mark.parametrize(
    ("p", "q"),
    [
        ((0, 0), (1, 0)),
        ((1, 0), (1, 0)),
        ((-2, -1), (5, 0)),
    ],
)
def test_terminating_cases(p: tuple[int, int], q: tuple[int, int]) -> None:
    result = stream_division(p, q).resolve()
    assert result.status is DivisionStreamStatus.TERMINATING
    assert result.terminates and result.resolved
    assert result.period_digits == ()
    assert_exact(result, p, q)
    assert_canonical_parity(p, q)


def test_periodic_and_shifted_cases() -> None:
    periodic = stream_division(1, 2).resolve()
    assert periodic.status is DivisionStreamStatus.EVENTUALLY_PERIODIC
    assert periodic.period_digits
    assert primitive_period(periodic.period_digits) == periodic.period_digits
    assert_exact(periodic, (1, 0), (2, 0))
    assert_canonical_parity((1, 0), (2, 0))

    shifted = stream_division(1, 5).resolve()
    assert shifted.status is DivisionStreamStatus.EVENTUALLY_PERIODIC
    assert shifted.power_offset < 0
    assert shifted.period_digits
    assert not shifted.terminates
    assert_exact(shifted, (1, 0), (5, 0))
    assert_canonical_parity((1, 0), (5, 0))


def test_gaussian_denominator() -> None:
    p, q = (3, 2), (1, -2)
    result = stream_division(p, q).resolve()
    assert result.resolved
    assert_exact(result, p, q)
    assert_canonical_parity(p, q)


def test_limit_is_honest_and_has_no_witness() -> None:
    result = stream_division(1, 2).resolve(max_steps=1)
    assert result.status is DivisionStreamStatus.LIMIT_REACHED
    assert not result.resolved
    assert not result.terminates
    assert result.witness is None
    with pytest.raises(DivisionSearchLimitError):
        result.to_witness()
    with pytest.raises(DivisionSearchLimitError):
        division_witness(1, 2, max_steps=1)

    finite_limit = stream_division(10**30 + 1).resolve(max_steps=1)
    assert finite_limit.status is DivisionStreamStatus.LIMIT_REACHED
    assert not finite_limit.resolved


def test_witness_round_trip_determinism_and_tamper_rejection() -> None:
    first = division_witness((3, 2), (1, -2))
    second = division_witness((3, 2), (1, -2))
    assert canonical_json(first) == canonical_json(second)
    payload = json.loads(canonical_json(first))
    validated = validate_division_witness(payload)
    assert canonical_json(validated) == canonical_json(first)
    payload["prefix_digits"][0] = (payload["prefix_digits"][0] + 1) % 5
    with pytest.raises(WitnessValidationError):
        validate_division_witness(payload)


def test_equivalent_fraction_witnesses_normalize_identically() -> None:
    a = division_witness(1, 2)
    b = division_witness(-1, -2)
    c = division_witness((2, 0), (4, 0))
    assert canonical_json(a) == canonical_json(b) == canonical_json(c)


def parity_corpus() -> list[tuple[tuple[int, int], tuple[int, int]]]:
    denominators = [
        (1, 0), (2, 0), (3, 0), (5, 0), (10, 0),
        (1, 1), (1, -1), (-1, 2), (2, 1), (-2, -1),
    ]
    numerators = [(n, m) for n in range(-5, 6) for m in (-2, 0, 2)]
    return [(p, q) for p in numerators for q in denominators][:120]


def test_at_least_one_hundred_deterministic_canonical_parity_cases() -> None:
    cases = parity_corpus()
    assert len(cases) >= 100
    for p, q in cases:
        assert_canonical_parity(p, q)
