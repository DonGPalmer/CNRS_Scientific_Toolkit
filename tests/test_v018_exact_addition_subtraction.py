"""Dedicated v0.18 exact finite-string addition/subtraction tests."""
from __future__ import annotations

import hashlib
import inspect
import json
import random

import pytest

import cnrs
from cnrs.cnrs_add import ADDITION_TABLE, CARRY_SET, CARRY_SET_PAIRS, add_cnrs
from cnrs.cnrs_mul import mul_cnrs
from cnrs.cnrs_ops import cnrs_add, cnrs_neg, cnrs_sub
from cnrs.cnrs_value import CVal
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
LONG_PAIR_SEED = 2026092205
LONG_PAIR_COUNT = 100
LONG_MAX_DIGITS = 1000
LONG_LAW_SEED = 2026092210
LONG_LAW_COUNT = 100
FRACTIONAL_CVAL_VECTORS = (
    (".1", ".4"),
    ("1.2", ".3"),
    ("23.1", "4.3"),
    ("0.004", "12.34"),
)


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


def _long_spelling(rng: random.Random, digit_count: int) -> str:
    digits = "".join(str(rng.randrange(5)) for _ in range(digit_count))
    point = rng.randrange(digit_count + 1)
    if point == 0:
        return "." + digits
    if point == digit_count:
        return digits
    return digits[:point] + "." + digits[point:]


def test_a05_one_hundred_long_input_pairs_to_one_thousand_digits():
    rng = random.Random(LONG_PAIR_SEED)
    observed_lengths = []
    for index in range(LONG_PAIR_COUNT):
        left_length = LONG_MAX_DIGITS if index == 0 else 64 + (index * 37) % 937
        right_length = LONG_MAX_DIGITS if index == 0 else 64 + (index * 53 + 17) % 937
        left = _long_spelling(rng, left_length)
        right = _long_spelling(rng, right_length)
        observed_lengths.extend((left_length, right_length))

        addition = add_cnrs(left, right)
        negation = cnrs_neg(left)
        subtraction = cnrs_sub(left, right)
        assert addition == legacy_add_cnrs(left, right)
        assert exact_string_value(addition) == exact_sum_value(left, right)
        assert exact_string_value(negation) == exact_negated_value(left)
        assert exact_string_value(subtraction) == exact_difference_value(left, right)

    assert len(observed_lengths) == 2 * LONG_PAIR_COUNT
    assert max(observed_lengths) == LONG_MAX_DIGITS
    assert all(64 <= length <= LONG_MAX_DIGITS for length in observed_lengths)


def test_a10_one_hundred_randomized_longer_domain_law_triples():
    rng = random.Random(LONG_LAW_SEED)
    for _ in range(LONG_LAW_COUNT):
        a, b, c = (_long_spelling(rng, 32 + rng.randrange(65)) for _ in range(3))

        ab = add_cnrs(a, b)
        ba = add_cnrs(b, a)
        assert ab == ba == cnrs_add(a, b)
        assert exact_string_value(ab) == exact_sum_value(a, b)

        left_associative = add_cnrs(ab, c)
        right_associative = add_cnrs(a, add_cnrs(b, c))
        assert left_associative == right_associative
        assert exact_string_value(left_associative) == exact_sum_value(ab, c)

        canonical_a = add_cnrs(a, "0")
        assert exact_string_value(canonical_a) == exact_string_value(a)
        assert add_cnrs(a, cnrs_neg(a)) == "0"
        assert cnrs_neg(cnrs_neg(a)) == canonical_a
        assert exact_string_value(cnrs_neg(a)) == exact_negated_value(a)

        difference = cnrs_sub(a, b)
        reverse_difference = cnrs_sub(b, a)
        assert difference == add_cnrs(a, cnrs_neg(b))
        assert difference == cnrs_neg(reverse_difference)
        assert cnrs_sub(a, "0") == canonical_a
        assert cnrs_sub(a, a) == "0"
        assert exact_string_value(difference) == exact_difference_value(a, b)

        distributed_left = mul_cnrs(a, add_cnrs(b, c))
        distributed_right = add_cnrs(mul_cnrs(a, b), mul_cnrs(a, c))
        assert exact_string_value(distributed_left) == exact_string_value(distributed_right)


def test_a13_fractional_direct_and_cval_route_parity():
    assert len(FRACTIONAL_CVAL_VECTORS) >= 4
    for left, right in FRACTIONAL_CVAL_VECTORS:
        direct_negation = cnrs_neg(left)
        cval_negation = (-CVal.from_str(left)).s
        assert direct_negation == cval_negation
        assert exact_string_value(direct_negation) == exact_negated_value(left)

        direct_subtraction = cnrs_sub(left, right)
        cval_subtraction = (CVal.from_str(left) - CVal.from_str(right)).s
        assert direct_subtraction == cval_subtraction
        assert exact_string_value(direct_subtraction) == exact_difference_value(left, right)


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
