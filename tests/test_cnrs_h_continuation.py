import cmath
import math

from cnrs.symbolic import Var, log, sqrt, pow_branch
from cnrs.cnrs_h_path import BranchPoint, circle_path
from cnrs.cnrs_h_continuation import (
    BranchDelta,
    branch_delta_from_events,
    shift_symbolic_branches,
    continued_jet_from_symbolic,
)


def test_branch_delta_from_log_event():
    path = circle_path(center=0, radius=1, turns=1, label="unit loop")
    from cnrs.cnrs_h_path import winding_events
    events = winding_events(path, [BranchPoint(0, kind="log")])
    delta = branch_delta_from_events(events)
    assert delta.log_delta == 1
    assert delta.winding_delta == 1


def test_shift_symbolic_log_branch():
    s = Var("s")
    expr = log(1 + s, branch=0)
    shifted = shift_symbolic_branches(expr, BranchDelta(log_delta=2, winding_delta=2))
    assert "log_2" in str(shifted)


def test_shift_symbolic_sqrt_branch_parity():
    s = Var("s")
    expr = sqrt(1 + s, branch=0)
    shifted = shift_symbolic_branches(expr, BranchDelta(sqrt_delta=1, winding_delta=1))
    assert "sqrt_1" in str(shifted)


def test_shift_symbolic_pow_branch():
    s = Var("s")
    expr = pow_branch(1 + s, 0.5, branch=0)
    shifted = shift_symbolic_branches(expr, BranchDelta(pow_delta=1, winding_delta=1))
    assert "branch=1" in str(shifted)


def test_continued_log_jet_rebuild_changes_constant_only():
    s = Var("s")
    path = circle_path(center=0, radius=1, turns=1, label="log loop")
    result = continued_jet_from_symbolic(
        log(1 + s),
        s,
        center=0,
        order=5,
        path=path,
        branch_points=[BranchPoint(0, kind="log")],
    )
    assert result.branch_delta.log_delta == 1
    assert result.continued_jet.branch_state.log_branch == 1
    # log branch shift adds 2*pi*i to the value coefficient; derivatives are unchanged.
    assert abs(result.continued_jet.coeff(0) - (result.original_jet.coeff(0) + 2j * math.pi)) < 1e-10
    for n in range(1, 5):
        assert abs(result.continued_jet.coeff(n) - result.original_jet.coeff(n)) < 1e-10


def test_continued_sqrt_jet_rebuild_flips_coefficients():
    s = Var("s")
    path = circle_path(center=0, radius=1, turns=1, label="sqrt loop")
    result = continued_jet_from_symbolic(
        sqrt(1 + s),
        s,
        center=0,
        order=4,
        path=path,
        branch_points=[BranchPoint(0, kind="sqrt")],
    )
    assert result.branch_delta.sqrt_delta == 1
    assert result.continued_jet.branch_state.sqrt_branch == 1
    for n in range(4):
        assert abs(result.continued_jet.coeff(n) + result.original_jet.coeff(n)) < 1e-10


def test_no_winding_rebuild_keeps_coefficients():
    s = Var("s")
    path = circle_path(center=5, radius=1, turns=1, label="far loop")
    result = continued_jet_from_symbolic(
        log(1 + s),
        s,
        center=0,
        order=5,
        path=path,
        branch_points=[BranchPoint(0, kind="log")],
    )
    assert result.branch_delta.is_zero
    assert result.max_coeff_delta < 1e-12
