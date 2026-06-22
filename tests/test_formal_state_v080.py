from cnrs.cnrs_formal_state import BranchIndex, CnrsFormalState
from cnrs.cnrs_value import CVal
from cnrs.cnrs_h_native import CnrsHNative


def test_formal_state_from_gaussian_coeffs():
    s = CnrsFormalState.from_gaussian_coeffs(1, [1, 2, 3], branch_index=2, branch_kind="log")
    assert isinstance(s.value, CVal)
    assert isinstance(s.jet, CnrsHNative)
    assert s.branch.index == 2
    assert s.order == 2


def test_formal_state_differentiation_preserves_branch():
    s = CnrsFormalState.from_gaussian_coeffs(0, [5, 3, 2], branch_index=1)
    ds = s.differentiate()
    assert ds.branch == s.branch
    assert ds.jet.coeff(0).to_gaussian() == 3
    assert ds.jet.coeff(1).to_gaussian() == 2


def test_formal_state_integration_prepends_constant():
    s = CnrsFormalState.from_gaussian_coeffs(0, [3, 2])
    is_ = s.integrate(7)
    assert is_.jet.coeff(0).to_gaussian() == 7
    assert is_.jet.coeff(1).to_gaussian() == 3


def test_branch_shift_explicit():
    s = CnrsFormalState(CVal.from_gaussian(1), BranchIndex(0, "log"), CnrsHNative.from_gaussian_list([1]))
    t = s.add_branch(3, note="looped around origin")
    assert t.branch.index == 3
    assert t.branch.kind == "log"
    assert t.branch.note == "looped around origin"


def test_coefficient_strings_are_cnrs_strings():
    s = CnrsFormalState.from_gaussian_coeffs(0, [1, 2])
    assert all(isinstance(x, str) for x in s.coefficient_strings())
