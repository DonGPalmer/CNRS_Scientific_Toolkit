from dataclasses import fields, replace
import importlib.util
import inspect
import json
from pathlib import Path
import random

import pytest

from cnrs import (
    CNRSFiniteSequence,
    ConvolutionLimitError,
    ConvolutionStatus,
    ConvolutionWitness,
    GaussianRational,
    NormalizationLimitError,
    convolve_exact,
    deserialize_convolution_witness,
    iter_convolution,
    multiply_with_witness,
    normalize_gaussian_laurent,
    serialize_convolution_witness,
    verify_convolution_witness,
)
from cnrs.validation.convolution_oracle import oracle_convolve

_CLAIM_GUARD_PATH = (
    Path(__file__).resolve().parents[1] / "tools" / "check_v015_claims.py"
)
_CLAIM_GUARD_SPEC = importlib.util.spec_from_file_location(
    "check_v015_claims", _CLAIM_GUARD_PATH
)
assert _CLAIM_GUARD_SPEC is not None and _CLAIM_GUARD_SPEC.loader is not None
_CLAIM_GUARD = importlib.util.module_from_spec(_CLAIM_GUARD_SPEC)
_CLAIM_GUARD_SPEC.loader.exec_module(_CLAIM_GUARD)
validate_public_claim_text = _CLAIM_GUARD.validate_public_claim_text

BETA = (-2, 1)


@pytest.mark.parametrize("value, expected", [(3, (3, 0)), ((2, -4), (2, -4))])
def test_scalar_coercion(value, expected):
    assert GaussianRational(value).numerator == expected


@pytest.mark.parametrize(
    "value", [True, False, 1.0, 1j, [1, 2], (1,), (1, 2, 3), (True, 0)]
)
def test_scalar_rejections(value):
    with pytest.raises(TypeError):
        GaussianRational(value)


def test_fraction_canonicalization_and_zero():
    assert GaussianRational((2, 2), (2, 0)) == GaussianRational((1, 1))
    assert GaussianRational(0, (7, -3)) == GaussianRational(0)
    with pytest.raises(ZeroDivisionError):
        GaussianRational(1, 0)


def test_sequence_trimming_support_lookup_and_zero():
    value = CNRSFiniteSequence((0, (0, 0), (2, 1), 0), -4)
    assert value.coefficients == ((2, 1),)
    assert value.offset == -2
    assert value.support == (-2, -2)
    assert value.coefficient(-2) == (2, 1)
    assert value.coefficient(99) == (0, 0)
    assert CNRSFiniteSequence((0, 0), 99) == CNRSFiniteSequence(())


def test_exact_laurent_evaluation_vectors():
    inverse = CNRSFiniteSequence((1,), -1).evaluate(BETA)
    assert inverse == GaussianRational((-2, -1), 5)
    with pytest.raises(ZeroDivisionError):
        CNRSFiniteSequence((1,), -1).evaluate(0)
    assert CNRSFiniteSequence((1,), 0).evaluate(0) == GaussianRational(1)


def test_convolution_known_offset_and_cancellation():
    left = CNRSFiniteSequence((1, 1), -2)
    right = CNRSFiniteSequence((1, -1), 3)
    result = convolve_exact(left, right)
    assert result == CNRSFiniteSequence((1, 0, -1), 1)
    assert result.evaluate(BETA) == left.evaluate(BETA) * right.evaluate(BETA)


def test_convolution_matches_independent_oracle_seeded():
    rng = random.Random(1500)
    for _ in range(250):
        left = CNRSFiniteSequence(
            tuple((rng.randrange(-5, 6), rng.randrange(-5, 6)) for _ in range(rng.randrange(5))),
            rng.randrange(-3, 4),
        )
        right = CNRSFiniteSequence(
            tuple((rng.randrange(-5, 6), rng.randrange(-5, 6)) for _ in range(rng.randrange(5))),
            rng.randrange(-3, 4),
        )
        assert convolve_exact(left, right) == oracle_convolve(left, right)


