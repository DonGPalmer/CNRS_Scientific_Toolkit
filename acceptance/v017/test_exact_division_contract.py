"""Executable acceptance contract for v0.17 exact string division."""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import gcd
import random

from cnrs import (
    DivisionStreamStatus,
    divide_cnrs_exact,
    validate_division_witness,
)
from cnrs.canonical_periodic import CanonicalPeriodicExpansion, primitive_period
from cnrs.validation.exact_division_oracle import (
    exact_quotient_value,
    exact_string_value,
)

Pair = tuple[int, int]
FractionPair = tuple[Fraction, Fraction]
_BETA: Pair = (-2, 1)


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


def _result_fraction(result) -> FractionPair:
    a, b = result.numerator
    c, d = result.denominator
    norm = c * c + d * d
    return Fraction(a * c + b * d, norm), Fraction(b * c - a * d, norm)


def _gsub(a: Pair, b: Pair) -> Pair:
    return a[0] - b[0], a[1] - b[1]


def _gmul(a: Pair, b: Pair) -> Pair:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def _gnorm(a: Pair) -> int:
    return a[0] * a[0] + a[1] * a[1]


def _nearest(num: int, den: int) -> int:
    return (2 * num + den) // (2 * den) if num >= 0 else -(
        (2 * (-num) + den) // (2 * den)
    )


def _gdivmod(a: Pair, b: Pair) -> tuple[Pair, Pair]:
    norm = _gnorm(b)
    product = _gmul(a, (b[0], -b[1]))
    quotient = _nearest(product[0], norm), _nearest(product[1], norm)
    return quotient, _gsub(a, _gmul(quotient, b))


def _ggcd(a: Pair, b: Pair) -> Pair:
    while b != (0, 0):
        _, remainder = _gdivmod(a, b)
        a, b = b, remainder
    return a


def _gdiv_exact(a: Pair, b: Pair) -> Pair:
    product = _gmul(a, (b[0], -b[1]))
    norm = _gnorm(b)
    assert product[0] % norm == 0 and product[1] % norm == 0
    return product[0] // norm, product[1] // norm


def _divides(divisor: Pair, value: Pair) -> bool:
    product = _gmul(value, (divisor[0], -divisor[1]))
    norm = _gnorm(divisor)
    return product[0] % norm == 0 and product[1] % norm == 0


def _independent_terminates(value: FractionPair) -> bool:
    real, imaginary = value
    common = real.denominator * imaginary.denominator // gcd(
        real.denominator, imaginary.denominator
    )
    numerator = int(real * common), int(imaginary * common)
    denominator = (common, 0)
    divisor = _ggcd(numerator, denominator)
    numerator = _gdiv_exact(numerator, divisor)
    denominator = _gdiv_exact(denominator, divisor)
    while _divides(_BETA, denominator):
        denominator = _gdiv_exact(denominator, _BETA)
    return _gnorm(denominator) == 1


def _noncanonical_variant(value: str) -> str:
    integer, separator, fractional = value.partition(".")
    if separator:
        return "00" + integer + "." + fractional + "00"
    return "00" + integer + ".00"


def test_a04_exhaustive_and_random_finite_value_conversion() -> None:
    values = _all_strings(4)
    assert len(values) == 4490
    for value in values:
        result = divide_cnrs_exact(value, "1", max_steps=1)
        assert _result_fraction(result) == exact_quotient_value(value, "1")
        if exact_string_value(value) != (Fraction(0), Fraction(0)):
            inverse = divide_cnrs_exact("1", value, max_steps=1)
            assert _result_fraction(inverse) == exact_quotient_value("1", value)

    rng = random.Random(2026091801)
    for _ in range(5000):
        dividend = _random_string(rng)
        divisor = _random_string(rng)
        while exact_string_value(divisor) == (Fraction(0), Fraction(0)):
            divisor = _random_string(rng)
        result = divide_cnrs_exact(dividend, divisor, max_steps=1)
        assert _result_fraction(result) == exact_quotient_value(dividend, divisor)


