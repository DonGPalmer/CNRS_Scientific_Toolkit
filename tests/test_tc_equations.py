"""
tests/test_tc_equations.py
--------------------------
Pytest suite linking the CNRS Python package to concrete equations and
claims in the Technical Companion (TC), Chapters 16--21 and 24.

Each test function names the TC chapter and claim it covers.  Bridge-
identity tests (TC Ch.24) are explicitly labelled CONDITIONAL: they
verify algebraic correctness under the bridge assumption
  Delta(L) = exp(4/L) - 1,
not the physical derivation of that assumption.

This file was promoted from cnrs_tc_equation_test_harness_v1.py
(Session 42, 2026-06-06).  Extend by adding tests keyed to TC equation
numbers once TC equation labels stabilise.

Does NOT establish:
  - full representation of all complex values
  - metric completeness of infinite expansions
  - physical validity of the Scale Space / CNRS bridge
  - derivation of the Born rule
  - proof of open TC claims
"""

from __future__ import annotations
import math
import random
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cnrs.cnrs_repr  import Z0, gaussian_to_cnrs_str, cnrs_to_gaussian
from cnrs.cnrs_add   import CARRY_SET_PAIRS, ADDITION_TABLE, add_cnrs
from cnrs.cnrs_mul   import mul_cnrs
from cnrs.cnrs_layer2 import Layer2
from cnrs.cnrs_h     import CnrsH


def assert_close(a: complex | float, b: complex | float,
                 tol: float = 1e-9, label: str = "") -> None:
    if abs(a - b) > tol:
        raise AssertionError(f"{label}: got {a!r}, expected {b!r}, diff={abs(a-b):.3e}")


# ── TC Chapter 16: base and digit architecture ────────────────────────────────

def test_tc_ch16_base_value():
    """TC Ch.16 — z0 = -2+i is the CNRS base."""
    assert Z0 == complex(-2, 1), f"Z0 mismatch: {Z0}"


def test_tc_ch16_base_norm():
    """TC Ch.16 — N(z0) = z0*conj(z0) = 5 (digit alphabet size)."""
    norm = int(round(Z0.real ** 2 + Z0.imag ** 2))
    assert norm == 5, f"N(z0) mismatch: {norm}"


# ── TC Chapter 17: finite Gaussian-integer representation ─────────────────────

def test_tc_ch17_roundtrip_samples():
    """TC Ch.17 — gaussian_to_cnrs_str / cnrs_to_gaussian round-trip for
    representative Gaussian integers including zero, units, and larger values."""
    samples = [0+0j, 1+0j, -1+0j, 0+1j, 0-1j, 3+4j, -7+2j, 11-9j]
    for g in samples:
        s = gaussian_to_cnrs_str(g)
        got = cnrs_to_gaussian(s)
        assert got == g, f"Round-trip failed: {g} → '{s}' → {got}"


def test_tc_ch17_roundtrip_random():
    """TC Ch.17 — round-trip for 200 random Gaussian integers in [-50, 50]."""
    rng = random.Random(20260606)
    for _ in range(200):
        g = complex(rng.randint(-50, 50), rng.randint(-50, 50))
        s = gaussian_to_cnrs_str(g)
        got = cnrs_to_gaussian(s)
        assert got == g, f"Round-trip failed: {g} → '{s}' → {got}"


# ── TC Chapter 18: Layer-2 branch-index arithmetic ───────────────────────────

def test_tc_ch18_layer2_addition_value():
    """TC Ch.18 — Layer-2 addition preserves Gaussian-integer value."""
    L1 = Layer2.from_gaussian(3+2j, k=4)
    L2 = Layer2.from_gaussian(-1+5j, k=-2)
    assert (L1 + L2).to_gaussian() == 2+7j


def test_tc_ch18_layer2_addition_branch():
    """TC Ch.18 — Layer-2 addition sums branch indices."""
    L1 = Layer2.from_gaussian(3+2j, k=4)
    L2 = Layer2.from_gaussian(-1+5j, k=-2)
    assert (L1 + L2).k == 2


def test_tc_ch18_layer2_multiplication_value():
    """TC Ch.18 — Layer-2 multiplication preserves Gaussian-integer value."""
    L1 = Layer2.from_gaussian(3+2j, k=4)
    L2 = Layer2.from_gaussian(-1+5j, k=-2)
    assert (L1 * L2).to_gaussian() == (3+2j) * (-1+5j)


def test_tc_ch18_layer2_multiplication_branch():
    """TC Ch.18 — Layer-2 multiplication sums branch indices."""
    L1 = Layer2.from_gaussian(3+2j, k=4)
    L2 = Layer2.from_gaussian(-1+5j, k=-2)
    assert (L1 * L2).k == 2


# ── TC Chapter 19: addition transducer and arithmetic semantics ───────────────

def test_tc_ch19_transducer_carry_count():
    """TC Ch.19 — addition transducer has exactly 14 carry states."""
    assert len(CARRY_SET_PAIRS) == 14, \
        f"Expected 14 carry states, got {len(CARRY_SET_PAIRS)}"


def test_tc_ch19_transducer_table_size():
    """TC Ch.19 — addition table has 14 × 5 × 5 = 350 entries."""
    assert len(ADDITION_TABLE) == 14 * 5 * 5, \
        f"Expected 350 entries, got {len(ADDITION_TABLE)}"


