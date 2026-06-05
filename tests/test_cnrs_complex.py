"""
tests/test_cnrs_complex.py
--------------------------
Tests for CnrsComplex: the unified complex interface for the CNRS toolkit.

Tests cover:
  - Construction: from value, from_polar, from_cnrs_float, zero, one, array
  - Properties: .value, .real, .imag, .L, .cnrs_float
  - Measurement: abs(), phase(), modulus_sq(), conjugate(),
                 real_part(), imag_part()
  - Arithmetic: +, -, *, /, negation, reflected operators
  - Type coercions: complex(), float()
  - Error reporting: encoding_error(), relative_error()
  - Array utilities: encode_array(), decode_array(), to_numpy()
  - Error bounds: verified against the theoretical 2*5^{-(L-1)/2} bound
  - Algebraic laws: commutativity, associativity, distributivity

All floating-point comparisons use tolerance tol = 100 * 5^{-(L-1)/2},
which is ~20x the single-operation error bound.

Session 42, 2026-06-06.
"""

from __future__ import annotations
import sys, os, math, cmath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from cnrs.cnrs_complex import (
    CnrsComplex, encode_array, decode_array, DEFAULT_L
)

# ---------------------------------------------------------------------------
# Tolerance helper
# ---------------------------------------------------------------------------

def _tol(L: int = DEFAULT_L) -> float:
    """100 * theoretical single-operation error bound at mantissa length L."""
    return 100 * 2 * (5 ** (-(L - 1) / 2))

