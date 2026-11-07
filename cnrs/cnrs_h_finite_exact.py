"""Repaired candidate exact, finite CNRS-H arithmetic over R_A = Z[i][(-2+i)^-1].

This is a standalone research candidate, not a change to the released Toolkit.
A HurwitzJet coefficient tuple a_n represents sum(a_n*x^n/n!).
All ring operations are integer-only. Ordinary polynomial comparison belongs
in the separate test module; no convergence or infinite-stream claim is made.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb, factorial
import re

Gaussian = tuple[int, int]
BETA: Gaussian = (-2, 1)
_DIGIT_GRAMMAR = re.compile(r"(?:[0-4]+(?:\.[0-4]*)?|\.[0-4]+)\Z", re.ASCII)


def _gaussian_pair(a: Gaussian) -> Gaussian:
    """Strict public helper input: two exact ints, no bool/float/complex coercion."""
    if type(a) is not tuple or len(a) != 2 or any(type(x) is not int for x in a):
        raise TypeError("Gaussian input must be a pair of exact Python ints")
    return a


def gadd(a: Gaussian, b: Gaussian) -> Gaussian:
    a, b = _gaussian_pair(a), _gaussian_pair(b)
    return a[0] + b[0], a[1] + b[1]


def gneg(a: Gaussian) -> Gaussian:
    a = _gaussian_pair(a)
    return -a[0], -a[1]


def gmul(a: Gaussian, b: Gaussian) -> Gaussian:
    a, b = _gaussian_pair(a), _gaussian_pair(b)
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def gpow(a: Gaussian, n: int) -> Gaussian:
    a = _gaussian_pair(a)
    if type(n) is not int or n < 0:
        raise ValueError("Gaussian power must be a nonnegative integer")
    acc = (1, 0)
    while n:
        if n & 1:
            acc = gmul(acc, a)
        a = gmul(a, a)
        n >>= 1
    return acc


def divide_beta_exact(a: Gaussian) -> Gaussian | None:
    """The exact Gaussian quotient by beta, if it exists."""
    a = _gaussian_pair(a)
    x, y = a
    re_n, im_n = -2*x + y, -x - 2*y
    if re_n % 5 or im_n % 5:
        return None
    return re_n // 5, im_n // 5


@dataclass(frozen=True)
class RA:
    """Exact element (a+bi)/beta^k with k>=0, normalized by beta cancellation.

    Coefficients outside this localization cannot be introduced. Float, complex,
    Fraction, and bool constructors are intentionally rejected.
    """
    real: int = 0
    imag: int = 0
    denominator_power: int = 0

    def __post_init__(self) -> None:
        if any(type(v) is not int for v in
               (self.real, self.imag, self.denominator_power)):
            raise TypeError("R_A requires exact integer numerator and exponent")
        if self.denominator_power < 0:
            raise ValueError("denominator power must be nonnegative")
        a = (self.real, self.imag)
        k = self.denominator_power
        if a == (0, 0):
            k = 0
        while k:
            q = divide_beta_exact(a)
            if q is None:
                break
            a = q
            k -= 1
        object.__setattr__(self, "real", a[0])
        object.__setattr__(self, "imag", a[1])
        object.__setattr__(self, "denominator_power", k)

    @staticmethod
    def gaussian(real: int, imag: int = 0) -> "RA":
        return RA(real, imag)

    @staticmethod
    def beta_inverse(power: int = 1) -> "RA":
        return RA(1, 0, power)

    @staticmethod
    def from_cnrs_string(text: str) -> "RA":
        """Strict finite CNRS-A spelling as one exact R_A coefficient."""
        if type(text) is not str:
            raise TypeError("CNRS spelling must be an exact str")
        if _DIGIT_GRAMMAR.fullmatch(text) is None:
            raise ValueError("finite CNRS-A strings use ASCII digits 0..4 and at most one radix point")
        integer, _, fraction = text.partition(".")
        digits = integer + fraction
        acc = RA()
        for j, c in enumerate(reversed(digits)):
            exp = j - len(fraction)
            d = int(c)
            if exp < 0:
                term = RA(d, 0, -exp)
            else:
                p = gmul((d, 0), gpow(BETA, exp))
                term = RA(*p)
            acc = acc + term
        return acc


    def to_cnrs_string(self, *, max_digits: int = 4096) -> str:
        """Canonical finite CNRS-A representation, using only Gaussian ints.

        Run the exact -2+i Euclidean digit recurrence on the integer numerator,
        then place the radix point `denominator_power` digits from the right.
        Raise rather than silently truncate for unrealistic source lengths.
        This returns a finite numeral, *not* an arbitrary Q(i) field fraction.
        """
        if type(max_digits) is not int or max_digits < 1:
            raise ValueError("max_digits must be a positive integer")
        if self == RA():
            return "0"
        current = (self.real, self.imag)
        lsd: list[int] = []
        for _ in range(max_digits):
            if current == (0, 0):
                break
            x, y = current
            digit = (x + 2*y) % 5
            next_state = divide_beta_exact((x-digit, y))
            if next_state is None:
                raise ArithmeticError("the exact Gaussian remainder invariant failed")
            lsd.append(digit)
            current = next_state
        if current != (0, 0):
            raise ValueError("maximum canonical digit length exceeded")
        digits = "".join(map(str, reversed(lsd)))
        k = self.denominator_power
        if max(len(digits), k + 1) > max_digits:
            raise ValueError("maximum canonical output digit length exceeded")
        if k:
            if len(digits) <= k:
                digits = "0"*(k+1-len(digits)) + digits
            digits = digits[:-k] + "." + digits[-k:]
        integer, sep, frac = digits.partition(".")
        integer = integer.lstrip("0") or "0"
        frac = frac.rstrip("0") if sep else ""
        return integer + ("." + frac if frac else "")

    def _as_pair(self) -> Gaussian:
        return self.real, self.imag

    def __neg__(self) -> "RA":
        return RA(-self.real, -self.imag, self.denominator_power)

    def __add__(self, other: object) -> "RA":
        if type(other) is int:
            other = RA(other)
        if not isinstance(other, RA):
            return NotImplemented
        k = max(self.denominator_power, other.denominator_power)
        a = gmul(self._as_pair(), gpow(BETA, k-self.denominator_power))
        b = gmul(other._as_pair(), gpow(BETA, k-other.denominator_power))
        c = gadd(a, b)
        return RA(*c, k)

    def __radd__(self, other: object) -> "RA":
        return self + other

    def __sub__(self, other: object) -> "RA":
        if type(other) is int:
            other = RA(other)
        if not isinstance(other, RA):
            return NotImplemented
        return self + (-other)

    def __rsub__(self, other: object) -> "RA":
        if type(other) is int:
            other = RA(other)
        if not isinstance(other, RA):
            return NotImplemented
        return other - self

    def __mul__(self, other: object) -> "RA":
        if type(other) is int:
            other = RA(other)
        if not isinstance(other, RA):
            return NotImplemented
        p = gmul(self._as_pair(), other._as_pair())
        return RA(*p, self.denominator_power+other.denominator_power)

    def __rmul__(self, other: object) -> "RA":
        return self * other

    def __pow__(self, exponent: int) -> "RA":
        if type(exponent) is not int or exponent < 0:
            raise ValueError("negative powers require the restricted inverse_unit()")
        p = gpow(self._as_pair(), exponent)
        return RA(*p, self.denominator_power*exponent)

    def inverse_unit(self) -> "RA":
        """Invert only units of R_A: gaussian units times powers of beta.

        A generic nonzero field element (e.g., 2 or conjugate(beta)) is NOT
        necessarily invertible in R_A.
        """
        if self.real == 0 and self.imag == 0:
            raise ZeroDivisionError("zero has no inverse")
        p = self._as_pair()
        k = 0
        while True:
            q = divide_beta_exact(p)
            if q is None:
                break
            p = q
            k += 1
        units: dict[Gaussian, Gaussian] = {
            (1, 0):(1,0),(-1,0):(-1,0),(0,1):(0,-1),(0,-1):(0,1)
        }
        if p not in units:
            raise ValueError("nonunit in R_A; inverse exists in Q(i), not in R_A")
        numerator = gmul(units[p], gpow(BETA, self.denominator_power))
        return RA(*numerator, k)

    def as_fraction_pair(self) -> tuple[Fraction, Fraction]:
        """Independent exact Q(i) embedding for comparison and interoperability."""
        u, v = gpow(BETA, self.denominator_power)
        norm = u*u+v*v
        return (Fraction(self.real*u+self.imag*v, norm),
                Fraction(self.imag*u-self.real*v, norm))


Z = RA()
ONE = RA(1)


def coerce(value: RA | int) -> RA:
    if isinstance(value, RA):
        return value
    if type(value) is int:
        return RA(value)
    raise TypeError("Hurwitz coefficients must be exact R_A elements or integers")


@dataclass(frozen=True)
class HurwitzJet:
    """Finite-support divided-power series Σ a_n rho^[n], rho^[n]=rho^n/n!."""
    coefficients: tuple[RA, ...]

    def __post_init__(self) -> None:
        cs = tuple(coerce(x) for x in self.coefficients)
        while len(cs) > 1 and cs[-1] == Z:
            cs = cs[:-1]
        if not cs:
            cs = (Z,)
        object.__setattr__(self, "coefficients", cs)

    @classmethod
    def from_coefficients(cls, *coefficients: RA | int) -> "HurwitzJet":
        return cls(tuple(coerce(c) for c in coefficients))


    @classmethod
    def from_cnrs_coefficients(cls, strings: tuple[str, ...] | list[str]) -> "HurwitzJet":
        """Exact nested finite CNRS-H coefficient decoder; no float/complex."""
        if type(strings) not in (tuple, list):
            raise TypeError("coefficient strings must be a list or tuple")
        return cls(tuple(RA.from_cnrs_string(s) for s in strings))

    def to_cnrs_coefficients(self, *, max_digits: int = 4096) -> tuple[str, ...]:
        """Exact nested finite CNRS-H coefficient encoder."""
        return tuple(a.to_cnrs_string(max_digits=max_digits) for a in self.coefficients)

    def coefficient(self, n: int) -> RA:
        if type(n) is not int or n < 0:
            raise ValueError("coefficient index must be nonnegative")
        return self.coefficients[n] if n < len(self.coefficients) else Z

    @property
    def degree(self) -> int:
        return -1 if self.coefficients == (Z,) else len(self.coefficients)-1

    def __add__(self, other: "HurwitzJet") -> "HurwitzJet":
        if not isinstance(other, HurwitzJet):
            return NotImplemented
        return HurwitzJet(tuple(self.coefficient(n)+other.coefficient(n)
                                for n in range(max(len(self.coefficients),len(other.coefficients)))))

    def __neg__(self) -> "HurwitzJet":
        return HurwitzJet(tuple(-x for x in self.coefficients))

    def __sub__(self, other: "HurwitzJet") -> "HurwitzJet":
        if not isinstance(other, HurwitzJet):
            return NotImplemented
        return self + (-other)

    def product(self, other: "HurwitzJet", through_degree: int | None = None) -> "HurwitzJet":
        """Exact Hurwitz-binomial convolution, optionally modulo rho^[N+1]."""
        if not isinstance(other, HurwitzJet):
            raise TypeError("other must be HurwitzJet")
        if through_degree is not None and (type(through_degree) is not int or through_degree < 0):
            raise ValueError("through_degree must be nonnegative")
        nmax = (len(self.coefficients)+len(other.coefficients)-2
                if through_degree is None else through_degree)
        return HurwitzJet(tuple(sum((RA(comb(n,k))*self.coefficient(k)*other.coefficient(n-k)
                                     for k in range(n+1)), Z) for n in range(nmax+1)))

    def __mul__(self, other: "HurwitzJet") -> "HurwitzJet":
        return self.product(other)

    def derivative(self) -> "HurwitzJet":
        return HurwitzJet(self.coefficients[1:])

    def antiderivative(self, supplied_constant: RA | int = 0) -> "HurwitzJet":
        return HurwitzJet((coerce(supplied_constant),)+self.coefficients)

    def truncate(self, through_degree: int) -> "HurwitzJet":
        if type(through_degree) is not int or through_degree < 0:
            raise ValueError("through_degree must be nonnegative")
        return HurwitzJet(self.coefficients[:through_degree+1])

    def inverse_truncated(self, through_degree: int) -> "HurwitzJet":
        """Formal reciprocal modulo degree N, only if a_0 is an R_A unit."""
        if type(through_degree) is not int or through_degree < 0:
            raise ValueError("through_degree must be nonnegative")
        inv = self.coefficient(0).inverse_unit()
        out = [inv]
        for n in range(1, through_degree+1):
            terms = sum((RA(comb(n,k))*self.coefficient(k)*out[n-k]
                         for k in range(1,n+1)), Z)
            out.append(-inv*terms)
        return HurwitzJet(tuple(out))

    def ordinary_coefficients(self) -> tuple[tuple[Fraction, Fraction], ...]:
        """Embed finite divided-power jet into ordinary Q(i)[rho] polynomial.

        The denominators n! can lie outside R_A. This does NOT alter the
        Hurwitz coefficient ring, and the output is a comparator, not R_A data.
        """
        return tuple((a.as_fraction_pair()[0]/factorial(n),
                      a.as_fraction_pair()[1]/factorial(n))
                     for n,a in enumerate(self.coefficients))


__all__ = ["RA", "HurwitzJet", "BETA", "Z", "ONE", "gadd", "gmul",
           "gpow", "divide_beta_exact"]
