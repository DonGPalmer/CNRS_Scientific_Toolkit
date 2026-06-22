"""
test_cval_native_arithmetic.py
==============================
Tests for fully-native CVal arithmetic — addition, negation, subtraction,
and multiplication — verifying that no operation falls back to Gaussian
(Python complex) arithmetic.

The key mathematical fact under test:
    -1  in base z0 = -2+i  is the finite digit string "144"
    i.e. 1*z0^2 + 4*z0 + 4 = (3-4i) + (-8+4i) + 4 = -1

This makes negation a pure mul_cnrs call, and subtraction a + (-b).
"""
import pytest
from cnrs.cnrs_value import CVal, _NEG_ONE
from cnrs.cnrs_mul import mul_cnrs
from cnrs.cnrs_add import add_cnrs
from cnrs.cnrs_repr import normalize_cnrs, cnrs_to_gaussian


# ---------------------------------------------------------------------------
# The -1 constant
# ---------------------------------------------------------------------------

class TestNegOneConstant:

    def test_neg_one_string_is_144(self):
        assert _NEG_ONE == "144"

    def test_neg_one_evaluates_to_minus_one(self):
        assert cnrs_to_gaussian(_NEG_ONE) == -1+0j

    def test_neg_one_derivation(self):
        """1*z0^2 + 4*z0 + 4 = -1 in base z0 = -2+i."""
        Z0 = complex(-2, 1)
        value = 1 * Z0**2 + 4 * Z0 + 4
        assert abs(value - (-1+0j)) < 1e-12

    def test_neg_one_cval_construction(self):
        v = CVal(_NEG_ONE)
        assert v.to_gaussian() == -1+0j


# ---------------------------------------------------------------------------
# Native negation
# ---------------------------------------------------------------------------

class TestNativeNegation:

    def test_neg_routes_through_mul_cnrs(self):
        """__neg__ output must match mul_cnrs(_NEG_ONE, v.s) directly."""
        for z in [1+0j, 2+3j, 7-2j, -4+1j, 5j]:
            v = CVal.from_gaussian(z)
            expected_str = normalize_cnrs(mul_cnrs(_NEG_ONE, v.s))
            result = -v
            assert result.s == expected_str, (
                f"neg({z}): got {result.s!r}, expected {expected_str!r}"
            )

    def test_neg_of_zero_is_zero(self):
        assert (-CVal.from_gaussian(0+0j)).to_gaussian() == 0

    def test_neg_of_one(self):
        result = -CVal.from_gaussian(1+0j)
        assert result.to_gaussian() == -1+0j
        assert result.s == "144"

    def test_neg_of_neg_one_is_one(self):
        result = -CVal(_NEG_ONE)
        assert result.to_gaussian() == 1+0j
        assert result.s == "1"

    def test_neg_involution(self):
        """neg(neg(v)) == v for all tested values."""
        for z in [1+0j, 3-2j, -5+4j, 0+7j, 10+0j]:
            v = CVal.from_gaussian(z)
            assert -(-v) == v

    def test_neg_correct_values(self):
        cases = [
            (1+0j,   -1+0j),
            (2+3j,   -2-3j),
            (-4+1j,   4-1j),
            (5j,     -5j),
            (7-2j,   -7+2j),
            (-1+0j,   1+0j),
            (10-3j, -10+3j),
        ]
        for z, expected in cases:
            result = (-CVal.from_gaussian(z)).to_gaussian()
            assert abs(result - expected) < 1e-10, f"neg({z}): got {result}"

    def test_neg_result_is_cval(self):
        v = CVal.from_gaussian(3+2j)
        assert isinstance(-v, CVal)

    def test_neg_result_is_canonical(self):
        """Digit string of negation must already be in canonical form."""
        for z in [1+0j, 5+0j, 3-2j, -7+4j]:
            v = CVal.from_gaussian(z)
            result = -v
            assert result.s == normalize_cnrs(result.s), (
                f"neg({z}) digit string {result.s!r} is not canonical"
            )


# ---------------------------------------------------------------------------
# Native subtraction
# ---------------------------------------------------------------------------

class TestNativeSubtraction:

    def test_sub_routes_through_add_and_neg(self):
        """a - b must equal a + (-b) at the digit-string level."""
        pairs = [
            (5+0j, 2+0j),
            (3+4j, 1+2j),
            (7-2j, 3-5j),
            (0+0j, 4+1j),
            (1+0j, 1+0j),
        ]
        for za, zb in pairs:
            a = CVal.from_gaussian(za)
            b = CVal.from_gaussian(zb)
            # subtract: a - b
            sub_result = a - b
            # same via a + (-b)
            add_neg_result = a + (-b)
            assert sub_result.s == add_neg_result.s, (
                f"({za}) - ({zb}): sub gave {sub_result.s!r}, "
                f"a+(-b) gave {add_neg_result.s!r}"
            )

    def test_sub_correct_values(self):
        cases = [
            (5+0j, 2+0j, 3+0j),
            (3+4j, 1+2j, 2+2j),
            (7-2j, 3-5j, 4+3j),
            (1+0j, 1+0j, 0+0j),
            (0+0j, 4+1j, -4-1j),
            (2+3j, 5+1j, -3+2j),
        ]
        for za, zb, expected in cases:
            result = (CVal.from_gaussian(za) - CVal.from_gaussian(zb)).to_gaussian()
            assert abs(result - expected) < 1e-10, (
                f"({za}) - ({zb}): got {result}, expected {expected}"
            )

    def test_sub_self_is_zero(self):
        for z in [1+0j, 3+2j, -4+1j]:
            v = CVal.from_gaussian(z)
            result = v - v
            assert result.to_gaussian() == 0

    def test_sub_zero_is_identity(self):
        zero = CVal.from_gaussian(0+0j)
        for z in [1+0j, 3+2j, -4+1j]:
            v = CVal.from_gaussian(z)
            assert v - zero == v

    def test_sub_result_is_cval(self):
        a = CVal.from_gaussian(5+3j)
        b = CVal.from_gaussian(2+1j)
        assert isinstance(a - b, CVal)

    def test_sub_result_is_canonical(self):
        a = CVal.from_gaussian(7+0j)
        b = CVal.from_gaussian(3+0j)
        result = a - b
        assert result.s == normalize_cnrs(result.s)

    def test_sub_antisymmetry(self):
        """a - b = -(b - a)."""
        for za, zb in [(5+2j, 3+1j), (1+0j, 4+0j), (2+3j, 2-1j)]:
            a = CVal.from_gaussian(za)
            b = CVal.from_gaussian(zb)
            assert a - b == -(b - a)

    def test_sub_gaussian_integer_coefficients(self):
        a = CVal.from_gaussian(3+5j)
        b = CVal.from_gaussian(1+2j)
        result = a - b
        assert result.to_gaussian() == 2+3j


