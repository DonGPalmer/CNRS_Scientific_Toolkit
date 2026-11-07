"""Independent boundary tests for the opt-in experimental finite facade."""
import pytest
from cnrs.cnrs_h_finite_exact import RA, HurwitzJet
from cnrs.cnrs_h_limits import BoundedFiniteOps, FiniteLimits


def test_small_exact_arithmetic():
    api = BoundedFiniteOps()
    a = api.decode("1.2")
    b = api.decode("3")
    assert api.decode(api.encode(api.add(a, b))) == a + b
    assert api.multiply(a, b) == a * b
    assert api.product(api.jet([a, b]), api.jet([b]), 1).coefficient(1) == b * b


def test_input_digits_and_exponents_bounded_before_work():
    api = BoundedFiniteOps(FiniteLimits(max_digit_length=4, max_numerator_bits=16,
                                        max_denominator_power=3, max_degree=2,
                                        max_convolution_terms=6))
    with pytest.raises(ValueError):
        api.decode("1" * 10000)
    with pytest.raises(ValueError):
        api.coefficient(1 << 10000)
    with pytest.raises(ValueError):
        api.coefficient(1, 0, 10000)
    with pytest.raises(ValueError):
        api.jet([RA(1)] * 10000)
    with pytest.raises(ValueError):
        api.product(api.jet([RA(1)]), api.jet([RA(1)]), 3)


def test_result_limits_and_strict_types():
    api = BoundedFiniteOps(FiniteLimits(max_digit_length=10, max_numerator_bits=4,
                                        max_denominator_power=4, max_degree=3,
                                        max_convolution_terms=10))
    with pytest.raises(ValueError):
        api.multiply(RA(15), RA(15))
    with pytest.raises(TypeError):
        api.coefficient(True)
    with pytest.raises(TypeError):
        api.decode(123)
    with pytest.raises(ValueError):
        FiniteLimits(max_degree=0)


def test_inverse_only_units():
    api = BoundedFiniteOps()
    one = api.jet([RA(1), RA(1)])
    inv = api.inverse_truncated(one, 3)
    assert api.product(one, inv, 3) == HurwitzJet((RA(1),))
    with pytest.raises(ValueError):
        api.inverse_truncated(api.jet([RA(2)]), 2)
