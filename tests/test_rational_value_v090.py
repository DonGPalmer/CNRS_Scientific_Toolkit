from fractions import Fraction
import pytest

from cnrs.rational_value import CnrsRationalValue, rational_value, rational_batch
from cnrs.division import DivisionStatus
from cnrs.cnrs_value import CVal


def test_integer_rational_value_collapses_to_cval():
    x = rational_value(7, 1, label="seven")
    assert x.status == DivisionStatus.GAUSSIAN_INTEGER
    assert x.is_finite
    cv = x.finite_cval()
    assert isinstance(cv, CVal)
    assert cv.to_gaussian() == 7 + 0j
    assert x.structured_report()["label"] == "seven"


def test_base_power_denominator_has_terminating_fractional_expansion():
    x = rational_value(1, 5)
    assert x.status == DivisionStatus.TERMINATING_BASE_POWER
    assert x.is_finite
    assert not x.has_periodic_tail
    assert abs(x.exact_value() - (0.2 + 0j)) < 1e-12
    # It terminates as a fractional/base-power expansion, not as a Gaussian-integer CVal.
    with pytest.raises(ValueError):
        x.finite_cval()


def test_coprime_denominator_is_periodic_and_not_cval():
    x = rational_value(1, 2, max_frac=50)
    assert x.status == DivisionStatus.PERIODIC_COPRIME_DENOMINATOR
    assert not x.is_finite
    assert x.has_periodic_tail
    assert x.period_length is not None
    with pytest.raises(ValueError):
        x.finite_cval()


def test_shifted_periodic_denominator_is_explicit():
    x = rational_value(1, 10, max_frac=80)
    assert x.status == DivisionStatus.SHIFTED_PERIODIC_TAIL
    assert x.has_periodic_tail
    assert x.persistent_denominator == 2
    rep = x.structured_report()
    assert rep["status"] == "shifted_periodic_tail"
    assert rep["power_offset"] < 0


def test_exact_fraction_access_for_periodic_value():
    x = rational_value(1, 2, max_frac=50)
    re, im = x.exact_value_fractions()
    assert re == Fraction(1, 2)
    assert im == Fraction(0, 1)


def test_rational_batch_constructs_values():
    vals = rational_batch([(1, 1), (1, 2), (1, 5)])
    assert len(vals) == 3
    assert [v.status for v in vals] == [
        DivisionStatus.GAUSSIAN_INTEGER,
        DivisionStatus.PERIODIC_COPRIME_DENOMINATOR,
        DivisionStatus.TERMINATING_BASE_POWER,
    ]
