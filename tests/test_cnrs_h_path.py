import cmath
import math

import pytest

from cnrs import BranchState
from cnrs.cnrs_h_path import (
    BranchPoint,
    ContinuationPath,
    ContinuationPathError,
    circle_path,
    continue_log,
    continue_sqrt,
    update_branch_state_along_path,
    winding_events,
    winding_number,
)
from cnrs.cnrs_h_jet import jet_from_symbolic
from cnrs.symbolic import Var, log


def test_circle_path_winds_once_around_zero():
    path = circle_path(center=0, radius=1, turns=1, samples_per_turn=32)
    assert winding_number(path, 0) == 1


def test_reversed_circle_winds_negative_once():
    path = circle_path(center=0, radius=1, turns=1, samples_per_turn=32).reversed()
    assert winding_number(path, 0) == -1


def test_open_path_winding_requires_closed_by_default():
    path = ContinuationPath([1, 1j, -1], label="open")
    with pytest.raises(ContinuationPathError):
        winding_number(path, 0)


def test_path_crossing_branch_point_raises():
    path = ContinuationPath([1, 0, 1], label="bad")
    with pytest.raises(ContinuationPathError):
        winding_number(path, 0)


def test_log_branch_updates_by_winding():
    path = circle_path(turns=2, samples_per_turn=32)
    state = update_branch_state_along_path(BranchState(log_branch=1), path, [BranchPoint(0, kind="log")])
    assert state.log_branch == 3
    assert state.winding == 2


def test_sqrt_branch_updates_by_parity():
    once = circle_path(turns=1, samples_per_turn=32)
    twice = circle_path(turns=2, samples_per_turn=32)
    s1 = update_branch_state_along_path(BranchState(), once, [BranchPoint(0, kind="sqrt")])
    s2 = update_branch_state_along_path(BranchState(), twice, [BranchPoint(0, kind="sqrt")])
    assert s1.sqrt_branch == 1
    assert s2.sqrt_branch == 0


def test_continue_log_after_one_loop():
    path = circle_path(turns=1, samples_per_turn=32)
    value = continue_log(1, path, BranchState())
    assert abs(value - 2j * math.pi) < 1e-12


def test_continue_sqrt_after_one_loop_changes_sign():
    path = circle_path(turns=1, samples_per_turn=32)
    assert abs(continue_sqrt(1, path, BranchState()) + 1) < 1e-12


def test_winding_events_for_multiple_branch_points():
    path = circle_path(center=0, radius=2, turns=1, samples_per_turn=64)
    events = winding_events(path, [BranchPoint(0, kind="log"), BranchPoint(5, kind="log")])
    assert len(events) == 1
    assert events[0].winding == 1


def test_jet_continue_along_records_branch_state_and_history():
    s = Var("s")
    jet = jet_from_symbolic(log(1 + s, branch=0), s, center=0, order=5)
    path = circle_path(turns=1, samples_per_turn=32, label="unit loop")
    continued = jet.continue_along(path, branch_points=[BranchPoint(0, kind="log")])
    assert continued.branch_state.log_branch == 1
    assert continued.branch_state.winding == 1
    assert continued.path_history
    assert "winding=1" in continued.branch_note


def test_path_imports_from_public_h_facade():
    from cnrs.h import ContinuationPath as FacadePath, circle_path as facade_circle

    assert FacadePath([1, 1j, 1]).points[0] == 1 + 0j
    assert facade_circle(turns=1).winding_number(0) == 1
