"""
test_lagrange_inversion.py
==========================
Tests for native Lagrange inversion (``invert_native``) in CNRS-A arithmetic.

The compositional inverse g of f satisfies f(g(s)) = s.  All coefficient
arithmetic runs through CVal (CNRS-A digit strings via add_cnrs / mul_cnrs).

Correctness standard: ``strings_match=True`` — every output coefficient
digit string is identical to the independently-computed expected value.
Numeric checks (``max_error``) are a secondary confirmation.

Test cases
----------
1. Identity:        f(s) = s                  → g(s) = s
2. Log from exp:    f(s) = exp(s)−1           → g(s) = log(1+s)
                    g_n = (−1)^{n−1} · (n−1)!   (integer, known closed form)
3. Quadratic shift: f(s) = s + s²/2!          → double-checked at digit level
4. Gaussian unit:   f(s) = i·s + s²/2!        → f′(0) = i, g′(0) = −i
5. Negation:        f(s) = −s                  → g(s) = −s (self-inverse)
6. Round-trip:      compose(f, invert(f)) = id  checked across multiple f
7. Error conditions: f(0)≠0 and f′(0) not a Gaussian unit both raise
                     InversionError correctly
"""

import math
import pytest

from cnrs.cnrs_h_native import (
    CnrsHNative,
    InversionError,
    compose_native,
    invert_native,
    verify_inversion,
    coeff_strings,
)
from cnrs.cnrs_value import CVal


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _g(result: dict) -> CnrsHNative:
    return result["g"]

def _gaussian_coeffs(h: CnrsHNative) -> list:
    return [c.to_gaussian() for c in h.coeffs]


# ---------------------------------------------------------------------------
# 1. Identity: f(s) = s  →  g(s) = s
# ---------------------------------------------------------------------------

class TestIdentityInversion:

    def test_identity_coefficients(self):
        """f(s) = s is its own compositional inverse."""
        f = CnrsHNative.from_gaussian_list([0, 1, 0, 0, 0, 0, 0, 0])
        g = invert_native(f, 8)
        coeffs = _gaussian_coeffs(g)
        assert coeffs[0] == 0
        assert coeffs[1] == 1
        assert all(c == 0 for c in coeffs[2:])

    def test_identity_digit_strings(self):
        """Digit strings for the identity inverse must be exact."""
        f = CnrsHNative.from_gaussian_list([0, 1, 0, 0, 0, 0])
        g = invert_native(f, 6)
        assert g.coeff(0).s == "0"
        assert g.coeff(1).s == "1"
        for n in range(2, 6):
            assert g.coeff(n).s == "0", f"g_{n} digit string should be '0'"

    def test_identity_verify(self):
        """verify_inversion reports strings_match=True and max_error=0."""
        f = CnrsHNative.from_gaussian_list([0, 1, 0, 0, 0, 0, 0])
        r = verify_inversion(f, 7)
        assert r["strings_match"] is True
        assert r["max_error"] == 0.0
        assert r["passed"] is True


# ---------------------------------------------------------------------------
# 2. Logarithm: f(s) = exp(s)−1  →  g(s) = log(1+s)
#    g_n = (−1)^{n−1} · (n−1)!   for n ≥ 1
# ---------------------------------------------------------------------------

class TestLogFromExp:
    """
    The cleanest closed-form test: f = exp(s)−1 has EGF coefficients
    [0,1,1,1,1,…] and its compositional inverse is log(1+s) with
    g_n = (−1)^{n−1}·(n−1)!  — all integers, all verifiable at digit level.
    """

    ORDER = 9
    F_COEFFS = [0] + [1] * ORDER      # exp(s)−1

    @pytest.fixture(scope="class")
    def result(self):
        f = CnrsHNative.from_gaussian_list(self.F_COEFFS)
        return verify_inversion(f, self.ORDER)

    def test_strings_match(self, result):
        """Every coefficient digit string agrees with the canonical CNRS-A form."""
        assert result["strings_match"] is True

    def test_max_error_zero(self, result):
        """Numeric error is exactly zero — no floating-point residual."""
        assert result["max_error"] == 0.0

    def test_passed(self, result):
        assert result["passed"] is True

    @pytest.mark.parametrize("n", range(1, 9))
    def test_coefficient_value(self, result, n):
        """g_n = (−1)^{n−1} · (n−1)! verified for each n."""
        expected = ((-1) ** (n - 1)) * math.factorial(n - 1)
        got = int(round(_g(result).coeff(n).to_gaussian().real))
        assert got == expected, f"g_{n}: got {got}, expected {expected}"

    @pytest.mark.parametrize("n,expected_str", [
        (1, "1"),
        (2, "144"),    # −1 in CNRS-A
        (3, "2"),
        (4, "13334"),  # −6 in CNRS-A
        (5, "121244"), # 24 in CNRS-A
        (6, "2310310"),# −120 in CNRS-A
    ])
    def test_digit_strings(self, result, n, expected_str):
        """Exact CNRS-A digit strings for known log(1+s) coefficients."""
        assert _g(result).coeff(n).s == expected_str, (
            f"g_{n}: digit string '{_g(result).coeff(n).s}' != '{expected_str}'"
        )

    def test_fog_is_identity_strings(self, result):
        """f(g(s)) digit strings match the identity series exactly."""
        fog = result["fog"]
        assert fog.coeff(0).s == "0"
        assert fog.coeff(1).s == "1"
        for n in range(2, self.ORDER):
            assert fog.coeff(n).s == "0", (
                f"(f∘g)_{n} should be '0', got '{fog.coeff(n).s}'"
            )