def test_convolution_large_integer_exactness():
    huge = 1 << 1000
    result = convolve_exact(CNRSFiniteSequence(((huge, huge),)), CNRSFiniteSequence(((huge, -huge),)))
    assert result.coefficients == ((2 * huge * huge, 0),)


def test_exact_api_preflights_product_limit(monkeypatch):
    left = CNRSFiniteSequence((1, 2))
    right = CNRSFiniteSequence((3, 4))
    with pytest.raises(ConvolutionLimitError):
        convolve_exact(left, right, max_products=3)


@pytest.mark.parametrize("bad", [True, 1.0, "1"])
def test_product_limit_type_validation(bad):
    with pytest.raises(TypeError):
        convolve_exact(CNRSFiniteSequence((1,)), CNRSFiniteSequence((1,)), max_products=bad)


def test_product_limit_value_validation():
    with pytest.raises(ValueError):
        convolve_exact(CNRSFiniteSequence((1,)), CNRSFiniteSequence((1,)), max_products=-1)


def test_iterator_traversal_chunking_and_terminal():
    left = CNRSFiniteSequence((1, 0, 2))
    right = CNRSFiniteSequence((3, 4))
    records = list(iter_convolution(left, right, chunk_products=2))
    assert [(r.status, r.products_completed, r.last_pair) for r in records] == [
        (ConvolutionStatus.IN_PROGRESS, 2, (0, 1)),
        (ConvolutionStatus.IN_PROGRESS, 4, (1, 1)),
        (ConvolutionStatus.COMPLETE, 6, (2, 1)),
    ]
    assert records[-1].result == convolve_exact(left, right)


def test_iterator_limit_and_zero_work():
    left, right = CNRSFiniteSequence((1, 2)), CNRSFiniteSequence((3, 4))
    limited = list(iter_convolution(left, right, chunk_products=2, max_products=3))
    assert limited[-1].status is ConvolutionStatus.LIMIT_REACHED
    assert limited[-1].products_completed == 3
    assert limited[-1].result is None
    zero = list(iter_convolution(CNRSFiniteSequence(()), right))
    assert len(zero) == 1 and zero[0].status is ConvolutionStatus.COMPLETE


def test_exact_chunk_boundary_has_no_duplicate_progress():
    records = list(iter_convolution(CNRSFiniteSequence((1, 2)), CNRSFiniteSequence((3, 4)), chunk_products=4))
    assert len(records) == 1
    assert records[0].status is ConvolutionStatus.COMPLETE


def test_normalization_frozen_vectors_and_alphabet():
    five = normalize_gaussian_laurent(CNRSFiniteSequence(((5, 0),), 0))
    assert five == CNRSFiniteSequence(((1, 0), (3, 0), (1, 0)), 1)
    unit = normalize_gaussian_laurent(CNRSFiniteSequence((BETA,), -1))
    assert unit == CNRSFiniteSequence(((1, 0),), 0)
    for coefficient in five.coefficients + unit.coefficients:
        assert coefficient[1] == 0 and 0 <= coefficient[0] <= 4


def test_normalization_random_value_preservation():
    rng = random.Random(1501)
    for _ in range(500):
        value = CNRSFiniteSequence(
            tuple((rng.randrange(-20, 21), rng.randrange(-20, 21)) for _ in range(rng.randrange(1, 7))),
            rng.randrange(-5, 6),
        )
        normalized = normalize_gaussian_laurent(value)
        assert normalized.evaluate(BETA) == value.evaluate(BETA)
        assert all(b == 0 and 0 <= a <= 4 for a, b in normalized.coefficients)


@pytest.mark.parametrize("bad", [True, 1.5, "2"])
def test_carry_limit_type_validation(bad):
    with pytest.raises(TypeError):
        normalize_gaussian_laurent(CNRSFiniteSequence((5,)), max_carry_steps=bad)


