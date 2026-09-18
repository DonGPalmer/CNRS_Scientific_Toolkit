from pathlib import Path

import pytest

from tools.check_release_assets import expected_assets, validate


def test_expected_v017_assets() -> None:
    assert expected_assets("0.17.0") == (
        "cnrs-0.17.0-py3-none-any.whl",
        "cnrs-0.17.0.tar.gz",
    )


def test_v017_release_asset_guard(tmp_path: Path) -> None:
    names = expected_assets("0.17.0")
    for index, name in enumerate(names):
        (tmp_path / name).write_bytes(f"asset-{index}".encode())
    import hashlib

    sums = "".join(
        f"{hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()}  {name}\n"
        for name in names
    )
    (tmp_path / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    assert set(validate("0.17.0", "v0.17.0", tmp_path)) == set(names)


def test_v017_release_asset_guard_rejects_wrong_tag(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not match"):
        validate("0.17.0", "v0.16.0", tmp_path)
