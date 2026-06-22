"""
test_cnrs_h_native.py
=====================
Tests for CnrsHNative: CNRS-H calculus with CNRS-A native coefficient arithmetic.

Each test documents what specific CNRS-A property is being verified.
"""
import pytest
from cnrs.cnrs_h_native import (
    CnrsHNative,
    NonGaussianCoefficientError,
    coeff_strings,
    verify_leibniz,
)
from cnrs.cnrs_value import CVal
from cnrs.cnrs_h import CnrsH
from cnrs.cnrs_add import add_cnrs
from cnrs.cnrs_mul import mul_cnrs
from cnrs.cnrs_repr import normalize_cnrs
from math import comb


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestConstruction:

    def test_from_gaussian_list_integers(self):
        h = CnrsHNative.from_gaussian_list([1, 2, 3])
        assert h.length == 3
        assert all(isinstance(c, CVal) for c in h.coeffs)

    def test_from_gaussian_list_gaussian_integers(self):
        h = CnrsHNative.from_gaussian_list([1+2j, 3-1j])
        assert h.coeff(0).to_gaussian() == 1+2j
        assert h.coeff(1).to_gaussian() == 3-1j

    def test_from_gaussian_list_non_gaussian_raises(self):
        with pytest.raises(NonGaussianCoefficientError):
            CnrsHNative.from_gaussian_list([1, 0.5])

    def test_from_gaussian_list_complex_non_gaussian_raises(self):
        with pytest.raises(NonGaussianCoefficientError):
            CnrsHNative.from_gaussian_list([1+0.3j])

    def test_zero(self):
        h = CnrsHNative.zero(4)
        assert h.length == 4
        assert all(c.to_gaussian() == 0 for c in h.coeffs)

    def test_one(self):
        h = CnrsHNative.one()
        assert h.coeff(0).to_gaussian() == 1

    def test_identity(self):
        h = CnrsHNative.identity()
        assert h.coeff(0).to_gaussian() == 0
        assert h.coeff(1).to_gaussian() == 1

    def test_constant(self):
        h = CnrsHNative.constant(5, length=3)
        assert h.coeff(0).to_gaussian() == 5
        assert h.coeff(1).to_gaussian() == 0
        assert h.coeff(2).to_gaussian() == 0

    def test_from_cnrs_h_roundtrip(self):
        original = CnrsH.from_list([1, 3, 2, 1])
        native = CnrsHNative.from_cnrs_h(original)
        back = native.to_cnrs_h()
        assert list(original.coeffs) == list(back.coeffs)

    def test_from_cnrs_h_non_gaussian_raises(self):
        h = CnrsH.from_list([1, 0.5, 1])
        with pytest.raises(NonGaussianCoefficientError):
            CnrsHNative.from_cnrs_h(h)


# ---------------------------------------------------------------------------
# Coefficients are CNRS-A digit strings
# ---------------------------------------------------------------------------

class TestCoefficientRepresentation:
    """Verify that coefficients are stored as CNRS-A digit strings, not Python numbers."""

    def test_coefficients_are_cval_instances(self):
        h = CnrsHNative.from_gaussian_list([1, 2, 3, 4])
        for c in h.coeffs:
            assert isinstance(c, CVal), f"Expected CVal, got {type(c).__name__}"

    def test_coefficient_strings_match_cnrs_repr(self):
        # 5 in CNRS-A base z0=-2+i should be '1310'
        h = CnrsHNative.from_gaussian_list([5])
        from cnrs.cnrs_repr import gaussian_to_cnrs_str, normalize_cnrs
        expected = normalize_cnrs(gaussian_to_cnrs_str(5+0j))
        assert h.coeff(0).s == expected

    def test_large_coefficient_stored_as_cnrs_string(self):
        # 252 = C(10,5), used in EGF convolution
        h = CnrsHNative.from_gaussian_list([252])
        g = h.coeff(0).to_gaussian()
        assert abs(g.real - 252) < 1e-10

    def test_gaussian_integer_coefficient(self):
        h = CnrsHNative.from_gaussian_list([3+4j])
        assert h.coeff(0).to_gaussian() == 3+4j

    def test_out_of_range_coeff_returns_zero_cval(self):
        h = CnrsHNative.from_gaussian_list([1, 2])
        zero = h.coeff(99)
        assert isinstance(zero, CVal)
        assert zero.to_gaussian() == 0