def test_carry_limit_count_and_exhaustion():
    value = CNRSFiniteSequence((5,))
    assert normalize_gaussian_laurent(value, max_carry_steps=3)
    with pytest.raises(NormalizationLimitError):
        normalize_gaussian_laurent(value, max_carry_steps=2)
    with pytest.raises(ValueError):
        normalize_gaussian_laurent(value, max_carry_steps=-1)


def test_multiply_result_limit_and_carry_validation_when_disabled():
    left, right = CNRSFiniteSequence((1, 2)), CNRSFiniteSequence((3, 4))
    limited = multiply_with_witness(left, right, max_products=3)
    assert limited.status is ConvolutionStatus.LIMIT_REACHED
    assert limited.raw_convolution is limited.normalized is limited.witness is None
    with pytest.raises(TypeError):
        multiply_with_witness(left, right, normalize=False, max_carry_steps=True)


def test_multiply_propagates_normalization_limit():
    with pytest.raises(NormalizationLimitError):
        multiply_with_witness(CNRSFiniteSequence((5,)), CNRSFiniteSequence((1,)), max_carry_steps=2)


def test_witness_field_order_canonical_bytes_and_roundtrip():
    result = multiply_with_witness(CNRSFiniteSequence((1, 2), -1), CNRSFiniteSequence((3, 4), 2))
    witness = result.witness
    assert witness is not None
    assert [field.name for field in fields(ConvolutionWitness)] == [
        "schema", "status", "algorithm", "traversal", "left", "right", "raw",
        "normalized", "normalization_requested", "products_required", "left_sha256",
        "right_sha256", "raw_sha256", "normalized_sha256",
    ]
    data = serialize_convolution_witness(witness)
    assert not data.startswith(b"\xef\xbb\xbf") and not data.endswith(b"\n")
    assert data == json.dumps(json.loads(data), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    assert deserialize_convolution_witness(data) == witness
    assert verify_convolution_witness(data).valid


def test_unnormalized_witness_null_pair():
    result = multiply_with_witness(CNRSFiniteSequence((1,)), CNRSFiniteSequence((2,)), normalize=False)
    assert result.normalized is None
    assert result.witness is not None
    assert result.witness.normalized is None
    assert result.witness.normalized_sha256 is None
    assert verify_convolution_witness(result.witness).valid


def test_witness_mutation_detection_and_serializer_rejection():
    witness = multiply_with_witness(CNRSFiniteSequence((1, 2)), CNRSFiniteSequence((3,))).witness
    assert witness is not None
    mutated = replace(witness, products_required=99)
    assert not verify_convolution_witness(mutated).valid
    with pytest.raises(ValueError):
        serialize_convolution_witness(mutated)


@pytest.mark.parametrize(
    "bad",
    [b"\xff", b"{}", b'{"schema":"x","schema":"y"}', b' {"x":1}', b'{"x":NaN}'],
)
def test_parser_rejects_invalid_bytes(bad):
    with pytest.raises(ValueError):
        deserialize_convolution_witness(bad)


def test_public_signatures_are_frozen():
    assert str(inspect.signature(convolve_exact)) == "(left: 'CNRSFiniteSequence', right: 'CNRSFiniteSequence', *, max_products: 'int | None' = None) -> 'CNRSFiniteSequence'"
    assert "chunk_products: 'int' = 1024" in str(inspect.signature(iter_convolution))
    assert "normalize: 'bool' = True" in str(inspect.signature(multiply_with_witness))


def test_sequence_subclass_is_accepted():
    class Derived(CNRSFiniteSequence):
        pass
    assert convolve_exact(Derived((1,)), Derived((2,))) == CNRSFiniteSequence((2,))


def test_nonsequence_rejected_everywhere():
    for function in (convolve_exact, multiply_with_witness):
        with pytest.raises(TypeError):
            function((1,), CNRSFiniteSequence((1,)))
    with pytest.raises(TypeError):
        normalize_gaussian_laurent((1,))


def test_exhaustive_small_convolution_and_evaluation():
    values = [(a, b) for a in range(-1, 2) for b in range(-1, 2)]
    for left_value in values:
        for right_value in values:
            for left_offset in (-1, 0, 1):
                for right_offset in (-1, 0, 1):
                    left = CNRSFiniteSequence((left_value,), left_offset)
                    right = CNRSFiniteSequence((right_value,), right_offset)
                    result = convolve_exact(left, right)
                    assert result == oracle_convolve(left, right)
                    assert result.evaluate(BETA) == (
                        left.evaluate(BETA) * right.evaluate(BETA)
                    )


def test_convolution_algebraic_laws_and_internal_zeros():
    zero = CNRSFiniteSequence(())
    one = CNRSFiniteSequence((1,))
    left = CNRSFiniteSequence(((2, -1), 0, (3, 4)), -2)
    right = CNRSFiniteSequence(((-1, 2), 0, 5), 3)
    third = CNRSFiniteSequence(((4, 1), -2), -1)
    assert convolve_exact(left, zero) == zero
    assert convolve_exact(left, one) == left
    assert convolve_exact(left, right) == convolve_exact(right, left)
    assert convolve_exact(convolve_exact(left, right), third) == convolve_exact(
        left, convolve_exact(right, third)
    )


def test_all_frozen_public_signatures_exactly():
    expected = {
        convolve_exact: "(left: 'CNRSFiniteSequence', right: 'CNRSFiniteSequence', *, max_products: 'int | None' = None) -> 'CNRSFiniteSequence'",
        iter_convolution: "(left: 'CNRSFiniteSequence', right: 'CNRSFiniteSequence', *, chunk_products: 'int' = 1024, max_products: 'int | None' = None) -> 'Iterator[ConvolutionProgress]'",
        multiply_with_witness: "(left: 'CNRSFiniteSequence', right: 'CNRSFiniteSequence', *, normalize: 'bool' = True, max_products: 'int | None' = None, max_carry_steps: 'int | None' = None) -> 'MultiplicationResult'",
        normalize_gaussian_laurent: "(value: 'CNRSFiniteSequence', *, max_carry_steps: 'int | None' = None) -> 'CNRSFiniteSequence'",
        serialize_convolution_witness: "(witness: 'ConvolutionWitness') -> 'bytes'",
        deserialize_convolution_witness: "(data: 'bytes') -> 'ConvolutionWitness'",
        verify_convolution_witness: "(witness: 'ConvolutionWitness | bytes') -> 'WitnessValidation'",
    }
    for function, signature in expected.items():
        assert str(inspect.signature(function)) == signature


@pytest.mark.parametrize("normalize", [False, True])
@pytest.mark.parametrize("limit_delta", [-1, 0, 1])
def test_multiply_limit_normalize_matrix(normalize, limit_delta):
    left = CNRSFiniteSequence((1, 2))
    right = CNRSFiniteSequence((3, 4))
    required = 4
    result = multiply_with_witness(
        left,
        right,
        normalize=normalize,
        max_products=required + limit_delta,
        max_carry_steps=20,
    )
    if limit_delta < 0:
        assert result.status is ConvolutionStatus.LIMIT_REACHED
        assert result.raw_convolution is None
        assert result.normalized is None
        assert result.witness is None
    else:
        assert result.status is ConvolutionStatus.COMPLETE
        assert result.raw_convolution == convolve_exact(left, right)
        assert (result.normalized is not None) is normalize
        assert result.witness is not None
        assert result.witness.normalization_requested is normalize


def test_fixed_sequence_digest_vector():
    result = multiply_with_witness(
        CNRSFiniteSequence((1,)), CNRSFiniteSequence((1,))
    )
    witness = result.witness
    assert witness is not None
    expected = "696f8debb065a59f2ad77572546943a0cdaa1bc0dfd90d613899ef1fca19a931"
    assert witness.left_sha256 == expected
    assert witness.right_sha256 == expected
    assert witness.raw_sha256 == expected
    assert witness.normalized_sha256 == expected


def _canonical_witness_bytes(obj):
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def test_parser_complete_rejection_matrix():
    witness = multiply_with_witness(
        CNRSFiniteSequence((1,)), CNRSFiniteSequence((1,))
    ).witness
    assert witness is not None
    canonical = serialize_convolution_witness(witness)
    obj = json.loads(canonical)

    bad_values = [bytearray(canonical), "not bytes", None]
    for value in bad_values:
        with pytest.raises(TypeError):
            deserialize_convolution_witness(value)

    mutations = []
    missing = dict(obj); missing.pop("status"); mutations.append(missing)
    unknown = dict(obj); unknown["unknown"] = 1; mutations.append(unknown)
    bad_schema = dict(obj); bad_schema["schema"] = "wrong"; mutations.append(bad_schema)
    bad_status = dict(obj); bad_status["status"] = "in_progress"; mutations.append(bad_status)
    bad_algorithm = dict(obj); bad_algorithm["algorithm"] = "wrong"; mutations.append(bad_algorithm)
    bad_traversal = dict(obj); bad_traversal["traversal"] = "wrong"; mutations.append(bad_traversal)
    bad_digest = dict(obj); bad_digest["left_sha256"] = "A" * 64; mutations.append(bad_digest)
    bad_pair = json.loads(canonical); bad_pair["left"]["coefficients"] = [[True, 0]]; mutations.append(bad_pair)
    bad_offset = json.loads(canonical); bad_offset["left"]["offset"] = True; mutations.append(bad_offset)
    bad_null = dict(obj); bad_null["normalized"] = None; mutations.append(bad_null)
    for mutation in mutations:
        with pytest.raises(ValueError):
            deserialize_convolution_witness(_canonical_witness_bytes(mutation))

    with pytest.raises(ValueError):
        deserialize_convolution_witness(b"\xef\xbb\xbf" + canonical)
    with pytest.raises(ValueError):
        deserialize_convolution_witness(canonical + b"\n")


def test_incomplete_witnesses_cannot_serialize_or_verify():
    witness = multiply_with_witness(
        CNRSFiniteSequence((1,)), CNRSFiniteSequence((2,))
    ).witness
    assert witness is not None
    for mutation in (
        replace(witness, status="in_progress"),
        replace(witness, raw=None),
        replace(witness, normalized=None),
        replace(witness, normalized_sha256=None),
    ):
        assert not verify_convolution_witness(mutation).valid
        with pytest.raises(ValueError):
            serialize_convolution_witness(mutation)


def test_every_decisive_witness_field_is_recomputed_or_validated():
    witness = multiply_with_witness(
        CNRSFiniteSequence((1, 2), -1), CNRSFiniteSequence((3, 4), 2)
    ).witness
    assert witness is not None
    changes = {
        "schema": "wrong",
        "status": "in_progress",
        "algorithm": "wrong",
        "traversal": "wrong",
        "left": CNRSFiniteSequence((9,)),
        "right": CNRSFiniteSequence((9,)),
        "raw": CNRSFiniteSequence((9,)),
        "normalized": CNRSFiniteSequence((9,)),
        "normalization_requested": False,
        "products_required": witness.products_required + 1,
        "left_sha256": "0" * 64,
        "right_sha256": "0" * 64,
        "raw_sha256": "0" * 64,
        "normalized_sha256": "0" * 64,
    }
    for field, value in changes.items():
        mutated = replace(witness, **{field: value})
        assert not verify_convolution_witness(mutated).valid, field
        with pytest.raises(ValueError):
            serialize_convolution_witness(mutated)


@pytest.mark.parametrize(
    "claim",
    [
        "This operation has bounded total computational resources.",
        "The algorithm provides bounded elapsed time.",
        "The implementation is universally faster.",
        "The method offers universal memory superiority.",
    ],
)
def test_claim_guard_rejects_total_resource_and_universal_claims(claim):
    with pytest.raises(ValueError):
        validate_public_claim_text("candidate.md", claim)


def test_claim_guard_accepts_exact_frozen_qualifications():
    validate_public_claim_text(
        "candidate.md",
        "Execution is product-count bounded and post-input carry-drain-count bounded only.",
    )
