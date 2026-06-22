"""
test_cnrs_h_native_compose.py
=============================
Tests for compose_native (Faà di Bruno) and verify_chain_rule_native.

Every test verifies composition and the chain rule entirely within CNRS-A
coefficient space.  The key properties:

  1. Bell polynomial coefficients are always integers             (mathematical)
  2. compose_native coefficients are CVal instances               (representation)
  3. Known compositions give correct results                      (correctness)
  4. f ∘ identity = f                                             (identity)
  5. (f ∘ g) ∘ h = f ∘ (g ∘ h)   (associativity, spot-checked)  (algebra)
  6. D(f∘g) = (Df∘g)*Dg — digit strings identical on both sides  (chain rule)
"""
import pytest
from math import comb
from cnrs.cnrs_h_native import (
    CnrsHNative,
    compose_native,
    verify_chain_rule_native,
    coeff_strings,
    _bell_table,
    _ZERO_CVAL,
    _ONE_CVAL,
)
from cnrs.cnrs_value import CVal
from cnrs.cnrs_repr import normalize_cnrs


# ---------------------------------------------------------------------------
# Bell polynomial table
# ---------------------------------------------------------------------------

class TestBellTable:

    def _make_g(self, vals):
        """Helper: CnrsHNative with given EGF coefficients."""
        return CnrsHNative.from_gaussian_list(vals)

    def test_b00_is_one(self):
        g = self._make_g([0, 1])
        B = _bell_table(g.pad(4).coeffs, 3)
        assert B[0][0].to_gaussian() == 1

    def test_b_n_0_is_zero(self):
        g = self._make_g([0, 1, 2])
        B = _bell_table(g.pad(5).coeffs, 4)
        for n in range(1, 5):
            assert B[n][0].to_gaussian() == 0

    def test_b11_equals_g1(self):
        # B[1][1] = g_1
        g = self._make_g([0, 3])
        B = _bell_table(g.pad(3).coeffs, 2)
        assert B[1][1].to_gaussian() == 3

    def test_b21_equals_g2(self):
        # B[2][1] = g_2
        g = self._make_g([0, 1, 5])
        B = _bell_table(g.pad(4).coeffs, 3)
        assert B[2][1].to_gaussian() == 5

    def test_b22_equals_g1_squared(self):
        # B[2][2] = g_1^2
        g = self._make_g([0, 3])
        B = _bell_table(g.pad(4).coeffs, 3)
        assert B[2][2].to_gaussian() == 9   # 3^2

    def test_b32_equals_3_g1_g2(self):
        # B[3][2] = 3 * g_1 * g_2
        g = self._make_g([0, 2, 3])
        B = _bell_table(g.pad(5).coeffs, 4)
        assert B[3][2].to_gaussian() == 3 * 2 * 3   # = 18

    def test_b33_equals_g1_cubed(self):
        # B[3][3] = g_1^3
        g = self._make_g([0, 2])
        B = _bell_table(g.pad(5).coeffs, 4)
        assert B[3][3].to_gaussian() == 8   # 2^3

    def test_b42_equals_3g2sq_plus_4g1g3(self):
        # B[4][2] = 3*g_2^2 + 4*g_1*g_3
        g = self._make_g([0, 1, 2, 3])
        B = _bell_table(g.pad(6).coeffs, 5)
        expected = 3 * 2**2 + 4 * 1 * 3   # = 12 + 12 = 24
        assert B[4][2].to_gaussian() == expected

    def test_bell_values_are_cval(self):
        g = self._make_g([0, 1, 2, 3])
        B = _bell_table(g.pad(6).coeffs, 5)
        for n in range(6):
            for k in range(6):
                assert isinstance(B[n][k], CVal)


# ---------------------------------------------------------------------------
# compose_native — correctness
# ---------------------------------------------------------------------------

