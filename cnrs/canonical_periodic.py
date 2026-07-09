"""Canonical eventually-periodic Laurent expansions in base ``-2+i``.

Canonical form is obtained by exact value recovery followed by deterministic
re-expansion.  It has minimal Laurent offset, least preperiod, and the primitive
state-cycle period.  Terminating values have an empty period.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from .gaussian_valuation import (
    Gaussian, BETA, gadd, gsub, gmul, gnorm, gdiv_exact, gpow,
    reduce_gaussian_fraction, gaussian_valuation, unit_normalize,
)
from .cnrs_repr import gaussian_to_cnrs_digits


def _phi(z: Gaussian) -> int: return (z[0]+2*z[1])%5

def primitive_period(block: Iterable[int]) -> tuple[int,...]:
    b=tuple(int(x) for x in block)
    if not b: return ()
    for p in range(1,len(b)+1):
        if len(b)%p==0 and b==b[:p]*(len(b)//p): return b[:p]
    return b

def _adic_digits(p: Gaussian, q: Gaussian, max_steps: int=100000) -> tuple[tuple[int,...],tuple[int,...]]:
    phiq=_phi(q)
    if phiq==0: raise ValueError("residual denominator must be coprime to beta")
    inv=pow(phiq,-1,5); state=p; seen:dict[Gaussian,int]={}; digits:list[int]=[]
    for _ in range(max_steps):
        if state==(0,0): return tuple(digits),()
        if state in seen:
            r=seen[state]
            return tuple(digits[:r]), primitive_period(digits[r:])
        seen[state]=len(digits)
        d=(_phi(state)*inv)%5; digits.append(d)
        state=gdiv_exact(gsub(state,(d*q[0],d*q[1])),BETA)
    raise RuntimeError(f"no cycle detected within {max_steps} states")

def _fraction_pair_add(a,b): return (a[0]+b[0],a[1]+b[1])
def _fraction_pair_mul(a,b): return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def _beta_fraction_power(n:int):
    if n>=0:
        z=gpow(BETA,n); return (Fraction(z[0]),Fraction(z[1]))
    z=gpow((-2,-1),-n); den=5**(-n); return (Fraction(z[0],den),Fraction(z[1],den))

@dataclass(frozen=True)
class CanonicalPeriodicExpansion:
    power_offset: int
    prefix: tuple[int,...]
    period: tuple[int,...]=()

    def __post_init__(self):
        if any(d not in range(5) for d in self.prefix+self.period):
            raise ValueError("digits must lie in {0,1,2,3,4}")
        if self.period and primitive_period(self.period)!=self.period:
            raise ValueError("period must be primitive")
        if self.period==(0,): raise ValueError("terminating values use an empty period")

    @property
    def is_finite(self)->bool: return not self.period
    @property
    def preperiod_length(self)->int: return len(self.prefix)
    @property
    def period_length(self)->int: return len(self.period)
    @property
    def digits_prefix(self)->tuple[int,...]: return self.prefix

    @classmethod
    def from_gaussian_fraction(cls,p:Gaussian,q:Gaussian=(1,0),*,max_steps:int=100000):
        rp,rq=reduce_gaussian_fraction(p,q)
        if rp==(0,0): return cls(0,(0,),())
        vq=gaussian_valuation(rq,BETA); residual=rq
        for _ in range(vq): residual=gdiv_exact(residual,BETA)
        # denominator normalization may have changed by a unit; keep exact quotient
        if gnorm(residual)==1:
            a=gdiv_exact(rp,residual)
            digits=tuple(int(d) for d in gaussian_to_cnrs_digits(complex(*a)))
            return cls(-vq,digits,())
        pre,per=_adic_digits(rp,residual,max_steps=max_steps)
        return cls(-vq,pre,per)

    @classmethod
    def from_integer_denominator(cls,p:Gaussian,q:int=1,**kwargs):
        return cls.from_gaussian_fraction(p,(int(q),0),**kwargs)

    def exact_value_fractions(self)->tuple[Fraction,Fraction]:
        total=(Fraction(0),Fraction(0))
        for k,d in enumerate(self.prefix):
            pw=_beta_fraction_power(self.power_offset+k)
            total=_fraction_pair_add(total,(d*pw[0],d*pw[1]))
        if self.period:
            T=len(self.period); block=(Fraction(0),Fraction(0))
            for j,d in enumerate(self.period):
                pw=_beta_fraction_power(self.power_offset+len(self.prefix)+j)
                block=_fraction_pair_add(block,(d*pw[0],d*pw[1]))
            bt=gpow(BETA,T); denom=(Fraction(1-bt[0]),Fraction(-bt[1]))
            n=denom[0]*denom[0]+denom[1]*denom[1]
            tail=_fraction_pair_mul(block,(denom[0]/n,-denom[1]/n))
            total=_fraction_pair_add(total,tail)
        return total

    def exact_gaussian_fraction(self)->tuple[Gaussian,Gaussian]:
        re,im=self.exact_value_fractions()
        from math import lcm
        d=lcm(re.denominator,im.denominator)
        p=(re.numerator*(d//re.denominator),im.numerator*(d//im.denominator))
        return reduce_gaussian_fraction(p,(d,0))

    def canonical(self):
        p,q=self.exact_gaussian_fraction()
        return type(self).from_gaussian_fraction(p,q)

    def equivalent_to(self,other:"CanonicalPeriodicExpansion")->bool:
        return self.exact_value_fractions()==other.exact_value_fractions()

    def as_dict(self)->dict[str,object]:
        return {"base":"-2+i","power_offset":self.power_offset,
                "prefix":list(self.prefix),"period":list(self.period)}

    def __str__(self)->str:
        off=f"[z0^{self.power_offset}]" if self.power_offset else ""
        pre=''.join(map(str,self.prefix)); per=''.join(map(str,self.period))
        return f"{off}{pre}"+(f"[{per}]" if per else "")

def canonicalize_periodic(expansion)->CanonicalPeriodicExpansion:
    """Canonicalize a compatible periodic object by exact value and re-expansion."""
    if isinstance(expansion,CanonicalPeriodicExpansion): return expansion.canonical()
    if hasattr(expansion,"z0_adic_value_fractions"):
        re,im=expansion.z0_adic_value_fractions()
        from math import lcm
        d=lcm(re.denominator,im.denominator)
        p=(re.numerator*(d//re.denominator),im.numerator*(d//im.denominator))
        return CanonicalPeriodicExpansion.from_integer_denominator(p,d)
    if all(hasattr(expansion,a) for a in ("power_offset","prefix","period")):
        temp=CanonicalPeriodicExpansion(int(expansion.power_offset),tuple(expansion.prefix),primitive_period(expansion.period))
        return temp.canonical()
    raise TypeError("unsupported periodic expansion object")

__all__=["CanonicalPeriodicExpansion","canonicalize_periodic","primitive_period"]
