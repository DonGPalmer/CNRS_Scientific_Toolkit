"""Independent exact validation of division classification and rational expansion."""
from fractions import Fraction
from math import gcd
import random
import pytest
from cnrs.division import classify_denominator, expand_division, DivisionStatus
from cnrs.cnrs_rational import gaussian_rational_to_cnrs

SEED = 20260708


def reduced_q(a,b,q):
    return abs(q)//gcd(gcd(abs(a),abs(b)),abs(q))


def v5(q):
    n=0
    while q and q%5==0:
        q//=5; n+=1
    return n,q


def divides_z0bar_power(a,b,e):
    for _ in range(e):
        nr, ni = -2*a-b, a-2*b
        if nr%5 or ni%5:
            return False
        a,b = nr//5, ni//5
    return True


def expected_status(a,b,q):
    rq=reduced_q(a,b,q); e,p=v5(rq)
    g=gcd(gcd(abs(a),abs(b)),abs(q))
    a,b=a//g,b//g
    if rq==1: return DivisionStatus.GAUSSIAN_INTEGER
    if e==0: return DivisionStatus.PERIODIC_COPRIME_DENOMINATOR
    if p==1 and divides_z0bar_power(a,b,e):
        return DivisionStatus.TERMINATING_BASE_POWER
    return DivisionStatus.SHIFTED_PERIODIC_TAIL


def test_random_classification_and_exact_reconstruction():
    rng=random.Random(SEED)
    for _ in range(250):
        a,b=rng.randint(-40,40),rng.randint(-40,40)
        q=rng.randint(1,40)
        c=classify_denominator((a,b),q)
        assert c.status == expected_status(a,b,q)
        r=gaussian_rational_to_cnrs((a,b),q,max_frac=3000)
        if r.is_z0_adic:
            re,im=r.z0_adic_value_fractions()
        else:
            re,im=Fraction(a,q),Fraction(b,q)
        assert re == Fraction(a,q)
        assert im == Fraction(b,q)
        assert r.round_trip_ok(tol=1e-13)


def test_equivalent_fraction_classification_invariance():
    for a,b,q,k in [(1,0,3,7),(1,1,5,4),(2,-1,15,9),(7,3,125,2)]:
        c1=classify_denominator((a,b),q)
        c2=classify_denominator((a*k,b*k),q*k)
        assert c1.status == c2.status
        assert c1.reduced_denominator == c2.reduced_denominator
        r1=expand_division((a,b),q,max_frac=3000)
        r2=expand_division((a*k,b*k),q*k,max_frac=3000)
        assert r1.expansion.z0_adic_value_fractions() == r2.expansion.z0_adic_value_fractions()


def test_detected_period_is_minimal_for_sampled_short_periods():
    for q in [2,3,7,11,13,17,19,31]:
        r=gaussian_rational_to_cnrs(1,q,max_frac=1000)
        block=r.frac_digits[r.period_start:]
        T=len(block)
        for d in range(1,T):
            if T%d==0:
                assert block != block[:d]*(T//d)


def test_invalid_denominator():
    with pytest.raises(ZeroDivisionError):
        classify_denominator(1,0)
    with pytest.raises(ValueError):
        gaussian_rational_to_cnrs(1,0)
