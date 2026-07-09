import pytest

from cnrs.cnrs_division_status import DivisionKind, classify_division
from cnrs.division import DivisionStatus, classify_denominator


STATUS_MAP = {
    DivisionStatus.GAUSSIAN_INTEGER: DivisionKind.GAUSSIAN_INTEGER,
    DivisionStatus.TERMINATING_BASE_POWER: DivisionKind.TERMINATING_Z0_POWER,
    DivisionStatus.PERIODIC_COPRIME_DENOMINATOR: DivisionKind.EVENTUALLY_PERIODIC,
    DivisionStatus.SHIFTED_PERIODIC_TAIL: DivisionKind.SHIFTED_EVENTUALLY_PERIODIC,
}


@pytest.mark.parametrize(
    "numerator,denominator",
    [
        (6 + 4j, 2),
        (1, 3),
        (1, 5),
        (1, 10),
        (1, 25),
        (-2 - 1j, 5),
        ((-2 - 1j) ** 2, 25),
        (2 + 1j, 15),
        (12 + 6j, 6),
        (1, -5),
        (5, 25),
    ],
)
def test_legacy_and_authoritative_classifiers_agree(numerator, denominator):
    current = classify_denominator(numerator, denominator)
    with pytest.warns(DeprecationWarning):
        legacy = classify_division(numerator, denominator)

    assert legacy.kind == STATUS_MAP[current.status]
    assert legacy.terminates == current.terminates
    assert legacy.has_periodic_tail == current.has_periodic_tail
    assert legacy.reduced_denominator == current.reduced_denominator
    assert legacy.z0_power_shift == current.base_power_exponent
