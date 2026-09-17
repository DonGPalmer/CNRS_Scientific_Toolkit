"""Dedicated tests for the v0.16 exact finite-string multiplication bridge."""
from __future__ import annotations

import inspect
import random

import pytest

import cnrs
from cnrs.cnrs_mul import mul_cnrs
from cnrs.finite_sequence import CNRSFiniteSequence
from cnrs.finite_string import (
    cnrs_string_to_finite_sequence,
    finite_sequence_to_cnrs_string,
)
from cnrs.validation.exact_string_oracle import (
    exact_product_value,
    exact_string_value,
)
from cnrs.validation.legacy_string_multiplication import legacy_mul_cnrs


@pytest.mark.parametrize(
    ("text", "coefficients", "offset", "canonical"),
    [
        ("0", (), 0, "0"),
        ("0012", ((2, 0), (1, 0)), 0, "12"),
        ("23.1", ((1, 0), (3, 0), (2, 0)), -1, "23.1"),
        (".1", ((1, 0),), -1, "0.1"),
        ("1.", ((1, 0),), 0, "1"),
        ("0.010", ((1, 0),), -2, "0.01"),
    ],
)
def test_frozen_parse_examples(text, coefficients, offset, canonical):
    parsed = cnrs_string_to_finite_sequence(text)
    assert parsed == CNRSFiniteSequence(coefficients, offset)
    assert finite_sequence_to_cnrs_string(parsed) == canonical


@pytest.mark.parametrize(
    "value",
    ["", ".", "5", "-1", "+1", " 1", "1 ", "1e2", "1..2", "1.2.3"],
)
def test_parser_rejects_malformed_strings(value):
    with pytest.raises(ValueError):
        cnrs_string_to_finite_sequence(value)


@pytest.mark.parametrize("value", [None, 1, 1.0, True, b"1"])
def test_parser_rejects_non_strings(value):
    with pytest.raises(TypeError):
        cnrs_string_to_finite_sequence(value)


@pytest.mark.parametrize(
    ("sequence", "text"),
    [
        (CNRSFiniteSequence(()), "0"),
        (CNRSFiniteSequence((1,), 2), "100"),
        (CNRSFiniteSequence((1,), -3), "0.001"),
        (CNRSFiniteSequence((1, 0, 2), -1), "20.1"),
    ],
)
def test_frozen_format_examples(sequence, text):
    assert finite_sequence_to_cnrs_string(sequence) == text


def test_formatter_accepts_subclasses_and_rejects_non_digits():
    class Derived(CNRSFiniteSequence):
        pass

    assert finite_sequence_to_cnrs_string(Derived((4,), 1)) == "40"
    with pytest.raises(TypeError):
        finite_sequence_to_cnrs_string((1,))
    for coefficient in ((5, 0), (-1, 0), (1, 1)):
        with pytest.raises(ValueError):
            finite_sequence_to_cnrs_string(CNRSFiniteSequence((coefficient,)))


def test_public_signatures_and_exports_are_frozen():
    assert str(inspect.signature(cnrs_string_to_finite_sequence)) == (
        "(value: 'str') -> 'CNRSFiniteSequence'"
    )
    assert str(inspect.signature(finite_sequence_to_cnrs_string)) == (
        "(value: 'CNRSFiniteSequence') -> 'str'"
    )
    assert str(inspect.signature(mul_cnrs)) == "(a: 'str', b: 'str') -> 'str'"
    assert cnrs.cnrs_string_to_finite_sequence is cnrs_string_to_finite_sequence
    assert cnrs.finite_sequence_to_cnrs_string is finite_sequence_to_cnrs_string
    assert "cnrs_string_to_finite_sequence" in cnrs.__all__
    assert "finite_sequence_to_cnrs_string" in cnrs.__all__


def test_exact_route_matches_independent_value_and_legacy_output():
    rng = random.Random(20260917)
    for _ in range(1000):
        left = "".join(str(rng.randrange(5)) for _ in range(rng.randint(1, 20)))
        right = "".join(str(rng.randrange(5)) for _ in range(rng.randint(1, 20)))
        left_point = rng.randrange(len(left) + 1)
        right_point = rng.randrange(len(right) + 1)
        if left_point < len(left):
            left = left[:left_point] + "." + left[left_point:]
        if right_point < len(right):
            right = right[:right_point] + "." + right[right_point:]
        result = mul_cnrs(left, right)
        assert result == legacy_mul_cnrs(left, right)
        assert exact_string_value(result) == exact_product_value(left, right)


def test_long_all_four_stress_parity():
    operand = "4" * 300
    assert mul_cnrs(operand, operand) == legacy_mul_cnrs(operand, operand)

