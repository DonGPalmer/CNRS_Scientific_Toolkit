"""Executable v0.18 exact-addition-and-subtraction acceptance contract."""
from __future__ import annotations

from itertools import product
import random
import subprocess

from cnrs.cnrs_add import add_cnrs
from cnrs.cnrs_ops import cnrs_add, cnrs_neg, cnrs_sub
from cnrs.cnrs_mul import mul_cnrs
from cnrs.cnrs_value import CVal
from cnrs.validation.exact_addition_subtraction_oracle import (
    exact_difference_value,
    exact_negated_value,
    exact_string_value,
    exact_sum_value,
)
from cnrs.validation.v017_addition_subtraction_baseline import (
    legacy_add_cnrs,
    legacy_cnrs_neg,
    legacy_cnrs_sub,
)

BASE_COMMIT = "b290f2e3b43dc1830bb1311eb81393475b341a94"
BASE_TREE = "ff732e56a6597d9ec98ce071f41507d7dd9bca21"
IMPLEMENTATION_COMMIT = "fe3c27795085b13b402272de9a91b7a42d9ddda0"
IMPLEMENTATION_TREE = "0a2fbba6151fd893231fe7f4bed459c0a7e0a853"
LONG_PAIR_SEED = 2026092205
LONG_PAIR_COUNT = 100
LONG_MAX_DIGITS = 1000
LONG_LAW_SEED = 2026092210
LONG_LAW_COUNT = 100
FRACTIONAL_CVAL_VECTORS = (
    (".1", ".4"),
    ("1.2", ".3"),
    ("23.1", "4.3"),
    ("0.004", "12.34"),
)
ALLOWED_PATHS = {
    "V018_ARCHITECTURE_FREEZE.md", "V018_EXACT_ADDITION_SUBTRACTION_API_CONTRACT.md",
    "acceptance/v018/README.md", "acceptance/v018/test_exact_addition_subtraction_contract.py",
    "cnrs/cnrs_add.py", "cnrs/cnrs_ops.py",
    "cnrs/validation/exact_addition_subtraction_oracle.py",
    "cnrs/validation/v017_addition_subtraction_baseline.py",
    "tests/test_v018_exact_addition_subtraction.py", "tools/check_v018_claims.py",
    "README.md", "docs/API_STATUS.md", "docs/CLAIM_STATUS.md", "SOURCE_INDEX.txt",
}


def _short_domain() -> list[str]:
    values = []
    for length in range(1, 4):
        for digits in map("".join, product("01234", repeat=length)):
            values.append(digits)
            values.extend(digits[:point] + "." + digits[point:] for point in range(length + 1))
    return values


def _long_spelling(rng: random.Random, digit_count: int) -> str:
    digits = "".join(str(rng.randrange(5)) for _ in range(digit_count))
    point = rng.randrange(digit_count + 1)
    if point == 0:
        return "." + digits
    if point == digit_count:
        return digits
    return digits[:point] + "." + digits[point:]


def _one_digit_law_domain() -> list[str]:
    return [form for digit in "01234" for form in (digit, digit + ".", "." + digit)]


def _assert_a10_laws(a: str, b: str, c: str) -> None:
    ab = add_cnrs(a, b)
    assert ab == add_cnrs(b, a) == cnrs_add(a, b)
    assert exact_string_value(ab) == exact_sum_value(a, b)

    left_associative = add_cnrs(ab, c)
    right_associative = add_cnrs(a, add_cnrs(b, c))
    assert left_associative == right_associative
    assert exact_string_value(left_associative) == exact_sum_value(ab, c)

    canonical_a = add_cnrs(a, "0")
    assert exact_string_value(canonical_a) == exact_string_value(a)
    assert add_cnrs(a, cnrs_neg(a)) == "0"
    assert cnrs_neg(cnrs_neg(a)) == canonical_a
    assert exact_string_value(cnrs_neg(a)) == exact_negated_value(a)

    difference = cnrs_sub(a, b)
    reverse_difference = cnrs_sub(b, a)
    assert difference == add_cnrs(a, cnrs_neg(b))
    assert difference == cnrs_neg(reverse_difference)
    assert cnrs_sub(a, "0") == canonical_a
    assert cnrs_sub(a, a) == "0"
    assert exact_string_value(difference) == exact_difference_value(a, b)

    distributed_left = mul_cnrs(a, add_cnrs(b, c))
    distributed_right = add_cnrs(mul_cnrs(a, b), mul_cnrs(a, c))
    assert exact_string_value(distributed_left) == exact_string_value(distributed_right)


