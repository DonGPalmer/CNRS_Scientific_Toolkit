import cmath

import pytest

from cnrs.symbolic import Var, log, sqrt, pow_branch
from cnrs.cnrs_h_path import circle_path
from cnrs.generalized_branch import (
    BranchObject,
    BranchRegistry,
    GeneralizedBranchError,
    apply_branch_registry,
    continue_symbolic_with_registry,
)
from cnrs.cnrs_h_continuation import continued_jet_from_branch_registry


def _value(expr, z):
    return complex(expr.eval({"z": z}, L=24))


def _expressions_and_registries():
    z = Var("z")
    direct = sqrt(z * (z - 1), branch_key="whole")
    factorized = sqrt(z, branch_key="at0") * sqrt(z - 1, branch_key="at1")
    direct_registry = BranchRegistry([
        BranchObject("whole", "sqrt", [0, 1], label="sqrt(z(z-1))"),
    ])
    factor_registry = BranchRegistry([
        BranchObject("at0", "sqrt", [0], label="sqrt(z)"),
        BranchObject("at1", "sqrt", [1], label="sqrt(z-1)"),
    ])
    return direct, factorized, direct_registry, factor_registry


@pytest.mark.parametrize(
    "path,z0,expected_changed",
    [
        (circle_path(center=0, radius=0.25, turns=1, label="around 0"), 0.25, {"whole", "at0"}),
        (circle_path(center=1, radius=0.25, turns=1, label="around 1"), 1.25, {"whole", "at1"}),
        (circle_path(center=0.5, radius=1.0, turns=1, label="around both"), 1.5, {"at0", "at1"}),
    ],
)
def test_representation_invariance_for_two_branch_points(path, z0, expected_changed):
    direct, factorized, direct_registry, factor_registry = _expressions_and_registries()
    d = continue_symbolic_with_registry(direct, path, direct_registry)
    f = continue_symbolic_with_registry(factorized, path, factor_registry)
    assert abs(_value(d.continued_expr, z0) - _value(f.continued_expr, z0)) < 2e-3
    changed = set(d.changed_keys) | set(f.changed_keys)
    assert changed == expected_changed


def test_direct_two_locus_sqrt_returns_after_loop_around_both():
    direct, _, registry, _ = _expressions_and_registries()
    path = circle_path(center=0.5, radius=1.0, turns=1, label="around both")
    result = continue_symbolic_with_registry(direct, path, registry)
    assert result.continued_registry.by_key()["whole"].state == 0
    assert result.changed_keys == ()


def test_log_registry_uses_integer_sheet_state():
    z = Var("z")
    expr = log(z, branch_key="log0")
    registry = BranchRegistry([BranchObject("log0", "log", [0])])
    path = circle_path(center=0, radius=1, turns=3, label="three turns")
    result = continue_symbolic_with_registry(expr, path, registry)
    assert result.continued_registry.by_key()["log0"].state == 3
    assert abs(_value(result.continued_expr, 1) - 6j * cmath.pi) < 2e-3


def test_registry_rejects_kind_mismatch():
    z = Var("z")
    expr = sqrt(z, branch_key="x")
    registry = BranchRegistry([BranchObject("x", "log", [0])])
    with pytest.raises(GeneralizedBranchError):
        apply_branch_registry(expr, registry)


def test_registry_strict_missing_key():
    z = Var("z")
    expr = pow_branch(z, 0.5, branch_key="missing")
    with pytest.raises(GeneralizedBranchError):
        apply_branch_registry(expr, BranchRegistry([]), strict=True)


def test_generalized_jet_rebuild_matches_factorization_after_loop_around_zero():
    direct, factorized, direct_registry, factor_registry = _expressions_and_registries()
    path = circle_path(center=0, radius=0.25, turns=1, label="around 0")
    d = continued_jet_from_branch_registry(
        direct, "z", center=0.25, order=5, path=path, registry=direct_registry
    )
    f = continued_jet_from_branch_registry(
        factorized, "z", center=0.25, order=5, path=path, registry=factor_registry
    )
    for n in range(5):
        assert abs(d.continued_jet.coeff(n) - f.continued_jet.coeff(n)) < 2e-3
