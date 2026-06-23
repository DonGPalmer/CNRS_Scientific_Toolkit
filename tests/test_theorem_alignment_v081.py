from cnrs.theorem_alignment import (
    TheoremStatus,
    all_theorem_records,
    by_status,
    get_theorem_record,
    theorem_alignment_table,
)


def test_theorem_alignment_registry_contains_v081_core_items():
    names = {record.name for record in all_theorem_records()}
    assert "Scoped addition normalisation" in names
    assert "General finite coefficient normalisation" in names
    assert "CNRS* formal state preservation" in names


def test_get_theorem_record_by_module():
    record = get_theorem_record("cnrs.normalization.normalize_general_coefficients")
    assert record.status == TheoremStatus.THEOREM_BACKED


def test_theorem_alignment_table_mentions_multiplication_scope():
    table = theorem_alignment_table(by_status(TheoremStatus.THEOREM_BACKED))
    assert "CNRS-A multiplication closure" in table
    assert "general normalisation" in table
