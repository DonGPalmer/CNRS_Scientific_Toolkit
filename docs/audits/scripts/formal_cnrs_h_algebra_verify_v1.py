"""Independent finite-order verification for the formal CNRS-H algebra paper."""
from __future__ import annotations

import math
import random
from fractions import Fraction

random.seed(20260708)


def add(a, b, n):
    return [a[i] + b[i] for i in range(n)]


def mul(a, b, n):
    out = []
    for m in range(n):
        out.append(sum(math.comb(m, k) * a[k] * b[m-k] for k in range(m+1)))
    return out


def D(a, n):
    return [a[i+1] if i+1 < len(a) else 0 for i in range(n)]


def J(a, c, n):
    return ([c] + list(a))[:n]


def bell_table(g, nmax):
    # exponential partial Bell polynomials B[n][k]
    B = [[Fraction(0) for _ in range(nmax+1)] for __ in range(nmax+1)]
    B[0][0] = Fraction(1)
    for n in range(1, nmax+1):
        for k in range(1, n+1):
            B[n][k] = sum(
                Fraction(math.comb(n-1, j-1)) * g[j] * B[n-j][k-1]
                for j in range(1, n-k+2)
            )
    return B


def compose(f, g, n):
    assert g[0] == 0
    B = bell_table(g, n-1)
    return [sum(f[k] * B[m][k] for k in range(m+1)) for m in range(n)]


def check(name, cond):
    if not cond:
        raise AssertionError(name)
    print(f"[PASS] {name}")


N = 12
for trial in range(500):
    a = [Fraction(random.randint(-5, 5)) for _ in range(N+2)]
    b = [Fraction(random.randint(-5, 5)) for _ in range(N+2)]
    c = [Fraction(random.randint(-5, 5)) for _ in range(N+2)]

    check("associativity", mul(mul(a,b,N+1), c, N) == mul(a, mul(b,c,N+1), N))
    check("commutativity", mul(a,b,N) == mul(b,a,N))
    check("Leibniz", D(mul(a,b,N+1),N) == add(mul(D(a,N),b,N), mul(a,D(b,N),N), N))
    check("integration right inverse", D(J(a, Fraction(7), N+1), N) == a[:N])

    g = [Fraction(0)] + [Fraction(random.randint(-3, 3)) for _ in range(N+1)]
    h = [Fraction(0)] + [Fraction(random.randint(-3, 3)) for _ in range(N+1)]
    # chain rule to order N-1; need one extra output coefficient on lhs
    lhs = D(compose(a, g, N+1), N)
    rhs = mul(compose(D(a,N+1), g, N), D(g,N), N)
    check("chain rule", lhs == rhs)

# Exponential eigenvectors and product law
for alpha in range(-4,5):
    for beta in range(-4,5):
        ea = [Fraction(alpha**n) for n in range(N+1)]
        eb = [Fraction(beta**n) for n in range(N+1)]
        check("exponential eigenvector", D(ea,N) == [Fraction(alpha)*ea[n] for n in range(N)])
        check("exponential product", mul(ea,eb,N) == [Fraction((alpha+beta)**n) for n in range(N)])

# Formal inverse example g=x+x^2 in EGF coefficients: g=[0,1,2,0,...]
g = [Fraction(0), Fraction(1), Fraction(2)] + [Fraction(0)]*(N-2)
# recursively solve c from g(c)=x by degree search using linearity in c_n
c = [Fraction(0)]*(N+1)
c[1] = Fraction(1)
for n in range(2, N+1):
    base = compose(g, c, n+1)[n]
    probe = c.copy(); probe[n] = 1
    coeff = compose(g, probe, n+1)[n] - base
    target = Fraction(0)
    c[n] = (target - base) / coeff
ident = [Fraction(0), Fraction(1)] + [Fraction(0)]*(N-1)
check("composition inverse round trip", compose(g,c,N+1) == ident[:N+1])

print("All formal CNRS-H algebra checks passed.")
