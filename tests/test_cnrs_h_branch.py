import pytest

from cnrs.symbolic import Var, log, sqrt, pow_branch, BranchState, DEFAULT_BRANCH_STATE
from cnrs.cnrs_h_branch import merge_branch_states, branch_state_from_symbolic, branch_merge_report
from cnrs.cnrs_h_jet import jet_from_symbolic, jet_identity, verify_jet_chain_rule


def test_branch_state_extracts_from_symbolic_log_sqrt_pow():
    s = Var("s")
    expr = log(1 + s, branch=2) + sqrt(1 + s, branch=1) + pow_branch(1 + s, 0.5, branch=3)
    state = branch_state_from_symbolic(expr)
    assert state.log_branch == 2
    assert state.sqrt_branch == 1
    assert state.pow_branch == 3


def test_branch_merge_preserves_non_default_values():
    a = BranchState(log_branch=2)
    b = BranchState(sqrt_branch=1)
    merged = merge_branch_states(a, b)
    assert not merged.has_conflicts
    assert merged.state.log_branch == 2
    assert merged.state.sqrt_branch == 1


def test_branch_merge_reports_conflict_but_keeps_left():
    merged = merge_branch_states(BranchState(log_branch=2), BranchState(log_branch=4))
    assert merged.has_conflicts
    assert merged.state.log_branch == 2
    assert merged.conflicts[0].field == "log_branch"


def test_jet_from_symbolic_carries_branch_state():
    s = Var("s")
    jet = jet_from_symbolic(log(1 + s, branch=2), s, center=0, order=5)
    assert jet.branch_state.log_branch == 2
    assert "log=2" in jet.branch_summary()


def test_jet_operations_preserve_branch_state():
    s = Var("s")
    jet = jet_from_symbolic(log(1 + s, branch=2), s, center=0, order=5)
    assert jet.diff(order=4).branch_state.log_branch == 2
    assert jet.integrate(order=5).branch_state.log_branch == 2
    assert jet.shift_center(0.1, order=5).branch_state.log_branch == 2


def test_jet_product_merges_branch_states():
    s = Var("s")
    log_jet = jet_from_symbolic(log(1 + s, branch=2), s, center=0, order=5)
    sqrt_jet = jet_from_symbolic(sqrt(1 + s, branch=1), s, center=0, order=5)
    product = log_jet * sqrt_jet
    assert product.branch_state.log_branch == 2
    assert product.branch_state.sqrt_branch == 1


def test_jet_composition_merges_branch_states():
    x = Var("x")
    s = Var("s")
    outer = jet_from_symbolic(log(1 + x, branch=2), x, center=0, order=6)
    inner = jet_from_symbolic(sqrt(1 + s, branch=1) - 1, s, center=0, order=6)
    composed = outer.compose(inner, order=5)
    assert composed.branch_state.log_branch == 2
    assert composed.branch_state.sqrt_branch == 1
    assert "no path continuation" in composed.branch_summary()


def test_chain_rule_preserves_merged_branch_state_on_lhs_and_rhs():
    x = Var("x")
    s = Var("s")
    outer = jet_from_symbolic(log(1 + x, branch=2), x, center=0, order=7)
    inner = jet_from_symbolic(sqrt(1 + s, branch=1) - 1, s, center=0, order=7)
    result = verify_jet_chain_rule(outer, inner, order=5, atol=1e-8)
    assert result.passed
    assert result.lhs.branch_state.log_branch == 2
    assert result.lhs.branch_state.sqrt_branch == 1
    assert result.rhs.branch_state.log_branch == 2
    assert result.rhs.branch_state.sqrt_branch == 1


def test_manual_branch_state_on_identity_jet():
    jet = jet_identity(order=4).with_branch_state(BranchState(winding=1), note="manual winding scaffold")
    assert jet.branch_state.winding == 1
    assert "manual winding" in jet.branch_summary()
