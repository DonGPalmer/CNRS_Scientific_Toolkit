"""Dedicated v0.18 exact finite-string addition/subtraction tests."""
from __future__ import annotations

import hashlib
import inspect
import json
import random

import pytest

import cnrs
from cnrs.cnrs_add import ADDITION_TABLE, CARRY_SET, CARRY_SET_PAIRS, add_cnrs
from cnrs.cnrs_ops import cnrs_add, cnrs_neg, cnrs_sub
from cnrs.validation.exact_addition_subtraction_oracle import (
    exact_difference_value,
    exact_negated_value,
    exact_string_value,
    exact_sum_value,
)
from cnrs.validation.v017_addition_subtraction_baseline import (
    legacy_add_cnrs,
    legacy_cnrs_neg,
    legacy_cnrs_sub,
)

TRANSITION_SHA256 = "b68818cdb0766aead9993639ca2f1b96351371154c94453e730bf9a67a0746ee"


def test_public_signatures_exports_and_constants_are_frozen():
    assert str(inspect.signature(add_cnrs)) == "(a: 'str', b: 'str') -> 'str'"
    assert str(inspect.signature(cnrs_add)) == "(a: 'str', b: 'str') -> 'str'"
    assert str(inspect.signature(cnrs_neg)) == "(a: 'str') -> 'str'"
    assert str(inspect.signature(cnrs_sub)) == "(a: 'str', b: 'str') -> 'str'"
    assert cnrs.add_cnrs is add_cnrs
    assert cnrs.cnrs_add is cnrs_add
    assert cnrs.cnrs_neg is cnrs_neg
    assert cnrs.cnrs_sub is cnrs_sub
    assert isinstance(CARRY_SET_PAIRS, list) and len(CARRY_SET_PAIRS) == 14
    assert isinstance(CARRY_SET, list) and CARRY_SET == [complex(*pair) for pair in CARRY_SET_PAIRS]
    assert isinstance(ADDITION_TABLE, dict) and len(ADDITION_TABLE) == 350


def test_exact_transition_identity_and_drain_bound():
    payload = {
        "carry_set_pairs": CARRY_SET_PAIRS,
        "transitions": [
            (*key, *value) for key, value in sorted(ADDITION_TABLE.items())
        ],
    }
    encoded = json.dumps(payload, separators=(",", ":")).encode()
    assert hashlib.sha256(encoded).hexdigest() == TRANSITION_SHA256
    assert max(
        _drain_length(index) for index in range(len(CARRY_SET_PAIRS))
    ) == 5


def _drain_length(index: int) -> int:
    steps = 0
    while index:
        _, index = ADDITION_TABLE[(index, 0, 0)]
        steps += 1
        assert steps <= 20
    return steps


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("0", "0", "0"), ("1", "2", "3"), ("4", "4", "1313"),
        ("10", "1", "11"), (".1", ".1", "0.2"), ("1", ".1", "1.1"),
        ("23.1", "4.3", "1332.4"), ("0001", "1.", "2"), (".4", "4.", "4.4"),
    ],
)
def test_fixed_addition_vectors(left, right, expected):
    assert add_cnrs(left, right) == expected
    assert add_cnrs(right, left) == expected
    assert cnrs_add(left, right) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("0", "0"), ("1", "144"), ("2", "143"), ("4", "141"),
     ("10", "1440"), (".1", "14.4"), (".4", "14.1"), ("23.1", "1441.4")],
)
def test_fixed_negation_vectors(value, expected):
    assert cnrs_neg(value) == expected
    assert exact_string_value(expected) == exact_negated_value(value)


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [("0", "0", "0"), ("1", "2", "144"), ("4", "4", "0"),
     ("10", "1", "13204"), ("1", ".1", "1320.4"), (".1", ".1", "0"),
     ("23.1", "4.3", "33.3"), ("0001", "1.", "0"), (".4", "4.", "141.4")],
)
def test_fixed_subtraction_vectors(left, right, expected):
    assert cnrs_sub(left, right) == expected
    assert exact_string_value(expected) == exact_difference_value(left, right)


def test_deterministic_random_exactness_and_addition_parity():
    rng = random.Random(20260922)
    for _ in range(10_000):
        left = _random_spelling(rng)
        right = _random_spelling(rng)
        addition = add_cnrs(left, right)
        negation = cnrs_neg(left)
        subtraction = cnrs_sub(left, right)
        assert addition == legacy_add_cnrs(left, right)
        assert exact_string_value(addition) == exact_sum_value(left, right)
        assert exact_string_value(negation) == exact_negated_value(left)
        assert exact_string_value(subtraction) == exact_difference_value(left, right)


def _random_spelling(rng: random.Random) -> str:
    digits = "".join(str(rng.randrange(5)) for _ in range(rng.randint(1, 24)))
    position = rng.randrange(len(digits) + 2)
    if position == len(digits) + 1:
        return digits
    return digits[:position] + "." + digits[position:]


def test_long_inputs_and_algebraic_laws():
    samples = ["4" * 1000, ("40" * 500), "." + "1234" * 250]
    for value in samples:
        canonical = add_cnrs(value, "0")
        assert exact_string_value(canonical) == exact_string_value(value)
        assert add_cnrs(value, cnrs_neg(value)) == "0"
        assert cnrs_sub(value, value) == "0"


@pytest.mark.parametrize("value", ["", ".", "5", "-1", "+1", " 1", "1 ", "1e2"])
def test_out_of_contract_negation_parity(value):
    try:
        expected = ("return", legacy_cnrs_neg(value))
    except Exception as error:  # noqa: BLE001 - parity includes exact exception types
        expected = ("raise", type(error))
    try:
        observed = ("return", cnrs_neg(value))
    except Exception as error:  # noqa: BLE001
        observed = ("raise", type(error))
    assert observed == expected


def test_correction_vectors_differ_only_when_baseline_is_inexact():
    for value in [".1", ".4", "23.1"]:
        assert cnrs_neg(value) != legacy_cnrs_neg(value)
        assert exact_string_value(cnrs_neg(value)) == exact_negated_value(value)
    for left, right in [(".1", ".1"), ("1", ".1"), ("23.1", "4.3")]:
        assert cnrs_sub(left, right) != legacy_cnrs_sub(left, right)
        assert exact_string_value(cnrs_sub(left, right)) == exact_difference_value(left, right)
