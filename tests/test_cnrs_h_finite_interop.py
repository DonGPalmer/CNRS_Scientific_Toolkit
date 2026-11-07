"""Independent tests for the CNRS-H localization codec and pinned digit API."""
from __future__ import annotations
import hashlib
import json
import random
import sys
import unittest
from fractions import Fraction
from pathlib import Path

from cnrs.cnrs_h_finite_exact import RA, HurwitzJet, BETA, Z, ONE, gadd, gmul, gpow, divide_beta_exact
from cnrs.cnrs_h_toolkit_interop import ToolkitDigitOps, InteropMismatch

from cnrs.cnrs_add import add_cnrs, ADDITION_TABLE  # noqa: E402
from cnrs.cnrs_mul import mul_cnrs  # noqa: E402
from cnrs.finite_string import cnrs_string_value_exact  # noqa: E402
from cnrs.gaussian_types import GaussianRational  # noqa: E402

# Intentionally independent evaluator in rational Gaussian pairs.
def add(x,y): return (x[0]+y[0],x[1]+y[1])
def mul(x,y): return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def div(x,y):
    den=y[0]**2+y[1]**2
    return ((x[0]*y[0]+x[1]*y[1])/den,(x[1]*y[0]-x[0]*y[1])/den)
def eval_string(s):
    integer,sep,frac=s.partition('.')
    base=(Fraction(-2),Fraction(1)); out=(Fraction(0),Fraction(0))
    for x in integer:out=add(mul(out,base),(Fraction(int(x)),Fraction(0)))
    sub=(Fraction(0),Fraction(0))
    for x in reversed(frac): sub=div(add(sub,(Fraction(int(x)),Fraction(0))),base)
    return add(out,sub)
def val(a):return div((Fraction(a.real),Fraction(a.imag)),tuple(map(Fraction,gpow(BETA,a.denominator_power))))

def source_random(rng):
    return RA(rng.randint(-5000,5000),rng.randint(-5000,5000),rng.randint(0,8))