# ---------------------------------------------------------------------------
# 3. Quadratic shift: f(s) = s + s²/2!
# ---------------------------------------------------------------------------

class TestQuadraticShift:
    """
    f(s) = s + s²/2! has known double-factorial inverse:
    g_n = (−1)^{n−1} · (2n−3)!! for n ≥ 2  (double factorial).
    g_1=1, g_2=−1, g_3=3, g_4=−15, g_5=105, g_6=−945, g_7=10395.
    """

    EXPECTED = {1: 1, 2: -1, 3: 3, 4: -15, 5: 105, 6: -945, 7: 10395}

    @pytest.fixture(scope="class")
    def result(self):
        f = CnrsHNative.from_gaussian_list([0, 1, 1, 0, 0, 0, 0, 0])
        return verify_inversion(f, 8)

    def test_strings_match(self, result):
        assert result["strings_match"] is True

    def test_max_error_zero(self, result):
        assert result["max_error"] == 0.0

    @pytest.mark.parametrize("n,expected", [
        (1, 1), (2, -1), (3, 3), (4, -15), (5, 105), (6, -945), (7, 10395)
    ])
    def test_coefficient_value(self, result, n, expected):
        got = int(round(_g(result).coeff(n).to_gaussian().real))
        assert got == expected, f"g_{n}: got {got}, expected {expected}"


# ---------------------------------------------------------------------------
# 4. Gaussian unit f′(0): f(s) = i·s + s²/2!
# ---------------------------------------------------------------------------

class TestGaussianUnitDerivative:
    """
    f′(0) = i is a Gaussian unit; inversion must produce g′(0) = 1/i = −i
    and all remaining coefficients must be pure imaginary Gaussian integers.
    """

    @pytest.fixture(scope="class")
    def result(self):
        f = CnrsHNative.from_gaussian_list([0, 1j, 1, 0, 0, 0, 0])
        return verify_inversion(f, 6)

    def test_strings_match(self, result):
        assert result["strings_match"] is True

    def test_g1_is_minus_i(self, result):
        """g_1 = 1/i = −i."""
        assert _g(result).coeff(1).to_gaussian() == -1j

    def test_all_coefficients_pure_imaginary(self, result):
        """All nonzero inverse coefficients are pure imaginary Gaussian integers."""
        for n in range(1, 6):
            g_n = _g(result).coeff(n).to_gaussian()
            assert abs(g_n.real) < 1e-12, f"g_{n}.real should be 0, got {g_n.real}"
            imag = g_n.imag
            assert abs(imag - round(imag)) < 1e-12, (
                f"g_{n}.imag={imag} is not an integer"
            )

    @pytest.mark.parametrize("n,expected", [
        (1, -1j), (2, -1j), (3, -3j), (4, -15j), (5, -105j)
    ])
    def test_coefficient_values(self, result, n, expected):
        got = _g(result).coeff(n).to_gaussian()
        assert abs(got - expected) < 1e-12, f"g_{n}: got {got}, expected {expected}"

    def test_fog_is_identity(self, result):
        assert result["max_error"] == 0.0


# ---------------------------------------------------------------------------
# 5. Negation: f(s) = −s  →  g(s) = −s  (self-inverse)
# ---------------------------------------------------------------------------

class TestNegationSelfInverse:

    @pytest.fixture(scope="class")
    def result(self):
        f = CnrsHNative.from_gaussian_list([0, -1, 0, 0, 0, 0])
        return verify_inversion(f, 6)

    def test_strings_match(self, result):
        assert result["strings_match"] is True

    def test_g1_is_minus_one(self, result):
        assert _g(result).coeff(1).to_gaussian() == -1

    def test_higher_coefficients_zero(self, result):
        for n in range(2, 6):
            assert _g(result).coeff(n).to_gaussian() == 0

    def test_double_inversion_identity(self):
        """invert(invert(f)) = f at the digit-string level."""
        f = CnrsHNative.from_gaussian_list([0, -1, 0, 0, 0, 0])
        g = invert_native(f, 6)
        gg = invert_native(g, 6)
        for n in range(6):
            assert gg.coeff(n).s == f.coeff(n).s, (
                f"Coeff {n}: double-invert gave '{gg.coeff(n).s}', "
                f"expected '{f.coeff(n).s}'"
            )


