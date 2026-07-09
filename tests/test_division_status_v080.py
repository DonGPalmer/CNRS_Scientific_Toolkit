import pytest

from cnrs.cnrs_division_status import (
    DivisionKind,
    classify_division,
    division_expansion,
)


def legacy_classify(numerator, denominator=1):
    with pytest.warns(DeprecationWarning):
        return classify_division(numerator, denominator)


def test_classify_gaussian_integer():
    c = legacy_classify(6 + 4j, 2)
    assert c.kind == DivisionKind.GAUSSIAN_INTEGER
    assert c.terminates
    assert c.reduced_denominator == 1


def test_classify_eventually_periodic():
    c = legacy_classify(1, 3)
    assert c.kind == DivisionKind.EVENTUALLY_PERIODIC
    assert c.has_periodic_tail


def test_classify_shifted_periodic():
    c = legacy_classify(1, 10)
    assert c.kind == DivisionKind.SHIFTED_EVENTUALLY_PERIODIC
    assert c.has_periodic_tail
    assert c.z0_power_shift == 1


def test_division_expansion_wraps_rational():
    with pytest.warns(DeprecationWarning):
        e = division_expansion(1, 3, max_frac=50)
    assert e.classification.kind == DivisionKind.EVENTUALLY_PERIODIC
    assert e.period_length is not None
    assert e.period


def test_one_over_five_is_shifted_periodic():
    c = legacy_classify(1, 5)
    assert c.kind == DivisionKind.SHIFTED_EVENTUALLY_PERIODIC
    assert not c.terminates
    assert c.z0_power_shift == 1


def test_one_over_twenty_five_is_shifted_periodic():
    c = legacy_classify(1, 25)
    assert c.kind == DivisionKind.SHIFTED_EVENTUALLY_PERIODIC
    assert not c.terminates
    assert c.z0_power_shift == 2


def test_conjugate_factor_cancellation_terminates():
    # beta_bar = -2-i and beta_bar/5 = 1/beta.
    c = legacy_classify(-2 - 1j, 5)
    assert c.kind == DivisionKind.TERMINATING_Z0_POWER
    assert c.terminates
    assert c.z0_power_shift == 1


def test_second_conjugate_factor_cancellation_terminates():
    # beta_bar**2 / 25 = 1 / beta**2.
    beta_bar_sq = (-2 - 1j) ** 2
    c = legacy_classify(beta_bar_sq, 25)
    assert c.kind == DivisionKind.TERMINATING_Z0_POWER
    assert c.terminates
    assert c.z0_power_shift == 2
