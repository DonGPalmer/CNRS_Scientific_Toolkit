import math

from cnrs.cnrs_scientific_state import CnrsScientificState, scientific_state_from_symbolic
from cnrs.symbolic import Var, exp, log, sqrt
from cnrs.cnrs_h_path import BranchPoint, circle_path


def test_state_from_symbolic_evaluates_scale_law_at_center():
    s = Var("s")
    state = CnrsScientificState.from_symbolic(exp(0.1 * s), s, center=-12, order=8)
    assert state.var == "s"
    assert state.scale_unit == "nat"
    assert abs(state.evaluate(-12) - math.exp(-1.2)) < 1e-10
    assert state.valid_for(-12) is True


def test_state_differentiation_uses_cnrs_h_shift():
    s = Var("s")
    state = scientific_state_from_symbolic(exp(0.1 * s), s, center=0, order=8)
    dstate = state.diff(order=7)
    assert abs(dstate.evaluate(0) - 0.1) < 1e-10
    assert dstate.source_expr is not None


def test_state_observation_maps_preserve_complex_until_requested():
    s = Var("s")
    state = CnrsScientificState.from_symbolic(exp(1j * s), s, center=0, order=10)
    raw = state.observe([0, 0.1], "complex")
    assert len(raw) == 2
    abs2 = state.observe([0, 0.1], "abs2")
    assert abs(float(abs2[0]) - 1.0) < 1e-8
    table = state.observation_table([0, 0.1, 0.2])
    assert "phase_current" in table


def test_state_continuation_rebuilds_log_constant_coefficient():
    s = Var("s")
    state = CnrsScientificState.from_symbolic(log(1 + s), s, center=0, order=6)
    path = circle_path(center=0, radius=1, turns=1, label="unit loop")
    continued = state.continue_along(path, branch_points=[BranchPoint(0, kind="log")])
    assert continued.branch_state.log_branch == state.branch_state.log_branch + 1
    assert abs((continued.evaluate(0) - state.evaluate(0)) - 2j * math.pi) < 1e-10
    assert continued.source_expr is not None


def test_state_continuation_sqrt_flips_coefficients():
    s = Var("s")
    state = CnrsScientificState.from_symbolic(sqrt(1 + s), s, center=0, order=6)
    path = circle_path(center=0, radius=1, turns=1)
    continued = state.continue_along(path, branch_points=[BranchPoint(0, kind="sqrt")])
    assert continued.branch_state.sqrt_branch % 2 == 1
    assert abs(continued.evaluate(0) + state.evaluate(0)) < 1e-10


def test_state_metadata_only_continuation_when_no_source_expr():
    s = Var("s")
    state = CnrsScientificState.from_symbolic(log(1 + s), s, center=0, order=6)
    wrapped = CnrsScientificState.from_jet(state.jet, source_expr=None)
    path = circle_path(center=0, radius=1, turns=1)
    continued = wrapped.continue_along(path, branch_points=[BranchPoint(0, kind="log")])
    assert continued.branch_state.log_branch == 1
    assert abs(continued.evaluate(0) - wrapped.evaluate(0)) < 1e-12
    assert continued.metadata["continuation"] == "metadata_only"


def test_state_taylor_model_wrapper():
    s = Var("s")
    state = CnrsScientificState.from_symbolic(exp(s), s, center=0, order=8)
    model = state.to_taylor_model(sample_point=0.1)
    value, radius = model.enclosure(0.1)
    assert abs(value - state.evaluate(0.1)) < 1e-15
    assert radius is not None


def test_state_summary_contains_core_metadata():
    s = Var("s")
    state = CnrsScientificState.from_symbolic(exp(s), s, center=0, order=4, metadata={"workflow": "test"})
    summary = state.summary()
    assert "CnrsScientificState" in summary
    assert "unit='nat'" in summary
    assert "finite_local_representation" in summary
