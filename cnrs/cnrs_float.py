"""
cnrs_float.py
=============
CNRS floating-point arithmetic (CNRS-float).

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533

Architecture
------------
A CNRS-float number is a pair (M, e) where:

    value = M * z0^e,   z0 = -2 + i,   M a Gaussian integer

M is stored as a CNRS-A digit string of length L (the mantissa length).
e is a signed integer exponent.

This is the exact complex analogue of IEEE-754 floating-point:

    IEEE-754:    value = mantissa * 2^exponent
    CNRS-float:  value = mantissa * z0^exponent

Normalisation
-------------
The exponent e is chosen so that the Gaussian integer M satisfies

    |z0|^(L-1) <= |M| < |z0|^L

i.e. M fills an L-digit CNRS mantissa.  The initial estimate is

    e = floor(log|c| / log|z0|) - (L-1)

followed by an overflow loop: if gaussian_to_cnrs(M) has more than L
digits, increment e by 1 and re-round until it fits.

Exact and approximate classes
------------------------------
Exact (for sufficient L):
    Z[i]            -- Gaussian integers (encode uses e=0 + direct digits)
    Z[i][1/z0]      -- fractions of the form d/z0^k, via encode_z0_fraction

Approximate:
    All other complex numbers, including Gaussian fractions a/b with
    gcd(N(b), 5) = 1.

    CRITICAL NOTE: The standard CNRS greedy algorithm produces all-zero
    digits for denominators coprime to 5 (stuck-greedy obstruction,
    Session 27, May 2026).  Z[i]-rounding is the correct method.

Error bound:
    |c_hat - c| <= C * |z0|^{-(L-1)} = C * 5^{-(L-1)/2}

References
----------
Palmer (2026), CNRS_problem3_arithmetic_closure_v4.tex
Palmer (2026), CNRS_problem4_partial_completeness_v3.tex
AI2/AI0 discussion, Session 28, May 27, 2026
"""

from __future__ import annotations
import math
from typing import List

from .cnrs_repr import Z0, DIGITS, gaussian_to_cnrs_digits, cnrs_to_gaussian

# Aliases matching the old cnrs_demo names used throughout this module
N_Z0 = 5  # N(z0) = (-2)^2 + 1^2 = 5
def gaussian_to_cnrs(z): return gaussian_to_cnrs_digits(z)
def cnrs_to_complex(digits, offset=0):
    result = complex(0, 0)
    current_power = Z0 ** offset
    for d in digits:
        result += d * current_power
        current_power *= Z0
    return result

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ABS_Z0     = math.sqrt(N_Z0)     # |z0| = sqrt(5)
LOG_ABS_Z0 = math.log(ABS_Z0)    # (1/2) log 5
DEFAULT_L  = 8

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_gaussian_integer(z: complex, tol: float = 1e-9) -> bool:
    return (abs(z.real - round(z.real)) < tol and
            abs(z.imag - round(z.imag)) < tol)

def round_to_gaussian(z: complex) -> complex:
    """Round to nearest Gaussian integer (round-half-to-even)."""
    return complex(round(z.real), round(z.imag))

def _encode_approx(c: complex, L: int):
    """
    Return (digits, e) for an approximate CNRS-float encoding of c.

    Uses Z[i]-rounding, not the greedy fractional algorithm.
    Iterates the exponent upward until the rounded mantissa fits in L digits.
    """
    # Initial exponent estimate
    e = math.floor(math.log(abs(c)) / LOG_ABS_Z0) - (L - 1)

    for _ in range(L + 5):          # at most L+5 iterations
        y = c / (Z0 ** e)
        M = round_to_gaussian(y)
        if M == 0:
            return [0] * L, e
        digits = gaussian_to_cnrs(M)
        if len(digits) <= L:
            return digits + [0] * (L - len(digits)), e
        e += 1                       # mantissa overflowed; scale up

    # Fallback: truncate (should not reach here for well-conditioned inputs)
    y = c / (Z0 ** e)
    M = round_to_gaussian(y)
    digits = gaussian_to_cnrs(M)
    return digits[:L], e

# ---------------------------------------------------------------------------
# CnrsFloat
# ---------------------------------------------------------------------------

