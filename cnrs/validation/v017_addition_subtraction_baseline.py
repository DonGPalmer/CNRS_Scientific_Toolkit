"""Frozen, validation-only v0.17 addition, negation, and subtraction oracle."""
from __future__ import annotations

_BASE = complex(-2, 1)
_CARRY_PAIRS = (
    (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1),
    (-2, 0), (2, 1), (-2, -1), (-2, -2), (2, 2), (-3, -1), (-3, -2),
)
_CARRIES = tuple(complex(real, imag) for real, imag in _CARRY_PAIRS)
_CARRY_INDEX = {pair: index for index, pair in enumerate(_CARRY_PAIRS)}


def _normalize(value: str) -> str:
    integer, separator, fractional = value.partition(".")
    integer = integer.lstrip("0") or "0"
    fractional = fractional.rstrip("0")
    return integer + "." + fractional if separator and fractional else integer


def _remainder(value: complex) -> int:
    for digit in range(5):
        quotient = (value - digit) / _BASE
        if abs(quotient.real - round(quotient.real)) < 1e-12 and abs(
            quotient.imag - round(quotient.imag)
        ) < 1e-12:
            return digit
    raise ValueError(f"No CNRS remainder exists for {value}")


def _addition_table() -> dict[tuple[int, int, int], tuple[int, int]]:
    table = {}
    for carry_index, carry in enumerate(_CARRIES):
        for left in range(5):
            for right in range(5):
                raw = carry + left + right
                digit = _remainder(raw)
                next_carry = (raw - digit) / _BASE
                pair = (int(round(next_carry.real)), int(round(next_carry.imag)))
                table[(carry_index, left, right)] = (digit, _CARRY_INDEX[pair])
    return table


_ADDITION_TABLE = _addition_table()


def legacy_add_cnrs(left: str, right: str) -> str:
    left_integer, _, left_fractional = left.partition(".")
    right_integer, _, right_fractional = right.partition(".")
    fractional_length = max(len(left_fractional), len(right_fractional))
    left_fractional = left_fractional.ljust(fractional_length, "0")
    right_fractional = right_fractional.ljust(fractional_length, "0")
    integer_length = max(len(left_integer), len(right_integer))
    left_digits = left_integer.zfill(integer_length) + left_fractional
    right_digits = right_integer.zfill(integer_length) + right_fractional
    carry_index = 0
    output = []
    for left_digit, right_digit in zip(reversed(left_digits), reversed(right_digits)):
        digit, carry_index = _ADDITION_TABLE[(carry_index, int(left_digit), int(right_digit))]
        output.append(str(digit))
    drain_steps = 0
    while carry_index:
        digit, carry_index = _ADDITION_TABLE[(carry_index, 0, 0)]
        output.append(str(digit))
        drain_steps += 1
        if drain_steps > 20:
            raise RuntimeError("Carry did not drain in CNRS-A addition")
    raw = "".join(reversed(output))
    if fractional_length:
        raw = raw[:-fractional_length] + "." + raw[-fractional_length:]
    return _normalize(raw)


def _to_gaussian(value: str) -> complex:
    integer, separator, fractional = value.partition(".")
    result = 0j
    for character in integer:
        result = result * _BASE + int(character)
    tail = 0j
    if separator:
        for character in reversed(fractional):
            tail = (tail + int(character)) / _BASE
    return result + tail


def _from_gaussian(value: complex, max_digits: int = 10000) -> str:
    current = complex(round(value.real), round(value.imag))
    if current == 0:
        return "0"
    digits = []
    for _ in range(max_digits):
        if current == 0:
            break
        digit = _remainder(current)
        digits.append(digit)
        quotient = (current - digit) / _BASE
        current = complex(round(quotient.real), round(quotient.imag))
    else:
        raise RuntimeError(f"CNRS-A expansion did not terminate for {value}")
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
    return _normalize("".join(str(digit) for digit in reversed(digits)))


def legacy_cnrs_neg(value: str) -> str:
    return _normalize(_from_gaussian(-_to_gaussian(value)))


def legacy_cnrs_sub(left: str, right: str) -> str:
    return legacy_add_cnrs(left, legacy_cnrs_neg(right))


__all__ = ["legacy_add_cnrs", "legacy_cnrs_neg", "legacy_cnrs_sub"]
