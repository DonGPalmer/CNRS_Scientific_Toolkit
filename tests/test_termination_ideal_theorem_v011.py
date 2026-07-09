from cnrs.gaussian_valuation import *

def test_beta_inverse_offsets():
    for m in range(1,7):
        a=analyze_termination((1,0),gpow(BETA,m))
        assert a.terminates and a.minimal_laurent_offset==m

def test_one_fifth_does_not_terminate():
    a=analyze_termination((1,0),(5,0))
    assert not a.terminates
    assert a.residual_denominator == unit_normalize(BETA_BAR)

def test_conjugate_over_five_terminates():
    a=analyze_termination(BETA_BAR,(5,0))
    assert a.terminates and a.minimal_laurent_offset==1

def test_units_do_not_change_result():
    base=analyze_termination((7,3),(11,2))
    for u in UNITS:
        x=analyze_termination(gmul(u,(7,3)),gmul(u,(11,2)))
        assert x.terminates==base.terminates
        assert x.minimal_laurent_offset==base.minimal_laurent_offset

def test_cancellation_before_valuation():
    p=gmul(BETA,(3,2)); q=gmul(BETA,gpow(BETA,3))
    a=analyze_termination(p,q)
    assert a.minimal_laurent_offset==3 and a.terminates

def test_non_beta_prime_is_obstruction():
    a=analyze_termination((1,0),(1,1))
    assert not a.terminates and a.obstruction_generator is not None
