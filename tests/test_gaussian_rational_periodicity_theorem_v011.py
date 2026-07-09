"""Regression tests for the Gaussian-rational periodicity theorem integration."""

from cnrs.division import DivisionStatus, classify_denominator, expand_division


def test_one_fifth_requires_shifted_periodic_tail():
    result = expand_division(1, 5, max_frac=500)
    assert result.status == DivisionStatus.SHIFTED_PERIODIC_TAIL
    assert result.expansion.power_offset == -1
    assert result.period_length is not None
    assert result.round_trip_ok(tol=1e-13)


def test_conjugate_base_factor_cancellation_terminates():
    # (-2-i)/5 = 1/(-2+i) = z0^{-1}.
    result = expand_division((-2, -1), 5, max_frac=100)
    assert result.status == DivisionStatus.TERMINATING_BASE_POWER
    assert result.terminates
    assert result.expansion.period_start is None
    assert result.round_trip_ok(tol=1e-13)


def test_higher_power_cancellation_criterion():
    # conjugate(z0)^2 / 25 = z0^{-2}.
    # (-2-i)^2 = 3+4i.
    terminating = classify_denominator((3, 4), 25)
    nonterminating = classify_denominator(1, 25)
    assert terminating.status == DivisionStatus.TERMINATING_BASE_POWER
    assert nonterminating.status == DivisionStatus.SHIFTED_PERIODIC_TAIL