class CnrsFloat:
    """
    A CNRS floating-point number.

    Stores:
        mantissa : List[int]  CNRS-A digit string, length L, LSB first
        exponent : int        power of z0
        L        : int        mantissa length

    Value: M * z0^exponent  where M = cnrs_to_complex(mantissa).
    """

    def __init__(self, mantissa: List[int], exponent: int, L: int):
        if len(mantissa) != L:
            raise ValueError(f"Mantissa length {len(mantissa)} != L={L}")
        if not all(d in DIGITS for d in mantissa):
            raise ValueError(f"Invalid digit in mantissa: {mantissa}")
        self.mantissa = list(mantissa)
        self.exponent = exponent
        self.L = L

    def to_complex(self) -> complex:
        return cnrs_to_complex(self.mantissa) * (Z0 ** self.exponent)

    def mantissa_value(self) -> complex:
        return cnrs_to_complex(self.mantissa)

    def __repr__(self) -> str:
        ds = ''.join(str(d) for d in reversed(self.mantissa))
        return f"CnrsFloat(mantissa={ds!r}, exp={self.exponent}, L={self.L})"

    def __str__(self) -> str:
        v  = self.to_complex()
        M  = self.mantissa_value()
        ds = ''.join(str(d) for d in reversed(self.mantissa))
        return (f"[{ds}] * z0^{self.exponent}  "
                f"≈ {v.real:.6g}{v.imag:+.6g}j  "
                f"(M = {M.real:.0f}{M.imag:+.0f}j)")

# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

def encode(c: complex, L: int = DEFAULT_L) -> CnrsFloat:
    """
    Encode a complex number c as a CnrsFloat with mantissa length L.

    For Gaussian integers: exact, using e=0 and direct CNRS integer digits.
    For all others:        Z[i]-rounding with exponent chosen for L digits.

    The greedy fractional algorithm is NOT used.
    """
    if L < 1:
        raise ValueError(f"L must be >= 1, got {L}")

    if c == 0:
        return CnrsFloat([0] * L, 0, L)

    # Exact path: Gaussian integers
    if _is_gaussian_integer(c):
        M      = complex(round(c.real), round(c.imag))
        digits = gaussian_to_cnrs(M)
        digits = (digits + [0] * (L - len(digits)))[:L]
        return CnrsFloat(digits, 0, L)

    # Approximate path
    digits, e = _encode_approx(c, L)
    return CnrsFloat(digits, e, L)


def encode_z0_fraction(numerator: complex, k: int,
                       L: int = DEFAULT_L) -> CnrsFloat:
    """
    Exactly encode value = numerator / z0^k  (a Z[i][1/z0]-fraction).

    numerator must be a Gaussian integer; k >= 0.
    """
    if not _is_gaussian_integer(numerator):
        raise ValueError(f"numerator {numerator} is not a Gaussian integer")
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    M      = complex(round(numerator.real), round(numerator.imag))
    digits = gaussian_to_cnrs(M)
    digits = (digits + [0] * (L - len(digits)))[:L]
    return CnrsFloat(digits, -k, L)

# ---------------------------------------------------------------------------
# Decode and error analysis
# ---------------------------------------------------------------------------

def decode(f: CnrsFloat) -> complex:
    return f.to_complex()

def encoding_error(c: complex, f: CnrsFloat) -> float:
    return abs(decode(f) - c)

def ulp(f: CnrsFloat) -> float:
    """Unit in the last place: |z0|^(exponent+1)."""
    return ABS_Z0 ** (f.exponent + 1)

def relative_error(c: complex, f: CnrsFloat) -> float:
    if abs(c) == 0:
        return 0.0
    return encoding_error(c, f) / abs(c)

# ---------------------------------------------------------------------------
# Worked examples
# ---------------------------------------------------------------------------

def _ex1_gaussian_integer():
    c = complex(3, 2)
    f = encode(c, L=4)
    return dict(c=c, f=f, c_hat=decode(f), error=encoding_error(c,f),
                exact=encoding_error(c,f)<1e-10,
                digits_check=gaussian_to_cnrs(c))

def _ex2_z0_fraction():
    c = 1.0 / Z0
    f = encode_z0_fraction(complex(1,0), k=1, L=4)
    return dict(c=c, f=f, c_hat=decode(f), error=encoding_error(c,f),
                exact=encoding_error(c,f)<1e-10)

def _ex3_coprime5():
    c = complex(0.5, -0.5)
    L = 4
    f = encode(c, L)
    bound = 2.0 * ABS_Z0 ** (-(L-1))
    return dict(c=c, f=f, c_hat=decode(f), error=encoding_error(c,f),
                exact=False, error_bound=bound)

