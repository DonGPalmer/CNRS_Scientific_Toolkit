from cnrs.normalization import (
    NormalizationScope,
    normalize_addition,
    normalize_general_coefficients,
    multiplication_raw_coefficients,
    normalize_multiplication_convolution,
)
from cnrs.cnrs_add import add_cnrs
from cnrs.cnrs_mul import mul_cnrs
from cnrs.cnrs_repr import normalize_cnrs, cnrs_to_gaussian


def test_addition_normalization_is_scoped():
    result = normalize_addition("4", "4")
    assert result.scope == NormalizationScope.ADDITION_BOUNDED
    assert result.value == normalize_cnrs(add_cnrs("4", "4"))
    assert "addition transducer" in result.algorithm


def test_general_normalization_handles_unbounded_coefficients():
    result = normalize_general_coefficients([40, 37, 12])
    assert result.scope == NormalizationScope.GENERAL_FINITE_COEFFICIENTS
    # Verify by evaluating the raw polynomial manually.
    z0 = complex(-2, 1)
    expected = 40 + 37 * z0 + 12 * z0**2
    assert abs(cnrs_to_gaussian(result.value) - expected) < 1e-9


def test_multiplication_convolution_is_general_not_addition_scoped():
    a = "444444"
    b = "444444"
    raw = multiplication_raw_coefficients(a, b)
    assert max(raw) > 8  # not an addition raw alphabet
    result = normalize_multiplication_convolution(a, b)
    assert result.scope == NormalizationScope.MULTIPLICATION_CONVOLUTION
    assert result.value == mul_cnrs(a, b)
    assert "general" in result.algorithm
