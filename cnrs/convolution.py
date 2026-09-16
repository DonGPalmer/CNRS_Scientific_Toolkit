"""Exact finite Gaussian convolution with deterministic product accounting."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator

from .finite_sequence import CNRSFiniteSequence
from .gaussian_normalization import (
    normalize_gaussian_laurent,
    validate_carry_limit,
)
from .gaussian_types import GaussianInteger
from .gaussian_valuation import gadd, gmul


class ConvolutionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    LIMIT_REACHED = "limit_reached"


class ConvolutionLimitError(RuntimeError):
    """The permitted stored-position scalar-product count is insufficient."""


@dataclass(frozen=True)
class ConvolutionProgress:
    status: ConvolutionStatus
    products_completed: int
    products_required: int
    last_pair: tuple[int, int] | None
    result: CNRSFiniteSequence | None


@dataclass(frozen=True)
class MultiplicationResult:
    status: ConvolutionStatus
    products_completed: int
    products_required: int
    raw_convolution: CNRSFiniteSequence | None
    normalized: CNRSFiniteSequence | None
    witness: "ConvolutionWitness | None"


def _require_sequence(value: object, name: str) -> CNRSFiniteSequence:
    if not isinstance(value, CNRSFiniteSequence):
        raise TypeError(f"{name} must be a CNRSFiniteSequence")
    return value


def _validate_limit(max_products: int | None) -> None:
    if max_products is not None and type(max_products) is not int:
        raise TypeError("max_products must be None or a nonnegative exact int")
    if max_products is not None and max_products < 0:
        raise ValueError("max_products must be nonnegative")


def _validate_chunk(chunk_products: int) -> None:
    if type(chunk_products) is not int:
        raise TypeError("chunk_products must be a positive exact int")
    if chunk_products <= 0:
        raise ValueError("chunk_products must be positive")


def _convolution_values(
    left: CNRSFiniteSequence, right: CNRSFiniteSequence
) -> list[GaussianInteger]:
    if not left.coefficients or not right.coefficients:
        return []
    output: list[GaussianInteger] = [
        (0, 0)
        for _ in range(len(left.coefficients) + len(right.coefficients) - 1)
    ]
    for i, left_value in enumerate(left.coefficients):
        for j, right_value in enumerate(right.coefficients):
            output[i + j] = gadd(output[i + j], gmul(left_value, right_value))
    return output


def convolve_exact(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    *,
    max_products: int | None = None,
) -> CNRSFiniteSequence:
    left = _require_sequence(left, "left")
    right = _require_sequence(right, "right")
    _validate_limit(max_products)
    required = len(left.coefficients) * len(right.coefficients)
    if max_products is not None and required > max_products:
        raise ConvolutionLimitError(
            f"convolution requires {required} products; limit is {max_products}"
        )
    return CNRSFiniteSequence(
        _convolution_values(left, right), left.offset + right.offset
    )


def iter_convolution(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    *,
    chunk_products: int = 1024,
    max_products: int | None = None,
) -> Iterator[ConvolutionProgress]:
    left = _require_sequence(left, "left")
    right = _require_sequence(right, "right")
    _validate_chunk(chunk_products)
    _validate_limit(max_products)
    required = len(left.coefficients) * len(right.coefficients)
    allowed = required if max_products is None else min(required, max_products)

    if required == 0:
        yield ConvolutionProgress(
            ConvolutionStatus.COMPLETE, 0, 0, None, CNRSFiniteSequence(())
        )
        return

    output: list[GaussianInteger] = [
        (0, 0)
        for _ in range(len(left.coefficients) + len(right.coefficients) - 1)
    ]
    completed = 0
    last_pair: tuple[int, int] | None = None
    for i, left_value in enumerate(left.coefficients):
        for j, right_value in enumerate(right.coefficients):
            if completed == allowed:
                yield ConvolutionProgress(
                    ConvolutionStatus.LIMIT_REACHED,
                    completed,
                    required,
                    last_pair,
                    None,
                )
                return
            output[i + j] = gadd(output[i + j], gmul(left_value, right_value))
            completed += 1
            last_pair = (i, j)
            if completed % chunk_products == 0 and completed < allowed:
                yield ConvolutionProgress(
                    ConvolutionStatus.IN_PROGRESS,
                    completed,
                    required,
                    last_pair,
                    None,
                )

    result = CNRSFiniteSequence(output, left.offset + right.offset)
    yield ConvolutionProgress(
        ConvolutionStatus.COMPLETE,
        completed,
        required,
        last_pair,
        result,
    )


def multiply_with_witness(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    *,
    normalize: bool = True,
    max_products: int | None = None,
    max_carry_steps: int | None = None,
) -> MultiplicationResult:
    left = _require_sequence(left, "left")
    right = _require_sequence(right, "right")
    if type(normalize) is not bool:
        raise TypeError("normalize must be a bool")
    _validate_limit(max_products)
    validate_carry_limit(max_carry_steps)
    required = len(left.coefficients) * len(right.coefficients)
    if max_products is not None and max_products < required:
        return MultiplicationResult(
            ConvolutionStatus.LIMIT_REACHED,
            max_products,
            required,
            None,
            None,
            None,
        )

    raw = convolve_exact(left, right)
    normalized = (
        normalize_gaussian_laurent(raw, max_carry_steps=max_carry_steps)
        if normalize
        else None
    )
    from .convolution_witnesses import build_convolution_witness

    witness = build_convolution_witness(left, right, raw, normalized, normalize)
    return MultiplicationResult(
        ConvolutionStatus.COMPLETE,
        required,
        required,
        raw,
        normalized,
        witness,
    )


__all__ = [
    "ConvolutionLimitError",
    "ConvolutionProgress",
    "ConvolutionStatus",
    "MultiplicationResult",
    "convolve_exact",
    "iter_convolution",
    "multiply_with_witness",
]
