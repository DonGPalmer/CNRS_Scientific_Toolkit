"""
cnrs_h_verify.py
----------------
Verification suite for the CnrsH calculus layer.

Tests all five algebraic properties that make CnrsH mathematically
legitimate as the CNRS-H function layer:

  P1  Exactness of differentiation
        val(D f, rho) == d/drho val(f, rho)     (numerical vs algebraic)

  P2  Exactness of integration
        val(int f, rho) == int_0^rho val(f, t) dt  (numerical vs algebraic)

  P3  Fundamental Theorem of Calculus
        D(int f) == f                            (exact, coefficient-level)

  P4  Leibniz rule
        D(f * g) == (D f) * g + f * (D g)       (numerical at test points)

  P5  Linearity of D
        D(a*f + b*g) == a*(D f) + b*(D g)       (numerical at test points)

  P6  nth derivative
        D^n f drops exactly n leading coefficients

  P7  EGF multiplication is correct
        val(f * g, rho) == val(f, rho) * val(g, rho)

  P8  scale_input
        val(f.scale_input(alpha), rho) == val(f, alpha*rho)
"""

from __future__ import annotations
import random
from typing import List

from .cnrs_h import CnrsH


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOL = 1e-8   # numerical tolerance for complex comparisons


def _rand_coeffs(length: int = 5, radius: int = 4) -> List[int]:
    """Random integer coefficient list."""
    return [random.randint(-radius, radius) for _ in range(length)]


def _rand_rho() -> complex:
    """Random complex test point with moderate magnitude."""
    return complex(random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5))


def _numerical_derivative(f: CnrsH, rho: complex, eps: float = 1e-7) -> complex:
    """Central-difference derivative of f at rho."""
    return (f(rho + eps) - f(rho - eps)) / (2 * eps)


def _numerical_integral(f: CnrsH, rho: complex, steps: int = 1000) -> complex:
    """Numerical integral of f from 0 to rho using the trapezoid rule."""
    total = complex(0)
    for k in range(steps):
        t0 = rho * k / steps
        t1 = rho * (k + 1) / steps
        total += (f(t0) + f(t1)) * (t1 - t0) / 2
    return total


def _close(a: complex, b: complex, tol: float = TOL) -> bool:
    return abs(a - b) <= tol


# ---------------------------------------------------------------------------
# P1: Exactness of differentiation
# ---------------------------------------------------------------------------

def test_p1_differentiation(samples: int = 200, seed: int = 0) -> None:
    """
    D f evaluated at rho equals the numerical derivative of f at rho.
    """
    random.seed(seed)
    for i in range(samples):
        ds = _rand_coeffs()
        rho = _rand_rho()
        f = CnrsH.from_list(ds)
        Df = f.differentiate()

        algebraic = Df(rho)
        numerical = _numerical_derivative(f, rho)

        if not _close(algebraic, numerical, tol=1e-5):
            raise AssertionError(
                f"P1 failed (sample {i}):\n"
                f"  coeffs={ds}, rho={rho}\n"
                f"  algebraic D f(rho) = {algebraic}\n"
                f"  numerical  d/drho  = {numerical}"
            )


# ---------------------------------------------------------------------------
# P2: Exactness of integration
# ---------------------------------------------------------------------------

def test_p2_integration(samples: int = 100, seed: int = 1) -> None:
    """
    int(f, C=0) evaluated at rho equals the numerical integral of f from 0 to rho.
    """
    random.seed(seed)
    for i in range(samples):
        ds = _rand_coeffs(length=4)
        rho = _rand_rho()
        f = CnrsH.from_list(ds)
        Intf = f.integrate(constant=0)

        algebraic = Intf(rho)
        numerical = _numerical_integral(f, rho)

        if not _close(algebraic, numerical, tol=1e-4):
            raise AssertionError(
                f"P2 failed (sample {i}):\n"
                f"  coeffs={ds}, rho={rho}\n"
                f"  algebraic int f(rho) = {algebraic}\n"
                f"  numerical  integral  = {numerical}"
            )


# ---------------------------------------------------------------------------
# P3: Fundamental Theorem of Calculus
# ---------------------------------------------------------------------------

