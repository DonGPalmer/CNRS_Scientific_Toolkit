"""Exact Gaussian-integer ideal and valuation utilities for CNRS division.

The CNRS base is ``BETA = -2+i``.  Since ``Z[i]`` is Euclidean, denominator
ideals are represented by unit-normalized Gaussian-integer generators.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

Gaussian = tuple[int, int]
BETA: Gaussian = (-2, 1)
BETA_BAR: Gaussian = (-2, -1)
UNITS: tuple[Gaussian, ...] = ((1,0), (-1,0), (0,1), (0,-1))


def gadd(a: Gaussian, b: Gaussian) -> Gaussian: return (a[0]+b[0], a[1]+b[1])
def gsub(a: Gaussian, b: Gaussian) -> Gaussian: return (a[0]-b[0], a[1]-b[1])
def gmul(a: Gaussian, b: Gaussian) -> Gaussian:
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
def gconj(a: Gaussian) -> Gaussian: return (a[0], -a[1])
def gnorm(a: Gaussian) -> int: return a[0]*a[0]+a[1]*a[1]
def giszero(a: Gaussian) -> bool: return a == (0,0)

def gdiv_exact(a: Gaussian, b: Gaussian) -> Gaussian:
    if giszero(b): raise ZeroDivisionError("Gaussian division by zero")
    n = gnorm(b); p = gmul(a, gconj(b))
    if p[0] % n or p[1] % n:
        raise ValueError(f"{a} is not exactly divisible by {b}")
    return (p[0]//n, p[1]//n)

def gaussian_divides(divisor: Gaussian, value: Gaussian) -> bool:
    if giszero(divisor): return giszero(value)
    p = gmul(value, gconj(divisor)); n = gnorm(divisor)
    return p[0] % n == 0 and p[1] % n == 0

def _nearest_int_ratio(num: int, den: int) -> int:
    # deterministic nearest integer; ties away from zero are harmless for gcd
    if num >= 0: return (2*num + den)//(2*den)
    return -((2*(-num) + den)//(2*den))

def gaussian_divmod(a: Gaussian, b: Gaussian) -> tuple[Gaussian, Gaussian]:
    if giszero(b): raise ZeroDivisionError("Gaussian division by zero")
    n = gnorm(b); p = gmul(a, gconj(b))
    q = (_nearest_int_ratio(p[0], n), _nearest_int_ratio(p[1], n))
    return q, gsub(a, gmul(q,b))

def unit_normalize(z: Gaussian) -> Gaussian:
    """Return the lexicographically preferred associate in the closed right half-plane."""
    if giszero(z): return z
    associates = [gmul(u,z) for u in UNITS]
    # positive real preferred, then zero real with nonnegative imaginary
    valid = [w for w in associates if w[0] > 0 or (w[0] == 0 and w[1] >= 0)]
    return min(valid, key=lambda w: (abs(w[1]), w[0], w[1]))

def gaussian_gcd(a: Gaussian, b: Gaussian) -> Gaussian:
    while not giszero(b):
        _, r = gaussian_divmod(a,b); a,b = b,r
    return unit_normalize(a)

def reduce_gaussian_fraction(p: Gaussian, q: Gaussian) -> tuple[Gaussian, Gaussian]:
    if giszero(q): raise ZeroDivisionError("denominator must be nonzero")
    if giszero(p): return (0,0), (1,0)
    d = gaussian_gcd(p,q)
    p1, q1 = gdiv_exact(p,d), gdiv_exact(q,d)
    qn = unit_normalize(q1)
    # find unit u with qn=u*q1 and apply to p1
    for u in UNITS:
        if gmul(u,q1)==qn:
            return gmul(u,p1), qn
    raise AssertionError("associate normalization failed")

def gaussian_valuation(z: Gaussian, prime: Gaussian=BETA) -> int:
    if giszero(z): raise ValueError("valuation of zero is infinite/undefined here")
    v=0
    while gaussian_divides(prime,z):
        z=gdiv_exact(z,prime); v+=1
    return v

def gpow(z: Gaussian, n: int) -> Gaussian:
    if n < 0: raise ValueError("gpow requires n >= 0")
    out=(1,0); base=z
    while n:
        if n&1: out=gmul(out,base)
        base=gmul(base,base); n//=2
    return out

@dataclass(frozen=True)
class TerminationAnalysis:
    numerator: Gaussian
    denominator: Gaussian
    reduced_numerator: Gaussian
    reduced_denominator: Gaussian
    denominator_ideal_generator: Gaussian
    beta_numerator_valuation: int
    beta_denominator_valuation: int
    minimal_laurent_offset: int
    residual_denominator: Gaussian
    terminates: bool
    obstruction_generator: Gaussian | None

    def as_dict(self) -> dict[str, object]:
        return {
            "numerator": self.numerator,
            "denominator": self.denominator,
            "reduced_numerator": self.reduced_numerator,
            "reduced_denominator": self.reduced_denominator,
            "denominator_ideal_generator": self.denominator_ideal_generator,
            "beta_numerator_valuation": self.beta_numerator_valuation,
            "beta_denominator_valuation": self.beta_denominator_valuation,
            "minimal_laurent_offset": self.minimal_laurent_offset,
            "residual_denominator": self.residual_denominator,
            "terminates": self.terminates,
            "obstruction_generator": self.obstruction_generator,
        }

def analyze_termination(p: Gaussian, q: Gaussian=(1,0)) -> TerminationAnalysis:
    rp,rq = reduce_gaussian_fraction(p,q)
    vp = 0 if giszero(rp) else gaussian_valuation(rp,BETA)
    vq = gaussian_valuation(rq,BETA)
    residual = rq
    for _ in range(vq): residual = gdiv_exact(residual,BETA)
    residual = unit_normalize(residual)
    terminates = gnorm(residual)==1
    return TerminationAnalysis(
        numerator=p, denominator=q, reduced_numerator=rp, reduced_denominator=rq,
        denominator_ideal_generator=rq,
        beta_numerator_valuation=vp, beta_denominator_valuation=vq,
        minimal_laurent_offset=max(0,vq-vp), residual_denominator=residual,
        terminates=terminates,
        obstruction_generator=None if terminates else residual,
    )

def denominator_ideal_generator(p: Gaussian, q: Gaussian=(1,0)) -> Gaussian:
    return analyze_termination(p,q).denominator_ideal_generator

def minimal_laurent_offset(p: Gaussian, q: Gaussian=(1,0)) -> int:
    return analyze_termination(p,q).minimal_laurent_offset

__all__ = [
    "Gaussian","BETA","BETA_BAR","UNITS","gadd","gsub","gmul","gconj","gnorm",
    "gdiv_exact","gaussian_divides","gaussian_divmod","gaussian_gcd","unit_normalize",
    "reduce_gaussian_fraction","gaussian_valuation","gpow","TerminationAnalysis",
    "analyze_termination","denominator_ideal_generator","minimal_laurent_offset",
]