# ---------------------------------------------------------------------------
# 6. Round-trip: compose(f, invert(f)) = identity
# ---------------------------------------------------------------------------

class TestRoundTrip:
    """
    For a range of f series, verify that f(g(s)) = s at the digit-string level
    using compose_native directly (not via verify_inversion).
    """

    @pytest.mark.parametrize("f_coeffs,label", [
        ([0, 1, 1, 1, 1, 1, 1, 1], "exp(s)-1"),
        ([0, 1, 2, 0, 0, 0, 0],    "s + 2·s²/2!"),
        ([0, 1, 0, 1, 0, 0, 0],    "s + s³/3!"),
        ([0, 1, 3, 6, 0, 0, 0],    "s + 3s²/2! + 6s³/3!"),
        ([0, -1, 0, 0, 0, 0],       "-s"),
        ([0, 1, 0, 0, 0, 0, 0],     "s (identity)"),
    ])
    def test_fog_equals_identity_strings(self, f_coeffs, label):
        """f(g(s)) has identity digit strings to full order."""
        order = len(f_coeffs)
        f = CnrsHNative.from_gaussian_list(f_coeffs)
        g = invert_native(f, order)
        fog = compose_native(f, g, order - 1).pad(order)

        assert fog.coeff(0).s == "0", f"[{label}] (f∘g)_0 should be '0'"
        assert fog.coeff(1).s == "1", f"[{label}] (f∘g)_1 should be '1'"
        for n in range(2, order):
            assert fog.coeff(n).s == "0", (
                f"[{label}] (f∘g)_{n} digit string '{fog.coeff(n).s}' != '0'"
            )

    def test_invert_then_compose_order_8(self):
        """Round-trip at order 8 for exp(s)−1, checking all digit strings."""
        f = CnrsHNative.from_gaussian_list([0, 1, 1, 1, 1, 1, 1, 1])
        g = invert_native(f, 8)
        fog = compose_native(f, g, 7).pad(8)
        assert fog.coeff(1).s == "1"
        for n in [0] + list(range(2, 8)):
            assert fog.coeff(n).s == "0"

    def test_invert_twice_returns_original_strings(self):
        """invert(invert(f)) = f  at the digit-string level."""
        f_coeffs = [0, 1, 1, 1, 1, 1]
        f = CnrsHNative.from_gaussian_list(f_coeffs)
        g = invert_native(f, 6)
        f_recovered = invert_native(g, 6)
        for n in range(6):
            assert f_recovered.coeff(n).s == f.coeff(n).s, (
                f"Coeff {n}: double-invert gave '{f_recovered.coeff(n).s}', "
                f"original was '{f.coeff(n).s}'"
            )


# ---------------------------------------------------------------------------
# 7. Error conditions
# ---------------------------------------------------------------------------

class TestInversionErrors:

    def test_nonzero_constant_raises(self):
        """f(0) ≠ 0: InversionError with informative message."""
        f = CnrsHNative.from_gaussian_list([1, 1, 0, 0])
        with pytest.raises(InversionError, match="f\\(0\\) = 0"):
            invert_native(f, 4)

    def test_non_unit_derivative_raises(self):
        """f′(0) = 2 is not a Gaussian unit: InversionError."""
        f = CnrsHNative.from_gaussian_list([0, 2, 0, 0])
        with pytest.raises(InversionError, match="Gaussian integer unit"):
            invert_native(f, 4)

    def test_zero_derivative_raises(self):
        """f′(0) = 0: InversionError (not a unit)."""
        f = CnrsHNative.from_gaussian_list([0, 0, 1, 0])
        with pytest.raises(InversionError):
            invert_native(f, 4)

    def test_general_integer_derivative_raises(self):
        """f′(0) = 3 (integer > 1) raises InversionError."""
        f = CnrsHNative.from_gaussian_list([0, 3, 1, 0])
        with pytest.raises(InversionError):
            invert_native(f, 4)

    def test_non_gaussian_derivative_raises(self):
        """f′(0) = 1+i is not a Gaussian unit: InversionError."""
        f = CnrsHNative.from_gaussian_list([0, 1+1j, 0, 0])
        with pytest.raises(InversionError):
            invert_native(f, 4)

    def test_zero_order_raises(self):
        """order ≤ 0 raises ValueError."""
        f = CnrsHNative.from_gaussian_list([0, 1, 1])
        with pytest.raises(ValueError):
            invert_native(f, 0)

    def test_all_four_gaussian_units_accepted(self):
        """f′(0) ∈ {1, −1, i, −i} all succeed without exception."""
        for f1 in [1, -1, 1j, -1j]:
            f = CnrsHNative.from_gaussian_list([0, f1, 0, 0, 0])
            g = invert_native(f, 5)   # must not raise
            # g_1 = 1/f_1
            expected_g1 = 1 / f1
            assert abs(g.coeff(1).to_gaussian() - expected_g1) < 1e-12
