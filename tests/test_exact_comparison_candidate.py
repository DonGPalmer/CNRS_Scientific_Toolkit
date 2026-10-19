"""Independent value-oracle tests for additive exact comparison interfaces."""
from fractions import Fraction
from itertools import product
import pytest
import cnrs
from cnrs.cnrs_ops import cnrs_eq, cnrs_eq_exact
from cnrs.cnrs_value import CVal
from cnrs.finite_string import cnrs_string_value_exact
from cnrs.gaussian_types import GaussianRational
from cnrs.validation.exact_addition_subtraction_oracle import exact_string_value


def fractions(value):
    a, b = value.numerator
    c, d = value.denominator
    return Fraction(a*c+b*d, c*c+d*d), Fraction(b*c-a*d, c*c+d*d)


@pytest.mark.parametrize('s', ['0', '.0', '001.000', '1.', '.1', '23.1', '144', '0.004'])
def test_exact_value_agrees_with_independent_oracle(s):
    value = cnrs_string_value_exact(s)
    assert isinstance(value, GaussianRational)
    assert fractions(value) == exact_string_value(s)
    assert CVal(s).to_gaussian_exact() == value


def test_large_values_not_merged_by_rounding():
    a = '1' + '0'*80
    b = a[:-1] + '1'
    assert cnrs_eq(a, b)  # Known legacy rounding collision remains compatible.
    assert not cnrs_eq_exact(a, b)
    assert not CVal(a).equals_exact(CVal(b))
    assert fractions(cnrs_string_value_exact(b)) == exact_string_value(b)


def test_nonzero_fraction_does_not_underflow():
    s = '0.' + '0'*1000 + '1'
    assert CVal(s).to_gaussian() == 0
    assert not cnrs_eq_exact(s, '0')
    assert fractions(cnrs_string_value_exact(s)) == exact_string_value(s)


def test_overflow_sized_values_and_spelling_equivalence():
    s = '1' + '0'*1100
    assert cnrs_eq_exact(s, '00' + s + '.000')
    assert cnrs_string_value_exact(s).numerator != (0, 0)


def test_short_domain_matches_oracle_for_every_pair():
    strings = []
    for n in (1, 2):
        for ds in product('01234', repeat=n):
            s = ''.join(ds)
            strings.append(s)
            strings.extend(s[:i]+'.'+s[i:] for i in range(n+1))
    values = {s: exact_string_value(s) for s in strings}
    exact = {s: cnrs_string_value_exact(s) for s in strings}
    assert len(strings) == 115
    for a, b in product(strings, repeat=2):
        assert (exact[a] == exact[b]) == (values[a] == values[b])
    for a in strings:
        assert cnrs_eq_exact(a, '00'+a)


@pytest.mark.parametrize('s', ['', '.', '5', '-1', ' 1', '1 ', '1..0', '1e2'])
def test_strict_malformed_input(s):
    with pytest.raises(ValueError): cnrs_string_value_exact(s)
    with pytest.raises(ValueError): cnrs_eq_exact('0', s)
    with pytest.raises(ValueError): CVal(s).equals_exact(CVal('0'))


@pytest.mark.parametrize('s', [None, True, 1, 1.0, b'1'])
def test_strict_input_types(s):
    with pytest.raises(TypeError): cnrs_string_value_exact(s)
    with pytest.raises(TypeError): cnrs_eq_exact(s, '0')


def test_exact_str_subclasses_are_rejected():
    class Text(str): pass
    with pytest.raises(TypeError): cnrs_string_value_exact(Text('1'))


def test_public_imports_and_other_type_policy():
    from cnrs.core import cnrs_eq_exact as core_equal
    assert cnrs.cnrs_eq_exact is core_equal is cnrs_eq_exact
    assert cnrs.cnrs_string_value_exact is cnrs_string_value_exact
    assert CVal('.1').to_gaussian_exact() == GaussianRational(1, (-2, 1))
    assert CVal('.1').equals_exact(CVal('00.100'))
    with pytest.raises(TypeError): CVal('1').equals_exact('1')
    assert CVal.__eq__(CVal('1'), '1') is NotImplemented
