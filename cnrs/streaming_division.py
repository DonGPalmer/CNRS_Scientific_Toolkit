"""Lazy exact CNRS division for Gaussian-rational inputs.

The stream recurrence is evaluated entirely with Gaussian integers.
Construction does not resolve or materialize the expansion.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Iterator, TypeAlias

from .canonical_periodic import CanonicalPeriodicExpansion, primitive_period
from .gaussian_valuation import (
    BETA, Gaussian, gdiv_exact, gnorm, gsub, gaussian_valuation,
    reduce_gaussian_fraction,
)

GaussianInt: TypeAlias = int | tuple[int, int]


class DivisionSearchLimitError(RuntimeError):
    """Raised when a mathematical witness is requested before resolution."""


class DivisionStreamStatus(str, Enum):
    TERMINATING = "terminating"
    EVENTUALLY_PERIODIC = "eventually_periodic"
    LIMIT_REACHED = "limit_reached"


@dataclass(frozen=True)
class CycleWitness:
    """Exact state-repetition evidence for an eventually-periodic tail."""

    first_state_index: int
    repeated_state_index: int
    repeated_state: Gaussian

    def to_dict(self) -> dict[str, object]:
        return {
            "first_state_index": self.first_state_index,
            "repeated_state_index": self.repeated_state_index,
            "repeated_state": list(self.repeated_state),
        }


def _as_gaussian(value: GaussianInt, parameter: str) -> Gaussian:
    if isinstance(value, bool):
        raise TypeError(f"{parameter} must be an int or a pair of ints")
    if isinstance(value, int):
        return (value, 0)
    if (
        isinstance(value, tuple)
        and len(value) == 2
        and type(value[0]) is int
        and type(value[1]) is int
    ):
        return value
    raise TypeError(f"{parameter} must be an int or a pair of ints")


def _phi(value: Gaussian) -> int:
    return (value[0] + 2 * value[1]) % 5


def _residual_denominator(denominator: Gaussian) -> tuple[int, Gaussian]:
    exponent = gaussian_valuation(denominator, BETA)
    residual = denominator
    for _ in range(exponent):
        residual = gdiv_exact(residual, BETA)
    return exponent, residual


def _integer_digits(value: Gaussian) -> Iterator[int]:
    if value == (0, 0):
        yield 0
        return
    state = value
    while state != (0, 0):
        digit = _phi(state)
        yield digit
        state = gdiv_exact(gsub(state, (digit, 0)), BETA)


def _periodic_digits(numerator: Gaussian, denominator: Gaussian) -> Iterator[int]:
    inverse = pow(_phi(denominator), -1, 5)
    state = numerator
    while True:
        digit = (_phi(state) * inverse) % 5
        yield digit
        state = gdiv_exact(
            gsub(state, (digit * denominator[0], digit * denominator[1])),
            BETA,
        )


@dataclass(frozen=True)
class DivisionResolution:
    status: DivisionStreamStatus
    numerator: Gaussian
    denominator: Gaussian
    power_offset: int
    prefix_digits: tuple[int, ...]
    period_digits: tuple[int, ...]
    steps: int
    witness: CycleWitness | None

    @property
    def terminates(self) -> bool:
        return self.status is DivisionStreamStatus.TERMINATING

    @property
    def resolved(self) -> bool:
        return self.status is not DivisionStreamStatus.LIMIT_REACHED

    @property
    def preperiod_length(self) -> int:
        return len(self.prefix_digits)

    @property
    def period_length(self) -> int:
        return len(self.period_digits)

    def exact_value_fractions(self) -> tuple[Fraction, Fraction]:
        if not self.resolved:
            raise DivisionSearchLimitError(
                "exact value requires a terminating or eventually-periodic resolution"
            )
        return CanonicalPeriodicExpansion(
            self.power_offset, self.prefix_digits, self.period_digits
        ).exact_value_fractions()

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "numerator": list(self.numerator),
            "denominator": list(self.denominator),
            "power_offset": self.power_offset,
            "prefix_digits": list(self.prefix_digits),
            "period_digits": list(self.period_digits),
            "steps": self.steps,
            "witness": None if self.witness is None else self.witness.to_dict(),
        }

    def to_witness(self):
        if not self.resolved:
            raise DivisionSearchLimitError(
                "cannot create a witness when the search limit was reached"
            )
        from .witnesses import _witness_from_resolution
        return _witness_from_resolution(self)


@dataclass(frozen=True)
class CnrsDivisionStream:
    numerator: Gaussian
    denominator: Gaussian
    power_offset: int

    def _components(self) -> tuple[Gaussian, Gaussian]:
        exponent, residual = _residual_denominator(self.denominator)
        if -exponent != self.power_offset:
            raise AssertionError("inconsistent normalized power offset")
        return self.numerator, residual

    def __iter__(self) -> Iterator[int]:
        numerator, residual = self._components()
        if gnorm(residual) == 1:
            yield from _integer_digits(gdiv_exact(numerator, residual))
            return
        yield from _periodic_digits(numerator, residual)

    def digit(self, index: int) -> int:
        if type(index) is not int or index < 0:
            raise ValueError("index must be a nonnegative integer")
        for position, digit in enumerate(self):
            if position == index:
                return digit
        raise IndexError("digit index lies beyond the terminating expansion")

    def take(self, count: int) -> tuple[int, ...]:
        if type(count) is not int or count < 0:
            raise ValueError("count must be a nonnegative integer")
        iterator = iter(self)
        digits: list[int] = []
        for _ in range(count):
            try:
                digits.append(next(iterator))
            except StopIteration:
                break
        return tuple(digits)

    def resolve(self, max_steps: int = 100_000) -> DivisionResolution:
        if type(max_steps) is not int or max_steps <= 0:
            raise ValueError("max_steps must be a positive integer")
        numerator, residual = self._components()

        if gnorm(residual) == 1:
            state = gdiv_exact(numerator, residual)
            if state == (0, 0):
                return DivisionResolution(
                    DivisionStreamStatus.TERMINATING, self.numerator,
                    self.denominator, self.power_offset, (0,), (), 1, None,
                )
            digits: list[int] = []
            for _ in range(max_steps):
                digit = _phi(state)
                digits.append(digit)
                state = gdiv_exact(gsub(state, (digit, 0)), BETA)
                if state == (0, 0):
                    return DivisionResolution(
                        DivisionStreamStatus.TERMINATING, self.numerator,
                        self.denominator, self.power_offset, tuple(digits), (),
                        len(digits), None,
                    )
            return DivisionResolution(
                DivisionStreamStatus.LIMIT_REACHED, self.numerator,
                self.denominator, self.power_offset, tuple(digits), (),
                len(digits), None,
            )

        inverse = pow(_phi(residual), -1, 5)
        state = numerator
        seen: dict[Gaussian, int] = {}
        digits: list[int] = []
        for _ in range(max_steps):
            if state == (0, 0):
                return DivisionResolution(
                    DivisionStreamStatus.TERMINATING, self.numerator,
                    self.denominator, self.power_offset, tuple(digits) or (0,),
                    (), len(digits), None,
                )
            if state in seen:
                first = seen[state]
                period = primitive_period(digits[first:])
                return DivisionResolution(
                    DivisionStreamStatus.EVENTUALLY_PERIODIC, self.numerator,
                    self.denominator, self.power_offset, tuple(digits[:first]),
                    period, len(digits), CycleWitness(first, len(digits), state),
                )
            seen[state] = len(digits)
            digit = (_phi(state) * inverse) % 5
            digits.append(digit)
            state = gdiv_exact(
                gsub(state, (digit * residual[0], digit * residual[1])), BETA
            )

        return DivisionResolution(
            DivisionStreamStatus.LIMIT_REACHED, self.numerator,
            self.denominator, self.power_offset, tuple(digits), (),
            len(digits), None,
        )


def stream_division(
    numerator: GaussianInt,
    denominator: GaussianInt = 1,
) -> CnrsDivisionStream:
    """Construct a lazy, replayable exact Gaussian-rational digit stream."""
    p = _as_gaussian(numerator, "numerator")
    q = _as_gaussian(denominator, "denominator")
    reduced_p, reduced_q = reduce_gaussian_fraction(p, q)
    exponent, _ = _residual_denominator(reduced_q)
    return CnrsDivisionStream(reduced_p, reduced_q, -exponent)


__all__ = [
    "GaussianInt", "DivisionSearchLimitError", "DivisionStreamStatus",
    "CycleWitness", "DivisionResolution", "CnrsDivisionStream",
    "stream_division",
]
