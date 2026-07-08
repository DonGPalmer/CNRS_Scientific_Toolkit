"""
cnrs_h.py
---------
CNRS-H: the calculus layer of the CNRS programme.

A CNRS-H object is a finite digit string [d0, d1, ..., dN] whose
place values are the EGF basis:

    f(rho) = sum_{n=0}^{N} d_n * rho^n / n!

This is an exponential generating function (EGF) representation.

The key property that makes CNRS-H the natural calculus layer:

    d/d(rho) f  =  drop d_0  =  [d1, d2, ..., dN]

    int f d(rho) =  prepend C =  [C, d0, d1, ..., dN]

Both operations are EXACT — no approximation, no floating-point error,
no Taylor truncation.  The derivative is a pure digit operation.

This realises the programme claim:
    "CNRS-H digit-shift realises d/ds exactly."

Relationship to HStream (the number layer)
------------------------------------------
HStream stores digits with positional place values rho^n (base-Z0 expansion).
CnrsH stores digits with EGF place values rho^n / n!.
These are different representations serving different purposes:

    HStream  : represents Gaussian integers / rationals (numbers)
    CnrsH    : represents functions of the scale variable (fields)

Arithmetic
----------
  Addition        : pointwise coefficient addition
  Scalar multiply : pointwise scalar multiplication
  Multiplication  : EGF (binomial) convolution
                    c_n = sum_{k=0}^n C(n,k) * a_k * b_{n-k}
  This satisfies the Leibniz rule:  D(f*g) = (Df)*g + f*(Dg)

Reference: cnrs_demo.py (Palmer 2026), functions cnrsh_differentiate,
           cnrsh_integrate, cnrsh_value.

Base:   z0 = -2 + i  (inherited from CNRS-A; rho is the scale variable)
Digits: integer coefficients (may be non-negative integers for pure
        CNRS-H strings, or general integers for linear combinations)
"""

from __future__ import annotations
from dataclasses import dataclass
from math import comb, factorial
from typing import List, Sequence, Union

Number = Union[int, float, complex]


