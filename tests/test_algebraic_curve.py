import sympy as sp
import pytest

from cnrs.algebraic_curve import (
    AlgebraicCurve,
    AlgebraicCurveError,
    finite_branch_points,
)


def _as_complex_set(values):
    return {complex(sp.N(v, 30)) for v in values}


def test_accepts_string_polynomial_and_reports_degrees():
    curve = AlgebraicCurve.from_expression("w**2 - z*(z-1)")
    assert curve.degree_w == 2
    assert curve.degree_z == 2
    assert sp.expand(curve.expression) == sp.expand(curve.w**2 - curve.z * (curve.z - 1))


def test_rejects_nonpolynomial_curve():
    with pytest.raises(AlgebraicCurveError):
        AlgebraicCurve.from_expression("exp(w) - z")


def test_square_root_two_finite_branch_points():
    analysis = finite_branch_points("w**2 - z*(z-1)")
    assert sp.factor(analysis.resultant) == -4 * analysis.curve.z * (analysis.curve.z - 1)
    assert _as_complex_set(analysis.finite_branch_values) == {0j, 1 + 0j}
    assert all(len(point.ramification_points) == 1 for point in analysis.branch_points)
    assert all(point.ramification_points[0].multiplicity == 2 for point in analysis.branch_points)
    assert all(complex(sp.N(point.ramification_points[0].w)) == 0j for point in analysis.branch_points)


def test_cubic_family_branch_values_plus_minus_two():
    analysis = finite_branch_points("w**3 - 3*w + z")
    assert _as_complex_set(analysis.finite_branch_values) == {-2 + 0j, 2 + 0j}
    ramification = {
        complex(sp.N(point.z)): complex(sp.N(point.ramification_points[0].w))
        for point in analysis.branch_points
    }
    assert ramification[-2 + 0j] == -1 + 0j
    assert ramification[2 + 0j] == 1 + 0j
    assert all(point.ramification_points[0].multiplicity == 2 for point in analysis.branch_points)


def test_unbranched_graph_has_no_finite_branch_points():
    analysis = finite_branch_points("w - z**2")
    assert analysis.branch_points == ()
    assert analysis.resultant == 1


def test_repeated_component_is_rejected():
    curve = AlgebraicCurve.from_expression("(w-z)**2")
    with pytest.raises(AlgebraicCurveError, match="resultant is identically zero"):
        curve.analyze_finite_branch_points()


def test_numerical_mode_returns_verified_candidates():
    analysis = finite_branch_points("w**5 - w + z", numerical=True, precision=40)
    assert len(analysis.branch_points) == 4
    assert all(point.ramification_points for point in analysis.branch_points)
    assert all(point.ramification_points[0].residual < 1e-7 for point in analysis.branch_points)