def _check(label: str, got: complex, expected: complex, L: int = DEFAULT_L):
    tol = _tol(L)
    err = abs(got - expected)
    assert err < tol, (
        f"{label}: got={got!r}, expected={expected!r}, err={err:.3e}, tol={tol:.3e}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Construction
# ══════════════════════════════════════════════════════════════════════════════

def test_construct_from_complex():
    z = CnrsComplex(0.5 - 0.3j)
    assert z.L == DEFAULT_L
    _check("construct complex", complex(z), 0.5 - 0.3j)

def test_construct_from_float():
    z = CnrsComplex(1.5)
    _check("construct float", complex(z), 1.5 + 0j)

def test_construct_from_int():
    z = CnrsComplex(3)
    _check("construct int", complex(z), 3 + 0j)

def test_construct_custom_L():
    z = CnrsComplex(0.5 - 0.3j, L=10)
    assert z.L == 10
    _check("construct L=10", complex(z), 0.5 - 0.3j, L=10)

def test_construct_zero_value():
    z = CnrsComplex(0j)
    _check("construct zero", complex(z), 0j)

def test_construct_from_polar():
    z = CnrsComplex.from_polar(1.0, 0.0)
    _check("polar r=1 theta=0", complex(z), 1.0 + 0j)

def test_construct_from_polar_quarter_turn():
    z = CnrsComplex.from_polar(1.0, math.pi / 2)
    _check("polar r=1 theta=pi/2", complex(z), 1j)

def test_construct_from_polar_general():
    r, theta = 0.8, 1.2
    z = CnrsComplex.from_polar(r, theta)
    expected = r * cmath.exp(1j * theta)
    _check("polar general", complex(z), expected)

def test_construct_zero_classmethod():
    z = CnrsComplex.zero()
    _check("zero()", complex(z), 0j)

def test_construct_one_classmethod():
    z = CnrsComplex.one()
    _check("one()", complex(z), 1.0 + 0j)

def test_construct_from_cnrs_float():
    from cnrs.cnrs_float import encode
    f = encode(0.5 - 0.3j, L=12)
    z = CnrsComplex.from_cnrs_float(f)
    assert z.L == 12
    _check("from_cnrs_float", complex(z), 0.5 - 0.3j, L=12)

def test_construct_array():
    vals = [0.1 + 0.2j, 0.3 - 0.1j, 0.5 + 0.5j]
    czs = CnrsComplex.array(vals)
    assert len(czs) == 3
    for v, z in zip(vals, czs):
        _check(f"array {v}", complex(z), v)


# ══════════════════════════════════════════════════════════════════════════════
# Properties
# ══════════════════════════════════════════════════════════════════════════════

def test_real_property():
    z = CnrsComplex(0.5 - 0.3j)
    assert abs(z.real - 0.5) < _tol()

def test_imag_property():
    z = CnrsComplex(0.5 - 0.3j)
    assert abs(z.imag - (-0.3)) < _tol()

def test_value_property():
    z = CnrsComplex(0.5 - 0.3j)
    _check("value property", z.value, 0.5 - 0.3j)

def test_L_property():
    z = CnrsComplex(1.0, L=10)
    assert z.L == 10

def test_cnrs_float_property():
    from cnrs.cnrs_float import CnrsFloat
    z = CnrsComplex(0.5 - 0.3j)
    assert isinstance(z.cnrs_float, CnrsFloat)


# ══════════════════════════════════════════════════════════════════════════════
# Measurement
# ══════════════════════════════════════════════════════════════════════════════

def test_abs():
    z = CnrsComplex(3.0 + 4.0j)
    assert abs(abs(z) - 5.0) < _tol()

def test_abs_pure_real():
    z = CnrsComplex(2.0)
    assert abs(abs(z) - 2.0) < _tol()

def test_abs_pure_imag():
    z = CnrsComplex(1j)
    assert abs(abs(z) - 1.0) < _tol()

def test_phase_zero():
    z = CnrsComplex(1.0)
    assert abs(z.phase() - 0.0) < _tol()

def test_phase_pi_over_2():
    z = CnrsComplex(1j)
    assert abs(z.phase() - math.pi / 2) < _tol()

def test_phase_general():
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    assert abs(z.phase() - cmath.phase(c)) < _tol()

def test_modulus_sq():
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    assert abs(z.modulus_sq() - abs(c) ** 2) < _tol()

def test_conjugate_value():
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    _check("conjugate value", complex(z.conjugate()), c.conjugate())

def test_conjugate_type():
    z = CnrsComplex(0.5 - 0.3j)
    assert isinstance(z.conjugate(), CnrsComplex)

def test_conjugate_same_L():
    z = CnrsComplex(0.5 - 0.3j, L=10)
    assert z.conjugate().L == 10

def test_real_part():
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    assert abs(z.real_part() - c.real) < _tol()

def test_imag_part():
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    assert abs(z.imag_part() - c.imag) < _tol()

def test_norm_of_conjugate_product():
    """z * conj(z) should equal |z|^2 (real, positive)."""
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    prod = z * z.conjugate()
    assert abs(complex(prod).imag) < _tol(), "z*conj(z) should be real"
    assert abs(complex(prod).real - abs(c)**2) < _tol(), "z*conj(z) should be |z|^2"


# ══════════════════════════════════════════════════════════════════════════════
# Arithmetic
# ══════════════════════════════════════════════════════════════════════════════

def test_add_two_cnrs():
    c1, c2 = 0.5 - 0.3j, 0.2 + 0.7j
    _check("z+w", complex(CnrsComplex(c1) + CnrsComplex(c2)), c1 + c2)

def test_add_cnrs_and_complex():
    c1 = 0.5 - 0.3j
    z = CnrsComplex(c1)
    _check("z+c", complex(z + (0.2 + 0.7j)), c1 + 0.2 + 0.7j)

def test_add_reflected():
    c1, c2 = 0.5 - 0.3j, 0.2 + 0.7j
    _check("c+z", complex(c2 + CnrsComplex(c1)), c2 + c1)

def test_sub():
    c1, c2 = 0.5 - 0.3j, 0.2 + 0.7j
    _check("z-w", complex(CnrsComplex(c1) - CnrsComplex(c2)), c1 - c2)

def test_sub_reflected():
    c1, c2 = 0.5 - 0.3j, 0.2 + 0.7j
    _check("c-z", complex(c2 - CnrsComplex(c1)), c2 - c1)

def test_mul():
    c1, c2 = 0.5 - 0.3j, 0.2 + 0.7j
    _check("z*w", complex(CnrsComplex(c1) * CnrsComplex(c2)), c1 * c2)

def test_mul_by_scalar():
    c = 0.5 - 0.3j
    _check("z*2", complex(CnrsComplex(c) * 2), c * 2)

def test_mul_reflected():
    c = 0.5 - 0.3j
    _check("2*z", complex(2 * CnrsComplex(c)), 2 * c)

def test_div():
    c1, c2 = 0.5 - 0.3j, 0.2 + 0.7j
    _check("z/w", complex(CnrsComplex(c1) / CnrsComplex(c2)), c1 / c2)

def test_div_by_scalar():
    c = 0.5 - 0.3j
    _check("z/2", complex(CnrsComplex(c) / 2), c / 2)

def test_div_reflected():
    c = 0.5 - 0.3j
    _check("1/z", complex(1 / CnrsComplex(c)), 1 / c)

def test_neg():
    c = 0.5 - 0.3j
    _check("-z", complex(-CnrsComplex(c)), -c)

def test_div_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        CnrsComplex(1.0) / CnrsComplex(0j)

def test_div_zero_reflected_raises():
    with pytest.raises(ZeroDivisionError):
        1.0 / CnrsComplex(0j)

def test_arithmetic_preserves_L():
    z = CnrsComplex(0.5 - 0.3j, L=10)
    w = CnrsComplex(0.2 + 0.7j, L=10)
    assert (z + w).L == 10
    assert (z * w).L == 10


# ══════════════════════════════════════════════════════════════════════════════
# Type coercions
# ══════════════════════════════════════════════════════════════════════════════

def test_complex_coercion():
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    assert isinstance(complex(z), complex)
    _check("complex(z)", complex(z), c)

def test_float_coercion_real():
    z = CnrsComplex(2.5 + 0j)
    assert abs(float(z) - 2.5) < _tol()

def test_float_coercion_raises_for_complex():
    z = CnrsComplex(1.0 + 1.0j)
    with pytest.raises(ValueError):
        float(z)


# ══════════════════════════════════════════════════════════════════════════════
# Error bounds
# ══════════════════════════════════════════════════════════════════════════════

def test_encoding_error_within_bound():
    """Encoding error should be within the theoretical bound 2*5^{-(L-1)/2}."""
    from cnrs.cnrs_float import ABS_Z0
    c = 0.5 - 0.3j
    for L in [8, 10, 12, 14]:
        z = CnrsComplex(c, L)
        err = z.encoding_error(c)
        bound = 2.0 * ABS_Z0 ** (-(L - 1))
        assert err <= bound + 1e-12, (
            f"L={L}: error {err:.4e} exceeds bound {bound:.4e}"
        )

def test_error_decreases_with_L():
    """Encoding error should decrease (non-strictly) as L increases."""
    c = 0.5 - 0.3j
    errs = [CnrsComplex(c, L).encoding_error(c) for L in range(6, 16)]
    for i in range(len(errs) - 1):
        assert errs[i] >= errs[i + 1] - 1e-10, (
            f"Error did not decrease from L={i+6} to L={i+7}: "
            f"{errs[i]:.4e} -> {errs[i+1]:.4e}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Array utilities
# ══════════════════════════════════════════════════════════════════════════════

def test_encode_array_length():
    vals = [0.1 + 0.2j, 0.3 - 0.1j, 0.5 + 0.5j]
    czs = encode_array(vals)
    assert len(czs) == 3

def test_encode_array_values():
    vals = [0.1 + 0.2j, 0.3 - 0.1j, 0.5 + 0.5j]
    czs = encode_array(vals)
    for v, z in zip(vals, czs):
        _check(f"encode_array {v}", complex(z), v)

def test_decode_array():
    vals = [0.1 + 0.2j, 0.3 - 0.1j, 0.5 + 0.5j]
    decoded = decode_array(encode_array(vals))
    assert len(decoded) == 3
    for v, d in zip(vals, decoded):
        _check(f"decode_array {v}", d, v)

def test_to_numpy():
    try:
        import numpy as np
    except ImportError:
        pytest.skip("numpy not installed")
    from cnrs.cnrs_complex import to_numpy
    vals = [0.1 + 0.2j, 0.3 - 0.1j, 0.5 + 0.5j]
    arr = to_numpy(encode_array(vals))
    assert arr.dtype == np.complex128
    assert len(arr) == 3
    for v, a in zip(vals, arr):
        _check(f"to_numpy {v}", a, v)

def test_encode_array_custom_L():
    vals = [0.1 + 0.2j, 0.5 + 0.5j]
    czs = encode_array(vals, L=10)
    assert all(z.L == 10 for z in czs)


# ══════════════════════════════════════════════════════════════════════════════
# Algebraic laws (approximate, within tolerance)
# ══════════════════════════════════════════════════════════════════════════════

def test_commutativity_add():
    c1, c2 = 0.5 - 0.3j, 0.2 + 0.7j
    z1, z2 = CnrsComplex(c1), CnrsComplex(c2)
    _check("commutativity +", complex(z1 + z2), complex(z2 + z1))

def test_commutativity_mul():
    c1, c2 = 0.5 - 0.3j, 0.2 + 0.7j
    z1, z2 = CnrsComplex(c1), CnrsComplex(c2)
    _check("commutativity *", complex(z1 * z2), complex(z2 * z1))

def test_associativity_add():
    c1, c2, c3 = 0.5 - 0.3j, 0.2 + 0.7j, -0.1 + 0.4j
    z1, z2, z3 = CnrsComplex(c1), CnrsComplex(c2), CnrsComplex(c3)
    _check("assoc +", complex((z1 + z2) + z3), c1 + c2 + c3)
    _check("assoc + rhs", complex(z1 + (z2 + z3)), c1 + c2 + c3)

def test_distributivity():
    c1, c2, c3 = 0.5 - 0.3j, 0.2 + 0.7j, -0.1 + 0.4j
    z1, z2, z3 = CnrsComplex(c1), CnrsComplex(c2), CnrsComplex(c3)
    _check("distributivity", complex(z1 * (z2 + z3)), c1 * (c2 + c3))

def test_additive_identity():
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    zero = CnrsComplex.zero()
    _check("additive identity", complex(z + zero), c)

def test_multiplicative_identity():
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    one = CnrsComplex.one()
    _check("multiplicative identity", complex(z * one), c)

def test_additive_inverse():
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    result = complex(z + (-z))
    assert abs(result) < _tol(), f"z + (-z) should be ~0, got {result}"

def test_multiply_by_conjugate_is_real():
    """z * conj(z) = |z|^2 (real, no imaginary part)."""
    c = 0.5 - 0.3j
    z = CnrsComplex(c)
    prod = z * z.conjugate()
    assert abs(complex(prod).imag) < _tol()
    assert abs(complex(prod).real - abs(c)**2) < _tol()
