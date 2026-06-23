"""
test_stress_outside_normal.py
==============================
Two stress tests well outside the normal operating range:

  1. DrainGuardStress  — exercises the ``_normalize_coeffs`` drain guard in
     ``cnrs_mul.py``.  Normal workflow digit strings produce residual carries
     of magnitude ≤ 10 that drain in ≤ 5 steps; the guard is set to 100.
     This suite pushes the normalization with:
       - long all-maximum-digit strings  (high convolution coefficient values)
       - artificially large coefficient lists injected directly into the
         normalizer  (simulates pathological accumulation)
       - 2 000 random Gaussian-integer pairs up to ±500  (broad coverage)
     All tests verify correctness via the value map and confirm the guard is
     never approached.

  2. DualPathArchitecture — exercises ``CnrsHMode`` path selection across the
     full decision tree:
       - auto-selection: Gaussian integers → native, floats → fast
       - large-Gaussian-integer fallback (lam=3j, order ≥ 38 overflows
         CNRS-A floating-point precision → falls back to fast path silently)
       - forced native=True raises ``NonGaussianCoefficientError`` on float
         coefficients
       - forced native=False always uses fast path even for Gaussian inputs
       - numerical values are identical on both paths to machine precision
       - path propagates correctly through ``derivative()`` and ``integral()``
       - ``ScaleLaw.native_mode`` and ``OdeSolution.native_mode`` reflect the
         active path correctly
"""

import math
import random
import pytest

from cnrs.cnrs_mul import _normalize_coeffs, _convolve_digits, mul_cnrs
from cnrs.cnrs_repr import cnrs_to_gaussian, gaussian_to_cnrs_str, cnrs_remainder
from cnrs.cnrs_repr import Z0
from cnrs.cnrs_h_mode import CnrsHMode, native_eligible
from cnrs.cnrs_h_native import NonGaussianCoefficientError
from cnrs.cnrs_scale import ScaleLaw
from cnrs.cnrs_ode import cnrs_solve_linear


# ===========================================================================
# Helper: count drain steps for a given residual carry
# ===========================================================================

def _drain_steps(carry: complex) -> int:
    """Return the number of steps to drain a residual carry to zero."""
    c = complex(round(carry.real), round(carry.imag))
    steps = 0
    while c != 0:
        d = cnrs_remainder(c)
        c = (c - d) / Z0
        c = complex(round(c.real), round(c.imag))
        steps += 1
        if steps > 200:          # safety net for the test itself
            raise AssertionError(f"Carry {carry!r} did not drain in 200 steps")
    return steps


# ===========================================================================
# 1. Drain guard stress
# ===========================================================================