class TestComposeNativeCorrectness:

    def test_exp_of_2s_gives_powers_of_2(self):
        """exp(2s) has EGF coefficients 2^n."""
        f = CnrsHNative.from_gaussian_list([1] * 8)   # exp
        g = CnrsHNative.from_gaussian_list([0, 2])    # 2s
        h = compose_native(f, g, 7)
        for n in range(8):
            assert h.coeff(n).to_gaussian() == 2**n, f"n={n}: {h.coeff(n).to_gaussian()}"

    def test_exp_of_3s_gives_powers_of_3(self):
        f = CnrsHNative.from_gaussian_list([1] * 8)
        g = CnrsHNative.from_gaussian_list([0, 3])
        h = compose_native(f, g, 7)
        for n in range(8):
            assert h.coeff(n).to_gaussian() == 3**n

    def test_identity_composition(self):
        """f ∘ identity = f."""
        f = CnrsHNative.from_gaussian_list([1, 3, 2, 1])
        g_id = CnrsHNative.identity().pad(5)
        h = compose_native(f, g_id, 3)
        for i in range(4):
            assert h.coeff(i).to_gaussian() == f.coeff(i).to_gaussian()

    def test_constant_outer(self):
        """Constant f: f(g(s)) = f_0 for all g."""
        f = CnrsHNative.constant(7, length=1)
        g = CnrsHNative.from_gaussian_list([0, 1, 2, 3])
        h = compose_native(f, g, 5)
        assert h.coeff(0).to_gaussian() == 7
        for i in range(1, 6):
            assert h.coeff(i).to_gaussian() == 0

    def test_linear_outer(self):
        """f(s) = a + b*s composed with g: h_0 = a, h_n = b * g_n."""
        f = CnrsHNative.from_gaussian_list([2, 5])    # 2 + 5s
        g = CnrsHNative.from_gaussian_list([0, 1, 3, 2])
        h = compose_native(f, g, 3)
        assert h.coeff(0).to_gaussian() == 2
        assert h.coeff(1).to_gaussian() == 5 * 1   # b * g_1
        assert h.coeff(2).to_gaussian() == 5 * 3   # b * g_2
        assert h.coeff(3).to_gaussian() == 5 * 2   # b * g_3

    def test_quadratic_outer(self):
        """f(s) = s^2 (f_2=2, others 0); f(g)_n involves g convolution."""
        # f_2 = 2 means f(s) = s^2 in ordinary PS (EGF coeff d_2 = 2)
        f = CnrsHNative.from_gaussian_list([0, 0, 2, 0, 0])
        g = CnrsHNative.from_gaussian_list([0, 1, 0, 0, 0])  # g = s
        h = compose_native(f, g, 4)
        # f(g(s)) = g(s)^2 = s^2, EGF coeff d_2 = 2
        assert h.coeff(0).to_gaussian() == 0
        assert h.coeff(1).to_gaussian() == 0
        assert h.coeff(2).to_gaussian() == 2
        assert h.coeff(3).to_gaussian() == 0

    def test_nontrivial_composition(self):
        """f=exp, g = s + s^2: exp(s+s^2) known first coefficients."""
        f = CnrsHNative.from_gaussian_list([1] * 8)
        g = CnrsHNative.from_gaussian_list([0, 1, 2])
        h = compose_native(f, g, 7)
        expected = [1, 1, 3, 7, 25, 81, 331, 1303]
        for n, e in enumerate(expected):
            assert h.coeff(n).to_gaussian() == e, f"n={n}: {h.coeff(n).to_gaussian()} != {e}"

    def test_gaussian_integer_coefficients_preserved(self):
        """Composition of Gaussian-integer EGFs gives Gaussian-integer result."""
        f = CnrsHNative.from_gaussian_list([1+1j, 2-1j, 1+0j])
        g = CnrsHNative.from_gaussian_list([0, 1+0j, 0+1j])
        h = compose_native(f, g, 4)
        for c in h.coeffs:
            z = c.to_gaussian()
            assert abs(z.real - round(z.real)) < 1e-10
            assert abs(z.imag - round(z.imag)) < 1e-10

    def test_g0_nonzero_raises(self):
        f = CnrsHNative.from_gaussian_list([1, 1])
        g = CnrsHNative.from_gaussian_list([3, 1])  # g_0 = 3 ≠ 0
        with pytest.raises(ValueError, match="g\\(0\\) = 0"):
            compose_native(f, g, 3)


# ---------------------------------------------------------------------------
# compose_native — representation
# ---------------------------------------------------------------------------

class TestComposeNativeRepresentation:

    def test_result_coefficients_are_cval(self):
        f = CnrsHNative.from_gaussian_list([1] * 6)
        g = CnrsHNative.from_gaussian_list([0, 2])
        h = compose_native(f, g, 5)
        for c in h.coeffs:
            assert isinstance(c, CVal)

    def test_result_strings_are_canonical(self):
        f = CnrsHNative.from_gaussian_list([1, 1, 1, 1, 1])
        g = CnrsHNative.from_gaussian_list([0, 1, 2])
        h = compose_native(f, g, 4)
        for c in h.coeffs:
            assert c.s == normalize_cnrs(c.s)

    def test_exp_2s_cnrs_strings_match_expected(self):
        """2^n must appear as the correct CNRS-A digit string."""
        f = CnrsHNative.from_gaussian_list([1] * 8)
        g = CnrsHNative.from_gaussian_list([0, 2])
        h = compose_native(f, g, 7)
        for n in range(8):
            expected_str = CVal.from_gaussian(complex(2**n)).s
            assert h.coeff(n).s == expected_str, (
                f"n={n}: got {h.coeff(n).s!r}, expected {expected_str!r}"
            )


