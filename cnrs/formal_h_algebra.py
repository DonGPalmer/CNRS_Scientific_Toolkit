"""Finite coefficient model of the formal CNRS-H/Hurwitz-series algebra.

The functions implement exact coefficient identities for finite truncations.
They do not assert analytic convergence of the associated EGF.
"""
from __future__ import annotations
from math import comb
from typing import Sequence, TypeVar

T = TypeVar("T")

def add(a: Sequence[T], b: Sequence[T]):
    n=max(len(a),len(b)); return tuple((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(n))

def hurwitz_product(a: Sequence[T], b: Sequence[T], order: int|None=None):
    n = (len(a)+len(b)-1) if order is None else order
    return tuple(sum(comb(m,k)*(a[k] if k<len(a) else 0)*(b[m-k] if m-k<len(b) else 0) for k in range(m+1)) for m in range(n))

def derivative(a: Sequence[T]):
    return tuple(a[1:]) if len(a)>1 else (0,)

def integral(a: Sequence[T], constant=0):
    return (constant,)+tuple(a)

def multiplicative_inverse(a: Sequence[T], order: int):
    if not a or a[0] == 0:
        raise ValueError("constant coefficient must be a unit/nonzero field element")
    out=[1/a[0]]
    for n in range(1, order):
        s=sum(comb(n,k)*a[k]*out[n-k] for k in range(1,n+1) if k<len(a))
        out.append(-s/a[0])
    return tuple(out)

def exponential_eigenfunction(alpha, order: int):
    return tuple(alpha**n for n in range(order))

__all__=["add","hurwitz_product","derivative","integral","multiplicative_inverse","exponential_eigenfunction"]
