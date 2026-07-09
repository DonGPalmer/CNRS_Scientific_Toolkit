"""
Independent verification checks for:
Metric and Topological Completeness in the CNRS Architecture.

The script checks finite approximations to:
1. the symbolic prefix ultrametric;
2. the isometry between first differing digit and beta-adic valuation;
3. stabilization of nested prefixes;
4. coefficientwise Cauchy convergence for CNRS-H product metrics.

It uses exact Gaussian-integer arithmetic and does not import the CNRS Toolkit.
"""
from __future__ import annotations

from fractions import Fraction
import random

random.seed(20260708)

BETA = (-2, 1)
DIGITS = range(5)


def gadd(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] + y[0], x[1] + y[1]


def gsub(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] - y[0], x[1] - y[1]


def gmul(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def beta_div_exact(z: tuple[int, int]) -> tuple[int, int]:
    """Divide exactly by beta=-2+i. Raises when beta does not divide z."""
    a, b = z
    # (a+bi)/(-2+i) = ((-2a+b) + (-a-2b)i)/5
    nr, ni = -2 * a + b, -a - 2 * b
    if nr % 5 or ni % 5:
        raise ValueError("not divisible by beta")
    return nr // 5, ni // 5


def vbeta(z: tuple[int, int]) -> int:
    if z == (0, 0):
        return 10**9
    n = 0
    while True:
        try:
            z = beta_div_exact(z)
            n += 1
        except ValueError:
            return n


def beta_power(n: int) -> tuple[int, int]:
    out = (1, 0)
    for _ in range(n):
        out = gmul(out, BETA)
    return out


def eval_digits(ds: list[int]) -> tuple[int, int]:
    total = (0, 0)
    p = (1, 0)
    for d in ds:
        total = gadd(total, (d * p[0], d * p[1]))
        p = gmul(p, BETA)
    return total


def first_difference(a: list[int], b: list[int]) -> int | None:
    for j, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return j
    return None


def check(name: str, cond: bool) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"[PASS] {name}")


# U1: ultrametric on finite prefixes, interpreted with common zero tails.
for _ in range(5000):
    n = 24
    a = [random.randrange(5) for _ in range(n)]
    b = [random.randrange(5) for _ in range(n)]
    c = [random.randrange(5) for _ in range(n)]

    def dist(x: list[int], y: list[int]) -> Fraction:
        r = first_difference(x, y)
        return Fraction(0) if r is None else Fraction(1, 5**r)

    check(
        "symbolic prefix distance satisfies ultrametric inequality",
        dist(a, c) <= max(dist(a, b), dist(b, c)),
    )

# U2: first differing digit equals beta-adic valuation of value difference.
for _ in range(3000):
    n = 30
    a = [random.randrange(5) for _ in range(n)]
    b = a.copy()
    r = random.randrange(n)
    choices = [d for d in DIGITS if d != a[r]]
    b[r] = random.choice(choices)
    # Keep later digits arbitrary.
    for j in range(r + 1, n):
        b[j] = random.randrange(5)
    diff = gsub(eval_digits(a), eval_digits(b))
    check("first-difference/isometry valuation identity", vbeta(diff) == r)

# U3: nested prefixes stabilize coordinatewise.
target = [random.randrange(5) for _ in range(100)]
approximants = [target[:m] + [0] * (100 - m) for m in range(1, 101)]
for r in range(1, 80):
    # After index r, all approximants agree with target through r digits.
    check(
        "nested prefixes form a Cauchy sequence with the expected limit",
        all(approximants[m][:r] == target[:r] for m in range(r, 100)),
    )

# H1: product metric tail estimate for coefficientwise convergence.
def h_metric(a: list[Fraction], b: list[Fraction]) -> Fraction:
    total = Fraction(0)
    for n, (x, y) in enumerate(zip(a, b)):
        delta = abs(x - y)
        clipped = min(Fraction(1), delta)
        total += clipped * Fraction(1, 2 ** (n + 1))
    return total

target_h = [Fraction((n * n + 3) % 11, n + 1) for n in range(80)]
h_approx = [target_h[:m] + [Fraction(0)] * (80 - m) for m in range(1, 81)]
for m in range(10, 70):
    # Difference is confined to coordinates >= m.
    check(
        "CNRS-H coefficientwise truncations obey product-metric tail bound",
        h_metric(h_approx[m - 1], target_h) <= Fraction(1, 2**m),
    )

print("\nAll metric/topological completeness verification checks passed.")
