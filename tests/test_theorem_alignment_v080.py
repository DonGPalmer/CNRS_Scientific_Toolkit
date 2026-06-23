from cnrs.native_status import get_component, NativeStatus


def test_native_status_contains_v080_components():
    assert get_component("CNRS-A native CVal").status == NativeStatus.NATIVE_CORE
    assert get_component("CNRS-A division classification").status == NativeStatus.NATIVE_FINITE
    assert get_component("CNRS-H native coefficients").status == NativeStatus.NATIVE_CORE
    assert get_component("CNRS* formal state").status == NativeStatus.NATIVE_LOCAL
