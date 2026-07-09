from fractions import Fraction
import random

from cnrs.hybrid import CoefficientCodec, HybridSeries, hybrid_from_values


def frac_codec():
    return CoefficientCodec(
        encode=lambda x: (x.numerator, x.denominator),
        decode=lambda p: Fraction(p[0], p[1]),
        zero=Fraction(0), one=Fraction(1),
    )


def test_codec_bijection_and_canonicalization():
    codec=frac_codec()
    s=hybrid_from_values([Fraction(2,4), Fraction(-3,9)], codec)
    assert s.values() == (Fraction(1,2), Fraction(-1,3))
    assert s.canonical() == s


def test_hybrid_hurwitz_transport_and_leibniz():
    codec=frac_codec(); rng=random.Random(20260709)
    for _ in range(100):
        a=[Fraction(rng.randint(-3,3),rng.randint(1,4)) for _ in range(8)]
        b=[Fraction(rng.randint(-3,3),rng.randint(1,4)) for _ in range(8)]
        A=HybridSeries.from_values(a,codec); B=HybridSeries.from_values(b,codec)
        lhs=A.hurwitz_product(B,order=8).derivative().values()
        rhs=A.derivative().hurwitz_product(B,order=7).add(A.hurwitz_product(B.derivative(),order=7),order=7).values()
        assert lhs == rhs


def test_integration_and_exponential_eigenfunction():
    codec=frac_codec()
    a=HybridSeries.from_values([Fraction(1),Fraction(4),Fraction(9)],codec)
    assert a.integral(Fraction(7)).derivative().values() == a.values()
    alpha=Fraction(2,3)
    e=a.exponential_eigenfunction(alpha,8)
    assert e.derivative().values() == tuple(alpha*x for x in e.values()[:-1])


def test_exponential_product_law():
    codec=frac_codec(); seed=HybridSeries.from_values([],codec)
    ea=seed.exponential_eigenfunction(Fraction(1,2),8)
    eb=seed.exponential_eigenfunction(Fraction(1,3),8)
    ec=seed.exponential_eigenfunction(Fraction(5,6),8)
    assert ea.hurwitz_product(eb,order=8).values() == ec.values()


def test_deterministic_serialization():
    codec=frac_codec(); s=HybridSeries.from_values([Fraction(1,2),Fraction(3,4)],codec)
    out=s.as_dict(serializer=lambda p:{"numerator":p[0],"denominator":p[1]})
    assert out == {"basis":"rho^n/n!","coefficients":[{"numerator":1,"denominator":2},{"numerator":3,"denominator":4}]}