class RepairedCodec(unittest.TestCase):
    def test_gaussian_exact_recurrence_and_uniqueness(self):
        for a in range(-75,76):
            for b in range(-9,10):
                x=RA(a,b)
                s=x.to_cnrs_string()
                self.assertEqual(x,RA.from_cnrs_string(s))
                self.assertEqual(val(x),eval_string(s))
                self.assertTrue('.' not in s)

    def test_all_localized_small_families(self):
        count=0
        for a in range(-15,16):
            for b in range(-15,16,3):
                for k in (0,1,2,3,7,20):
                    x=RA(a,b,k);s=x.to_cnrs_string()
                    self.assertEqual(RA.from_cnrs_string(s),x)
                    self.assertEqual(eval_string(s),val(x))
                    self.assertEqual(s,RA.from_cnrs_string(s).to_cnrs_string())
                    count+=1
        self.assertEqual(count,2046)

    def test_15k_random_localized_values(self):
        rng=random.Random(202611071)
        for _ in range(15000):
            x=source_random(rng)
            s=x.to_cnrs_string()
            self.assertEqual(eval_string(s),val(x))
            self.assertEqual(RA.from_cnrs_string(s),x)

    def test_raw_spellings_and_canonical_normalization(self):
        rng=random.Random(202611072)
        examples=['0','00000','1.','.1','1.0','01.00200','0.00','.0004','4.','0004.0040','0.00001']
        for _ in range(5000):
            n=rng.randrange(1,35);nfrac=rng.randrange(0,36)
            s=''.join(str(rng.randrange(5)) for _ in range(n))
            if rng.random()<.85: s+='.'+''.join(str(rng.randrange(5)) for _ in range(nfrac))
            if rng.random()<.2: s='.'+s.split('.')[1] if '.' in s and s.split('.')[1] else s
            examples.append(s)
        for s in examples:
            x=RA.from_cnrs_string(s); canon=x.to_cnrs_string()
            self.assertEqual(eval_string(s),eval_string(canon))
            self.assertEqual(RA.from_cnrs_string(canon),x)
            self.assertFalse(canon.startswith('00'))
            self.assertFalse(canon.endswith('.'))
            if '.' in canon:self.assertNotEqual(canon[-1],'0')

    def test_powers_zeros_boundaries_and_errors(self):
        for k in (0,1,2,3,10,100,1024):
            self.assertEqual(RA.beta_inverse(k).to_cnrs_string(), '0.'+'0'*(k-1)+'1' if k else '1')
        self.assertEqual(RA().to_cnrs_string(),'0')
        self.assertEqual(HurwitzJet.from_coefficients().to_cnrs_coefficients(),('0',))
        for invalid in ('', '.', '-1','+1','1e3','1..0','1.3.4','5','8', '1\n', ' 1'):
            with self.assertRaises(ValueError): RA.from_cnrs_string(invalid)
        for raw in (1,1.0,complex(1),True, None):
            with self.assertRaises(TypeError): RA.from_cnrs_string(raw)
        for k in (0,-1,1.0,True):
            with self.assertRaises(ValueError):RA(1).to_cnrs_string(max_digits=k)
        with self.assertRaises(ValueError):RA(100000).to_cnrs_string(max_digits=1)
        with self.assertRaises(ValueError):RA.beta_inverse(4096).to_cnrs_string()
        for bad in (((1,2.0),(2,3)),((True,0),(1,2)),((1,), (2,3))):
            with self.assertRaises(TypeError): gadd(*bad)
            with self.assertRaises(TypeError): gmul(*bad)

    def test_nested_hurwitz_codecs(self):
        rng=random.Random(202611073)
        for _ in range(1000):
            a=HurwitzJet(tuple(source_random(rng) for _ in range(1+rng.randrange(8))))
            strings=a.to_cnrs_coefficients()
            self.assertEqual(HurwitzJet.from_cnrs_coefficients(strings),a)
            self.assertTrue(all(RA.from_cnrs_string(s).to_cnrs_string()==s for s in strings))
        for bad in (3, 3.0, None,True,'123'):
            with self.assertRaises(TypeError):HurwitzJet.from_cnrs_coefficients(bad)
        with self.assertRaises(ValueError):HurwitzJet.from_cnrs_coefficients(['1','5'])

    def test_toolkit_strict_exact_finite_value(self):
        rng=random.Random(202611074)
        for _ in range(2000):
            a=source_random(rng);s=a.to_cnrs_string()
            g=cnrs_string_value_exact(s)
            u,v=g.numerator;w,z=g.denominator
            got=div((Fraction(u),Fraction(v)),(Fraction(w),Fraction(z)))
            self.assertEqual(got,val(a))

    def test_toolkit_add_multiply_contract(self):
        ops=ToolkitDigitOps(add_cnrs, mul_cnrs)
        rng=random.Random(202611075)
        for _ in range(1250):
            a,b=source_random(rng),source_random(rng)
            self.assertEqual(ops.add_checked(a,b),a+b)
            self.assertEqual(ops.multiply_checked(a,b),a*b)
        self.assertEqual(len(ADDITION_TABLE),350)

    def test_native_digit_hurwitz_bounded(self):
        ops=ToolkitDigitOps(add_cnrs,mul_cnrs,max_jet_degree=8)
        rng=random.Random(202611076)
        for _ in range(70):
            a=HurwitzJet(tuple(source_random(rng) for _ in range(rng.randrange(1,5))))
            b=HurwitzJet(tuple(source_random(rng) for _ in range(rng.randrange(1,5))))
            n=rng.randrange(0,5)
            self.assertEqual(ops.hurwitz_product_checked(a,b,n), a.product(b,through_degree=n))
        with self.assertRaises(ValueError):ops.hurwitz_product_checked(a,b,9)

    def test_negative_controls_wrong_toolkit_operations(self):
        bad=ToolkitDigitOps(lambda a,b:'0',mul_cnrs)
        with self.assertRaises(InteropMismatch):bad.add_checked(RA(1),RA(2))
        bad2=ToolkitDigitOps(add_cnrs,lambda a,b:'0')
        with self.assertRaises(InteropMismatch):bad2.multiply_checked(RA(2),RA(3))
        # A generic field inverse is not a valid R_A coefficient inverse.
        for r in (RA(2),RA(-2,-1),RA(3)):
            with self.assertRaises(ValueError):r.inverse_unit()

if __name__=='__main__':
    unittest.main(verbosity=2)
