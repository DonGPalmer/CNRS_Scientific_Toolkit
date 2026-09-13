"""Deterministic witnesses for exact CNRS streaming division."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from .streaming_division import (
    CycleWitness, DivisionResolution, DivisionSearchLimitError,
    DivisionStreamStatus, GaussianInt, stream_division,
)

DIVISION_WITNESS_SCHEMA = "cnrs-division-witness-v1"
DIVISION_ALGORITHM = "cnrs-gaussian-rational-stream-v1"


class WitnessValidationError(ValueError):
    """Raised when a supplied witness is malformed or mathematically invalid."""


@dataclass(frozen=True)
class DivisionWitness:
    schema: str
    algorithm: str
    base: tuple[int, int]
    numerator: tuple[int, int]
    denominator: tuple[int, int]
    power_offset: int
    status: DivisionStreamStatus
    prefix_digits: tuple[int, ...]
    period_digits: tuple[int, ...]
    steps: int
    cycle: CycleWitness | None
    exact_value: tuple[tuple[int, int], tuple[int, int]]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "algorithm": self.algorithm,
            "base": list(self.base),
            "numerator": list(self.numerator),
            "denominator": list(self.denominator),
            "power_offset": self.power_offset,
            "status": self.status.value,
            "prefix_digits": list(self.prefix_digits),
            "period_digits": list(self.period_digits),
            "steps": self.steps,
            "cycle": None if self.cycle is None else self.cycle.to_dict(),
            "exact_value": {
                "real": list(self.exact_value[0]),
                "imaginary": list(self.exact_value[1]),
            },
        }


def _fraction_pair(value: Fraction) -> tuple[int, int]:
    return (value.numerator, value.denominator)


def _witness_from_resolution(result: DivisionResolution) -> DivisionWitness:
    if not result.resolved:
        raise DivisionSearchLimitError(
            "cannot create a witness when the search limit was reached"
        )
    real, imaginary = result.exact_value_fractions()
    return DivisionWitness(
        DIVISION_WITNESS_SCHEMA, DIVISION_ALGORITHM, (-2, 1),
        result.numerator, result.denominator, result.power_offset,
        result.status, result.prefix_digits, result.period_digits,
        result.steps, result.witness,
        (_fraction_pair(real), _fraction_pair(imaginary)),
    )


def division_witness(
    numerator: GaussianInt,
    denominator: GaussianInt = 1,
    *,
    max_steps: int = 100_000,
) -> DivisionWitness:
    """Resolve an exact stream and return its deterministic witness."""
    return stream_division(numerator, denominator).resolve(max_steps).to_witness()


def _pair(value: object, field: str) -> tuple[int, int]:
    if (
        isinstance(value, (list, tuple)) and len(value) == 2
        and type(value[0]) is int and type(value[1]) is int
    ):
        return (value[0], value[1])
    raise WitnessValidationError(f"{field} must be a two-integer array")


def _digits(value: object, field: str) -> tuple[int, ...]:
    if not isinstance(value, (list, tuple)):
        raise WitnessValidationError(f"{field} must be an array")
    if any(type(d) is not int or d < 0 or d > 4 for d in value):
        raise WitnessValidationError(f"{field} contains an invalid digit")
    return tuple(value)


def _from_mapping(payload: Mapping[str, object]) -> DivisionWitness:
    try:
        exact = payload["exact_value"]
        if not isinstance(exact, Mapping):
            raise WitnessValidationError("exact_value must be an object")
        cycle_data = payload["cycle"]
        cycle = None
        if cycle_data is not None:
            if not isinstance(cycle_data, Mapping):
                raise WitnessValidationError("cycle must be an object or null")
            cycle = CycleWitness(
                int(cycle_data["first_state_index"]),
                int(cycle_data["repeated_state_index"]),
                _pair(cycle_data["repeated_state"], "cycle.repeated_state"),
            )
        return DivisionWitness(
            str(payload["schema"]), str(payload["algorithm"]),
            _pair(payload["base"], "base"),
            _pair(payload["numerator"], "numerator"),
            _pair(payload["denominator"], "denominator"),
            int(payload["power_offset"]),
            DivisionStreamStatus(str(payload["status"])),
            _digits(payload["prefix_digits"], "prefix_digits"),
            _digits(payload["period_digits"], "period_digits"),
            int(payload["steps"]), cycle,
            (
                _pair(exact["real"], "exact_value.real"),
                _pair(exact["imaginary"], "exact_value.imaginary"),
            ),
        )
    except WitnessValidationError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise WitnessValidationError(f"malformed division witness: {exc}") from exc


def validate_division_witness(
    witness: DivisionWitness | Mapping[str, object],
) -> DivisionWitness:
    """Recompute and validate all mathematical fields of a witness."""
    supplied = witness if isinstance(witness, DivisionWitness) else _from_mapping(witness)
    if supplied.schema != DIVISION_WITNESS_SCHEMA:
        raise WitnessValidationError("unsupported witness schema")
    if supplied.algorithm != DIVISION_ALGORITHM:
        raise WitnessValidationError("unsupported division algorithm")
    if supplied.base != (-2, 1):
        raise WitnessValidationError("unexpected CNRS base")
    try:
        expected = division_witness(
            supplied.numerator, supplied.denominator,
            max_steps=max(1, supplied.steps + 1),
        )
    except (TypeError, ValueError, ZeroDivisionError, DivisionSearchLimitError) as exc:
        raise WitnessValidationError(f"witness recurrence is invalid: {exc}") from exc
    if supplied != expected:
        raise WitnessValidationError(
            "witness does not match the recomputed exact division"
        )
    return expected


__all__ = [
    "DIVISION_WITNESS_SCHEMA", "DIVISION_ALGORITHM", "CycleWitness",
    "DivisionWitness", "WitnessValidationError", "division_witness",
    "validate_division_witness",
]

