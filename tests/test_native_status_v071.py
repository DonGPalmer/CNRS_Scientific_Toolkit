"""v0.9.0 native-status and internal-consistency tests."""


def test_native_status_registry_classifies_core_components():
    from cnrs.native_status import NativeStatus, get_component, native_components

    base = get_component("CNRS base and digit alphabet")
    assert base.status == NativeStatus.NATIVE_CORE
    assert base.is_native

    chain = get_component("CNRS-H chain rule")
    assert chain.status == NativeStatus.NATIVE_FINITE
    assert chain.is_native

    names = {item.name for item in native_components()}
    assert "CNRS-H calculus" in names
    assert "CNRS scientific state" in names


def test_support_layers_are_not_marked_native():
    from cnrs.native_status import NativeStatus, get_component

    assert get_component("Autodiff reference").status == NativeStatus.VALIDATION
    assert not get_component("Autodiff reference").is_native
    assert get_component("Symbolic expressions").status == NativeStatus.BRIDGE
    assert not get_component("Symbolic expressions").is_native
    assert get_component("CNRS-H Taylor-model metadata").status == NativeStatus.SCAFFOLD


def test_status_table_renders_markdown():
    from cnrs.native_status import by_status, status_table, NativeStatus

    table = status_table(by_status(NativeStatus.NATIVE_CORE))
    assert "| Component | Module | Status | Layer | Claim |" in table
    assert "cnrs.core.base" in table
    assert "native_core" in table


def test_native_status_exported_from_flat_package():
    import cnrs
    from cnrs import NativeStatus, get_component_status

    assert cnrs.__version__ == "0.12.1"
    assert NativeStatus.NATIVE_CORE.value == "native_core"
    assert get_component_status("CNRS-H calculus").is_native


def test_science_facade_is_documented_as_native_local():
    from cnrs.native_status import get_component
    from cnrs.science import CnrsScientificState

    status = get_component("CNRS scientific state")
    assert status.is_native
    assert status.module == "cnrs.science.state"
    assert CnrsScientificState is not None