def test_tc_ch19_transducer_carry_set():
    """TC Ch.19 — carry-state list matches the specified 14 pairs."""
    expected = [
        (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (-1, -1), (-2, 0), (2, 1), (-2, -1),
        (-2, -2), (2, 2), (-3, -1), (-3, -2),
    ]
    assert CARRY_SET_PAIRS == expected, \
        f"Carry-state mismatch:\n  got      {CARRY_SET_PAIRS}\n  expected {expected}"


def test_tc_ch19_addition_semantics():
    """TC Ch.19 — CNRS-A addition matches Gaussian integer addition,
    100 random samples in [-8, 8] × [-8, 8]."""
    rng = random.Random(20260604)
    for _ in range(100):
        a = complex(rng.randint(-8, 8), rng.randint(-8, 8))
        b = complex(rng.randint(-8, 8), rng.randint(-8, 8))
        sa, sb = gaussian_to_cnrs_str(a), gaussian_to_cnrs_str(b)
        result = cnrs_to_gaussian(add_cnrs(sa, sb))
        assert result == a + b, f"add_cnrs({a}, {b}): got {result}, expected {a+b}"


def test_tc_ch19_multiplication_semantics():
    """TC Ch.19 — CNRS-A multiplication matches Gaussian integer multiplication,
    100 random samples in [-8, 8] × [-8, 8]."""
    rng = random.Random(20260604)
    for _ in range(100):
        a = complex(rng.randint(-8, 8), rng.randint(-8, 8))
        b = complex(rng.randint(-8, 8), rng.randint(-8, 8))
        sa, sb = gaussian_to_cnrs_str(a), gaussian_to_cnrs_str(b)
        result = cnrs_to_gaussian(mul_cnrs(sa, sb))
        assert result == a * b, f"mul_cnrs({a}, {b}): got {result}, expected {a*b}"


def test_tc_ch19_arithmetic_larger_range():
    """TC Ch.19 — CNRS-A add/mul for larger Gaussian integers in [-50, 50],
    50 random samples."""
    rng = random.Random(20260606_2)
    for _ in range(50):
        a = complex(rng.randint(-50, 50), rng.randint(-50, 50))
        b = complex(rng.randint(-50, 50), rng.randint(-50, 50))
        sa, sb = gaussian_to_cnrs_str(a), gaussian_to_cnrs_str(b)
        assert cnrs_to_gaussian(add_cnrs(sa, sb)) == a + b
        assert cnrs_to_gaussian(mul_cnrs(sa, sb)) == a * b


# ── TC Chapter 20: CNRS-H calculus ───────────────────────────────────────────

def test_tc_ch20_exp_derivative_coeffs():
    """TC Ch.20 — derivative of exp(ρ) is exp(ρ): coefficient shift returns
    the same stream (EGF convention, coefficients all 1)."""
    exp_rho = CnrsH.exponential(1, terms=8)
    assert exp_rho.differentiate().coeffs == tuple([1] * 7)


def test_tc_ch20_exp_derivative_values():
    """TC Ch.20 — derivative of exp(ρ) evaluates correctly at sample points."""
    exp_rho = CnrsH.exponential(1, terms=8)
    for rho in [0, 0.5, -1.0, 1+0.25j]:
        assert_close(
            exp_rho.differentiate().evaluate(rho),
            CnrsH.exponential(1, terms=7).evaluate(rho),
            label=f"exp derivative at rho={rho}"
        )


def test_tc_ch20_identity_derivative():
    """TC Ch.20 — derivative of the identity stream ρ → ρ is the constant 1."""
    rho_fn = CnrsH.identity()
    one = rho_fn.differentiate()
    assert one.coeffs == (1,), f"Expected (1,), got {one.coeffs}"


def test_tc_ch20_egf_product_convention():
    """TC Ch.20 — EGF product convention: ρ·ρ has coefficient stream (0, 0, 2).
    Under the EGF convention f(ρ) = Σ aₙ ρⁿ/n!, the function ρ² has
    coefficients [0, 0, 2] because ρ² = 2 · ρ²/2!."""
    rho_fn = CnrsH.identity()
    rho_squared = rho_fn * rho_fn
    assert rho_squared.coeffs == (0, 0, 2), \
        f"Expected (0, 0, 2), got {rho_squared.coeffs}"


# ── TC Chapter 24: bridge identity (CONDITIONAL) ─────────────────────────────

def test_tc_ch24_bridge_identity_conditional():
    """TC Ch.24 — triangulation identity T(Delta(L)) = 1 + 2/L is
    algebraically correct for the specified functions.

    CONDITIONAL: this verifies algebra under the bridge assumption
      Delta(L) = exp(4/L) - 1
    and does NOT establish the physical derivation of that assumption.
    The bridge identification z0 = e^(2/L) is a proposed link, not a
    derived result.
    """
    def Delta(L: float) -> float:
        return math.exp(4.0 / L) - 1.0

    def T(delta: float) -> float:
        return 1.0 + 0.5 * math.log(1.0 + delta)

    for L in [2.0, 5.0, 10.0, 20.0, 100.0, 1e3]:
        assert_close(T(Delta(L)), 1.0 + 2.0 / L, tol=1e-12,
                     label=f"bridge identity at L={L}")