# ---------------------------------------------------------------------------
# All four operations together: ring axioms
# ---------------------------------------------------------------------------

class TestRingAxioms:
    """Spot-check that CVal satisfies ring axioms using native arithmetic only."""

    SAMPLES = [0+0j, 1+0j, -1+0j, 2+3j, -4+1j, 5-2j]

    def test_additive_commutativity(self):
        for za in self.SAMPLES:
            for zb in self.SAMPLES:
                a, b = CVal.from_gaussian(za), CVal.from_gaussian(zb)
                assert a + b == b + a

    def test_additive_associativity(self):
        for za in self.SAMPLES[:4]:
            for zb in self.SAMPLES[:4]:
                for zc in self.SAMPLES[:4]:
                    a = CVal.from_gaussian(za)
                    b = CVal.from_gaussian(zb)
                    c = CVal.from_gaussian(zc)
                    assert (a + b) + c == a + (b + c)

    def test_additive_inverse(self):
        zero = CVal.from_gaussian(0+0j)
        for z in self.SAMPLES:
            v = CVal.from_gaussian(z)
            assert v + (-v) == zero
            assert (-v) + v == zero

    def test_multiplicative_commutativity(self):
        for za in self.SAMPLES:
            for zb in self.SAMPLES:
                a, b = CVal.from_gaussian(za), CVal.from_gaussian(zb)
                assert a * b == b * a

    def test_distributivity(self):
        """a * (b + c) == a*b + a*c."""
        for za in self.SAMPLES[:4]:
            for zb in self.SAMPLES[:4]:
                for zc in self.SAMPLES[:4]:
                    a = CVal.from_gaussian(za)
                    b = CVal.from_gaussian(zb)
                    c = CVal.from_gaussian(zc)
                    assert a * (b + c) == a * b + a * c


# ---------------------------------------------------------------------------
# CnrsHNative subtraction is now fully native
# ---------------------------------------------------------------------------

class TestCnrsHNativeSubtractionNative:
    """
    With CVal.__neg__ and CVal.__sub__ now native, CnrsHNative subtraction
    must produce coefficient strings consistent with native arithmetic only.
    """

    def test_subtraction_result_coefficients_are_cval(self):
        from cnrs.cnrs_h_native import CnrsHNative
        f = CnrsHNative.from_gaussian_list([5, 3, 2])
        g = CnrsHNative.from_gaussian_list([2, 1, 1])
        result = f - g
        for c in result.coeffs:
            assert isinstance(c, CVal)

    def test_subtraction_correct_values(self):
        from cnrs.cnrs_h_native import CnrsHNative
        f = CnrsHNative.from_gaussian_list([5, 3, 2])
        g = CnrsHNative.from_gaussian_list([2, 1, 1])
        result = f - g
        assert result.coeff(0).to_gaussian() == 3
        assert result.coeff(1).to_gaussian() == 2
        assert result.coeff(2).to_gaussian() == 1

    def test_subtraction_string_matches_native_path(self):
        """Each coefficient string must equal add_cnrs(a.s, neg(b).s)."""
        from cnrs.cnrs_h_native import CnrsHNative
        f = CnrsHNative.from_gaussian_list([7, 4, 3])
        g = CnrsHNative.from_gaussian_list([3, 1, 2])
        result = f - g
        for i in range(3):
            expected = normalize_cnrs(
                add_cnrs(f.coeff(i).s, (-g.coeff(i)).s)
            )
            assert result.coeff(i).s == expected, (
                f"coeff {i}: got {result.coeff(i).s!r}, expected {expected!r}"
            )

    def test_negation_of_cnrs_h_native(self):
        from cnrs.cnrs_h_native import CnrsHNative
        f = CnrsHNative.from_gaussian_list([1, 2, 3])
        neg_f = -f
        for i in range(3):
            assert neg_f.coeff(i).s == (-f.coeff(i)).s

    def test_diff_of_sum_is_sum_of_diffs(self):
        """(f + g)' = f' + g' — fully native path."""
        from cnrs.cnrs_h_native import CnrsHNative
        f = CnrsHNative.from_gaussian_list([1, 3, 2, 4])
        g = CnrsHNative.from_gaussian_list([2, 1, 3, 1])
        lhs = (f + g).differentiate()
        rhs = f.differentiate() + g.differentiate()
        assert lhs == rhs