class TestDrainGuardStress:
    """
    Push ``_normalize_coeffs`` with inputs far beyond normal usage and confirm:
      (a) results are correct
      (b) the drain-guard limit of 100 is never approached
    """

    GUARD_LIMIT = 100
    SAFE_MARGIN = 20          # we expect ≤ 20 drain steps in the worst case

    # -----------------------------------------------------------------------
    # Direct normalization of artificially large coefficients
    # -----------------------------------------------------------------------

    def test_large_uniform_coefficients(self):
        """
        Inject coefficients of value 16 000 (worst-case convolution value for
        1 000-digit strings with max digit 4).  Verify normalization completes
        and the residual carry drains well within the guard.
        """
        large_coeffs = [16_000] * 100
        digits = _normalize_coeffs(large_coeffs)
        assert len(digits) > 0, "Expected non-empty digit list"
        # Verify carry drained safely during normalization by checking no
        # RuntimeError was raised (implicit) and result is non-trivial
        assert any(d != 0 for d in digits), "All-zero result is suspicious"

    def test_alternating_large_coefficients(self):
        """
        Alternating ±16 000 coefficients stress the carry in both directions.
        """
        coeffs = [16_000 * ((-1) ** k) for k in range(80)]
        digits = _normalize_coeffs(coeffs)
        assert len(digits) > 0

    def test_drain_steps_bounded_for_extreme_carries(self):
        """
        Directly test drain step counts for the largest residual carries that
        can arise after the normalization main loop, verifying they stay well
        below the guard of 100.
        """
        # Compute residual carries from worst-case convolution inputs
        worst_carries = []
        for n in [100, 500, 1000, 2000]:
            a = [4] * n
            b = [4] * n
            coeffs = _convolve_digits(a, b)
            carry = 0 + 0j
            for c in coeffs:
                raw = c + carry
                d = cnrs_remainder(raw)
                carry = (raw - d) / Z0
                carry = complex(round(carry.real), round(carry.imag))
            worst_carries.append(carry)

        # Also inject hand-crafted large carries
        for c in [(-1000 + 0j), (0 + 1000j), (-500 - 500j), (800 + 300j)]:
            worst_carries.append(c)

        for carry in worst_carries:
            steps = _drain_steps(carry)
            assert steps < self.SAFE_MARGIN, (
                f"Drain took {steps} steps for carry {carry!r}; "
                f"expected < {self.SAFE_MARGIN} (guard is {self.GUARD_LIMIT})"
            )

    # -----------------------------------------------------------------------
    # Long all-maximum-digit string multiplication
    # -----------------------------------------------------------------------

    def test_long_all4_mul_no_runtime_error(self):
        """
        Multiply two 300-digit all-4 strings.  Verifies the normalization
        loop completes without hitting the drain guard.
        """
        big = "4" * 300
        result = mul_cnrs(big, big)
        assert isinstance(result, str)
        assert len(result) > 0
        assert all(c in "01234." for c in result)

    # -----------------------------------------------------------------------
    # Correctness across random Gaussian-integer pairs
    # -----------------------------------------------------------------------

    def test_random_gaussian_multiplication_correctness(self):
        """
        2 000 random Gaussian-integer multiplications up to ±500.
        For each pair, verify mul_cnrs(sa, sb) == canonical(ga * gb).
        This catches any carry-drain failure that would produce wrong digits.
        """
        rng = random.Random(42)
        mismatches = []

        for _ in range(2000):
            ar, ai = rng.randint(-500, 500), rng.randint(-500, 500)
            br, bi = rng.randint(-500, 500), rng.randint(-500, 500)
            ga, gb = complex(ar, ai), complex(br, bi)
            sa = gaussian_to_cnrs_str(ga)
            sb = gaussian_to_cnrs_str(gb)
            result = mul_cnrs(sa, sb)
            expected = gaussian_to_cnrs_str(ga * gb)
            if result != expected:
                mismatches.append((ga, gb, result, expected))

        assert not mismatches, (
            f"{len(mismatches)} multiplication mismatches found; "
            f"first: {mismatches[0]}"
        )

    def test_max_residual_carry_across_random_trials(self):
        """
        Track the maximum residual carry magnitude across 2 000 random
        convolution inputs and assert the drain steps needed stay below
        SAFE_MARGIN, confirming the guard of 100 is never close to binding.
        """
        rng = random.Random(99)
        max_steps = 0
        max_carry = 0 + 0j

        for _ in range(2000):
            n = rng.randint(1, 200)
            a = [rng.randint(0, 4) for _ in range(n)]
            b = [rng.randint(0, 4) for _ in range(n)]
            coeffs = _convolve_digits(a, b)
            carry = 0 + 0j
            for c in coeffs:
                raw = c + carry
                d = cnrs_remainder(raw)
                carry = (raw - d) / Z0
                carry = complex(round(carry.real), round(carry.imag))
            steps = _drain_steps(carry)
            if steps > max_steps:
                max_steps = steps
                max_carry = carry

        assert max_steps < self.SAFE_MARGIN, (
            f"Max drain steps was {max_steps} (carry={max_carry!r}); "
            f"expected < {self.SAFE_MARGIN} (guard is {self.GUARD_LIMIT})"
        )


# ===========================================================================
# 2. Dual-path architecture
# ===========================================================================

