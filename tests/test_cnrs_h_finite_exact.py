"""Independent, seeded exact tests of the CNRS-H finite coefficient candidate.

Standard-library only. Compare with an independent Fraction-pair Q(i)[x]
polynomial oracle. Tests do not treat numerical evidence as a general proof.
"""
from __future__ import annotations

import json
import random
import unittest
from fractions import Fraction
from math import factorial
from pathlib import Path

from cnrs.cnrs_h_finite_exact import RA, HurwitzJet, BETA, ONE, Z, gpow, divide_beta_exact

FP = tuple[Fraction, Fraction]
FZERO: FP = (Fraction(0),Fraction(0))
FONE: FP = (Fraction(1),Fraction(0))


def fadd(a: FP, b: FP) -> FP:
    return a[0]+b[0], a[1]+b[1]


def fneg(a: FP) -> FP:
    return -a[0],-a[1]


def fmul(a: FP, b: FP) -> FP:
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def fdiv(a: FP, b: FP) -> FP:
    den=b[0]*b[0]+b[1]*b[1]
    if not den: raise ZeroDivisionError
    return ((a[0]*b[0]+a[1]*b[1])/den,(a[1]*b[0]-a[0]*b[1])/den)


def as_qi_reference(z: RA) -> FP:
    """Independent direct fraction division, not RA.as_fraction_pair()."""
    return fdiv((Fraction(z.real),Fraction(z.imag)),
                (Fraction(gpow(BETA,z.denominator_power)[0]),
                 Fraction(gpow(BETA,z.denominator_power)[1])))


def polynomial_product(a: tuple[FP,...],b: tuple[FP,...]) -> tuple[FP,...]:
    out=[FZERO]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j]=fadd(out[i+j],fmul(x,y))
    return tuple(out)


def trim_poly(a: tuple[FP,...]) -> tuple[FP,...]:
    t=list(a)
    while len(t)>1 and t[-1]==FZERO:
        t.pop()
    return tuple(t)


def mk_ra(rng:random.Random) -> RA:
    return RA(rng.randint(-25,25),rng.randint(-25,25),rng.randrange(0,7))


def mk_jet(rng:random.Random) -> HurwitzJet:
    return HurwitzJet(tuple(mk_ra(rng) for _ in range(rng.randrange(1,7))))


