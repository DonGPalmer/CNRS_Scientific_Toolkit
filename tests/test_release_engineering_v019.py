"""Active version consistency and actual v0.19 distribution integrity guards."""
import ast
import hashlib
import importlib.util
from pathlib import Path
import re

import pytest
import cnrs

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("v019_release_assets", ROOT / "tools/check_release_assets.py")
assert _SPEC is not None and _SPEC.loader is not None
_GUARD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_GUARD)


def test_active_version_consistency():
    """Prevent packaging, runtime, citation and reproducible builder divergence."""
    package = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(), re.M)
    citation = re.search(r'^version: "([^"]+)"', (ROOT / "CITATION.cff").read_text(), re.M)
    builder = ast.parse((ROOT / "tools/build_reproducible_distributions.py").read_text())
    version = next(ast.literal_eval(node.value) for node in builder.body
                   if isinstance(node, ast.Assign) and
                   any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets))
    assert package is not None and citation is not None
    assert cnrs.__version__ == package.group(1) == citation.group(1) == version == "0.19.0"


@pytest.mark.parametrize("damage", [None, "wheel_bytes", "sdist_bytes", "inventory", "missing", "old_tag"])
def test_v019_asset_integrity_contract(tmp_path, damage):
    names = _GUARD.expected_assets("0.19.0")
    assert names == ("cnrs-0.19.0-py3-none-any.whl", "cnrs-0.19.0.tar.gz")
    for name in names:
        (tmp_path / name).write_bytes(("payload:" + name).encode())
    sums = "".join(hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() + "  " + name + "\n"
                   for name in names)
    (tmp_path / "SHA256SUMS.txt").write_text(sums)
    if damage == "wheel_bytes":
        (tmp_path / names[0]).write_bytes(b"changed wheel")
    elif damage == "sdist_bytes":
        (tmp_path / names[1]).write_bytes(b"changed sdist")
    elif damage == "inventory":
        (tmp_path / "SHA256SUMS.txt").write_text(sums + "unexpected extra entry\n")
    elif damage == "missing":
        (tmp_path / names[1]).unlink()
    tag = "v0.18.0" if damage == "old_tag" else "v0.19.0"
    if damage is None:
        assert set(_GUARD.validate("0.19.0", tag, tmp_path)) == set(names)
    else:
        with pytest.raises((ValueError, FileNotFoundError)):
            _GUARD.validate("0.19.0", tag, tmp_path)