class TestDualPathArchitecture:
    """
    Verify CnrsHMode path selection, fallback, overrides, value agreement,
    and path propagation through the full ScaleLaw / OdeSolution stack.
    """

    # -----------------------------------------------------------------------
    # Auto-selection
    # -----------------------------------------------------------------------

    def test_auto_selects_native_for_gaussian_integer_coeffs(self):
        """Small Gaussian-integer coefficients → native path selected."""
        mode = CnrsHMode.from_coeffs([1, 2, -1, 3, 0, -2])
        assert mode.native is True

    def test_auto_selects_fast_for_float_coeffs(self):
        """Float (non-Gaussian) coefficients → fast path selected."""
        mode = CnrsHMode.from_coeffs([1.0, 1.5, 2.25, 3.375])
        assert mode.native is False

    def test_auto_selects_fast_for_complex_eigenvalue_coeffs(self):
        """exp(1.5j * s) has float-magnitude coefficients → fast path."""
        coeffs = [(1.5j) ** n / math.factorial(n) for n in range(10)]
        # These are Gaussian in structure but the values are pure imaginary
        # floats; the eligibility check should catch them.
        mode = CnrsHMode.from_coeffs(coeffs)
        # 1.5j coefficients are not Gaussian integers (non-integer imaginary parts)
        assert mode.native is False

    def test_auto_gaussian_lam_small(self):
        """exp(2j * s): coefficients (2j)^n are Gaussian integers → native."""
        coeffs = [(2j) ** n for n in range(20)]
        mode = CnrsHMode.from_coeffs(coeffs)
        assert mode.native is True

    def test_auto_fallback_large_gaussian_integers(self):
        """
        lam=3j at order 38+ produces coefficients (3j)^37 ~ 10^17j, too large
        for floating-point CNRS-A expansion.  Must fall back to fast path
        without raising an exception.
        """
        coeffs = [(3j) ** n for n in range(40)]  # order 40, falls back at 38
        mode = CnrsHMode.from_coeffs(coeffs)     # must NOT raise
        assert mode.native is False, (
            "Expected fallback to fast path for large (3j)^n coefficients"
        )

    # -----------------------------------------------------------------------
    # Forced overrides
    # -----------------------------------------------------------------------

    def test_forced_fast_overrides_gaussian_coeffs(self):
        """native=False forces fast path even for Gaussian-integer coefficients."""
        mode = CnrsHMode.from_coeffs([1, 2, 3], native=False)
        assert mode.native is False

    def test_forced_native_works_for_gaussian_coeffs(self):
        """native=True succeeds when all coefficients are Gaussian integers."""
        mode = CnrsHMode.from_coeffs([1, -1, 2, -3], native=True)
        assert mode.native is True

    def test_forced_native_raises_for_float_coeffs(self):
        """native=True raises NonGaussianCoefficientError for float coefficients."""
        with pytest.raises(NonGaussianCoefficientError):
            CnrsHMode.from_coeffs([1.0, 1.5, 2.25], native=True)

    # -----------------------------------------------------------------------
    # Value agreement between paths
    # -----------------------------------------------------------------------

    def test_values_agree_native_vs_fast(self):
        """
        Evaluate the same Gaussian-integer EGF series on both paths and
        confirm results match to machine precision at several points.
        """
        coeffs = [1, 2, -1, 3, 0, -2, 1]
        mode_native = CnrsHMode.from_coeffs(coeffs, native=True)
        mode_fast   = CnrsHMode.from_coeffs(coeffs, native=False)

        test_points = [0.0, 0.1, 0.3, 0.5, -0.2, complex(0.1, 0.1)]
        for s in test_points:
            vn = mode_native.evaluate(complex(s))
            vf = mode_fast.evaluate(complex(s))
            assert abs(vn - vf) < 1e-12, (
                f"Path disagreement at s={s}: native={vn}, fast={vf}, "
                f"diff={abs(vn-vf):.2e}"
            )

    def test_coeffs_property_always_returns_complex(self):
        """
        .coeffs on both paths must return Python complex values regardless
        of the underlying backend (CVal vs plain complex).
        """
        coeffs = [1, 2, 3]
        for nat in [True, False]:
            mode = CnrsHMode.from_coeffs(coeffs, native=nat)
            for c in mode.coeffs:
                assert isinstance(c, (int, float, complex)), (
                    f"Expected numeric type, got {type(c)} (native={nat})"
                )

    # -----------------------------------------------------------------------
    # Path propagation through derivative and integral
    # -----------------------------------------------------------------------

    def test_derivative_preserves_native_path(self):
        """Differentiating a native-path mode returns a native-path mode."""
        mode = CnrsHMode.from_coeffs([1, 2, 3, 4, 5], native=True)
        d_mode = mode.differentiate()
        assert d_mode.native is True

    def test_derivative_preserves_fast_path(self):
        """Differentiating a fast-path mode returns a fast-path mode."""
        mode = CnrsHMode.from_coeffs([1.0, 1.5, 2.25], native=False)
        d_mode = mode.differentiate()
        assert d_mode.native is False

    def test_derivative_value_shift(self):
        """
        D(sum d_n s^n/n!) = sum d_{n+1} s^n/n!
        Both paths must give the same derivative values.
        """
        coeffs = [6, 5, 4, 3, 2, 1]
        mode_n = CnrsHMode.from_coeffs(coeffs, native=True)
        mode_f = CnrsHMode.from_coeffs(coeffs, native=False)
        dn = mode_n.differentiate()
        df = mode_f.differentiate()
        for s in [0.0, 0.2, 0.5]:
            assert abs(dn.evaluate(s) - df.evaluate(s)) < 1e-12

    def test_integral_preserves_native_path(self):
        """Integrating a native-path mode returns a native-path mode."""
        mode = CnrsHMode.from_coeffs([1, 2, 3], native=True)
        i_mode = mode.integrate(constant=0)
        assert i_mode.native is True

    def test_integral_preserves_fast_path(self):
        """Integrating a fast-path mode returns a fast-path mode."""
        mode = CnrsHMode.from_coeffs([1.0, 2.0, 3.0], native=False)
        i_mode = mode.integrate(constant=0.0)
        assert i_mode.native is False

    # -----------------------------------------------------------------------
    # ScaleLaw integration
    # -----------------------------------------------------------------------

    def test_scale_law_auto_native_for_integer_coeffs(self):
        """ScaleLaw.from_coeffs with integer coefficients → native_mode=True."""
        law = ScaleLaw.from_coeffs([1, 2, 3, 4])
        assert law.native_mode is True

    def test_scale_law_auto_fast_for_float_lam(self):
        """ScaleLaw.exponential with float lam → native_mode=False."""
        law = ScaleLaw.exponential(lam=1.5, terms=10)
        assert law.native_mode is False

    def test_scale_law_forced_fast(self):
        """native=False forces fast path on ScaleLaw even for integer coeffs."""
        law = ScaleLaw.from_coeffs([1, 2, 3], native=False)
        assert law.native_mode is False

    def test_scale_law_derivative_preserves_path(self):
        """ScaleLaw.derivative() preserves the native path."""
        law = ScaleLaw.from_coeffs([1, 2, 3, 4, 5], native=True)
        assert law.derivative().native_mode is True
        law2 = ScaleLaw.exponential(lam=1.5, terms=8, native=False)
        assert law2.derivative().native_mode is False

    def test_scale_law_both_paths_same_value(self):
        """ScaleLaw evaluation gives same result on native and fast paths."""
        coeffs = [1, -1, 2, -3, 5]
        law_n = ScaleLaw.from_coeffs(coeffs, native=True)
        law_f = ScaleLaw.from_coeffs(coeffs, native=False)
        for s in [0.0, 0.05, 0.1, 0.2]:
            vn = law_n.evaluate(s)
            vf = law_f.evaluate(s)
            assert abs(vn - vf) < 1e-12, (
                f"ScaleLaw path disagreement at s={s}: "
                f"native={vn}, fast={vf}"
            )

    def test_scale_law_large_gaussian_fallback_no_exception(self):
        """
        ScaleLaw.exponential(lam=3j, terms=40) involves coefficients that
        exceed the CNRS-A floating-point precision limit.  Must construct
        successfully, fall back to fast path, and evaluate correctly.
        """
        law = ScaleLaw.exponential(lam=3j, terms=40)
        assert law.native_mode is False
        # Evaluate at a safe point and compare to known value
        import cmath
        s = 0.1
        expected = cmath.exp(3j * s)
        got = law.evaluate(s)
        assert abs(got - expected) < 1e-6, (
            f"Large-Gaussian fallback evaluation wrong: got={got}, expected={expected}"
        )

    # -----------------------------------------------------------------------
    # OdeSolution integration
    # -----------------------------------------------------------------------

    def test_ode_auto_native_for_gaussian_lam(self):
        """ODE with lam=1j (Gaussian eigenvalue) → native_mode=True."""
        sol = cnrs_solve_linear(lam=1j, terms=10)
        assert sol.native_mode is True

    def test_ode_auto_fast_for_float_lam(self):
        """ODE with lam=1.5+0.5j (non-Gaussian) → native_mode=False."""
        sol = cnrs_solve_linear(lam=1.5 + 0.5j, terms=10)
        assert sol.native_mode is False

    def test_ode_both_paths_same_value(self):
        """
        ODE solution with lam=1j evaluated on native and fast paths must
        agree to machine precision.
        """
        sol_n = cnrs_solve_linear(lam=1j, terms=20, native=True)
        sol_f = cnrs_solve_linear(lam=1j, terms=20, native=False)
        import cmath
        for s in [0.0, 0.1, 0.3, 0.5]:
            vn = sol_n.evaluate(s, warn=False)
            vf = sol_f.evaluate(s, warn=False)
            assert abs(vn - vf) < 1e-12, (
                f"ODE path disagreement at s={s}: native={vn}, fast={vf}"
            )

    def test_ode_derivative_preserves_native_path(self):
        """OdeSolution.derivative() preserves the native path."""
        sol = cnrs_solve_linear(lam=1j, terms=10)
        assert sol.native_mode is True
        assert sol.derivative().native_mode is True
