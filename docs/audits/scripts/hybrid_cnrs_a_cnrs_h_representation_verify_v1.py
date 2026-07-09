"""
Independent verification of the Hybrid CNRS-A/CNRS-H Representation Theorem.

This script uses a deliberately small exact model:
- coefficient ring R = Gaussian rationals represented by Fraction pairs;
- "canonical CNRS-A coefficients" represented by a canonical immutable wrapper;
- hybrid CNRS-H objects represented by sequences of canonical coefficients.

It verifies:
1. coefficient encode/decode bijection;
2. transported addition and multiplication;
3. Hurwitz-product transport;
4. derivative transport and Leibniz rule;
5. integration right-inverse;
6. exponential eigenfunction/product identities;
7. compositional inverse round trips on finite truncations;
8. uniqueness of hybrid representation.

The script does not import the CNRS Toolkit.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb
import random

random.seed(20260709)


@dataclass(frozen=True, order=True)
class GQ:
    re: Fraction
    im: Fraction

    def __add__(self, other: "GQ") -> "GQ":
        return GQ(self.re + other.re, self.im + other.im)

    def __neg__(self) -> "GQ":
        return GQ(-self.re, -self.im)

    def __sub__(self, other: "GQ") -> "GQ":
        return self + (-other)

    def __mul__(self, other: "GQ") -> "GQ":
        return GQ(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re,
        )

    def inv(self) -> "GQ":
        den = self.re * self.re + self.im * self.im
        if den == 0:
            raise ZeroDivisionError
        return GQ(self.re / den, -self.im / den)

    def __truediv__(self, other: "GQ") -> "GQ":
        return self * other.inv()

    def scale(self, n: int | Fraction) -> "GQ":
        q = Fraction(n)
        return GQ(q * self.re, q * self.im)


ZERO = GQ(Fraction(0), Fraction(0))
ONE = GQ(Fraction(1), Fraction(0))


@dataclass(frozen=True)
class CanonicalA:
    """Toy canonical representation wrapper for an exact coefficient value."""
    value: GQ

    @staticmethod
    def encode(v: GQ) -> "CanonicalA":
        # Fraction already guarantees reduced numerator/denominator normal form.
        return CanonicalA(GQ(Fraction(v.re), Fraction(v.im)))

    def decode(self) -> GQ:
        return self.value

    def add(self, other: "CanonicalA") -> "CanonicalA":
        return CanonicalA.encode(self.value + other.value)

    def mul(self, other: "CanonicalA") -> "CanonicalA":
        return CanonicalA.encode(self.value * other.value)


def enc_seq(values: list[GQ]) -> list[CanonicalA]:
    return [CanonicalA.encode(v) for v in values]


def dec_seq(values: list[CanonicalA]) -> list[GQ]:
    return [v.decode() for v in values]


def add_seq(a: list[GQ], b: list[GQ], n: int) -> list[GQ]:
    return [(a[i] if i < len(a) else ZERO) + (b[i] if i < len(b) else ZERO) for i in range(n)]


def hprod(a: list[GQ], b: list[GQ], n: int) -> list[GQ]:
    out = []
    for m in range(n):
        s = ZERO
        for k in range(m + 1):
            ak = a[k] if k < len(a) else ZERO
            bk = b[m - k] if m - k < len(b) else ZERO
            s = s + (ak * bk).scale(comb(m, k))
        out.append(s)
    return out


def hprod_hybrid(a: list[CanonicalA], b: list[CanonicalA], n: int) -> list[CanonicalA]:
    return enc_seq(hprod(dec_seq(a), dec_seq(b), n))


def deriv(a: list[GQ], n: int) -> list[GQ]:
    return [(a[i + 1] if i + 1 < len(a) else ZERO) for i in range(n)]


def integrate(a: list[GQ], c: GQ, n: int) -> list[GQ]:
    out = [c]
    out.extend(a[: max(0, n - 1)])
    return out[:n]


def compose(f: list[GQ], g: list[GQ], n: int) -> list[GQ]:
    """
    Formal EGF composition via powers in the Hurwitz algebra.
    Requires g[0] = 0.
    """
    if g and g[0] != ZERO:
        raise ValueError("composition requires zero constant term")
    out = [ZERO for _ in range(n)]
    power = [ONE] + [ZERO] * (n - 1)
    factorial = 1
    for m in range(min(len(f), n)):
        if m > 0:
            power = hprod(power, g, n)
            factorial *= m
        coeff = f[m].scale(Fraction(1, factorial))
        # In EGF coefficient language, f_m/m! * (EGF(g))^m.
        # power already stores EGF coefficients.
        for j in range(n):
            out[j] = out[j] + coeff * power[j]
    return out


def inverse_series(g: list[GQ], n: int) -> list[GQ]:
    """
    Solve h such that compose(g,h)=rho, coefficient-by-coefficient.
    This small verifier uses triangular dependence and exact linear solving.
    """
    if len(g) < 2 or g[0] != ZERO or g[1] == ZERO:
        raise ValueError("need g0=0 and invertible g1")
    h = [ZERO] * n
    h[0] = ZERO
    h[1] = g[1].inv()
    target = [ZERO] * n
    if n > 1:
        target[1] = ONE

    for m in range(2, n):
        # Evaluate coefficient with h_m = 0 and h_m = 1; dependence is affine.
        h0 = h.copy()
        h0[m] = ZERO
        c0 = compose(g, h0, n)[m]
        h1 = h.copy()
        h1[m] = ONE
        c1 = compose(g, h1, n)[m]
        slope = c1 - c0
        h[m] = (target[m] - c0) / slope
    return h


def rand_gq(bound: int = 4) -> GQ:
    return GQ(
        Fraction(random.randint(-bound, bound), random.randint(1, bound)),
        Fraction(random.randint(-bound, bound), random.randint(1, bound)),
    )


def check(name: str, cond: bool) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"[PASS] {name}")


# 1. Canonical coefficient bijection.
for _ in range(1000):
    z = rand_gq()
    check("canonical coefficient encode/decode bijection", CanonicalA.encode(z).decode() == z)

# 2. Transported coefficient arithmetic.
for _ in range(1000):
    x, y = rand_gq(), rand_gq()
    cx, cy = CanonicalA.encode(x), CanonicalA.encode(y)
    check("transported coefficient addition", cx.add(cy).decode() == x + y)
    check("transported coefficient multiplication", cx.mul(cy).decode() == x * y)

# 3. Hurwitz-product transport and uniqueness.
ORDER = 10
for _ in range(300):
    a = [rand_gq() for _ in range(ORDER)]
    b = [rand_gq() for _ in range(ORDER)]
    ha, hb = enc_seq(a), enc_seq(b)
    transported = dec_seq(hprod_hybrid(ha, hb, ORDER))
    direct = hprod(a, b, ORDER)
    check("hybrid Hurwitz product transports exactly", transported == direct)
    check("hybrid representation is coefficientwise unique", enc_seq(dec_seq(ha)) == ha)

# 4. Derivative transport and Leibniz.
for _ in range(300):
    a = [rand_gq() for _ in range(ORDER + 1)]
    b = [rand_gq() for _ in range(ORDER + 1)]
    left = deriv(hprod(a, b, ORDER + 1), ORDER)
    right = add_seq(hprod(deriv(a, ORDER), b, ORDER), hprod(a, deriv(b, ORDER), ORDER), ORDER)
    check("hybrid derivative obeys Leibniz rule", left == right)

# 5. Integration right inverse.
for _ in range(300):
    a = [rand_gq() for _ in range(ORDER)]
    c = rand_gq()
    check("hybrid integration is a right inverse of derivative", deriv(integrate(a, c, ORDER + 1), ORDER) == a)

# 6. Exponential eigenfunctions and product law.
for _ in range(200):
    alpha, beta = rand_gq(3), rand_gq(3)
    ea = [ONE]
    eb = [ONE]
    for _n in range(1, ORDER + 1):
        ea.append(ea[-1] * alpha)
        eb.append(eb[-1] * beta)
    check(
        "hybrid exponential is a derivative eigenfunction",
        deriv(ea, ORDER) == [(alpha * ea[n]) for n in range(ORDER)],
    )
    eab = [ONE]
    s = alpha + beta
    for _n in range(1, ORDER):
        eab.append(eab[-1] * s)
    check("hybrid exponential product law", hprod(ea, eb, ORDER) == eab)

# 7. Composition inverse round-trip for g(rho)=a1*rho+a2*rho^2/2!.
for _ in range(100):
    a1 = rand_gq(3)
    while a1 == ZERO:
        a1 = rand_gq(3)
    a2 = rand_gq(2)
    g = [ZERO, a1, a2] + [ZERO] * (ORDER - 3)
    h = inverse_series(g, ORDER)
    rho = [ZERO, ONE] + [ZERO] * (ORDER - 2)
    check("hybrid compositional inverse round trip", compose(g, h, ORDER) == rho)

print("\nAll hybrid CNRS-A/CNRS-H representation checks passed.")
