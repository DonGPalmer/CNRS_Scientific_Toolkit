"""Independent v0.10.3 cross-validation and CNRS-H eigenfunction tests."""
from __future__ import annotations
import random
from fractions import Fraction
import pytest

Gaussian=tuple[int,int]
Z0=(-2,1)
def gadd(x,y): return x[0]+y[0],x[1]+y[1]
def gmul(x,y): return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def ref_encode(g:Gaussian):
    a,b=g; out=[]
    while a or b:
        d=(a+2*b)%5; na,nb=a-d,b; x,y=-2*na+nb,-na-2*nb
        assert x%5==0 and y%5==0; a,b=x//5,y//5; out.append(d)
        assert len(out)<300
    return out or [0]
def ref_eval(ds):
    total=(0,0); p=(1,0)
    for d in ds: total=gadd(total,(d*p[0],d*p[1])); p=gmul(p,Z0)
    return total

def test_exact_reference_roundtrip_and_toolkit_encoding():
    from cnrs.core.digits import gaussian_to_cnrs_digits, gaussian_to_cnrs_str, cnrs_to_gaussian
    rng=random.Random(20260707)
    for _ in range(400):
        g=(rng.randint(-500,500),rng.randint(-500,500)); z=complex(*g)
        assert ref_eval(ref_encode(g))==g
        assert list(gaussian_to_cnrs_digits(z))==ref_encode(g)
        assert cnrs_to_gaussian(gaussian_to_cnrs_str(z))==z

def test_independent_arithmetic_cross_validation():
    from cnrs.core.digits import gaussian_to_cnrs_str, cnrs_to_gaussian
    from cnrs.core.arithmetic import cnrs_add,cnrs_mul,cnrs_sub
    rng=random.Random(20260708)
    for _ in range(300):
        a=complex(rng.randint(-200,200),rng.randint(-200,200)); b=complex(rng.randint(-200,200),rng.randint(-200,200))
        sa,sb=gaussian_to_cnrs_str(a),gaussian_to_cnrs_str(b)
        assert cnrs_to_gaussian(cnrs_add(sa,sb))==a+b
        assert cnrs_to_gaussian(cnrs_mul(sa,sb))==a*b
        assert cnrs_to_gaussian(cnrs_sub(sa,sb))==a-b

def test_digit_alphabet_normalization_and_carry_set():
    from cnrs.core.digits import gaussian_to_cnrs_digits, gaussian_to_cnrs_str, normalize_cnrs
    from cnrs.cnrs_add import CARRY_SET_PAIRS
    rng=random.Random(20260709)
    for _ in range(200):
        z=complex(rng.randint(-500,500),rng.randint(-500,500)); ds=gaussian_to_cnrs_digits(z); s=gaussian_to_cnrs_str(z)
        assert set(ds)<=set(range(5)); assert normalize_cnrs(s)==s
    assert len(CARRY_SET_PAIRS)==14

def test_cnrs_h_eigen_exponential_relation():
    from cnrs.h.series import CnrsH
    h=CnrsH.eigen_exponential(alpha=2,terms=24); dh=h.D()
    for i in range(20): assert dh.coeff(i)==2*h.coeff(i)
    assert CnrsH.exponential(2,4).coeffs==(2,2,2,2)

def test_cnrs_h_native_eigen_exponential_relation():
    from cnrs.cnrs_h_native import CnrsHNative
    h=CnrsHNative.eigen_exponential(alpha=1+1j,terms=10); dh=h.D()
    a=1+1j
    for i in range(8): assert dh.coeff(i).to_gaussian()==a*h.coeff(i).to_gaussian()

def test_native_composition_and_inversion_independent_reference():
    from cnrs.cnrs_h_native import CnrsHNative,compose_native,invert_native
    order=8; F=CnrsHNative.from_gaussian_list([1]*order); G=CnrsHNative.from_gaussian_list([0,1,2]+[0]*(order-3))
    comp=compose_native(F,G,order)
    a=[Fraction(0) for _ in range(order)]; a[0]=1
    for n in range(1,order): a[n]=(a[n-1]+(2*a[n-2] if n>=2 else 0))/n
    fact=1
    for n in range(order):
        if n: fact*=n
        assert comp.coeff(n).to_gaussian()==complex(int(a[n]*fact))
    inv=invert_native(G,order); ident=compose_native(G,inv,order)
    expected=[0,1]+[0]*(order-2)
    for n,x in enumerate(expected): assert ident.coeff(n).to_gaussian()==complex(x)

def test_invalid_eigen_exponential_terms():
    from cnrs.h.series import CnrsH
    from cnrs.cnrs_h_native import CnrsHNative
    with pytest.raises(ValueError): CnrsH.eigen_exponential(1,0)
    with pytest.raises(ValueError): CnrsHNative.eigen_exponential(1,0)