def test_a05_exhaustive_and_random_exact_quotient_construction() -> None:
    values = _canonical_strings(3)
    assert len(values) == 425
    nonzero = tuple(
        value for value in values
        if exact_string_value(value) != (Fraction(0), Fraction(0))
    )
    checked = 0
    for dividend in values:
        for divisor in nonzero:
            result = divide_cnrs_exact(dividend, divisor, max_steps=1)
            assert _result_fraction(result) == exact_quotient_value(dividend, divisor)
            checked += 1
    assert checked == 180_200

    rng = random.Random(2026091802)
    for _ in range(5000):
        dividend = _random_string(rng, 20)
        divisor = _random_string(rng, 20)
        while exact_string_value(divisor) == (Fraction(0), Fraction(0)):
            divisor = _random_string(rng, 20)
        result = divide_cnrs_exact(dividend, divisor, max_steps=1)
        assert _result_fraction(result) == exact_quotient_value(dividend, divisor)


def test_a06_a07_small_domain_resolution_status_value_and_witness() -> None:
    values = _canonical_strings(2)
    nonzero = tuple(
        value for value in values
        if exact_string_value(value) != (Fraction(0), Fraction(0))
    )
    terminating = periodic = 0
    for dividend in values:
        for divisor in nonzero:
            expected = exact_quotient_value(dividend, divisor)
            result = divide_cnrs_exact(dividend, divisor)
            assert result.resolved
            assert result.exact_value_fractions() == expected
            assert _result_fraction(result) == expected
            assert result.terminates is _independent_terminates(expected)
            canonical = CanonicalPeriodicExpansion.from_gaussian_fraction(
                result.numerator, result.denominator
            )
            assert result.power_offset == canonical.power_offset
            assert result.prefix_digits == canonical.prefix
            assert result.period_digits == canonical.period
            witness = result.to_witness()
            assert validate_division_witness(witness) == witness
            if result.terminates:
                terminating += 1
                assert result.period_digits == ()
            else:
                periodic += 1
                assert primitive_period(result.period_digits) == result.period_digits
                assert result.witness is not None
    assert terminating > 0 and periodic > 0


def test_a08_limit_result_is_replayable_operational_evidence_only() -> None:
    first = divide_cnrs_exact("1", "2", max_steps=1)
    second = divide_cnrs_exact("01.0", "02.00", max_steps=1)
    assert first.to_dict() == second.to_dict()
    assert first.status is DivisionStreamStatus.LIMIT_REACHED
    assert first.steps == 1 and first.prefix_digits == (3,)
    assert first.witness is None and not first.resolved


def test_a09_two_thousand_equivalent_spelling_pairs() -> None:
    rng = random.Random(2026091803)
    values = _canonical_strings(3)
    nonzero = tuple(
        value for value in values
        if exact_string_value(value) != (Fraction(0), Fraction(0))
    )
    for _ in range(2000):
        dividend = rng.choice(values)
        divisor = rng.choice(nonzero)
        canonical = divide_cnrs_exact(dividend, divisor, max_steps=20).to_dict()
        variant = divide_cnrs_exact(
            _noncanonical_variant(dividend),
            _noncanonical_variant(divisor),
            max_steps=20,
        ).to_dict()
        assert canonical == variant


def test_a16_readme_example_contract() -> None:
    terminating = divide_cnrs_exact("1", "10")
    periodic = divide_cnrs_exact("1", "2")
    assert terminating.status is DivisionStreamStatus.TERMINATING
    assert terminating.exact_value_fractions() == (Fraction(-2, 5), Fraction(-1, 5))
    assert periodic.status is DivisionStreamStatus.EVENTUALLY_PERIODIC
    assert periodic.exact_value_fractions() == (Fraction(1, 2), Fraction(0))
    assert validate_division_witness(terminating.to_witness()) == terminating.to_witness()
    assert validate_division_witness(periodic.to_witness()) == periodic.to_witness()
    limited = divide_cnrs_exact("1", "2", max_steps=1)
    assert limited.status is DivisionStreamStatus.LIMIT_REACHED