# ---------------------------------------------------------------------------
# Exact structural calculus (no arithmetic on coefficients)
# ---------------------------------------------------------------------------

class TestDifferentiateIntegrate:

    def test_differentiate_drops_d0(self):
        h = CnrsHNative.from_gaussian_list([5, 3, 2, 1])
        dh = h.differentiate()
        # d0 is dropped; remaining coefficients are untouched
        assert dh.length == 3
        assert dh.coeff(0).to_gaussian() == 3
        assert dh.coeff(1).to_gaussian() == 2
        assert dh.coeff(2).to_gaussian() == 1

    def test_differentiate_does_not_modify_coefficients(self):
        # The digit strings after differentiation are unchanged from input
        h = CnrsHNative.from_gaussian_list([0, 7, 4])
        dh = h.differentiate()
        assert dh.coeff(0).s == h.coeff(1).s
        assert dh.coeff(1).s == h.coeff(2).s

    def test_differentiate_constant_gives_zero(self):
        h = CnrsHNative.from_gaussian_list([3])
        dh = h.differentiate()
        assert dh.coeff(0).to_gaussian() == 0

    def test_integrate_prepends_constant(self):
        h = CnrsHNative.from_gaussian_list([2, 3])
        ih = h.integrate(constant=7)
        assert ih.length == 3
        assert ih.coeff(0).to_gaussian() == 7
        assert ih.coeff(1).to_gaussian() == 2
        assert ih.coeff(2).to_gaussian() == 3

    def test_integrate_existing_coefficients_unchanged(self):
        h = CnrsHNative.from_gaussian_list([2, 3])
        ih = h.integrate(constant=0)
        assert ih.coeff(1).s == h.coeff(0).s
        assert ih.coeff(2).s == h.coeff(1).s

    def test_diff_of_integral_is_identity(self):
        h = CnrsHNative.from_gaussian_list([1, 2, 3, 4])
        recovered = h.integrate(0).differentiate()
        assert recovered == h

    def test_nth_derivative(self):
        h = CnrsHNative.from_gaussian_list([1, 2, 3, 4, 5])
        d2 = h.nth_derivative(2)
        assert d2.coeff(0).to_gaussian() == 3
        assert d2.coeff(1).to_gaussian() == 4
        assert d2.coeff(2).to_gaussian() == 5


# ---------------------------------------------------------------------------
# CNRS-A native addition (FST transducer)
# ---------------------------------------------------------------------------

class TestNativeAddition:

    def test_addition_uses_fst(self):
        """Verify addition result matches add_cnrs directly."""
        a = CnrsHNative.from_gaussian_list([3, 5])
        b = CnrsHNative.from_gaussian_list([2, 4])
        result = a + b
        # The coefficient strings must match what add_cnrs produces
        expected_d0 = normalize_cnrs(add_cnrs(a.coeff(0).s, b.coeff(0).s))
        expected_d1 = normalize_cnrs(add_cnrs(a.coeff(1).s, b.coeff(1).s))
        assert result.coeff(0).s == expected_d0
        assert result.coeff(1).s == expected_d1

    def test_addition_correct_values(self):
        a = CnrsHNative.from_gaussian_list([1, 2, 3])
        b = CnrsHNative.from_gaussian_list([4, 5, 6])
        c = a + b
        assert c.coeff(0).to_gaussian() == 5
        assert c.coeff(1).to_gaussian() == 7
        assert c.coeff(2).to_gaussian() == 9

    def test_addition_commutative(self):
        a = CnrsHNative.from_gaussian_list([1, 3, 2])
        b = CnrsHNative.from_gaussian_list([2, 1, 4])
        assert a + b == b + a

    def test_addition_identity(self):
        h = CnrsHNative.from_gaussian_list([3, 7, 2])
        z = CnrsHNative.zero(3)
        assert h + z == h

    def test_addition_different_lengths(self):
        a = CnrsHNative.from_gaussian_list([1, 2, 3])
        b = CnrsHNative.from_gaussian_list([10])
        c = a + b
        assert c.coeff(0).to_gaussian() == 11
        assert c.coeff(1).to_gaussian() == 2
        assert c.coeff(2).to_gaussian() == 3

    def test_addition_gaussian_integer_coefficients(self):
        a = CnrsHNative.from_gaussian_list([1+2j, 3-1j])
        b = CnrsHNative.from_gaussian_list([2-1j, 1+3j])
        c = a + b
        assert c.coeff(0).to_gaussian() == 3+1j
        assert c.coeff(1).to_gaussian() == 4+2j


