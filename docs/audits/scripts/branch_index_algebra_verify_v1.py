"""Independent numerical checks for branch-index multiplication/logarithm algebra."""
from __future__ import annotations
import cmath
import math
import random

random.seed(20260709)
TWOPI = 2.0 * math.pi


def argp(z: complex) -> float:
    a = math.atan2(z.imag, z.real)
    # Lock principal range to (-pi, pi], including signed-zero cases.
    if math.isclose(a, -math.pi, abs_tol=1e-15):
        return math.pi
    return a


def omega(z: complex, w: complex) -> int:
    raw = (argp(z) + argp(w) - argp(z*w)) / TWOPI
    return int(round(raw))


def mul(x: tuple[complex, int], y: tuple[complex, int]) -> tuple[complex, int]:
    z, k = x
    w, l = y
    return z*w, k+l+omega(z, w)


def llog(x: tuple[complex, int]) -> complex:
    z, k = x
    return math.log(abs(z)) + 1j*(argp(z)+TWOPI*k)


def inv(x: tuple[complex, int]) -> tuple[complex, int]:
    z, k = x
    zi = 1/z
    return zi, -k-omega(z, zi)


def close(a: complex, b: complex, tol: float = 1e-10) -> bool:
    return abs(a-b) < tol


def main() -> None:
    for _ in range(5000):
        def rz() -> complex:
            r = math.exp(random.uniform(-3, 3))
            t = random.uniform(-math.pi, math.pi)
            return r*cmath.exp(1j*t)
        x = (rz(), random.randint(-5,5))
        y = (rz(), random.randint(-5,5))
        z = (rz(), random.randint(-5,5))

        a1=mul(mul(x,y),z); a2=mul(x,mul(y,z)); assert a1[1]==a2[1] and close(a1[0],a2[0])
        c1=mul(x,y); c2=mul(y,x); assert c1[1]==c2[1] and close(c1[0],c2[0])
        e=mul(x,(1+0j,0)); assert e[1]==x[1] and close(e[0],x[0])
        ii=mul(x,inv(x)); assert ii[1]==0 and close(ii[0],1+0j)
        assert close(llog(mul(x,y)), llog(x)+llog(y))

    # branch-boundary cases
    for r in (0.1,1.0,7.0):
        x = (-r+0j, 0)
        xi = inv(x)
        assert xi[1] == -1
        ii=mul(x,xi); assert ii[1]==0 and close(ii[0],1+0j)

    print("PASS: 5000 randomized group/logarithm checks")
    print("PASS: negative-real branch-boundary inverse checks")


if __name__ == "__main__":
    main()
