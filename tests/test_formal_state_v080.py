from cnrs.formal_state import CnrsFormalState
from cnrs.cnrs_value import CVal
from cnrs.cnrs_h_native import CnrsHNative


def test_formal_state_from_gaussian_coefficients():
    s = CnrsFormalState.from_gaussian_coefficients(3 + 2j, [1, 2, 3], branch_state=1, center=0, domain="unit")
    assert isinstance(s.value, CVal)
    assert isinstance(s.coefficients, CnrsHNative)
    assert s.branch_state == 1
    assert s.order == 2
    assert s.domain == "unit"


def test_formal_state_differentiation_preserves_metadata():
    s = CnrsFormalState.from_gaussian_coefficients(0, [5, 3, 2], branch_state="k", center=1)
    ds = s.differentiate()
    assert ds.coefficients.coeff(0).to_gaussian() == 3
    assert ds.branch_state == "k"
    assert ds.center == 1
    assert ds.metadata["operation"] == "differentiate"


def test_formal_state_integration_prepends_constant():
    s = CnrsFormalState.from_gaussian_coefficients(0, [2, 3])
    is_ = s.integrate(7)
    assert is_.coefficients.coeff(0).to_gaussian() == 7
    assert is_.coefficients.coeff(1).to_gaussian() == 2