# ---------------------------------------------------------------------------
# CNRS-A native multiplication (EGF convolution with CVal arithmetic)
# ---------------------------------------------------------------------------

class TestNativeMultiplication:

    def test_multiplication_uses_cnrs_a_arithmetic(self):
        """Verify each term uses mul_cnrs, not Python multiplication."""
        a = CnrsHNative.from_gaussian_list([2, 3])
        b = CnrsHNative.from_gaussian_list([4, 5])
        result = a * b
        # c_0 = C(0,0) * a_0 * b_0 = 1 * 2 * 4 = 8
        expected_c0 = normalize_cnrs(mul_cnrs(mul_cnrs("1", "2"), "4"))
        assert result.coeff(0).s == expected_c0

    def test_multiplication_constant_by_one(self):
        h = CnrsHNative.from_gaussian_list([3, 7, 2])
        one = CnrsHNative.one()
        assert h * one.pad(3) == h.pad(h.length + 2)

    def test_multiplication_correct_egf_convolution(self):
        # f = 1 + s (d0=1, d1=1)   g = 1 + s
        # f*g = 1 + 2s + s^2, EGF coeffs: [1, 2, 2]
        f = CnrsHNative.from_gaussian_list([1, 1])
        g = CnrsHNative.from_gaussian_list([1, 1])
        fg = f * g
        assert fg.coeff(0).to_gaussian() == 1
        assert fg.coeff(1).to_gaussian() == 2
        assert fg.coeff(2).to_gaussian() == 2

    def test_multiplication_exp_times_exp(self):
        # exp(s) * exp(s) = exp(2s), EGF coeffs are 2^n
        # Truncated to 5 terms: first 5 coefficients should be 1,2,4,8,16
        exp5 = CnrsHNative.from_gaussian_list([1, 1, 1, 1, 1])
        prod = exp5 * exp5
        for n in range(5):
            assert prod.coeff(n).to_gaussian() == 2**n

    def test_multiplication_commutative(self):
        f = CnrsHNative.from_gaussian_list([1, 2, 1])
        g = CnrsHNative.from_gaussian_list([3, 1])
        assert f * g == g * f

    def test_multiplication_coefficients_are_cval(self):
        f = CnrsHNative.from_gaussian_list([2, 3])
        g = CnrsHNative.from_gaussian_list([4, 5])
        fg = f * g
        for c in fg.coeffs:
            assert isinstance(c, CVal)

    def test_scalar_multiply(self):
        h = CnrsHNative.from_gaussian_list([1, 2, 3])
        scaled = h * 3
        assert scaled.coeff(0).to_gaussian() == 3
        assert scaled.coeff(1).to_gaussian() == 6
        assert scaled.coeff(2).to_gaussian() == 9


# ---------------------------------------------------------------------------
# Leibniz rule D(f*g) = Df*g + f*Dg — verified in CNRS-A coefficient space
# ---------------------------------------------------------------------------

