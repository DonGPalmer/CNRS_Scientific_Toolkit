"""Approval identity controls, including regenerated-checksum and real Git cases."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("approval", ROOT / "tools/check_v019_release_approval.py")
approval = importlib.util.module_from_spec(spec)
spec.loader.exec_module(approval)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def release(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()
    git("init", "-q")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Release control test")
    (repo / "source.txt").write_text("approved source")
    git("add", "source.txt")
    git("commit", "-qm", "approved source")
    git("tag", "-a", "v0.19.0", "-m", "test-only tag")
    dist = tmp_path / "dist"
    dist.mkdir()
    for name in approval.ASSETS:
        (dist / name).write_bytes(("approved:" + name).encode())
    data = {"schema": 1, "version": "0.19.0", "tag": "v0.19.0",
            "commit": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
            "assets": {n: digest((dist / n).read_bytes()) for n in approval.ASSETS},
            "approval_record": "TEST ONLY — no release approval"}
    return repo, dist, data, git


@pytest.mark.parametrize("damage", [None, "version", "tag", "commit_format", "tree_format",
                                  "asset_set", "asset_hash", "approval", "schema", "extra", "digest", "missing_digest", "duplicate"])
def test_manifest_trust_and_schema(release, tmp_path, damage):
    _, _, data, _ = release
    data = copy.deepcopy(data)
    if damage == "version": data["version"] = "0.18.0"
    if damage == "tag": data["tag"] = "v0.18.0"
    if damage == "commit_format": data["commit"] = "abc"
    if damage == "tree_format": data["tree"] = "x" * 40
    if damage == "asset_set": data["assets"]["extra.whl"] = "a" * 64
    if damage == "asset_hash": data["assets"][approval.ASSETS[0]] = "bad"
    if damage == "approval": data["approval_record"] = " "
    if damage == "schema": data["schema"] = True
    if damage == "extra": data["untrusted"] = True
    raw = json.dumps(data).encode()
    if damage == "duplicate": raw = raw[:-1] + b', "version": "0.19.0"}'
    path = tmp_path / "manifest.json"
    path.write_bytes(raw)
    trusted = digest(raw)
    if damage == "digest": trusted = "0" * 64
    if damage == "missing_digest": trusted = ""
    if damage is None:
        assert approval.load_approval(path, trusted) == data
    else:
        with pytest.raises(ValueError): approval.load_approval(path, trusted)


@pytest.mark.parametrize("damage", [None, "commit", "tree", "tag", "missing_tag", "dirty_source", "wheel", "sdist", "missing_asset"])
def test_approved_source_and_bytes(release, damage):
    repo, dist, data, git = release
    if damage == "commit":
        # Same source tree/version, different commit: checkout/tag agreement alone
        # would pass, but the separately approved commit must still be enforced.
        git("commit", "--allow-empty", "-qm", "unapproved commit")
        git("tag", "-f", "v0.19.0")
    if damage == "tree": data["tree"] = "0" * 40
    if damage == "tag": git("tag", "-f", "v0.19.0", "HEAD^{tree}")
    if damage == "missing_tag": git("tag", "-d", "v0.19.0")
    if damage == "dirty_source": (repo / "source.txt").write_text("unapproved")
    if damage in ("wheel", "sdist"):
        name = approval.ASSETS[damage == "sdist"]
        (dist / name).write_bytes(b"unapproved build bytes")
        # Recomputing the local checksum file cannot change approval.
        (dist / "SHA256SUMS.txt").write_text("".join(digest((dist / n).read_bytes()) + "  " + n + "\n" for n in approval.ASSETS))
    if damage == "missing_asset": (dist / approval.ASSETS[0]).unlink()
    def check():
        approval.verify_source(repo, data)
        approval.verify_assets(dist, data)
    if damage is None:
        check()
    else:
        with pytest.raises((ValueError, FileNotFoundError, subprocess.CalledProcessError)): check()


def test_manifest_edit_cannot_replace_approval(release, tmp_path):
    _, _, data, _ = release
    raw = json.dumps(data).encode()
    trusted = digest(raw)
    data["assets"][approval.ASSETS[0]] = "0" * 64
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="approved SHA256"):
        approval.load_approval(path, trusted)