def test_p3_ftc(samples: int = 200, seed: int = 2) -> None:
    """
    D(int f) == f at the coefficient level (exact, not numerical).
    """
    random.seed(seed)
    for i in range(samples):
        ds = _rand_coeffs()
        f = CnrsH.from_list(ds)
        Intf = f.integrate(constant=0)
        reconstructed = Intf.differentiate()

        # Compare coefficients (reconstructed should equal f exactly)
        n = max(f.length, reconstructed.length)
        for k in range(n):
            if f.coeff(k) != reconstructed.coeff(k):
                raise AssertionError(
                    f"P3 failed (sample {i}), coeff {k}:\n"
                    f"  original coeff     = {f.coeff(k)}\n"
                    f"  D(int f) coeff     = {reconstructed.coeff(k)}"
                )


# ---------------------------------------------------------------------------
# P4: Leibniz rule
# ---------------------------------------------------------------------------

def test_p4_leibniz(samples: int = 200, seed: int = 3) -> None:
    """
    D(f * g) == (D f) * g + f * (D g)   evaluated at random rho.
    """
    random.seed(seed)
    for i in range(samples):
        a_ds = _rand_coeffs(length=4)
        b_ds = _rand_coeffs(length=4)
        rho = _rand_rho()

        f = CnrsH.from_list(a_ds)
        g = CnrsH.from_list(b_ds)

        lhs = (f * g).differentiate()(rho)
        rhs = (f.differentiate() * g + f * g.differentiate())(rho)

        if not _close(lhs, rhs, tol=1e-7):
            raise AssertionError(
                f"P4 Leibniz failed (sample {i}):\n"
                f"  f coeffs={a_ds}, g coeffs={b_ds}, rho={rho}\n"
                f"  D(f*g)(rho)          = {lhs}\n"
                f"  (Df*g + f*Dg)(rho)   = {rhs}"
            )


# ---------------------------------------------------------------------------
# P5: Linearity
# ---------------------------------------------------------------------------

def test_p5_linearity(samples: int = 200, seed: int = 4) -> None:
    """
    D(a*f + b*g) == a*(D f) + b*(D g)   evaluated at random rho.
    """
    random.seed(seed)
    for i in range(samples):
        f_ds = _rand_coeffs()
        g_ds = _rand_coeffs()
        a = complex(random.uniform(-3, 3), random.uniform(-3, 3))
        b = complex(random.uniform(-3, 3), random.uniform(-3, 3))
        rho = _rand_rho()

        f = CnrsH.from_list(f_ds)
        g = CnrsH.from_list(g_ds)

        lhs = (a * f + b * g).differentiate()(rho)
        rhs = (a * f.differentiate() + b * g.differentiate())(rho)

        if not _close(lhs, rhs, tol=1e-8):
            raise AssertionError(
                f"P5 linearity failed (sample {i}):\n"
                f"  f={f_ds}, g={g_ds}, a={a}, b={b}, rho={rho}\n"
                f"  D(af+bg)(rho) = {lhs}\n"
                f"  aDf+bDg(rho)  = {rhs}"
            )


# ---------------------------------------------------------------------------
# P6: nth derivative drops n leading coefficients
# ---------------------------------------------------------------------------

def test_p6_nth_derivative(samples: int = 200, seed: int = 5) -> None:
    """
    D^n f == CnrsH([d_n, d_{n+1}, ..., d_N])  at the coefficient level.
    """
    random.seed(seed)
    for i in range(samples):
        length = random.randint(3, 8)
        ds = _rand_coeffs(length=length)
        n = random.randint(0, length)
        f = CnrsH.from_list(ds)
        Dnf = f.nth_derivative(n)

        expected = ds[n:] if n < len(ds) else [0]
        for k, exp_k in enumerate(expected):
            if Dnf.coeff(k) != exp_k:
                raise AssertionError(
                    f"P6 nth_derivative failed (sample {i}), n={n}, coeff {k}:\n"
                    f"  ds={ds}\n"
                    f"  expected coeff = {exp_k}\n"
                    f"  got coeff      = {Dnf.coeff(k)}"
                )


# ---------------------------------------------------------------------------
# P7: EGF multiplication is correct
# ---------------------------------------------------------------------------

