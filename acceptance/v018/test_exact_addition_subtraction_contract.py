"""Executable v0.18 exact-addition-and-subtraction acceptance contract."""
from __future__ import annotations

from itertools import product
import random
import subprocess

from cnrs.cnrs_add import add_cnrs
from cnrs.cnrs_ops import cnrs_add, cnrs_neg, cnrs_sub
from cnrs.cnrs_mul import mul_cnrs
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


def test_a01_candidate_identity_ancestry_and_changed_paths():
    assert subprocess.check_output(["git", "merge-base", "HEAD", BASE_COMMIT], text=True).strip() == BASE_COMMIT
    assert subprocess.check_output(["git", "rev-parse", f"{BASE_COMMIT}^{{tree}}"], text=True).strip() == BASE_TREE
    changed = set(subprocess.check_output(["git", "diff", "--name-only", BASE_COMMIT], text=True).splitlines())
    changed.update(subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"], text=True
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


def test_a10_randomized_laws_and_distributivity():
    rng = random.Random(1800)
    domain = _short_domain()
    for _ in range(1_000):
        a, b, c = (rng.choice(domain) for _ in range(3))
        assert add_cnrs(a, b) == add_cnrs(b, a)
        assert add_cnrs(add_cnrs(a, b), c) == add_cnrs(a, add_cnrs(b, c))
        assert cnrs_sub(a, b) == cnrs_neg(cnrs_sub(b, a))
        left = mul_cnrs(a, add_cnrs(b, c))
        right = add_cnrs(mul_cnrs(a, b), mul_cnrs(a, c))
        assert exact_string_value(left) == exact_string_value(right)
