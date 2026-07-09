"""Independent exact checks for canonical periodic normalization in base -2+i."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
import random

BETA = (-2, 1)
DIGITS = range(5)


def add(x, y): return (x[0] + y[0], x[1] + y[1])
def sub(x, y): return (x[0] - y[0], x[1] - y[1])
def mul(x, y): return (x[0]*y[0] - x[1]*y[1], x[0]*y[1] + x[1]*y[0])
def scale(n, x): return (n*x[0], n*x[1])
def norm(x): return x[0]*x[0] + x[1]*x[1]

def div_beta_exact(x):
    # (a+bi)/(-2+i) = ((-2a+b)+(-a-2b)i)/5
    a, b = x
    nr, ni = -2*a + b, -a - 2*b
    assert nr % 5 == 0 and ni % 5 == 0
    return (nr//5, ni//5)

def residue(x):
    return (x[0] + 2*x[1]) % 5

def gaussian_div_exact(p, q):
    den = norm(q)
    nr = p[0]*q[0] + p[1]*q[1]
    ni = p[1]*q[0] - p[0]*q[1]
    assert nr % den == 0 and ni % den == 0
    return (nr//den, ni//den)

def digit_for_state(n, q):
    rq = residue(q)
    inv = pow(rq, -1, 5)
    return (residue(n) * inv) % 5

@dataclass(frozen=True)
class Canon:
    offset: int
    prefix: tuple[int, ...]
    period: tuple[int, ...] | None


def v_beta_int(x):
    if x == (0, 0):
        return 10**9
    v = 0
    while residue(x) == 0:
        x = div_beta_exact(x)
        v += 1
    return v


def canonical_from_reduced(p, q, max_steps=200000):
    # p/q assumed Gaussian-reduced enough for tests; remove beta valuation.
    vp, vq = v_beta_int(p), v_beta_int(q)
    offset = min(0, vp - vq)
    # y = beta^-offset * p/q. If offset negative, divide q by beta^-offset.
    if offset < 0:
        for _ in range(-offset):
            q = div_beta_exact(q)
    # cancel common beta from numerator if present after denominator shift
    while p != (0,0) and residue(p) == 0 and residue(q) == 0:
        p, q = div_beta_exact(p), div_beta_exact(q)
    assert residue(q) != 0
    seen = {}
    ds = []
    n = p
    for _ in range(max_steps):
        if n == (0,0):
            return Canon(offset, tuple(ds), None)
        if n in seen:
            mu = seen[n]
            return Canon(offset, tuple(ds[:mu]), tuple(ds[mu:]))
        seen[n] = len(ds)
        d = digit_for_state(n, q)
        ds.append(d)
        n = div_beta_exact(sub(n, scale(d, q)))
    raise RuntimeError("period bound exceeded")


def exact_value(c: Canon):
    # Return pair of Fractions via exact complex rational arithmetic.
    def powg(n):
        if n >= 0:
            z=(1,0)
            for _ in range(n): z=mul(z,BETA)
            return (Fraction(z[0]), Fraction(z[1]))
        # inverse powers
        z=(1,0)
        for _ in range(-n): z=mul(z,(-2,-1))
        den=5**(-n)
        return (Fraction(z[0],den), Fraction(z[1],den))
    def cmul(x,y): return (x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0])
    def cadd(x,y): return (x[0]+y[0],x[1]+y[1])
    total=(Fraction(0),Fraction(0))
    for j,d in enumerate(c.prefix): total=cadd(total,(d*powg(c.offset+j)[0],d*powg(c.offset+j)[1]))
    if c.period is None: return total
    T=len(c.period); block=(Fraction(0),Fraction(0))
    for j,d in enumerate(c.period): block=cadd(block,(d*powg(c.offset+len(c.prefix)+j)[0],d*powg(c.offset+len(c.prefix)+j)[1]))
    bt=powg(T); den=(Fraction(1)-bt[0], -bt[1])
    den_norm=den[0]*den[0]+den[1]*den[1]
    quot=((block[0]*den[0]+block[1]*den[1])/den_norm,(block[1]*den[0]-block[0]*den[1])/den_norm)
    return cadd(total,quot)


def primitive(word):
    n=len(word)
    return all(word != word[:d]*(n//d) for d in range(1,n) if n%d==0)

random.seed(20260709)
checks=0
for _ in range(500):
    # denominators chosen coprime to beta to exercise periodic recurrence.
    p=(random.randint(-50,50),random.randint(-50,50))
    q=(random.randint(-20,20),random.randint(-20,20))
    if q==(0,0) or residue(q)==0: continue
    c=canonical_from_reduced(p,q)
    # exact value must equal p/q
    den=norm(q)
    target=(Fraction(p[0]*q[0]+p[1]*q[1],den), Fraction(p[1]*q[0]-p[0]*q[1],den))
    assert exact_value(c)==target
    if c.period is not None:
        assert primitive(c.period)
        # Duplicating the period does not change value.
        dup=Canon(c.offset,c.prefix,c.period+c.period)
        assert exact_value(dup)==target
        # Moving a full cycle into prefix does not change value.
        moved=Canon(c.offset,c.prefix+c.period,c.period)
        assert exact_value(moved)==target
    checks+=1

print(f"PASS: {checks} random Gaussian-rational canonical forms")
print("PASS: exact value preservation")
print("PASS: primitive periods")
print("PASS: duplicated-period invariance")
print("PASS: full-cycle prefix invariance")