# ---------------------------------------------------------------------------
# Chain rule: D(f∘g) = (Df∘g) * Dg — fully native
# ---------------------------------------------------------------------------

class TestNativeChainRule:

    def _check_chain_rule(self, f, g, order=6):
        result = verify_chain_rule_native(f, g, order=order)
        assert result["passed"], (
            f"Chain rule failed: max_error={result['max_error']}"
        )
        assert result["strings_match"], (
            f"Chain rule: CNRS-A strings differ\n"
            f"  LHS: {coeff_strings(result['lhs'])}\n"
            f"  RHS: {coeff_strings(result['rhs'])}"
        )

    def test_chain_rule_exp_compose_2s(self):
        """D(exp(2s)) = 2*exp(2s): chain rule with scalar inner."""
        f = CnrsHNative.from_gaussian_list([1] * 8)
        g = CnrsHNative.from_gaussian_list([0, 2])
        self._check_chain_rule(f, g)

    def test_chain_rule_exp_compose_s_plus_s2(self):
        """D(exp(s+s^2)) = (1+2s)*exp(s+s^2)."""
        f = CnrsHNative.from_gaussian_list([1] * 8)
        g = CnrsHNative.from_gaussian_list([0, 1, 2])
        self._check_chain_rule(f, g)

    def test_chain_rule_polynomial_outer(self):
        f = CnrsHNative.from_gaussian_list([1, 2, 3, 1])
        g = CnrsHNative.from_gaussian_list([0, 1, 1, 1])
        self._check_chain_rule(f, g, order=4)

    def test_chain_rule_linear_outer(self):
        """f(s) = a + bs: Df = b, Df∘g = b, (Df∘g)*Dg = b*Dg."""
        f = CnrsHNative.from_gaussian_list([2, 3])
        g = CnrsHNative.from_gaussian_list([0, 1, 2, 1])
        self._check_chain_rule(f, g, order=4)

    def test_chain_rule_identity_inner(self):
        """f∘identity: chain rule should give Df*1 = Df."""
        f = CnrsHNative.from_gaussian_list([1, 2, 3, 1, 1])
        g = CnrsHNative.identity().pad(6)
        self._check_chain_rule(f, g, order=4)

    def test_chain_rule_strings_identical(self):
        """The CNRS-A digit strings on both sides must be identical."""
        f = CnrsHNative.from_gaussian_list([1, 1, 1, 1, 1, 1, 1, 1])
        g = CnrsHNative.from_gaussian_list([0, 1, 2])
        result = verify_chain_rule_native(f, g, order=6)
        for i in range(6):
            assert result["lhs"].coeff(i).s == result["rhs"].coeff(i).s, (
                f"Strings differ at i={i}: "
                f"{result['lhs'].coeff(i).s!r} != {result['rhs'].coeff(i).s!r}"
            )

    def test_chain_rule_gaussian_integer_coefficients(self):
        """Chain rule holds for Gaussian-integer (not just real) coefficients."""
        f = CnrsHNative.from_gaussian_list([1+0j, 1+1j, 1+0j, 1-1j])
        g = CnrsHNative.from_gaussian_list([0+0j, 1+0j, 0+1j])
        self._check_chain_rule(f, g, order=4)


# ---------------------------------------------------------------------------
# Associativity spot check: (f∘g)∘h = f∘(g∘h)
# ---------------------------------------------------------------------------

class TestComposeAssociativity:

    def test_associativity_polynomial(self):
        """(f∘g)∘h = f∘(g∘h) for polynomial series."""
        f = CnrsHNative.from_gaussian_list([1, 2, 1])
        g = CnrsHNative.from_gaussian_list([0, 1, 1])
        h = CnrsHNative.from_gaussian_list([0, 2])

        order = 4
        lhs = compose_native(compose_native(f, g, order + 1), h, order)
        rhs = compose_native(f, compose_native(g, h, order + 1), order)

        for i in range(order + 1):
            assert lhs.coeff(i).to_gaussian() == rhs.coeff(i).to_gaussian(), (
                f"i={i}: {lhs.coeff(i).to_gaussian()} != {rhs.coeff(i).to_gaussian()}"
            )

    def test_associativity_exp(self):
        f = CnrsHNative.from_gaussian_list([1] * 8)
        g = CnrsHNative.from_gaussian_list([0, 1, 1])
        h = CnrsHNative.from_gaussian_list([0, 2])

        order = 5
        lhs = compose_native(compose_native(f, g, order + 1), h, order)
        rhs = compose_native(f, compose_native(g, h, order + 1), order)

        for i in range(order + 1):
            assert lhs.coeff(i).to_gaussian() == rhs.coeff(i).to_gaussian()