# ---------------------------------------------------------------------------
# CnrsH class
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CnrsH:
    """
    CNRS-H function object.

    Internally stores coefficients LSB-first: [d0, d1, ..., dN].

    The represented function is:
        f(rho) = sum_{n=0}^{N} d_n * rho^n / n!

    Differentiation (d/drho) = drop d_0   (exact, algebraic).
    Integration (int drho)   = prepend C  (exact, algebraic).
    """
    coeffs: tuple  # immutable; entries are int/float/complex

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @staticmethod
    def from_list(ds: Sequence[Number]) -> "CnrsH":
        """
        Build from a coefficient list [d0, d1, ..., dN].
        """
        return CnrsH(tuple(ds))

    @staticmethod
    def from_int(d: int, length: int = 1) -> "CnrsH":
        """
        Constant function f(rho) = d.
        """
        return CnrsH((d,) + (0,) * (length - 1))

    @staticmethod
    def zero(length: int = 1) -> "CnrsH":
        """Zero function."""
        return CnrsH((0,) * length)

    @staticmethod
    def one() -> "CnrsH":
        """Constant function f(rho) = 1."""
        return CnrsH((1,))

    @staticmethod
    def identity() -> "CnrsH":
        """
        Identity function f(rho) = rho.
        Coefficients: d0=0, d1=1  ->  0 + 1*rho/1! = rho.
        """
        return CnrsH((0, 1))

    @staticmethod
    def exponential(d: Number = 1, terms: int = 10) -> "CnrsH":
        """
        Truncated EGF of d * exp(rho):
            f(rho) = d * sum_{n=0}^{terms-1} rho^n / n!
        Coefficients: [d, d, d, ..., d]  (all equal to d).
        """
        return CnrsH(tuple(d for _ in range(terms)))

    @staticmethod
    def eigen_exponential(alpha: Number = 1, terms: int = 10) -> "CnrsH":
        """Truncated EGF for ``exp(alpha * rho)``.

        The EGF coefficients are ``alpha**n``. Consequently, within the
        represented truncation, differentiation shifts the coefficients and
        satisfies ``D(h_alpha) = alpha * h_alpha`` away from the final
        truncation boundary.

        This differs from :meth:`exponential`, whose argument is an overall
        amplitude and which represents ``d * exp(rho)``.
        """
        if terms < 1:
            raise ValueError("terms must be at least 1")
        return CnrsH(tuple(alpha ** n for n in range(terms)))

    # ------------------------------------------------------------------
    # Core properties
    # ------------------------------------------------------------------

    @property
    def degree(self) -> int:
        """Highest non-zero coefficient index."""
        for n in range(len(self.coeffs) - 1, -1, -1):
            if self.coeffs[n] != 0:
                return n
        return 0

    @property
    def length(self) -> int:
        return len(self.coeffs)

    def coeff(self, n: int) -> Number:
        """Return coefficient d_n (0 if out of range)."""
        return self.coeffs[n] if n < len(self.coeffs) else 0

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, rho: complex) -> complex:
        """
        Evaluate f(rho) = sum_{n=0}^{N} d_n * rho^n / n!

        Uses Horner-like accumulation for numerical stability.
        """
        result = complex(0)
        rho_power = complex(1)
        fact = 1
        for n, d in enumerate(self.coeffs):
            if n > 0:
                rho_power *= rho
                fact *= n
            result += d * rho_power / fact
        return result

    def __call__(self, rho: complex) -> complex:
        """Shorthand: f(rho)."""
        return self.evaluate(rho)

    # ------------------------------------------------------------------
    # Calculus: the core CNRS-H operations
    # ------------------------------------------------------------------

    def differentiate(self) -> "CnrsH":
        """
        Exact differentiation: d/d(rho) f.

        Drop the leading coefficient d_0:
            [d0, d1, d2, ..., dN]  ->  [d1, d2, ..., dN]

        This realises:
            d/drho [ sum_n d_n rho^n/n! ]
            = sum_n d_n * rho^{n-1}/(n-1)!
            = sum_m d_{m+1} * rho^m/m!

        The dropped d_0 is the constant term (lost, as in ordinary calculus).

        Returns
        -------
        CnrsH
            The derivative, one coefficient shorter.
        """
        if len(self.coeffs) <= 1:
            return CnrsH((0,))
        return CnrsH(self.coeffs[1:])

    # Alias: D = differentiate, matching programme notation
    D = differentiate

    def integrate(self, constant: Number = 0) -> "CnrsH":
        """
        Exact integration: int f d(rho).

        Prepend the constant of integration C:
            [d0, d1, ..., dN]  ->  [C, d0, d1, ..., dN]

        This realises:
            int [ sum_n d_n rho^n/n! ] drho
            = C + sum_n d_n rho^{n+1}/(n+1)!
            = C + sum_m d_{m-1} rho^m/m!

        Parameters
        ----------
        constant : int/float/complex
            The constant of integration (default 0).

        Returns
        -------
        CnrsH
            The antiderivative, one coefficient longer.
        """
        return CnrsH((constant,) + self.coeffs)

    def nth_derivative(self, n: int) -> "CnrsH":
        """
        Apply differentiation n times.

            D^n f  =  drop first n coefficients.

        D^n [d0, d1, ..., dN] = [dn, d_{n+1}, ..., dN]
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return self
        if n >= len(self.coeffs):
            return CnrsH((0,))
        return CnrsH(self.coeffs[n:])

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------

    def __add__(self, other: "CnrsH") -> "CnrsH":
        """
        Pointwise coefficient addition.

            (f + g)_n = f_n + g_n
        """
        n = max(len(self.coeffs), len(other.coeffs))
        result = tuple(
            self.coeff(i) + other.coeff(i) for i in range(n)
        )
        return CnrsH(result)

    def __sub__(self, other: "CnrsH") -> "CnrsH":
        """
        Pointwise coefficient subtraction.
        """
        n = max(len(self.coeffs), len(other.coeffs))
        result = tuple(
            self.coeff(i) - other.coeff(i) for i in range(n)
        )
        return CnrsH(result)

    def __neg__(self) -> "CnrsH":
        return CnrsH(tuple(-c for c in self.coeffs))

    def __mul__(self, other: object) -> "CnrsH":
        """
        EGF (binomial) convolution if other is CnrsH;
        scalar multiplication if other is a number.

        EGF convolution:
            c_n = sum_{k=0}^{n} C(n,k) * a_k * b_{n-k}

        This is the correct multiplication for EGF series:
            if f(rho) = sum a_n rho^n/n!  and  g(rho) = sum b_n rho^n/n!
            then (f*g)(rho) has coefficients c_n as above.

        The Leibniz rule holds:  D(f*g) = (Df)*g + f*(Dg).
        """
        if isinstance(other, CnrsH):
            return self._egf_convolve(other)
        # Scalar
        try:
            s = complex(other)
        except TypeError:
            return NotImplemented
        return CnrsH(tuple(s * c for c in self.coeffs))

    def __rmul__(self, scalar: Number) -> "CnrsH":
        return self.__mul__(scalar)

    def _egf_convolve(self, other: "CnrsH") -> "CnrsH":
        """
        EGF binomial convolution of two CnrsH objects.
        """
        na = len(self.coeffs)
        nb = len(other.coeffs)
        nc = na + nb - 1
        c = [complex(0)] * nc
        for i in range(na):
            for j in range(nb):
                c[i + j] += comb(i + j, i) * self.coeffs[i] * other.coeffs[j]
        # If all coefficients are real integers, keep them as such
        result = []
        for x in c:
            if x.imag == 0 and x.real == round(x.real):
                result.append(int(round(x.real)))
            elif x.imag == 0:
                result.append(x.real)
            else:
                result.append(x)
        return CnrsH(tuple(result))

    # ------------------------------------------------------------------
    # Truncation and padding
    # ------------------------------------------------------------------

    def truncate(self, n: int) -> "CnrsH":
        """Keep only the first n coefficients."""
        return CnrsH(self.coeffs[:n])

    def pad(self, n: int) -> "CnrsH":
        """Extend to length n by appending zeros."""
        if len(self.coeffs) >= n:
            return self
        return CnrsH(self.coeffs + (0,) * (n - len(self.coeffs)))

    # ------------------------------------------------------------------
    # Composition helpers
    # ------------------------------------------------------------------

    def scale_input(self, alpha: Number) -> "CnrsH":
        """
        Return the CnrsH representing f(alpha * rho).

        If f(rho) = sum_n d_n rho^n/n!, then
        f(alpha*rho) = sum_n d_n (alpha*rho)^n/n!
                     = sum_n (alpha^n * d_n) rho^n/n!

        So the new coefficients are alpha^n * d_n.
        """
        result = []
        alpha_pow = complex(1)
        for n, d in enumerate(self.coeffs):
            result.append(alpha_pow * d)
            alpha_pow *= alpha
        return CnrsH(tuple(result))

    # ------------------------------------------------------------------
    # Display and comparison
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CnrsH):
            return NotImplemented
        n = max(len(self.coeffs), len(other.coeffs))
        return all(self.coeff(i) == other.coeff(i) for i in range(n))

    def __str__(self) -> str:
        cs = list(self.coeffs)
        # trim trailing zeros for display
        while len(cs) > 1 and cs[-1] == 0:
            cs.pop()
        return f"CnrsH({cs})"

    def __repr__(self) -> str:
        return str(self)

    def pretty(self, var: str = "s") -> str:
        """
        Human-readable polynomial form.
        f(s) = d0 + d1*s + d2*s^2/2 + ...
        """
        terms = []
        for n, d in enumerate(self.coeffs):
            if d == 0:
                continue
            if n == 0:
                terms.append(str(d))
            elif n == 1:
                terms.append(f"{d}*{var}")
            else:
                terms.append(f"{d}*{var}^{n}/{factorial(n)}")
        return " + ".join(terms) if terms else "0"
