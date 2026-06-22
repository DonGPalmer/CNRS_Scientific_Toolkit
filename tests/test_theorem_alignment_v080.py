from cnrs.native_status import get_component
from cnrs import __version__


def test_version_is_080():
    assert __version__ == "0.8.0"


def test_native_registry_contains_new_v080_components():
    for name in [
        "CNRS-A native CVal",
        "CNRS-H native coefficient calculus",
        "CNRS-H native composition",
        "CNRS division classification",
        "CNRS formal state",
    ]:
        component = get_component(name)
        assert component.is_native


def test_composition_status_not_finite_state_claim():
    component = get_component("CNRS-H native composition")
    assert "not a fixed finite-state" in component.notes
