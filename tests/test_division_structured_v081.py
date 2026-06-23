from cnrs.division import DivisionStatus, division_summary, expand_division


def test_division_summary_gaussian_integer():
    summary = division_summary(6, 3)
    assert summary["status"] == DivisionStatus.GAUSSIAN_INTEGER.value
    assert summary["terminates"] is True
    assert summary["round_trip_ok"] is True


def test_division_summary_periodic_has_structured_tail():
    result = expand_division(1, 2, max_frac=200)
    data = result.structured_digits()
    assert result.status == DivisionStatus.PERIODIC_COPRIME_DENOMINATOR
    assert data["terminates"] is False
    assert data["period_digits"]
    assert data["period_length"] == len(data["period_digits"])
    assert data["tail_kind"] == "eventually_periodic"


def test_division_summary_shifted_periodic():
    # 10 = 5 * 2: a finite base-power shift plus persistent coprime denominator.
    result = expand_division(1, 10, max_frac=200)
    assert result.status == DivisionStatus.SHIFTED_PERIODIC_TAIL
    assert result.shifted_by_base_power
    assert result.persistent_denominator == 2
    assert result.tail_kind == "shifted_eventually_periodic"
