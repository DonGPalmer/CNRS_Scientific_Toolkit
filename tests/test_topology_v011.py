from fractions import Fraction
import random

from cnrs.topology import (
    first_difference, symbolic_distance, beta_adic_absolute,
    beta_adic_distance, evaluate_finite_digits, first_difference_isometry,
    coefficientwise_distance,
)


def test_symbolic_distance_basic_and_ultrametric():
    assert first_difference((1,2,3), (1,2,4)) == 2
    assert symbolic_distance((1,2,3), (1,2,4)) == Fraction(1,25)
    assert symbolic_distance((1,2), (1,2)) == 0
    rng=random.Random(20260709)
    for _ in range(500):
        a=tuple(rng.randrange(5) for _ in range(20))
        b=tuple(rng.randrange(5) for _ in range(20))
        c=tuple(rng.randrange(5) for _ in range(20))
        assert symbolic_distance(a,c) <= max(symbolic_distance(a,b), symbolic_distance(b,c))


def test_beta_adic_examples():
    assert beta_adic_absolute((0,0)) == 0
    assert beta_adic_absolute((-2,1)) == Fraction(1,5)
    assert beta_adic_distance((1,0), (1,0)) == 0


def test_first_difference_isometry_randomized():
    rng=random.Random(20260709)
    for _ in range(500):
        a=[rng.randrange(5) for _ in range(24)]
        b=a.copy(); r=rng.randrange(24)
        b[r]=rng.choice([d for d in range(5) if d != a[r]])
        for j in range(r+1,24): b[j]=rng.randrange(5)
        assert first_difference_isometry(a,b)
        assert beta_adic_distance(evaluate_finite_digits(a), evaluate_finite_digits(b)) == Fraction(1,5**r)


def test_coefficientwise_metric_tail():
    target=[1/(n+1) for n in range(30)]
    approx=target[:12]+[0]*18
    assert coefficientwise_distance(approx,target) <= 2**-12
