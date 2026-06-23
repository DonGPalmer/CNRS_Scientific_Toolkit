from cnrs.division import (
    DivisionStatus,
    classify_denominator,
    expand_division,
    terminating_expansion,
    periodic_expansion,
)


def test_gaussian_integer_status():
    c = classify_denominator(6 + 2j, 2)
    assert c.status == DivisionStatus.GAUSSIAN_INTEGER
    assert c.reduced_denominator == 1
    assert c.terminates


def test_terminating_base_power_status():
    c = classify_denominator(1, 5)
    assert c.status == DivisionStatus.TERMINATING_BASE_POWER
    assert c.base_power_exponent == 1
    assert c.persistent_denominator == 1
    assert c.terminates


def test_periodic_coprime_status():
    c = classify_denominator(1, 2)
    assert c.status == DivisionStatus.PERIODIC_COPRIME_DENOMINATOR
    assert c.has_periodic_tail


def test_shifted_periodic_tail_status():
    c = classify_denominator(1, 10)
    assert c.status == DivisionStatus.SHIFTED_PERIODIC_TAIL
    assert c.base_power_exponent == 1
    assert c.persistent_denominator == 2
    assert c.has_periodic_tail


def test_expand_division_terminating_round_trip():
    r = expand_division(1, 5, max_frac=200)
    assert r.terminates
    assert r.round_trip_ok()


def test_expand_division_periodic_round_trip():
    r = expand_division(1, 2, max_frac=200)
    assert r.status == DivisionStatus.PERIODIC_COPRIME_DENOMINATOR
    assert r.period_length is not None
    assert r.round_trip_ok()


def test_helper_rejects_wrong_kind():
    terminating_expansion(1, 5)
    periodic_expansion(1, 2)
    try:
        terminating_expansion(1, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("expected periodic denominator to reject terminating_expansion")