def _ex4_ai2():
    c = complex(1.5, 1.0)
    f = encode(c, L=2)
    return dict(c=c, f=f, c_hat=decode(f), error=encoding_error(c,f),
                ai2_M=complex(2,1), ai2_e=0, ai2_err=0.5)

# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

def run_tests() -> int:
    failures = 0

    def check(name: str, cond: bool, detail: str = '') -> None:
        nonlocal failures
        if not cond: failures += 1
        suffix = f'  [{detail}]' if detail else ''
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{suffix}")

    print("=" * 60)
    print("CNRS-float test suite")
    print("=" * 60)

    # F1: Zero
    print("\nF1  Zero")
    f0 = encode(0j, L=4)
    check("F1.1  zero mantissa", all(d==0 for d in f0.mantissa))
    check("F1.2  zero decode",   abs(decode(f0)) < 1e-10)

    # F2: Gaussian integers exact
    print("\nF2  Gaussian integers (exact)")
    test_ints = [1+0j, 1j, -1+0j, -1j, 3+2j, -2+3j, 5-4j, 7+7j]
    for c in test_ints:
        f   = encode(c, L=8)
        err = encoding_error(c, f)
        check(f"F2    c={c}", err < 1e-9, f"err={err:.2e}")

    # F3: Z[i][1/z0]-fractions exact
    print("\nF3  Z[i][1/z0]-fractions (exact)")
    cases = [
        (1.0/Z0,             complex(1,0), 1, "1/z0"),
        (1.0/(Z0**2),        complex(1,0), 2, "1/z0^2"),
        (complex(2,3)/(Z0**2), complex(2,3), 2, "(2+3i)/z0^2"),
    ]
    for c, num, k, label in cases:
        f   = encode_z0_fraction(num, k=k, L=6)
        err = encoding_error(c, f)
        check(f"F3    {label}", err < 1e-9, f"err={err:.2e}")

    # F4: Coprime-5 fractions -- error < 2 (sanity)
    print("\nF4  Coprime-5 fractions (approximate)")
    coprime5 = [(0.5-0.5j,"(1-i)/2"),(0.5+0j,"1/2"),(1/3+0j,"1/3"),
                (0+0.5j,"i/2"),(1.5+1j,"(3+2i)/2")]
    for c, label in coprime5:
        f   = encode(c, L=8)
        err = encoding_error(c, f)
        check(f"F4    {label}", err < 2.0, f"err={err:.4f}")

    # F5: Error decreases with L
    print("\nF5  Error decreases with L")
    c_test = 0.5-0.5j
    errs = [encoding_error(c_test, encode(c_test, L)) for L in range(2,10)]
    ok = all(errs[i] >= errs[i+1] - 1e-9 for i in range(len(errs)-1))
    check("F5.1  non-increasing", ok, ' '.join(f'{e:.4f}' for e in errs))

    # F6: Roundtrip Gaussian integers
    print("\nF6  Roundtrip Gaussian integers")
    for c in test_ints:
        check(f"F6    c={c}", abs(decode(encode(c, L=8)) - c) < 1e-9)

    # F7: 3+2i known digits
    print("\nF7  Worked example: 3+2i")
    ex = _ex1_gaussian_integer()
    expected = gaussian_to_cnrs(3+2j)
    check("F7.1  exact", ex['exact'])
    check("F7.2  digits", ex['f'].mantissa[:len(expected)] == expected,
          f"got {ex['f'].mantissa}, expected {expected}")

    # F8: 1/z0 exact
    print("\nF8  Worked example: 1/z0")
    ex2 = _ex2_z0_fraction()
    check("F8.1  exact",     ex2['exact'], f"err={ex2['error']:.2e}")
    check("F8.2  exp=-1",    ex2['f'].exponent == -1)
    check("F8.3  M=1",       abs(ex2['f'].mantissa_value()-1) < 1e-9)

    # F9: AI2 v3 verification
    print("\nF9  AI2 v3 example: (3+2i)/2, L=2")
    ex4 = _ex4_ai2()
    f4  = ex4['f']
    check("F9.1  exp=0",  f4.exponent == 0, f"exp={f4.exponent}")
    check("F9.2  M=2+i",  abs(f4.mantissa_value()-complex(2,1)) < 1e-9,
          f"M={f4.mantissa_value()}")
    check("F9.3  err=0.5", abs(ex4['error']-0.5) < 1e-9,
          f"err={ex4['error']:.6f}")

    # F10: Error bound err <= 2 * |z0|^{-(L-1)}
    print("\nF10  Error bound  err <= 2 * |z0|^{-(L-1)}")
    for c, label in coprime5:
        for L in [4, 6, 8]:
            f     = encode(c, L)
            err   = encoding_error(c, f)
            bound = 2.0 * ABS_Z0 ** (-(L-1))
            check(f"F10   {label} L={L}", err <= bound + 1e-9,
                  f"err={err:.5f}, bound={bound:.5f}")

    # F11: Input validation
    print("\nF11  Input validation")
    try:
        encode_z0_fraction(0.5+0j, k=1, L=4)
        check("F11.1  non-integer raises", False)
    except ValueError:
        check("F11.1  non-integer raises", True)
    try:
        encode_z0_fraction(1+0j, k=-1, L=4)
        check("F11.2  negative k raises", False)
    except ValueError:
        check("F11.2  negative k raises", True)

    print()
    print("=" * 60)
    print(f"Failures: {failures}")
    print("All tests PASS." if failures == 0 else f"{failures} test(s) FAILED.")
    print("=" * 60)
    return failures

