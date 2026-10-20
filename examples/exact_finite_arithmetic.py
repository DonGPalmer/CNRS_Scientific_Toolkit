"""Run from a checkout with cnrs installed: python examples/exact_finite_arithmetic.py."""
from fractions import Fraction
from cnrs import (
    CVal, GaussianRational, add_cnrs, cnrs_eq_exact, cnrs_neg, cnrs_sub,
    cnrs_string_value_exact, divide_cnrs_exact, validate_division_witness,
)


def main():
    assert add_cnrs('23.1', '4.3') == '1332.4'
    assert cnrs_neg('.1') == '14.4'
    assert cnrs_sub('23.1', '4.3') == '33.3'
    assert cnrs_string_value_exact('.1') == GaussianRational(1, (-2, 1))
    assert CVal('.1').equals_exact(CVal('00.100'))
    a = '1' + '0'*80
    assert not cnrs_eq_exact(a, a[:-1]+'1')
    result = divide_cnrs_exact('1', '2')
    assert result.exact_value_fractions() == (Fraction(1, 2), Fraction(0))
    witness = result.to_witness()
    assert validate_division_witness(witness) == witness
    print('PASS: finite arithmetic, exact comparison, periodic division and witness validation')


if __name__ == '__main__':
    main()
