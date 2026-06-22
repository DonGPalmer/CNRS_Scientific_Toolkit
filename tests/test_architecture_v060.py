"""v0.6.0 architecture and compatibility tests."""


def test_core_facade_exports_native_objects():
    from cnrs.core import CVal, Z0, DIGITS, BranchState, gaussian_to_cnrs_str

    assert Z0 == complex(-2, 1)
    assert set(DIGITS) == {0, 1, 2, 3, 4}
    assert gaussian_to_cnrs_str(0 + 0j) == "0"
    assert CVal.from_gaussian(1 + 0j).to_gaussian() == 1 + 0j
    bs = BranchState(log_branch=2)
    assert bs.log_branch == 2


def test_h_facade_exports_native_calculus_objects():
    from cnrs.h import CnrsH, CnrsHJet, jet_identity, verify_jet_chain_rule

    series = CnrsH.from_list([1, 2, 3])
    assert series.evaluate(0) == 1

    jet = jet_identity(var="s", center=0, order=5)
    assert isinstance(jet, CnrsHJet)

    # f(x)=x^2, g(s)=s, so the local chain rule should verify exactly.
    outer = CnrsHJet(CnrsH.from_list([0, 0, 2]), center=0, var="x")
    inner = jet_identity(var="s", center=0, order=5)
    result = verify_jet_chain_rule(outer, inner, order=5)
    assert result.passed


def test_validation_facade_contains_reference_autodiff_not_native_core():
    from cnrs.validation import CnrsDual, derivative, exp

    d = CnrsDual(0.0, 1.0)
    y = exp(d)
    assert abs(y.deriv - 1.0) < 1e-12
    assert abs(derivative(lambda x: exp(x), 0.0) - 1.0) < 1e-12


def test_workflow_facade_imports():
    from cnrs.workflows.scale_laws import ScaleLaw

    law = ScaleLaw.exponential(lam=0.5, scale=2.0)
    assert abs(law.evaluate(0.0) - 2.0) < 1e-12


def test_flat_imports_still_work():
    from cnrs.cnrs_h_jet import CnrsHJet
    from cnrs.autodiff import CnrsDual
    from cnrs import __version__

    assert __version__ == "0.6.0"
    assert CnrsHJet is not None
    assert CnrsDual is not None
