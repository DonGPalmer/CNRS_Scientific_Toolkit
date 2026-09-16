"""Exact canonical base ``-2+i`` normalization for finite Laurent sequences."""
from __future__ import annotations

from .finite_sequence import CNRSFiniteSequence
from .gaussian_types import GaussianInteger
from .gaussian_valuation import BETA, gadd, gdiv_exact, gsub

_ZERO: GaussianInteger = (0, 0)


class NormalizationLimitError(RuntimeError):
    """The permitted post-input carry-drain count was exhausted."""


def validate_carry_limit(max_carry_steps: int | None) -> None:
    if max_carry_steps is not None and type(max_carry_steps) is not int:
        raise TypeError("max_carry_steps must be None or a nonnegative exact int")
    if max_carry_steps is not None and max_carry_steps < 0:
        raise ValueError("max_carry_steps must be nonnegative")


def _step(total: GaussianInteger) -> tuple[GaussianInteger, GaussianInteger]:
    x, y = total
    digit = (x + 2 * y) % 5
    emitted = (digit, 0)
    return emitted, gdiv_exact(gsub(total, emitted), BETA)


def normalize_gaussian_laurent(
    value: CNRSFiniteSequence,
    *,
    max_carry_steps: int | None = None,
) -> CNRSFiniteSequence:
    if not isinstance(value, CNRSFiniteSequence):
        raise TypeError("value must be a CNRSFiniteSequence")
    validate_carry_limit(max_carry_steps)
    if not value.coefficients:
        return CNRSFiniteSequence(())

    output: list[GaussianInteger] = []
    carry = _ZERO
    for coefficient in value.coefficients:
        emitted, carry = _step(gadd(coefficient, carry))
        output.append(emitted)

    drained = 0
    while carry != _ZERO:
        if max_carry_steps is not None and drained == max_carry_steps:
            raise NormalizationLimitError(
                "post-input carry-drain limit exhausted"
            )
        emitted, carry = _step(carry)
        output.append(emitted)
        drained += 1
    return CNRSFiniteSequence(output, value.offset)


__all__ = [
    "NormalizationLimitError",
    "normalize_gaussian_laurent",
    "validate_carry_limit",
]