class ExactHurwitzTests(unittest.TestCase):
    def test_gaussian_beta_division(self):
        rng=random.Random(511)
        for _ in range(2000):
            re,im=rng.randrange(-100,101),rng.randrange(-100,101)
            q=divide_beta_exact((re,im))
            self.assertEqual(q is not None,(re+2*im)%5 == 0)
            if q is not None:
                self.assertEqual(((-2*q[0]-q[1]),q[0]-2*q[1]),(re,im))

    def test_ra_canonical_and_rejection(self):
        self.assertEqual(RA(-2,1,1),ONE)
        self.assertEqual(RA(0,0,500),Z)
        self.assertEqual(RA(2,0,1),RA(2,0,1))
        self.assertNotEqual(RA(2,0,1),RA(2,0,0))
        for args in [(True,0,0),(0,0,1.0),(0,2+1j,0),(Fraction(1,2),0,0)]:
            with self.assertRaises(TypeError): RA(*args)
        with self.assertRaises(ValueError): RA(1,0,-1)
        with self.assertRaises(ValueError): RA(1,0,0)**-1

    def test_ra_ring_and_fraction_oracle(self):
        rng=random.Random(20261107)
        for _ in range(2200):
            a,b,c=mk_ra(rng),mk_ra(rng),mk_ra(rng)
            self.assertEqual(a.as_fraction_pair(),as_qi_reference(a))
            self.assertEqual((a+b).as_fraction_pair(),fadd(as_qi_reference(a),as_qi_reference(b)))
            self.assertEqual((a*b).as_fraction_pair(),fmul(as_qi_reference(a),as_qi_reference(b)))
            self.assertEqual(a+(b+c),(a+b)+c)
            self.assertEqual(a*(b+c),a*b+a*c)
            self.assertEqual(a*b,b*a)
            self.assertEqual(a+(-a),Z)
            self.assertEqual(a*ONE,a)
            self.assertEqual(a**0,ONE)

    def test_exact_cnrs_digit_parser(self):
        rng=random.Random(360)
        cases=["0","4","0001",".1","1.","0.004","12.34",".0004","0000.00",".4"]
        for _ in range(1700):
            left="".join(str(rng.randrange(5)) for _ in range(rng.randint(1,16)))
            right="".join(str(rng.randrange(5)) for _ in range(rng.randint(0,12)))
            cases.append(left+("."+right if rng.choice((True,False)) else ""))
        for s in cases:
            a=RA.from_cnrs_string(s)
            left,_,right=s.partition(".")
            ref=FZERO
            beta=(Fraction(-2),Fraction(1))
            for c in left:
                ref=fadd(fmul(ref,beta),(Fraction(int(c)),Fraction(0)))
            fraction=FZERO
            for c in reversed(right):
                fraction=fdiv(fadd(fraction,(Fraction(int(c)),Fraction(0))),beta)
            self.assertEqual(a.as_fraction_pair(),fadd(ref,fraction))
        for bad in ("",".","5","-1","+1"," 1","1 ","1e3","1..2","1.2.3","①","4\u0660","１","\n","1\n"):
            with self.assertRaises(ValueError): RA.from_cnrs_string(bad)
        with self.assertRaises(TypeError): RA.from_cnrs_string(1)

    def test_ra_localization_unit_boundary(self):
        rng=random.Random(434)
        for _ in range(360):
            base=RA(*rng.choice([(1,0),(-1,0),(0,1),(0,-1)]))
            beta=RA(*BETA)
            power=rng.randrange(0,9)
            depth=rng.randrange(0,9)
            unit=base*beta**power*RA.beta_inverse(depth)
            inv=unit.inverse_unit()
            self.assertEqual(unit*inv,ONE)
            self.assertEqual(inv*unit,ONE)
        for nonunit in (RA(2),RA(-2,-1),RA(3),RA(0,2),RA(2,0,1)):
            with self.assertRaises(ValueError): nonunit.inverse_unit()
        with self.assertRaises(ZeroDivisionError): Z.inverse_unit()

    def test_basis_product(self):
        for m in range(0,9):
            for n in range(0,9):
                a=HurwitzJet(tuple([Z]*m+[ONE]))
                b=HurwitzJet(tuple([Z]*n+[ONE]))
                p=a*b
                self.assertEqual(p.coefficient(m+n),RA(__import__('math').comb(m+n,m)))
                self.assertTrue(all(p.coefficient(k)==Z for k in range(m+n)))

    def test_exact_vs_ordinary_polynomial_oracle(self):
        rng=random.Random(125551)
        for _ in range(700):
            a,b=mk_jet(rng),mk_jet(rng)
            p=a*b
            aq=tuple((x[0]/factorial(n),x[1]/factorial(n)) for n,x in enumerate(as_qi_reference(c) for c in a.coefficients))
            bq=tuple((x[0]/factorial(n),x[1]/factorial(n)) for n,x in enumerate(as_qi_reference(c) for c in b.coefficients))
            expected=trim_poly(polynomial_product(aq,bq))
            self.assertEqual(p.ordinary_coefficients(),expected)
            self.assertEqual((a+b).ordinary_coefficients(),trim_poly(tuple(fadd(aq[k] if k<len(aq) else FZERO,bq[k] if k<len(bq) else FZERO) for k in range(max(len(aq),len(bq))))))

    def test_leibniz_distributivity_associativity(self):
        rng=random.Random(733)
        for _ in range(360):
            a,b,c=mk_jet(rng),mk_jet(rng),mk_jet(rng)
            self.assertEqual((a*b).derivative(),a.derivative()*b+a*b.derivative())
            self.assertEqual(a*(b+c),a*b+a*c)
            self.assertEqual((a*b)*c,a*(b*c))
            self.assertEqual(a+b,b+a)

    def test_antiderivative_identities(self):
        rng=random.Random(12345)
        for _ in range(500):
            a=mk_jet(rng)
            gamma=mk_ra(rng)
            I=a.antiderivative(gamma)
            self.assertEqual(I.derivative(),a)
            self.assertEqual(I.coefficient(0),gamma)
            self.assertEqual(a.derivative().antiderivative(a.coefficient(0)),a)
            self.assertEqual(a.antiderivative().derivative(),a)

    def test_truncation_and_derivative_boundary(self):
        rng=random.Random(441)
        for _ in range(450):
            a,b=mk_jet(rng),mk_jet(rng)
            n=rng.randrange(0,9)
            self.assertEqual((a*b).truncate(n),a.truncate(n).product(b.truncate(n),through_degree=n))
            self.assertEqual(a.derivative().truncate(n),a.truncate(n+1).derivative().truncate(n))
        x=HurwitzJet.from_coefficients(0,0,1)
        self.assertNotEqual(x.truncate(1).derivative(),x.derivative().truncate(1))
        for n in (-1,1.0,True):
            with self.assertRaises(ValueError): x.truncate(n)

    def test_formal_reciprocal_only_for_units(self):
        rng=random.Random(992)
        bases=[ONE,-ONE,RA(*BETA),RA.beta_inverse(1),RA(0,1),RA(-2,1,3)]
        for _ in range(260):
            a=HurwitzJet(tuple([rng.choice(bases)]+[mk_ra(rng) for _ in range(rng.randint(0,5))]))
            n=rng.randrange(0,9)
            inv=a.inverse_truncated(n)
            product=a.product(inv,through_degree=n)
            self.assertEqual(product,HurwitzJet.from_coefficients(1))
        with self.assertRaises(ValueError): HurwitzJet.from_coefficients(2,1).inverse_truncated(5)
        with self.assertRaises(ZeroDivisionError): HurwitzJet.from_coefficients(0,1).inverse_truncated(5)

    def test_exponential_identity_in_finite_truncation(self):
        for a,b in ((RA(1),RA(2)),(RA(*BETA),RA.beta_inverse(1)),(RA(0,1),RA(1,0,3))):
            n=9
            ea=HurwitzJet(tuple(a**k for k in range(n+1)))
            eb=HurwitzJet(tuple(b**k for k in range(n+1)))
            ec=HurwitzJet(tuple((a+b)**k for k in range(n+1)))
            self.assertEqual(ea.product(eb,through_degree=n),ec)

    def test_negative_input_guards(self):
        with self.assertRaises(TypeError): HurwitzJet.from_coefficients(Fraction(1,2))
        with self.assertRaises(TypeError): HurwitzJet.from_coefficients(True)
        with self.assertRaises(TypeError): HurwitzJet.from_coefficients(1.0)
        with self.assertRaises(ValueError): HurwitzJet.from_coefficients(1).product(HurwitzJet.from_coefficients(1),through_degree=-1)


if __name__ == '__main__':
    import sys
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ExactHurwitzTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={"run":"CNRS-H finite exact candidate independent tests",
            "tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),
            "success":result.wasSuccessful(),"seeded_test_cases": {
                "gaussian_divisibility":2000,"ra_random_ring":2200,"cnrs_strings":1710,
                "ra_unit_inverse":360,"basis_products":81,"hurwitz_vs_poly":700,
                "leibniz_associativity":360,"differential_integral":500,
                "truncation":450,"unit_hurwitz_inverse":260},
            "note":"Counters describe explicitly specified independent cases; no universal proof or publication assertion."}
    Path('test_results.json').write_text(json.dumps(report,indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() else 1)
