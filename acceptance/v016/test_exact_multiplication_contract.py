"""Executable acceptance contract for v0.16 exact string multiplication."""
from __future__ import annotations

from itertools import product
import random

from cnrs.cnrs_mul import mul_cnrs
from cnrs.finite_string import (
    cnrs_string_to_finite_sequence,
    finite_sequence_to_cnrs_string,
)
from cnrs.validation.exact_string_oracle import (
    exact_product_value,
    exact_string_value,
)
from cnrs.validation.legacy_string_multiplication import legacy_mul_cnrs


def _forms(digits: str) -> set[str]:
    forms = {digits}
    for position in range(len(digits) + 1):
        forms.add(digits[:position] + "." + digits[position:])
    return forms


def _canonicalize(value: str) -> str:
    integer, separator, fractional = value.partition(".")
    integer = integer.lstrip("0") or "0"
    fractional = fractional.rstrip("0") if separator else ""
    return integer + ("." + fractional if fractional else "")


def _all_strings(max_digits: int) -> set[str]:
    values: set[str] = set()
    for length in range(1, max_digits + 1):
        for digits in product("01234", repeat=length):
            values.update(_forms("".join(digits)))
    return values


def _canonical_strings(max_digits: int) -> tuple[str, ...]:
    return tuple(sorted({_canonicalize(value) for value in _all_strings(max_digits)}))


def _random_string(rng: random.Random, max_digits: int = 40) -> str:
    digits = "".join(str(rng.randrange(5)) for _ in range(rng.randint(1, max_digits)))
    position = rng.randrange(len(digits) + 1)
    return digits if position == len(digits) else digits[:position] + "." + digits[position:]


def test_a04_exhaustive_round_trip_laws_through_four_digits():
    for value in _all_strings(4):
        parsed = cnrs_string_to_finite_sequence(value)
        canonical = finite_sequence_to_cnrs_string(parsed)
        assert canonical == _canonicalize(value)
        assert cnrs_string_to_finite_sequence(canonical) == parsed


def test_a04_randomized_long_round_trips():
    rng = random.Random(2026091701)
    for _ in range(5000):
        value = _random_string(rng)
        parsed = cnrs_string_to_finite_sequence(value)
        assert finite_sequence_to_cnrs_string(parsed) == _canonicalize(value)


def test_a05_a06_exhaustive_exact_value_and_historical_parity():
    values = _canonical_strings(3)
    for left, right in product(values, repeat=2):
        result = mul_cnrs(left, right)
        assert exact_string_value(result) == exact_product_value(left, right)
        assert result == legacy_mul_cnrs(left, right)


def test_a05_a06_randomized_exact_value_and_historical_parity():
    rng = random.Random(2026091702)
    for _ in range(5000):
        left = _random_string(rng)
        right = _random_string(rng)
        result = mul_cnrs(left, right)
        assert exact_string_value(result) == exact_product_value(left, right)
        assert result == legacy_mul_cnrs(left, right)


def test_a06_existing_vectors_and_long_all_four_input():
    vectors = (
        ("0", "0"),
        ("0", "444"),
        ("1", "1"),
        ("4", "4"),
        ("104", "23.1"),
        (".1", "1."),
        ("444444", "444444"),
        ("4" * 300, "4" * 300),
    )
    for left, right in vectors:
        result = mul_cnrs(left, right)
        assert result == legacy_mul_cnrs(left, right)
        assert exact_string_value(result) == exact_product_value(left, right)

