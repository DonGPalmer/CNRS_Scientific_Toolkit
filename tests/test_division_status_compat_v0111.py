"""Regression tests for the deprecated v0.8.x division-status compatibility API."""
import pytest

from cnrs.cnrs_division_status import DivisionKind, classify_division


def classify(numerator, denominator):
    with pytest.warns(DeprecationWarning):
        return classify_division(numerator, denominator)


def test_one_over_five_is_shifted_periodic():
    c = classify(1, 5)
    assert c.kind == DivisionKind.SHIFTED_EVENTUALLY_PERIODIC
    assert not c.terminates
    assert c.z0_power_shift == 1


def test_one_over_twenty_five_is_shifted_periodic():
    c = classify(1, 25)
    assert c.kind == DivisionKind.SHIFTED_EVENTUALLY_PERIODIC
    assert not c.terminates
    assert c.z0_power_shift == 2


def test_conjugate_factor_cancellation_terminates():
    c = classify(-2 - 1j, 5)
    assert c.kind == DivisionKind.TERMINATING_Z0_POWER
    assert c.terminates


def test_second_conjugate_factor_cancellation_terminates():
    c = classify((-2 - 1j) ** 2, 25)
    assert c.kind == DivisionKind.TERMINATING_Z0_POWER
    assert c.terminates
