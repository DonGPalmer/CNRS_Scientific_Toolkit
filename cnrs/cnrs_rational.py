"""
cnrs_rational.py
----------------
CNRS-A representation of Gaussian fractions.

This module extends the CNRS-A number layer from Gaussian integers to the
full field of Gaussian rationals Q[i].  Three cases are handled:

  1. Finitely representable  (Z[i][1/z0])
     Values of the form p / z0^k for p in Z[i], k >= 0.
     Their CNRS string terminates: e.g. 1/z0 = '0.1', 1/z0^2 = '0.01'.

  2. Pure z0-adic periodic  (denominator coprime to 5)
     Values p/q with gcd(q, 5) = 1, e.g. 1/2, 1/3, (1+i)/7.
     Represented as a leftward z0-adic series
         sum_{k>=0}  d_k * z0^k   (eventually periodic).
     Stored with power_offset = 0.

  3. Laurent-periodic z0-adic  (denominator divisible by 5)
     Values p/q where q = 5^s * r, gcd(r, 5) = 1, s >= 1, e.g. 1/5, 1/10.
     Key identity:
         p/q  =  z0^{-s} * p / (z0bar^s * r)
     The Gaussian denominator Q = z0bar^s * r is coprime to z0, so the
     z0-adic algorithm applies to p/Q.  The result is shifted by
     power_offset = -s, giving a Laurent-periodic expansion that starts
     at z0^{-s}.
     Stored with power_offset = -s < 0.

All arithmetic is exact: no floating-point rounding.

Algorithm
---------
Shared z0-adic digit rule for Gaussian denominator Q = C + Di coprime to z0.

  phi(A+Bi)  = (A + 2*B) mod 5       [i ≡ 2 (mod z0)]
  phi(Q)^{-1} mod 5  -- exists since gcd(Q, 5) = 1 in Z[i], i.e. phi(Q) != 0

  At each step, current state is N = A + Bi (numerator in Z[i]):
      d  = phi(N) * phi(Q)^{-1}  mod 5         in {0,1,2,3,4}
      N' = (N - d*Q) / z0                       exact in Z[i]

  State (A, B) stays bounded, eventually repeats -> period detection.

Evaluation of periodic strings
-------------------------------
The z0-adic series  sum d_k * z0^(ell + k)  does NOT converge in C because
|z0| = sqrt(5) > 1.  The value is assigned by the rational closed form:

    x  =  pre_val  +  period_block / (1 - z0^T)

where  pre_val = sum_{j=0}^{p-1} d_j * z0^(ell+j),
       period_block = sum_{j=0}^{T-1} e_j * z0^(ell+p+j),
       T = period length, ell = power_offset.

This identity follows from S = period_block * z0^{0} + z0^T * S.

Public API
----------
  gaussian_rational_to_cnrs(numerator, denominator=1, max_frac=200)
      -> CnrsRational

  CnrsRational
      .power_offset          : int   (0 for cases 1-2; negative for case 3)
      .integer_str           : str   (integer part, MSB first)
      .frac_digits           : list[int]  (z0-adic digits from z0^power_offset)
      .period_start          : int or None
      .is_finite             : bool
      .is_z0_adic            : bool  (True for cases 2-3)
      .z0_adic_value()       : complex  (floating-point; may lose precision for long periods)
      .z0_adic_value_fractions() : (Fraction, Fraction)  (fully exact; no floating-point)
      .z0_adic_value_exact() : complex  (calls fractions(), converts to complex)
      .evaluate(n_frac)      : complex  (partial-sum evaluation; exact for case 1)
      .round_trip_ok(tol)    : bool

Mathematical references
-----------------------
  Frougny & Solomyak (1996). On representation of integers in linear numeration
      systems.  Ergodic Theory Dynam. Systems 16(2), 257-271.
  Gilbert (1981). Radix representations of quadratic fields.
      J. Math. Anal. Appl. 83(1), 264-274.
  Brzicova, Frougny, Pelantova & Svobodova (2016). arXiv:1610.08309.
      (OL property for complex bases; complement to CNRS Problem 3.)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from math import gcd
from typing import List, Optional, Tuple

from .cnrs_repr import Z0, cnrs_remainder, cnrs_to_gaussian, normalize_cnrs


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

Z0_BAR = complex(-2, -1)   # conjugate of z0 = -2+i; z0 * z0bar = 5


# ---------------------------------------------------------------------------
# Internal exact-arithmetic helpers
# ---------------------------------------------------------------------------

def _reduce(A: int, B: int, q: int) -> Tuple[int, int, int]:
    """Reduce (A+Bi)/q by dividing through by gcd(A, B, q)."""
    g = gcd(gcd(abs(A) if A else 0, abs(B) if B else 0), q)
    if g <= 1:
        return A, B, q
    return A // g, B // g, q // g


def _mul_Z0(A: int, B: int) -> Tuple[int, int]:
    """(A+Bi) * z0 = (A+Bi)(-2+i) = (-2A-B) + (A-2B)i."""
    return -2 * A - B, A - 2 * B


def _mul_Z0BAR(A: int, B: int) -> Tuple[int, int]:
    """(A+Bi) * z0bar = (A+Bi)(-2-i) = (-2A+B) + (-A-2B)i."""
    return -2 * A + B, -A - 2 * B


def _div_Z0_exact(A: int, B: int) -> Tuple[int, int]:
    """
    Divide the Gaussian integer A+Bi by z0 = -2+i exactly.

    (A+Bi) / z0  =  (A+Bi) * z0bar / N(z0)  =  (A+Bi)(-2-i) / 5.

    Raises AssertionError if not divisible.
    """
    re = -2 * A + B
    im = -A - 2 * B
    assert re % 5 == 0 and im % 5 == 0, (
        f"({A}+{B}i) not divisible by z0"
    )
    return re // 5, im // 5


def _div_Z0_integer_exact(A: int, B: int, q: int) -> Optional[Tuple[int, int, int, int]]:
    """
    Find digit d in {0..4} such that ((A+Bi)/q - d) / z0 is a Gaussian integer,
    and return (d, nA, nB, 1).  Used in the integer phase only (q divides A,B).

    Returns None if q does not divide A and B (can't extract an integer digit).
    """
    if A % q != 0 or B % q != 0:
        return None
    a, b = A // q, B // q
    d = cnrs_remainder(complex(a, b))
    num_re = -2 * (a - d) + b
    num_im = -2 * b - (a - d)
    if num_re % 5 != 0 or num_im % 5 != 0:
        raise RuntimeError(
            f"Integer-phase division not exact for ({a}+{b}i), digit {d}"
        )
    return d, num_re // 5, num_im // 5, 1


def _phi(A: int, B: int) -> int:
    """Residue map: phi(A+Bi) = (A + 2*B) mod 5.  (Since i ≡ 2 (mod z0).)"""
    return (A + 2 * B) % 5


def _gaussian_pow(re: int, im: int, n: int) -> Tuple[int, int]:
    """(re+im*i)^n in Z[i], exact integer arithmetic."""
    ar, ai = 1, 0
    br, bi = re, im
    while n:
        if n & 1:
            ar, ai = ar * br - ai * bi, ar * bi + ai * br
        br, bi = br * br - bi * bi, 2 * br * bi
        n >>= 1
    return ar, ai



# ---------------------------------------------------------------------------
# Gaussian-denominator z0-adic algorithm  (shared by cases 2 and 3)
# ---------------------------------------------------------------------------

def _z0_adic_gaussian_denom(
    N_re: int, N_im: int,
    Q_re: int, Q_im: int,
    max_frac: int = 200,
) -> Tuple[List[int], Optional[int]]:
    """
    Expand N/Q (N, Q Gaussian integers, Q coprime to z0) as a z0-adic series.

    Returns (digits, period_start) where digits[period_start:] repeats.
    If the expansion terminates, period_start is None.

    Digit rule: d = phi(N) * phi(Q)^{-1} mod 5,  then N <- (N - d*Q) / z0.

    The state (N_re, N_im) stays bounded (|N| contracts by sqrt(5) per step)
    and eventually repeats, guaranteeing termination.

    Raises ValueError if Q is divisible by z0 (phi(Q) == 0 mod 5).
    """
    phi_Q = _phi(Q_re, Q_im)
    if phi_Q == 0:
        raise ValueError(
            f"Denominator Q = {Q_re}+{Q_im}i is divisible by z0; "
            "use the integer-phase extraction first."
        )
    inv_phi_Q = pow(phi_Q, -1, 5)   # exists since phi_Q in {1,2,3,4}

    digits: List[int] = []
    seen: dict = {}
    A, B = N_re, N_im
    period_start: Optional[int] = None

    for step in range(max_frac):
        if A == 0 and B == 0:
            break
        state = (A, B)
        if state in seen:
            period_start = seen[state]
            break
        seen[state] = step

        d = (_phi(A, B) * inv_phi_Q) % 5
        digits.append(d)

        # N  <-  (N - d*Q) / z0   (exact in Z[i])
        nA = A - d * Q_re
        nB = B - d * Q_im
        A, B = _div_Z0_exact(nA, nB)
    else:
        # Loop completed without detecting a period or reaching zero.
        # period_start=None here would be misread as "finite/terminating".
        raise RuntimeError(
            f"No period detected within max_frac={max_frac} steps. "
            f"The period length exceeds max_frac. "
            f"Increase max_frac (e.g. max_frac=1000 or more) and retry. "
            f"Hint: for q={Q_re}+{Q_im}i the period may be long."
        )

    return digits, period_start


# ---------------------------------------------------------------------------
# CnrsRational: the result object
# ---------------------------------------------------------------------------

@dataclass
class CnrsRational:
    """
    CNRS-A representation of a Gaussian rational value.

    The expansion is a z0-adic digit string starting at z0^power_offset:

        value = sum_{k=0}^{p-1} d_k * z0^(power_offset + k)
              + [period sum] / (1 - z0^T)

    For finitely representable values (case 1): is_z0_adic=False, integer_str
    holds the integer part and frac_digits holds trailing fractional digits;
    power_offset is computed from the fractional digit count but stored as 0
    (the evaluate() path via cnrs_to_gaussian handles this).

    For cases 2 and 3: is_z0_adic=True; frac_digits[k] is the coefficient
    of z0^(power_offset + k); use z0_adic_value() for exact evaluation.

    Fields
    ------
    numerator_re, numerator_im, denominator : original p/q
    integer_digits : list[int], LSB first (integer part; cases 1-2)
    frac_digits    : list[int], MSB first (fractional / z0-adic digits)
    period_start   : int or None
    power_offset   : int  (0 for cases 1-2; negative for case 3)
    is_z0_adic     : bool (True for cases 2-3)
    """
    numerator_re: int
    numerator_im: int
    denominator: int
    integer_digits: List[int]   # LSB first
    frac_digits: List[int]      # MSB first; z0-adic coefficients for cases 2-3
    period_start: Optional[int]
    power_offset: int = 0       # ell in z0^(ell+k); 0 for cases 1-2, <0 for case 3
    is_z0_adic: bool = False

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def is_finite(self) -> bool:
        """True if the CNRS expansion terminates (value in Z[i][1/z0])."""
        return self.period_start is None and not self.is_z0_adic

    @property
    def integer_str(self) -> str:
        if not self.integer_digits:
            return "0"
        return "".join(str(d) for d in reversed(self.integer_digits))

    @property
    def period_length(self) -> Optional[int]:
        if self.period_start is None:
            return None
        return len(self.frac_digits) - self.period_start

    # ------------------------------------------------------------------
    # String representations
    # ------------------------------------------------------------------

    def to_str(self, max_frac: int = 40) -> str:
        """
        CNRS string for finite/fractional values (case 1 only).
        For z0-adic values, this is a truncated approximation.
        """
        int_s = self.integer_str
        frac_s = "".join(str(d) for d in self.frac_digits[:max_frac])
        if not frac_s:
            return int_s
        return normalize_cnrs(int_s + "." + frac_s)

    def to_str_with_period(self) -> str:
        """Human-readable string showing the repeating block."""
        if self.is_z0_adic:
            ell = self.power_offset
            ps = self.period_start
            digits = self.frac_digits
            pre = digits[:ps] if ps is not None else digits
            per = digits[ps:] if ps is not None else []
            pre_s = "".join(str(d) for d in pre)
            per_s = "".join(str(d) for d in per)
            offset_s = f"[z0^{ell}]" if ell != 0 else ""
            if per_s:
                return f"{offset_s}{pre_s}[{per_s}]"
            return f"{offset_s}{pre_s}"
        # Case 1: standard fractional string
        int_s = self.integer_str
        if self.period_start is None:
            frac_s = "".join(str(d) for d in self.frac_digits)
            return int_s + ("." + frac_s if frac_s else "")
        pre = "".join(str(d) for d in self.frac_digits[:self.period_start])
        per = "".join(str(d) for d in self.frac_digits[self.period_start:])
        return f"{int_s}.{pre}[{per}]"

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def partial_sum(self, n_digits: Optional[int] = None) -> complex:
        """Return the finite formal partial sum of the stored expansion.

        For finite case-1 values this is the ordinary finite CNRS value.  For
        periodic and Laurent-periodic z0-adic values this is *not* an
        approximation converging in the ordinary complex norm, because
        ``abs(z0) > 1``.  It is provided for diagnostics and respects
        ``power_offset`` exactly.
        """
        n = len(self.frac_digits) if n_digits is None else max(0, int(n_digits))
        if not self.is_z0_adic:
            return cnrs_to_gaussian(self.to_str(max_frac=n))
        return sum(
            d * Z0 ** (self.power_offset + k)
            for k, d in enumerate(self.frac_digits[:n])
        )

    def evaluate(self, n_frac: Optional[int] = None) -> complex:
        """Evaluate the represented value as a Python ``complex``.

        - Finite case-1 values are evaluated directly from their CNRS string.
        - Periodic and Laurent-periodic z0-adic values are evaluated from the
          exact rational closed form, including ``power_offset``.
        - Passing ``n_frac`` requests a diagnostic finite partial sum; for
          z0-adic values this does not imply convergence in the ordinary
          complex norm.  Prefer :meth:`partial_sum` when that intent matters.

        This v0.11.0 behavior removes the former Laurent-periodic ambiguity in
        which ``evaluate()`` ignored ``power_offset``.
        """
        if self.is_z0_adic and n_frac is None:
            return self.z0_adic_value_exact()
        return self.partial_sum(n_frac)

    def exact_value(self) -> complex:
        """The exact complex value (A+Bi)/q as a Python complex."""
        return complex(self.numerator_re, self.numerator_im) / self.denominator

    def z0_adic_value(self) -> complex:
        """
        Evaluate the z0-adic expansion via the rational closed form.

        For a z0-adic expansion with power_offset ell, preperiod d_0..d_{p-1}
        and period e_0..e_{T-1}:

            value = sum_{j=0}^{p-1} d_j * z0^(ell+j)
                  + [sum_{j=0}^{T-1} e_j * z0^(ell+p+j)] / (1 - z0^T)

        This is NOT a convergent series in C (|z0|>1); it is the rational
        value assigned by the periodic identity S = block + z0^T * S.

        For long periods (period length > ~200), floating-point intermediate
        values of z0^T may become very large and lose precision.  Use
        z0_adic_value_exact() for guaranteed full-precision evaluation at
        any period length.

        Raises ValueError if is_z0_adic is False.
        """
        if not self.is_z0_adic:
            raise ValueError(
                "z0_adic_value() is only valid for z0-adic expansions "
                "(is_z0_adic=True). Use evaluate() for finite expansions."
            )
        digits = self.frac_digits
        ps = self.period_start
        ell = self.power_offset

        if ps is None:
            # Terminates: sum d_j * z0^(ell+j)
            return sum(d * Z0 ** (ell + k) for k, d in enumerate(digits))

        pre = digits[:ps]
        period = digits[ps:]
        T = len(period)
        pre_val = sum(d * Z0 ** (ell + k) for k, d in enumerate(pre))
        period_block = sum(period[j] * Z0 ** (ell + ps + j) for j in range(T))
        return pre_val + period_block / (1 - Z0 ** T)

    def z0_adic_value_fractions(self):
        """
        Evaluate the z0-adic expansion and return an exact (real, imag) Fraction pair.

        Uses Python arbitrary-precision integers and fractions.Fraction throughout.
        No floating-point arithmetic is involved.  Reliable for any period length.

        Returns
        -------
        (real_part, imag_part) : tuple of fractions.Fraction
            The exact rational value of this expansion.  To convert to a Python
            complex: complex(float(re), float(im)).

        Raises ValueError if is_z0_adic is False.

        Example
        -------
        >>> from fractions import Fraction
        >>> r = gaussian_rational_to_cnrs(1, 23, max_frac=1000)
        >>> re, im = r.z0_adic_value_fractions()
        >>> re == Fraction(1, 23), im == Fraction(0)
        (True, True)
        """
        if not self.is_z0_adic:
            raise ValueError(
                "z0_adic_value_fractions() is only valid for z0-adic expansions "
                "(is_z0_adic=True). Use evaluate() for finite expansions."
            )
        from fractions import Fraction

        digits = self.frac_digits
        ps = self.period_start
        ell = self.power_offset
        Z0r, Z0i = -2, 1

        # Starting power z0^ell as exact Fraction pair.
        if ell >= 0:
            base_re_raw, base_im_raw = _gaussian_pow(Z0r, Z0i, ell)
            cur_re = Fraction(base_re_raw)
            cur_im = Fraction(base_im_raw)
        else:
            z0bar_re, z0bar_im = _gaussian_pow(-2, -1, -ell)
            den = 5 ** (-ell)
            cur_re = Fraction(z0bar_re, den)
            cur_im = Fraction(z0bar_im, den)

        def step() -> None:
            nonlocal cur_re, cur_im
            new_re = Z0r * cur_re - Z0i * cur_im
            new_im = Z0r * cur_im + Z0i * cur_re
            cur_re, cur_im = new_re, new_im

        if ps is None:
            acc_re = Fraction(0)
            acc_im = Fraction(0)
            for d in digits:
                if d != 0:
                    acc_re += d * cur_re
                    acc_im += d * cur_im
                step()
            return acc_re, acc_im

        pre = digits[:ps]
        period = digits[ps:]
        T = len(period)

        pre_re = Fraction(0)
        pre_im = Fraction(0)
        for d in pre:
            if d != 0:
                pre_re += d * cur_re
                pre_im += d * cur_im
            step()

        pb_re = Fraction(0)
        pb_im = Fraction(0)
        for d in period:
            if d != 0:
                pb_re += d * cur_re
                pb_im += d * cur_im
            step()

        zT_re, zT_im = _gaussian_pow(Z0r, Z0i, T)
        denom_re = Fraction(1 - zT_re)
        denom_im = Fraction(-zT_im)
        N = denom_re * denom_re + denom_im * denom_im

        val_re = (pb_re * denom_re + pb_im * denom_im) / N
        val_im = (pb_im * denom_re - pb_re * denom_im) / N

        return pre_re + val_re, pre_im + val_im

    def z0_adic_value_exact(self) -> complex:
        """
        Evaluate the z0-adic expansion with exact internal arithmetic.

        Calls z0_adic_value_fractions() (which uses fractions.Fraction throughout)
        and converts the result to a Python complex.  The internal computation is
        exact; the returned complex has standard float precision.

        For fully exact results without any floating-point conversion, use
        z0_adic_value_fractions() directly, which returns (Fraction, Fraction).

        Reliable for any period length.  See z0_adic_value() for the fast but
        potentially imprecise floating-point alternative.

        Raises ValueError if is_z0_adic is False.
        """
        if not self.is_z0_adic:
            raise ValueError(
                "z0_adic_value_exact() is only valid for z0-adic expansions "
                "(is_z0_adic=True). Use evaluate() for finite expansions."
            )
        re, im = self.z0_adic_value_fractions()
        return complex(float(re), float(im))

    def round_trip_ok(self, tol: float = 1e-10) -> bool:
        """Check that z0_adic_value_exact() or evaluate() matches the exact value."""
        if self.is_z0_adic:
            return abs(self.z0_adic_value_exact() - self.exact_value()) < tol
        return abs(self.evaluate() - self.exact_value()) < tol

    # ------------------------------------------------------------------
    # Exact arithmetic operators
    # ------------------------------------------------------------------

    def _exact_fractions(self):
        """
        Return the exact value as a (real, imag) pair of fractions.Fraction.

        For finite cases (case 1): uses stored numerator/denominator directly.
        For z0-adic cases (cases 2-3): uses z0_adic_value_fractions().
        """
        from fractions import Fraction
        if self.is_z0_adic:
            return self.z0_adic_value_fractions()
        return (Fraction(self.numerator_re, self.denominator),
                Fraction(self.numerator_im, self.denominator))

    @staticmethod
    def _from_fractions(re, im, max_frac=500):
        """
        Construct a CnrsRational from a (Fraction, Fraction) exact value.

        Finds the common denominator, converts to Gaussian integer numerator,
        and calls gaussian_rational_to_cnrs.
        """
        from math import lcm
        d = lcm(re.denominator, im.denominator)
        return gaussian_rational_to_cnrs(
            complex(int(re * d), int(im * d)), d, max_frac=max_frac
        )

    def __add__(self, other):
        """Exact addition: returns a new CnrsRational."""
        if not isinstance(other, CnrsRational):
            return NotImplemented
        re1, im1 = self._exact_fractions()
        re2, im2 = other._exact_fractions()
        return CnrsRational._from_fractions(re1 + re2, im1 + im2)

    def __sub__(self, other):
        """Exact subtraction: returns a new CnrsRational."""
        if not isinstance(other, CnrsRational):
            return NotImplemented
        re1, im1 = self._exact_fractions()
        re2, im2 = other._exact_fractions()
        return CnrsRational._from_fractions(re1 - re2, im1 - im2)

    def __mul__(self, other):
        """Exact multiplication: returns a new CnrsRational."""
        if not isinstance(other, CnrsRational):
            return NotImplemented
        re1, im1 = self._exact_fractions()
        re2, im2 = other._exact_fractions()
        return CnrsRational._from_fractions(
            re1 * re2 - im1 * im2,
            re1 * im2 + im1 * re2,
        )

    def __neg__(self):
        """Exact negation: returns a new CnrsRational."""
        re, im = self._exact_fractions()
        return CnrsRational._from_fractions(-re, -im)

    def __eq__(self, other):
        """Exact equality via Fraction comparison."""
        if not isinstance(other, CnrsRational):
            return NotImplemented
        re1, im1 = self._exact_fractions()
        re2, im2 = other._exact_fractions()
        return re1 == re2 and im1 == im2

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        exact = f"({self.numerator_re}+{self.numerator_im}i)/{self.denominator}"
        if self.is_z0_adic:
            case = "Laurent-periodic" if self.power_offset < 0 else "z0-adic"
            T = self.period_length
            return (
                f"CnrsRational({exact}, {case}, "
                f"offset={self.power_offset}, "
                f"period={T} @ pos {self.period_start})"
            )
        if self.is_finite:
            return f"CnrsRational({exact} -> {self.to_str()!r} [finite])"
        return (
            f"CnrsRational({exact} -> "
            f"[period {self.period_length} @ pos {self.period_start}])"
        )

    def __repr__(self) -> str:
        return str(self)


# ---------------------------------------------------------------------------
# Main expansion function
# ---------------------------------------------------------------------------

def gaussian_rational_to_cnrs(
    numerator: complex,
    denominator: int = 1,
    max_frac: int = 200,
) -> CnrsRational:
    """
    Expand a Gaussian rational p/q into its CNRS-A representation.

    Handles all three cases:
      1. Finite (Z[i][1/z0]): terminates.
      2. Pure z0-adic (gcd(q,5)=1): periodic, power_offset=0.
      3. Laurent-periodic (q divisible by 5, not a pure z0-power): periodic,
         power_offset = -v5(q) < 0, using Gaussian denominator Q = z0bar^s * r.

    Parameters
    ----------
    numerator : complex
        The Gaussian integer numerator. Real and imaginary parts are rounded.
    denominator : int
        Positive integer denominator q.
    max_frac : int
        Maximum z0-adic digits before declaring non-termination.

    Returns
    -------
    CnrsRational

    Raises
    ------
    NotImplementedError
        Should not occur; all cases are now handled.
    ValueError
        If denominator <= 0.

    Examples
    --------
    >>> gaussian_rational_to_cnrs(3+2j)           # finite, case 1
    >>> gaussian_rational_to_cnrs(1, 2)            # z0-adic, case 2
    >>> gaussian_rational_to_cnrs(1, 5)            # Laurent-periodic, case 3
    """
    if denominator <= 0:
        raise ValueError(f"denominator must be positive, got {denominator}")

    # Parse numerator
    if isinstance(numerator, tuple):
        p_re, p_im = int(numerator[0]), int(numerator[1])
    else:
        p_re = int(round(numerator.real))
        p_im = int(round(numerator.imag))

    orig_re, orig_im, orig_q = p_re, p_im, denominator

    # Reduce fraction
    A, B, q = _reduce(p_re, p_im, denominator)

    # ------------------------------------------------------------------
    # Phase 1: integer digits (LSB first)
    # Extract digits while (A+Bi)/q is exactly divisible by z0.
    # ------------------------------------------------------------------
    integer_digits: List[int] = []

    if A == 0 and B == 0:
        integer_digits = [0]

    while A != 0 or B != 0:
        result = _div_Z0_integer_exact(A, B, q)
        if result is None:
            break
        d, nA, nB, _ = result
        integer_digits.append(d)
        A, B, q = nA, nB, 1

    # ------------------------------------------------------------------
    # Phase 2: determine case and run appropriate algorithm
    # ------------------------------------------------------------------
    frac_digits: List[int] = []
    period_start: Optional[int] = None
    power_offset: int = 0
    is_z0_adic: bool = False

    if A == 0 and B == 0:
        # Exact Gaussian integer or Z[i][1/z0] fraction: finite, done.
        pass

    elif gcd(q, 5) == 1:
        # ---- Case 2: denominator coprime to 5 ---------------------------
        # Pure z0-adic: N = A+Bi, Q = q (a positive integer, hence coprime to z0).
        is_z0_adic = True
        power_offset = 0
        frac_digits, period_start = _z0_adic_gaussian_denom(A, B, q, 0, max_frac)

    else:
        # ---- Case 3: q divisible by 5 -----------------------------------
        # Factor q = 5^s * r, gcd(r, 5) = 1.
        s = 0
        r = q
        while r % 5 == 0:
            r //= 5
            s += 1

        # Sub-case 3a: finitely representable in Z[i][1/z0].
        # Occurs when r = 1 (q = 5^s pure power) AND z0bar^s | A+Bi in Z[i].
        # Equivalently: dividing A+Bi by z0bar s times is exact.
        # Division by z0bar: multiply by z0 = (-2+i), divide by 5.
        if r == 1:
            fA, fB = A, B
            finite_ok = True
            for _ in range(s):
                nre = -2 * fA - fB
                nim = fA - 2 * fB
                if nre % 5 != 0 or nim % 5 != 0:
                    finite_ok = False
                    break
                fA, fB = nre // 5, nim // 5
        else:
            finite_ok = False

        if finite_ok:
            # Value is fA+fBi in Z[i] divided by z0^s.
            # Expand as: integer_part + frac_digits where frac has exactly s terms.
            # Algorithm: work from the z0^{-s} place upward (LSB-first), then reverse.
            # At each step: d_k = cnrs_remainder(cur); cur <- (cur - d_k) / z0.
            # After s steps the remainder cA+cBi is a Gaussian integer -> integer phase.
            cA, cB = fA, fB
            frac_digits_fin: List[int] = []
            for _ in range(s):
                d = cnrs_remainder(complex(cA, cB))
                frac_digits_fin.append(d)
                nre = -2 * (cA - d) + cB
                nim = -(cA - d) - 2 * cB
                assert nre % 5 == 0 and nim % 5 == 0, (
                    f"Finite fractional expansion: division not exact at "
                    f"cA={cA}, cB={cB}, d={d}"
                )
                cA, cB = nre // 5, nim // 5
            frac_digits_fin.reverse()  # convert to MSB-first

            # cA+cBi is now a Gaussian integer (the integer part of the value).
            # Extract its integer digits (LSB-first) and prepend to integer_digits.
            int_digits_extra: List[int] = []
            iA, iB = cA, cB
            while iA != 0 or iB != 0:
                res = _div_Z0_integer_exact(iA, iB, 1)
                if res is None:
                    break
                d, iA, iB, _ = res
                int_digits_extra.append(d)
            all_int_digits = integer_digits + int_digits_extra  # LSB-first

            return CnrsRational(
                numerator_re=orig_re,
                numerator_im=orig_im,
                denominator=orig_q,
                integer_digits=all_int_digits,
                frac_digits=frac_digits_fin,
                period_start=None,
                power_offset=0,
                is_z0_adic=False,
            )

        # Sub-case 3b: Laurent-periodic.
        # Key identity: p/q = z0^{-s} * p / (z0bar^s * r), where z0bar^s * r
        # is a Gaussian integer coprime to z0.  Run the z0-adic algorithm on
        # numerator A+Bi with Gaussian denominator Q = z0bar^s * r.
        z0bar_s_re, z0bar_s_im = _gaussian_pow(-2, -1, s)
        Q_re = z0bar_s_re * r
        Q_im = z0bar_s_im * r

        is_z0_adic = True
        power_offset = -s
        frac_digits, period_start = _z0_adic_gaussian_denom(
            A, B, Q_re, Q_im, max_frac
        )

    return CnrsRational(
        numerator_re=orig_re,
        numerator_im=orig_im,
        denominator=orig_q,
        integer_digits=integer_digits,
        frac_digits=frac_digits,
        period_start=period_start,
        power_offset=power_offset,
        is_z0_adic=is_z0_adic,
    )