class TestLeibnizRule:

    def _check_leibniz(self, f, g, order=6):
        result = verify_leibniz(f, g, order=order)
        assert result["passed"], (
            f"Leibniz failed: max_error={result['max_error']}\n"
            f"  LHS: {coeff_strings(result['lhs'])}\n"
            f"  RHS: {coeff_strings(result['rhs'])}"
        )
        # LHS and RHS coefficient strings must be identical
        for i in range(order):
            assert result["lhs"].coeff(i).s == result["rhs"].coeff(i).s, (
                f"Coefficient strings differ at index {i}: "
                f"{result['lhs'].coeff(i).s!r} != {result['rhs'].coeff(i).s!r}"
            )

    def test_leibniz_polynomials(self):
        f = CnrsHNative.from_gaussian_list([1, 2, 1])      # 1 + 2s + s^2/2
        g = CnrsHNative.from_gaussian_list([3, 1, 0, 1])   # 3 + s + s^3/6
        self._check_leibniz(f, g)

    def test_leibniz_exp_times_linear(self):
        exp5 = CnrsHNative.from_gaussian_list([1, 1, 1, 1, 1])
        linear = CnrsHNative.from_gaussian_list([1, 2])
        self._check_leibniz(exp5, linear)

    def test_leibniz_exp_times_exp(self):
        exp5 = CnrsHNative.from_gaussian_list([1, 1, 1, 1, 1])
        self._check_leibniz(exp5, exp5)

    def test_leibniz_constant_factors(self):
        f = CnrsHNative.constant(3, length=4)
        g = CnrsHNative.from_gaussian_list([1, 2, 1])
        self._check_leibniz(f, g)

    def test_leibniz_gaussian_integer_coefficients(self):
        f = CnrsHNative.from_gaussian_list([1+1j, 2, 1-1j])
        g = CnrsHNative.from_gaussian_list([2+0j, 1+1j])
        self._check_leibniz(f, g)

    def test_leibniz_lhs_rhs_strings_identical(self):
        """The CNRS-A digit strings — not just the values — must match."""
        f = CnrsHNative.from_gaussian_list([1, 3, 2, 1])
        g = CnrsHNative.from_gaussian_list([2, 1, 3])
        result = verify_leibniz(f, g, order=5)
        for i in range(5):
            assert result["lhs"].coeff(i).s == result["rhs"].coeff(i).s


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

class TestEvaluation:

    def test_constant_evaluates_correctly(self):
        h = CnrsHNative.from_gaussian_list([7])
        assert abs(h.evaluate(0) - 7) < 1e-12
        assert abs(h.evaluate(3.5) - 7) < 1e-12

    def test_identity_evaluates_correctly(self):
        h = CnrsHNative.identity()
        assert abs(h.evaluate(0) - 0) < 1e-12
        assert abs(h.evaluate(2.5) - 2.5) < 1e-12

    def test_polynomial_evaluates_correctly(self):
        # f coeffs [1, 2, 2] represents 1 + 2s + s^2
        h = CnrsHNative.from_gaussian_list([1, 2, 2])
        assert abs(h.evaluate(0) - 1) < 1e-12
        assert abs(h.evaluate(1) - 4) < 1e-12   # 1 + 2 + 1
        assert abs(h.evaluate(2) - 9) < 1e-12   # 1 + 4 + 4

    def test_matches_cnrs_h_evaluation(self):
        coeffs = [1, 3, 2, 1, 4]
        native = CnrsHNative.from_gaussian_list(coeffs)
        standard = CnrsH.from_list(coeffs)
        for s in [0, 0.5, 1.0, -1.0, 1+1j]:
            assert abs(native.evaluate(s) - standard.evaluate(s)) < 1e-10


# ---------------------------------------------------------------------------
# Truncation and padding
# ---------------------------------------------------------------------------

class TestTruncatePad:

    def test_truncate(self):
        h = CnrsHNative.from_gaussian_list([1, 2, 3, 4, 5])
        t = h.truncate(3)
        assert t.length == 3
        assert t.coeff(0).to_gaussian() == 1
        assert t.coeff(2).to_gaussian() == 3

    def test_pad(self):
        h = CnrsHNative.from_gaussian_list([1, 2])
        p = h.pad(5)
        assert p.length == 5
        assert p.coeff(2).to_gaussian() == 0
        assert p.coeff(4).to_gaussian() == 0

    def test_truncate_then_pad_roundtrip(self):
        h = CnrsHNative.from_gaussian_list([1, 2, 3])
        assert h.truncate(3).pad(3) == h


# ---------------------------------------------------------------------------
# coeff_strings diagnostic
# ---------------------------------------------------------------------------

class TestCoeffStrings:

    def test_coeff_strings_returns_cnrs_strings(self):
        h = CnrsHNative.from_gaussian_list([1, 5, 3])
        strings = coeff_strings(h)
        assert strings[0] == "1"
        assert strings[1] == "1310"   # 5 in CNRS-A base z0=-2+i
        assert strings[2] == "3"