def test_a01_candidate_identity_ancestry_and_changed_paths():
    assert subprocess.check_output(
        ["git", "merge-base", IMPLEMENTATION_COMMIT, BASE_COMMIT], text=True
    ).strip() == BASE_COMMIT
    assert subprocess.check_output(
        ["git", "rev-parse", f"{BASE_COMMIT}^{{tree}}"], text=True
    ).strip() == BASE_TREE
    assert subprocess.check_output(
        ["git", "rev-parse", f"{IMPLEMENTATION_COMMIT}^{{tree}}"], text=True
    ).strip() == IMPLEMENTATION_TREE
    changed = set(subprocess.check_output(
        ["git", "diff", "--name-only", BASE_COMMIT, IMPLEMENTATION_COMMIT],
        text=True,
    ).splitlines())
    assert changed == ALLOWED_PATHS


def test_a04_to_a09_exhaustive_short_domain_and_correction_ledger():
    values = _short_domain()
    assert len(values) == 740 and len(set(values)) == 740
    exact_values = {value: exact_string_value(value) for value in values}
    exact_negations = {value: cnrs_neg(value) for value in values}
    baseline_negations = {value: legacy_cnrs_neg(value) for value in values}
    negation_corrections = 0
    for value in values:
        result = exact_negations[value]
        baseline = baseline_negations[value]
        assert exact_string_value(result) == exact_negated_value(value)
        assert result == mul_cnrs("144", value)
        assert cnrs_neg(result) == add_cnrs(value, "0")
        if exact_string_value(baseline) == exact_negated_value(value):
            assert result == baseline
        else:
            negation_corrections += 1
    assert negation_corrections == 392

    subtraction_corrections = 0
    for left in values:
        for right in values:
            addition = add_cnrs(left, right)
            assert addition == cnrs_add(left, right) == legacy_add_cnrs(left, right)
            assert exact_string_value(addition) == exact_sum_value(left, right)
            subtraction = add_cnrs(left, exact_negations[right])
            assert subtraction == cnrs_sub(left, right)
            assert exact_string_value(subtraction) == exact_difference_value(left, right)
            baseline = legacy_cnrs_sub(left, right)
            if exact_string_value(baseline) == exact_difference_value(left, right):
                assert subtraction == baseline
            else:
                subtraction_corrections += 1
    assert subtraction_corrections == 290_080


def test_a05_one_hundred_long_input_pairs_to_one_thousand_digits():
    rng = random.Random(LONG_PAIR_SEED)
    observed_lengths = []
    for index in range(LONG_PAIR_COUNT):
        left_length = LONG_MAX_DIGITS if index == 0 else 64 + (index * 37) % 937
        right_length = LONG_MAX_DIGITS if index == 0 else 64 + (index * 53 + 17) % 937
        left = _long_spelling(rng, left_length)
        right = _long_spelling(rng, right_length)
        observed_lengths.extend((left_length, right_length))

        addition = add_cnrs(left, right)
        negation = cnrs_neg(left)
        subtraction = cnrs_sub(left, right)
        assert addition == legacy_add_cnrs(left, right)
        assert exact_string_value(addition) == exact_sum_value(left, right)
        assert exact_string_value(negation) == exact_negated_value(left)
        assert exact_string_value(subtraction) == exact_difference_value(left, right)

    assert len(observed_lengths) == 2 * LONG_PAIR_COUNT
    assert max(observed_lengths) == LONG_MAX_DIGITS
    assert all(64 <= length <= LONG_MAX_DIGITS for length in observed_lengths)


def test_a10_exhaustive_short_and_randomized_longer_domain_laws():
    domain = _one_digit_law_domain()
    assert len(domain) == 15 and len(set(domain)) == 15
    for a, b, c in product(domain, repeat=3):
        _assert_a10_laws(a, b, c)

    rng = random.Random(LONG_LAW_SEED)
    for _ in range(LONG_LAW_COUNT):
        a, b, c = (_long_spelling(rng, 32 + rng.randrange(65)) for _ in range(3))
        _assert_a10_laws(a, b, c)


def test_a13_fractional_direct_and_cval_route_parity():
    assert len(FRACTIONAL_CVAL_VECTORS) >= 4
    for left, right in FRACTIONAL_CVAL_VECTORS:
        direct_negation = cnrs_neg(left)
        cval_negation = (-CVal.from_str(left)).s
        assert direct_negation == cval_negation
        assert exact_string_value(direct_negation) == exact_negated_value(left)

        direct_subtraction = cnrs_sub(left, right)
        cval_subtraction = (CVal.from_str(left) - CVal.from_str(right)).s
        assert direct_subtraction == cval_subtraction
        assert exact_string_value(direct_subtraction) == exact_difference_value(left, right)
