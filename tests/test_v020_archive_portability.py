"""Host-independent distribution normalization and source inventory checks."""
from __future__ import annotations

import io
import gzip
import subprocess
import tarfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from tools.build_reproducible_distributions import normalize_wheel, normalize_sdist

EPOCH = 1794153600
ROOT = Path(__file__).resolve().parents[1]


def test_wheel_bytes_do_not_depend_on_input_deflate_level(tmp_path):
    outputs = []
    for level in (1, 9):
        path = tmp_path / f"compression-{level}.whl"
        with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=level) as archive:
            archive.writestr("cnrs/__init__.py", b"data" * 75000)
            archive.writestr("cnrs-0.20.0.dist-info/METADATA", b"Version: 0.20.0\n")
        normalize_wheel(path, EPOCH)
        with ZipFile(path) as checked:
            assert checked.read("cnrs/__init__.py") == b"data" * 75000
            assert all(member.compress_type == 0 for member in checked.infolist())
        outputs.append(path.read_bytes())
    assert outputs[0] == outputs[1]


def test_sdist_bytes_do_not_depend_on_input_deflate_level(tmp_path):
    outputs = []
    payload = b"data" * 75000
    for level in (1, 9):
        path = tmp_path / f"compression-{level}.tar.gz"
        with tarfile.open(path, "w:gz", compresslevel=level) as archive:
            member = tarfile.TarInfo("cnrs-0.20.0/cnrs/module.py")
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))
        normalize_sdist(path, EPOCH)
        with gzip.open(path, "rb") as extracted:
            with tarfile.open(fileobj=io.BytesIO(extracted.read())) as checked:
                assert checked.extractfile("cnrs-0.20.0/cnrs/module.py").read() == payload
        outputs.append(path.read_bytes())
    assert outputs[0] == outputs[1]


def test_v020_source_index_matches_tracked_files():
    result = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True,
                            capture_output=True, check=True)
    actual = set(result.stdout.splitlines())
    lines = (ROOT / "SOURCE_INDEX.txt").read_text(encoding="utf-8").splitlines()
    listed = {line for line in lines if line and not line.startswith("#")}
    assert listed == actual
    assert sum(line == "SOURCE_INDEX.txt" for line in lines) == 1


def test_build_dependencies_are_pinned():
    contents = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires = ["setuptools==80.9.0", "wheel==0.45.1"]' in contents
