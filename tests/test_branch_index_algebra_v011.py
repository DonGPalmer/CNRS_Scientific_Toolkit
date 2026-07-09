import cmath, math, random
from cnrs.branch_algebra import LiftedComplex, branch_wrap

def rand_nonzero(rng):
    while True:
        z=complex(rng.randint(-5,5),rng.randint(-5,5))
        if z: return z

def test_cocycle_associativity_and_log_law():
    rng=random.Random(20260709)
    for _ in range(1000):
        a=LiftedComplex(rand_nonzero(rng),rng.randint(-3,3)); b=LiftedComplex(rand_nonzero(rng),rng.randint(-3,3)); c=LiftedComplex(rand_nonzero(rng),rng.randint(-3,3))
        assert (a*b)*c == a*(b*c)
        assert abs((a*b).log()-(a.log()+b.log())) < 1e-10

def test_inverse_and_power():
    x=LiftedComplex(-1+0j,2)
    one=x*x.inverse()
    assert abs(one.z-1)<1e-12 and one.k==0
    assert abs((x**3).log()-3*x.log())<1e-10

def test_wrap_boundary():
    z=cmath.exp(1j*3*math.pi/4); w=cmath.exp(1j*3*math.pi/4)
    assert branch_wrap(z,w)==1
