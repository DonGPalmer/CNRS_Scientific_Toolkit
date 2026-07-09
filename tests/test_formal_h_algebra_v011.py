from fractions import Fraction
from cnrs.formal_h_algebra import hurwitz_product, derivative, integral, multiplicative_inverse, exponential_eigenfunction

def test_leibniz_exact():
    a=(Fraction(1),Fraction(2),Fraction(3),Fraction(4)); b=(Fraction(2),Fraction(-1),Fraction(5))
    lhs=derivative(hurwitz_product(a,b))
    rhs=tuple(x+y for x,y in zip(hurwitz_product(derivative(a),b,order=len(lhs)),hurwitz_product(a,derivative(b),order=len(lhs))))
    assert lhs==rhs

def test_integral_right_inverse():
    a=(1,4,1,5,9)
    assert derivative(integral(a))==a

def test_inverse_product_identity():
    a=(Fraction(2),Fraction(3),Fraction(-1),Fraction(4))
    inv=multiplicative_inverse(a,8)
    p=hurwitz_product(a,inv,order=8)
    assert p[0]==1 and all(x==0 for x in p[1:])

def test_exponential_law():
    ea=exponential_eigenfunction(Fraction(2),8); eb=exponential_eigenfunction(Fraction(3),8)
    assert hurwitz_product(ea,eb,order=8)==exponential_eigenfunction(Fraction(5),8)
