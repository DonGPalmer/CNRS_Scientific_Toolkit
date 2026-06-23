from cnrs.formal_state import CnrsFormalState


def test_formal_state_well_formed_report():
    state = CnrsFormalState.from_gaussian_coefficients(1, [1, 2, 3], branch_state=0)
    report = state.preservation_report()
    assert report["well_formed"] is True
    assert report["value_type"] == "CVal"
    assert report["coefficient_type"] == "CnrsHNative"


def test_formal_state_differentiation_preserves_structure():
    state = CnrsFormalState.from_gaussian_coefficients(1, [5, 3, 2])
    d = state.differentiate()
    assert d.well_formed
    assert d.coefficients.coeff(0).to_gaussian() == 3
    assert d.metadata["operation"] == "differentiate"


def test_formal_state_add_and_multiply_preserve_well_formedness():
    a = CnrsFormalState.from_gaussian_coefficients(2, [1, 1], branch_state="main")
    b = CnrsFormalState.from_gaussian_coefficients(3, [2, 1], branch_state="main")
    s = a + b
    p = a * b
    assert s.well_formed and p.well_formed
    assert s.value.to_gaussian() == 5
    assert p.value.to_gaussian() == 6
    assert s.branch_state == "main"
    assert p.metadata["operation"] == "multiply"
