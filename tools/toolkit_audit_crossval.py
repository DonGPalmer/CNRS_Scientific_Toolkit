#!/usr/bin/env python3
"""Independent deterministic cross-validation for CNRS Scientific Toolkit.

The reference CNRS-A encoder/evaluator uses exact integer pairs and does not
reuse Toolkit encoding or arithmetic code. Any failed check exits nonzero.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SEED = 20260707
random.seed(SEED)
failures: list[str] = []

def check(name: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    if not condition:
        failures.append(name)

Gaussian = tuple[int, int]

def gadd(x: Gaussian, y: Gaussian) -> Gaussian:
    return x[0] + y[0], x[1] + y[1]

def gmul(x: Gaussian, y: Gaussian) -> Gaussian:
    return x[0]*y[0] - x[1]*y[1], x[0]*y[1] + x[1]*y[0]

Z0: Gaussian = (-2, 1)

def ref_encode(g: Gaussian) -> list[int]:
    a, b = g
    digits: list[int] = []
    while a or b:
        d = (a + 2*b) % 5
        na, nb = a-d, b
        qa_num, qb_num = -2*na + nb, -na - 2*nb
        assert qa_num % 5 == 0 and qb_num % 5 == 0
        a, b = qa_num//5, qb_num//5
        digits.append(d)
        if len(digits) >= 300:
            raise RuntimeError('reference encoder did not terminate')
    return digits or [0]

def ref_eval(digits: list[int]) -> Gaussian:
    total: Gaussian = (0, 0)
    power: Gaussian = (1, 0)
    for d in digits:
        total = gadd(total, (d*power[0], d*power[1]))
        power = gmul(power, Z0)
    return total

for _ in range(500):
    g=(random.randint(-500,500), random.randint(-500,500))
    assert ref_eval(ref_encode(g)) == g
check('A0 independent exact reference round-trips 500 Gaussian integers', True)

from cnrs.core.digits import gaussian_to_cnrs_digits, gaussian_to_cnrs_str, cnrs_to_gaussian, normalize_cnrs
from cnrs.core.arithmetic import cnrs_add, cnrs_mul, cnrs_sub

N=400; enc=dec=0
for _ in range(N):
    g=(random.randint(-300,300), random.randint(-300,300)); z=complex(*g)
    enc += list(gaussian_to_cnrs_digits(z)) == ref_encode(g)
    dec += cnrs_to_gaussian(gaussian_to_cnrs_str(z)) == z
check(f'A1 encode matches independent exact expansion ({enc}/{N})', enc==N)
check(f'A2 decode round-trips ({dec}/{N})', dec==N)

M=300; add=mul=sub=0
for _ in range(M):
    a=(random.randint(-200,200), random.randint(-200,200)); b=(random.randint(-200,200), random.randint(-200,200))
    za,zb=complex(*a),complex(*b); sa,sb=gaussian_to_cnrs_str(za),gaussian_to_cnrs_str(zb)
    add += cnrs_to_gaussian(cnrs_add(sa,sb)) == za+zb
    mul += cnrs_to_gaussian(cnrs_mul(sa,sb)) == za*zb
    sub += cnrs_to_gaussian(cnrs_sub(sa,sb)) == za-zb
check(f'A3 addition agrees ({add}/{M})', add==M)
check(f'A4 multiplication agrees ({mul}/{M})', mul==M)
check(f'A5 subtraction agrees ({sub}/{M})', sub==M)

alpha=idem=0
for _ in range(200):
    z=complex(random.randint(-500,500), random.randint(-500,500))
    alpha += all(0 <= d <= 4 for d in gaussian_to_cnrs_digits(z))
    s=gaussian_to_cnrs_str(z); idem += normalize_cnrs(s) == s
check(f'A6 digit alphabet within 0..4 ({alpha}/200)', alpha==200)
check(f'A7 normalization idempotent ({idem}/200)', idem==200)
from cnrs.cnrs_add import CARRY_SET_PAIRS
check('A8 addition carry set has 14 states', len(CARRY_SET_PAIRS)==14)

from cnrs.h.series import CnrsH
f=CnrsH.from_list([3,2,5,7]); df=f.D()
check('H1 EGF differentiation is coefficient shift', [df.coeff(i) for i in range(3)] == [2,5,7])
check('H2 EGF evaluation matches direct polynomial value', abs(f.evaluate(.37)-(3+2*.37+5*.37**2/2+7*.37**3/6)) < 1e-12)
h=CnrsH.eigen_exponential(2,24); dh=h.D()
check('H3 D exp(alpha*rho) = alpha exp(alpha*rho)', all(abs(dh.coeff(i)-2*h.coeff(i)) < 1e-12 for i in range(20)))
g=CnrsH.from_list([1,4,1,5,9,2,6])
check('H4 D(integrate(f)) = f', g.integrate().D().coeffs == g.coeffs)

from cnrs.cnrs_h_native import CnrsHNative, compose_native, invert_native
ORDER=8
F=CnrsHNative.from_gaussian_list([1]*ORDER)
G=CnrsHNative.from_gaussian_list([0,1,2]+[0]*(ORDER-3))
comp=compose_native(F,G,ORDER)
# independent EGF composition recurrence for exp(rho+rho^2)
# ordinary series coefficients via recurrence n*a_n = a_{n-1}+2*a_{n-2}; compare EGF n!*a_n
from fractions import Fraction
a=[Fraction(0) for _ in range(ORDER)]; a[0]=Fraction(1)
for n in range(1,ORDER):
    a[n]=(a[n-1] + (2*a[n-2] if n>=2 else 0))/n
facts=[1]
for n in range(1,ORDER): facts.append(facts[-1]*n)
ref=[int(a[n]*facts[n]) for n in range(ORDER)]
got=[complex(comp.coeff(n).to_gaussian()) for n in range(ORDER)]
check('H5 native composition matches independent exp(rho+rho^2) recurrence', all(got[n] == complex(ref[n]) for n in range(ORDER)))
ginv=invert_native(G,ORDER); gg=compose_native(G,ginv,ORDER)
ident=[0,1]+[0]*(ORDER-2)
check('H6 compose(g,invert(g)) is identity', all(complex(gg.coeff(n).to_gaussian()) == complex(ident[n]) for n in range(ORDER)))

if failures:
    raise SystemExit(f'{len(failures)} checks failed: ' + '; '.join(failures))
print(f'All 15 audit groups passed (seed={SEED}).')
