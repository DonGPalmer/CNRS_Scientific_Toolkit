"""Fail-closed negative controls for the v0.20.0 publication identity gate."""
import hashlib
import json
from pathlib import Path
import subprocess
import pytest

from tools.check_v020_release_approval import (
    ASSETS, TAG, load_approval, verify_assets, verify_source,
)


def _manifest(**changes):
    data = {
        "schema": 1, "version": "0.20.0", "tag": TAG,
        "commit": "a" * 40, "tree": "b" * 40,
        "assets": {ASSETS[0]: "c" * 64, ASSETS[1]: "d" * 64},
        "approval_record": "Author approval in governed SSC journal: test reference",
    }
    data.update(changes)
    return data


def _write(tmp_path, obj=None, raw=None):
    data = (json.dumps(_manifest() if obj is None else obj, sort_keys=True) + "\n").encode() if raw is None else raw
    path = tmp_path / "approved.json"
    path.write_bytes(data)
    return path, hashlib.sha256(data).hexdigest()


def test_valid_manifest_schema(tmp_path):
    path, digest = _write(tmp_path)
    assert load_approval(path, digest)["version"] == "0.20.0"


def test_untrusted_missing_or_altered_digest(tmp_path):
    path, digest = _write(tmp_path)
    for wrong in ("", "z" * 64, "0" * 64):
        with pytest.raises(ValueError):
            load_approval(path, wrong)
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError):
        load_approval(path, digest)


@pytest.mark.parametrize("field,value", [
    ("version", "0.19.0"), ("tag", "v0.19.0"), ("schema", True),
    ("commit", "bad"), ("tree", ""), ("approval_record", " "),
    ("assets", {"unapproved.zip": "c" * 64}),
])
def test_changed_fields_fail_closed(tmp_path, field, value):
    path, digest = _write(tmp_path, _manifest(**{field: value}))
    with pytest.raises(ValueError):
        load_approval(path, digest)


def test_duplicate_key_rejected(tmp_path):
    raw = b'{"schema":1,"schema":1,"version":"0.20.0"}'
    path, digest = _write(tmp_path, raw=raw)
    with pytest.raises(ValueError, match="duplicate"):
        load_approval(path, digest)


def test_asset_tampering_rejected_even_if_sidecar_changes(tmp_path):
    files = {ASSETS[0]: b"wheel", ASSETS[1]: b"sdist"}
    for name, value in files.items():
        (tmp_path / name).write_bytes(value)
    approved = _manifest(assets={name: hashlib.sha256(value).hexdigest()
                                 for name, value in files.items()})
    verify_assets(tmp_path, approved)
    (tmp_path / ASSETS[0]).write_bytes(b"changed")
    (tmp_path / "SHA256SUMS.txt").write_text("invented inventory\n")
    with pytest.raises(ValueError, match="asset bytes"):
        verify_assets(tmp_path, approved)


def _git(cwd, *args):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def test_source_tag_tree_and_cleanliness(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Publication Gate Test")
    (repo / "file.txt").write_text("governed\n")
    _git(repo, "add", "file.txt")
    _git(repo, "commit", "-qm", "test commit")
    _git(repo, "tag", TAG)
    commit = _git(repo, "rev-parse", "HEAD")
    tree = _git(repo, "rev-parse", "HEAD^{tree}")
    approval = _manifest(commit=commit, tree=tree)
    verify_source(repo, approval)
    with pytest.raises(ValueError, match="HEAD"):
        verify_source(repo, _manifest(commit="a" * 40, tree=tree))
    with pytest.raises(ValueError, match="tree"):
        verify_source(repo, _manifest(commit=commit, tree="b" * 40))
    (repo / "file.txt").write_text("changed tracked bytes\n")
    with pytest.raises(ValueError, match="tracked"):
        verify_source(repo, approval)
    (repo / "file.txt").write_text("governed\n")
    _git(repo, "tag", "-d", TAG)
    with pytest.raises((subprocess.CalledProcessError, ValueError)):
        verify_source(repo, approval)
