"""Canonical evidence records for complete finite convolutions."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any

from .finite_sequence import CNRSFiniteSequence
from .gaussian_normalization import normalize_gaussian_laurent
from .validation.convolution_oracle import oracle_convolve

CONVOLUTION_WITNESS_SCHEMA = "cnrs-convolution-witness-v1"
CONVOLUTION_ALGORITHM = "schoolbook-gaussian-exact-v1"
CONVOLUTION_TRAVERSAL = "left-major-right-minor-v1"
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_TOP_KEYS = {
    "algorithm",
    "left",
    "left_sha256",
    "normalization_requested",
    "normalized",
    "normalized_sha256",
    "products_required",
    "raw",
    "raw_sha256",
    "right",
    "right_sha256",
    "schema",
    "status",
    "traversal",
}


@dataclass(frozen=True)
class ConvolutionWitness:
    schema: str
    status: str
    algorithm: str
    traversal: str
    left: CNRSFiniteSequence
    right: CNRSFiniteSequence
    raw: CNRSFiniteSequence
    normalized: CNRSFiniteSequence | None
    normalization_requested: bool
    products_required: int
    left_sha256: str
    right_sha256: str
    raw_sha256: str
    normalized_sha256: str | None


@dataclass(frozen=True)
class WitnessValidation:
    valid: bool
    errors: tuple[str, ...]


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sequence_object(value: CNRSFiniteSequence) -> dict[str, object]:
    return {
        "coefficients": [[a, b] for a, b in value.coefficients],
        "offset": value.offset,
    }


def _sequence_digest(value: CNRSFiniteSequence) -> str:
    return hashlib.sha256(_canonical_json(_sequence_object(value))).hexdigest()


def build_convolution_witness(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    raw: CNRSFiniteSequence,
    normalized: CNRSFiniteSequence | None,
    normalization_requested: bool,
) -> ConvolutionWitness:
    return ConvolutionWitness(
        schema=CONVOLUTION_WITNESS_SCHEMA,
        status="complete",
        algorithm=CONVOLUTION_ALGORITHM,
        traversal=CONVOLUTION_TRAVERSAL,
        left=left,
        right=right,
        raw=raw,
        normalized=normalized,
        normalization_requested=normalization_requested,
        products_required=len(left.coefficients) * len(right.coefficients),
        left_sha256=_sequence_digest(left),
        right_sha256=_sequence_digest(right),
        raw_sha256=_sequence_digest(raw),
        normalized_sha256=(
            _sequence_digest(normalized) if normalized is not None else None
        ),
    )


def _witness_object(witness: ConvolutionWitness) -> dict[str, object]:
    return {
        "algorithm": witness.algorithm,
        "left": _sequence_object(witness.left),
        "left_sha256": witness.left_sha256,
        "normalization_requested": witness.normalization_requested,
        "normalized": (
            _sequence_object(witness.normalized)
            if witness.normalized is not None
            else None
        ),
        "normalized_sha256": witness.normalized_sha256,
        "products_required": witness.products_required,
        "raw": _sequence_object(witness.raw),
        "raw_sha256": witness.raw_sha256,
        "right": _sequence_object(witness.right),
        "right_sha256": witness.right_sha256,
        "schema": witness.schema,
        "status": witness.status,
        "traversal": witness.traversal,
    }


def _check_sequence(value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, CNRSFiniteSequence):
        errors.append(f"{field} must be a CNRSFiniteSequence")


def verify_convolution_witness(
    witness: ConvolutionWitness | bytes,
) -> WitnessValidation:
    if type(witness) is bytes:
        try:
            witness = deserialize_convolution_witness(witness)
        except (TypeError, ValueError, UnicodeDecodeError) as exc:
            return WitnessValidation(False, (str(exc),))
    elif not isinstance(witness, ConvolutionWitness):
        raise TypeError("witness must be ConvolutionWitness or exact bytes")

    errors: list[str] = []
    if witness.schema != CONVOLUTION_WITNESS_SCHEMA:
        errors.append("invalid schema")
    if witness.status != "complete":
        errors.append("status must be complete")
    if witness.algorithm != CONVOLUTION_ALGORITHM:
        errors.append("invalid algorithm")
    if witness.traversal != CONVOLUTION_TRAVERSAL:
        errors.append("invalid traversal")
    if type(witness.normalization_requested) is not bool:
        errors.append("normalization_requested must be bool")
    if type(witness.products_required) is not int or witness.products_required < 0:
        errors.append("products_required must be a nonnegative exact int")
    _check_sequence(witness.left, "left", errors)
    _check_sequence(witness.right, "right", errors)
    _check_sequence(witness.raw, "raw", errors)
    if witness.normalized is not None:
        _check_sequence(witness.normalized, "normalized", errors)
    if bool(witness.normalized is not None) != bool(witness.normalization_requested):
        errors.append("normalized nullability mismatch")
    if bool(witness.normalized_sha256 is not None) != bool(
        witness.normalization_requested
    ):
        errors.append("normalized digest nullability mismatch")

    for field in ("left_sha256", "right_sha256", "raw_sha256"):
        digest = getattr(witness, field)
        if type(digest) is not str or _HEX.fullmatch(digest) is None:
            errors.append(f"{field} is not lowercase SHA-256")
    if witness.normalized_sha256 is not None and (
        type(witness.normalized_sha256) is not str
        or _HEX.fullmatch(witness.normalized_sha256) is None
    ):
        errors.append("normalized_sha256 is not lowercase SHA-256")

    if errors:
        return WitnessValidation(False, tuple(errors))

    assert isinstance(witness.left, CNRSFiniteSequence)
    assert isinstance(witness.right, CNRSFiniteSequence)
    assert isinstance(witness.raw, CNRSFiniteSequence)
    expected_count = len(witness.left.coefficients) * len(
        witness.right.coefficients
    )
    if witness.products_required != expected_count:
        errors.append("products_required mismatch")
    for name, sequence, recorded in (
        ("left", witness.left, witness.left_sha256),
        ("right", witness.right, witness.right_sha256),
        ("raw", witness.raw, witness.raw_sha256),
    ):
        if _sequence_digest(sequence) != recorded:
            errors.append(f"{name} digest mismatch")
    expected_raw = oracle_convolve(witness.left, witness.right)
    if witness.raw != expected_raw:
        errors.append("raw convolution mismatch")
    if witness.normalization_requested:
        assert witness.normalized is not None
        expected_normalized = normalize_gaussian_laurent(expected_raw)
        if witness.normalized != expected_normalized:
            errors.append("normalized value mismatch")
        if _sequence_digest(witness.normalized) != witness.normalized_sha256:
            errors.append("normalized digest mismatch")
    return WitnessValidation(not errors, tuple(errors))


def serialize_convolution_witness(witness: ConvolutionWitness) -> bytes:
    if not isinstance(witness, ConvolutionWitness):
        raise TypeError("witness must be a ConvolutionWitness")
    validation = verify_convolution_witness(witness)
    if not validation.valid:
        raise ValueError("invalid convolution witness: " + "; ".join(validation.errors))
    return _canonical_json(_witness_object(witness))


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_sequence(value: object, field: str) -> CNRSFiniteSequence:
    if type(value) is not dict or set(value) != {"coefficients", "offset"}:
        raise ValueError(f"{field} must have exact sequence keys")
    offset = value["offset"]
    coefficients = value["coefficients"]
    if type(offset) is not int or type(coefficients) is not list:
        raise ValueError(f"invalid {field} sequence types")
    pairs: list[tuple[int, int]] = []
    for pair in coefficients:
        if (
            type(pair) is not list
            or len(pair) != 2
            or type(pair[0]) is not int
            or type(pair[1]) is not int
        ):
            raise ValueError(f"invalid {field} coefficient pair")
        pairs.append((pair[0], pair[1]))
    sequence = CNRSFiniteSequence(pairs, offset)
    if _sequence_object(sequence) != value:
        raise ValueError(f"noncanonical {field} sequence")
    return sequence


def deserialize_convolution_witness(data: bytes) -> ConvolutionWitness:
    if type(data) is not bytes:
        raise TypeError("data must be exact bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("witness is not valid UTF-8") from exc
    try:
        obj = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"invalid witness JSON: {exc}") from exc
    if type(obj) is not dict or set(obj) != _TOP_KEYS:
        raise ValueError("witness must have the exact top-level key set")
    if _canonical_json(obj) != data:
        raise ValueError("witness bytes are not canonical JSON")
    if type(obj["normalization_requested"]) is not bool:
        raise ValueError("normalization_requested must be bool")
    if type(obj["products_required"]) is not int or obj["products_required"] < 0:
        raise ValueError("products_required must be a nonnegative exact int")
    left = _parse_sequence(obj["left"], "left")
    right = _parse_sequence(obj["right"], "right")
    raw = _parse_sequence(obj["raw"], "raw")
    normalized_value = obj["normalized"]
    normalized = (
        None
        if normalized_value is None
        else _parse_sequence(normalized_value, "normalized")
    )
    witness = ConvolutionWitness(
        schema=obj["schema"],
        status=obj["status"],
        algorithm=obj["algorithm"],
        traversal=obj["traversal"],
        left=left,
        right=right,
        raw=raw,
        normalized=normalized,
        normalization_requested=obj["normalization_requested"],
        products_required=obj["products_required"],
        left_sha256=obj["left_sha256"],
        right_sha256=obj["right_sha256"],
        raw_sha256=obj["raw_sha256"],
        normalized_sha256=obj["normalized_sha256"],
    )
    validation = verify_convolution_witness(witness)
    if not validation.valid:
        raise ValueError("invalid convolution witness: " + "; ".join(validation.errors))
    return witness


__all__ = [
    "CONVOLUTION_ALGORITHM",
    "CONVOLUTION_TRAVERSAL",
    "CONVOLUTION_WITNESS_SCHEMA",
    "ConvolutionWitness",
    "WitnessValidation",
    "build_convolution_witness",
    "deserialize_convolution_witness",
    "serialize_convolution_witness",
    "verify_convolution_witness",
]
