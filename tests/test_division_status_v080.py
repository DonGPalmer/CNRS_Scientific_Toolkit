from cnrs.cnrs_division_status import (
    DivisionKind,
    classify_division,
    division_expansion,
)


def test_classify_gaussian_integer():
    c = classify_division(6 + 4j, 2)
    assert c.kind == DivisionKind.GAUSSIAN_INTEGER
    assert c.terminates
    assert c.reduced_denominator == 1


def test_classify_eventually_periodic():
    c = classify_division(1, 3)
    assert c.kind == DivisionKind.EVENTUALLY_PERIODIC
    assert c.has_periodic_tail


def test_classify_shifted_periodic():
    c = classify_division(1, 10)
    assert c.kind == DivisionKind.SHIFTED_EVENTUALLY_PERIODIC
    assert c.has_periodic_tail
    assert c.z0_power_shift == 1


def test_division_expansion_wraps_rational():
    e = division_expansion(1, 3, max_frac=50)
    assert e.classification.kind == DivisionKind.EVENTUALLY_PERIODIC
    assert e.period_length is not None
    assert e.period


def test_classify_power_of_five_denominator():
    c = classify_division(1, 25)
    assert c.kind == DivisionKind.TERMINATING_Z0_POWER
    assert c.terminates
    assert c.z0_power_shift == 2
