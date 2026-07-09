import random
from cnrs.canonical_periodic import *
from cnrs.gaussian_valuation import BETA_BAR

def test_primitive_period_utility():
    assert primitive_period((1,2,1,2))==(1,2)
    assert primitive_period((3,3,3))==(3,)

def test_known_termination_examples():
    assert CanonicalPeriodicExpansion.from_integer_denominator(BETA_BAR,5).is_finite
    assert not CanonicalPeriodicExpansion.from_integer_denominator((1,0),5).is_finite

def test_idempotence_and_exact_value_random():
    rng=random.Random(20260709)
    for _ in range(150):
        p=(rng.randint(-40,40),rng.randint(-40,40)); q=rng.randint(1,40)
        c=CanonicalPeriodicExpansion.from_integer_denominator(p,q,max_steps=50000)
        assert c.canonical()==c
        rp,rq=c.exact_gaussian_fraction()
        c2=CanonicalPeriodicExpansion.from_gaussian_fraction(rp,rq,max_steps=50000)
        assert c2==c

def test_duplicated_period_canonicalizes():
    c=CanonicalPeriodicExpansion.from_integer_denominator((1,0),3)
    assert c.period
    raw=CanonicalPeriodicExpansion(c.power_offset,c.prefix,c.period) # valid canonical
    assert raw.canonical()==c

def test_serialization_is_deterministic():
    c=CanonicalPeriodicExpansion.from_integer_denominator((1,2),7)
    assert c.as_dict()==c.canonical().as_dict()