def test_p7_egf_multiplication(samples: int = 200, seed: int = 6) -> None:
    """
    val(f * g, rho) == val(f, rho) * val(g, rho).
    """
    random.seed(seed)
    for i in range(samples):
        f_ds = _rand_coeffs(length=4)
        g_ds = _rand_coeffs(length=4)
        rho = _rand_rho()

        f = CnrsH.from_list(f_ds)
        g = CnrsH.from_list(g_ds)
        fg = f * g

        lhs = fg(rho)
        rhs = f(rho) * g(rho)

        if not _close(lhs, rhs, tol=1e-7):
            raise AssertionError(
                f"P7 EGF mul failed (sample {i}):\n"
                f"  f={f_ds}, g={g_ds}, rho={rho}\n"
                f"  (f*g)(rho)   = {lhs}\n"
                f"  f(rho)*g(rho)= {rhs}"
            )


# ---------------------------------------------------------------------------
# P8: scale_input
# ---------------------------------------------------------------------------

def test_p8_scale_input(samples: int = 200, seed: int = 7) -> None:
    """
    val(f.scale_input(alpha), rho) == val(f, alpha*rho).
    """
    random.seed(seed)
    for i in range(samples):
        ds = _rand_coeffs()
        rho = _rand_rho()
        alpha = complex(random.uniform(-2, 2), random.uniform(-2, 2))

        f = CnrsH.from_list(ds)
        f_scaled = f.scale_input(alpha)

        lhs = f_scaled(rho)
        rhs = f(alpha * rho)

        if not _close(lhs, rhs, tol=1e-8):
            raise AssertionError(
                f"P8 scale_input failed (sample {i}):\n"
                f"  ds={ds}, alpha={alpha}, rho={rho}\n"
                f"  f.scale_input(alpha)(rho) = {lhs}\n"
                f"  f(alpha*rho)              = {rhs}"
            )


# ---------------------------------------------------------------------------
# Smoke tests for constructors and helpers
# ---------------------------------------------------------------------------

def test_constructors() -> None:
    """Basic sanity checks on constructors."""
    # zero
    z = CnrsH.zero()
    assert z(1+0j) == 0, "zero() failed"

    # one
    o = CnrsH.one()
    assert o(2+0j) == 1, "one() failed"

    # identity
    ident = CnrsH.identity()
    rho = 3+2j
    assert _close(ident(rho), rho), f"identity() failed: got {ident(rho)}, expected {rho}"

    # exponential: sum_{n=0}^{N-1} rho^n/n! ~ exp(rho) for large N
    exp_f = CnrsH.exponential(1, terms=20)
    import cmath
    assert _close(exp_f(1+0j), cmath.exp(1+0j), tol=1e-6), \
        f"exponential() failed: got {exp_f(1+0j)}, expected {cmath.exp(1+0j)}"

    # nth_derivative of a monomial [0,0,...,0,1] should give [1]
    mono = CnrsH.from_list([0, 0, 0, 1])   # d3*rho^3/3!
    D3 = mono.nth_derivative(3)
    assert D3.coeff(0) == 1, f"D^3 monomial failed: {D3}"

    # pretty print (just check it runs)
    f = CnrsH.from_list([1, 2, 3])
    _ = f.pretty()


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_all_tests() -> None:
    """Run the complete CnrsH verification suite."""
    print("Running CnrsH verification suite...")

    test_constructors()
    print("  ✓ Constructors and helpers")

    test_p1_differentiation()
    print("  ✓ P1  Exact differentiation  (algebraic == numerical derivative)")

    test_p2_integration()
    print("  ✓ P2  Exact integration       (algebraic == numerical integral)")

    test_p3_ftc()
    print("  ✓ P3  Fundamental Theorem     (D ∘ int == identity, exact)")

    test_p4_leibniz()
    print("  ✓ P4  Leibniz rule            (D(f*g) == Df*g + f*Dg)")

    test_p5_linearity()
    print("  ✓ P5  Linearity               (D(af+bg) == aDf + bDg)")

    test_p6_nth_derivative()
    print("  ✓ P6  nth derivative          (D^n drops n leading coefficients)")

    test_p7_egf_multiplication()
    print("  ✓ P7  EGF multiplication      (val(f*g) == val(f)*val(g))")

    test_p8_scale_input()
    print("  ✓ P8  Scale input             (f.scale_input(α)(ρ) == f(αρ))")

    print("All CnrsH tests passed.")