# ---------------------------------------------------------------------------
# Pretty-print
# ---------------------------------------------------------------------------

def print_worked_examples() -> None:
    print("\n" + "=" * 60)
    print("CNRS-float: Worked Examples")
    print("=" * 60)

    print("\nExample 1: Gaussian integer  c = 3+2i")
    print("  Known CNRS-A string: 1332  (digits [2,3,3,1] LSB-first)")
    ex = _ex1_gaussian_integer()
    print(f"  encode(3+2i, L=4)  = {ex['f']}")
    print(f"  decode             = {ex['c_hat']}")
    print(f"  error              = {ex['error']:.2e}  (exact: {ex['exact']})")
    print(f"  digits from demo   = {ex['digits_check']}")

    print("\nExample 2: Z[i][1/z0]-fraction  c = 1/z0 = (-2-i)/5")
    ex2 = _ex2_z0_fraction()
    print(f"  encode_z0_fraction(1, k=1, L=4) = {ex2['f']}")
    print(f"  decode  = {ex2['c_hat']}  (true = {1/Z0:.6g})")
    print(f"  error   = {ex2['error']:.2e}  (exact: {ex2['exact']})")

    print("\nExample 3: Coprime-5 fraction  c = (1-i)/2 = 1/(1+i)")
    print("  Denominator 2 coprime to 5 => not exactly representable.")
    print("  Greedy algorithm: stuck-greedy (all-zero output).")
    print("  CNRS-float uses Z[i]-rounding instead.")
    ex3 = _ex3_coprime5()
    print(f"  encode((1-i)/2, L=4)  = {ex3['f']}")
    print(f"  decode  = {ex3['c_hat']}")
    print(f"  true c  = {ex3['c']}")
    print(f"  error   = {ex3['error']:.4f}  (bound ~ 2*|z0|^{{-3}} = {ex3['error_bound']:.4f})")

    print("\nExample 4: AI2 v3 hand computation  c = (3+2i)/2 = 1.5+i,  L=2")
    print("  AI2 predicted: M=2+i, exponent=0, error=0.5")
    ex4 = _ex4_ai2()
    f4  = ex4['f']
    ok  = (abs(f4.mantissa_value()-complex(2,1)) < 1e-9 and
           f4.exponent == 0 and abs(ex4['error']-0.5) < 1e-9)
    print(f"  encode(1.5+j, L=2)  = {f4}")
    print(f"  M={f4.mantissa_value()},  e={f4.exponent},  error={ex4['error']:.4f}")
    print(f"  AI2 prediction verified: {ok}")

    print("\nError scaling  (c = (1-i)/2, coprime-5)")
    print(f"  {'L':>4}  {'error':>12}  {'2*|z0|^-(L-1)':>16}  {'ratio':>8}")
    c_test = 0.5-0.5j
    for L in range(2, 12):
        f     = encode(c_test, L)
        err   = encoding_error(c_test, f)
        bound = 2.0 * ABS_Z0 ** (-(L-1))
        ratio = err / bound if bound > 1e-15 else float('nan')
        print(f"  {L:>4}  {err:>12.6f}  {bound:>16.6f}  {ratio:>8.4f}")


if __name__ == '__main__':
    print_worked_examples()
    print()
    failures = run_tests()
    raise SystemExit(0 if failures == 0 else 1)
