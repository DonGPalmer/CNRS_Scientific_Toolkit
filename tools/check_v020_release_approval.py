#!/usr/bin/env python3
"""Fail-closed release identity gate for CNRS Toolkit v0.20.0.

The trusted manifest and SHA-256 digest must be supplied independently through
the separately approved publication environment. This tool verifies identities;
it cannot itself establish that the author approved publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

VERSION = "0.20.0"
TAG = "v0.20.0"
ASSETS = ("cnrs-0.20.0-py3-none-any.whl", "cnrs-0.20.0.tar.gz")
REQUIRED_KEYS = {"schema", "version", "tag", "commit", "tree", "assets", "approval_record"}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate manifest key: " + key)
        result[key] = value
    return result


def _is_hex(value, n):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{%d}" % n, value) is not None


def load_approval(path: Path, trusted_sha256: str) -> dict:
    """Only the separately recorded manifest hash is trusted, not a build output."""
    if not _is_hex(trusted_sha256, 64):
        raise ValueError("separately approved manifest SHA256 is required")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != trusted_sha256:
        raise ValueError("manifest bytes differ from separately approved digest")
    data = json.loads(raw, object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or set(data) != REQUIRED_KEYS:
        raise ValueError("incorrect approval manifest schema")
    if (type(data["schema"]) is not int or data["schema"] != 1
            or data["version"] != VERSION or data["tag"] != TAG):
        raise ValueError("incorrect approval version or tag")
    if not _is_hex(data["commit"], 40) or not _is_hex(data["tree"], 40):
        raise ValueError("invalid full commit/tree SHA1 identity")
    approval_record = data["approval_record"]
    if not isinstance(approval_record, str) or not approval_record.strip():
        raise ValueError("a durable author publication approval record is required")
    assets = data["assets"]
    if (not isinstance(assets, dict) or set(assets) != set(ASSETS)
            or not all(_is_hex(assets[name], 64) for name in ASSETS)):
        raise ValueError("exactly two approved asset SHA256 identities are required")
    return data


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def verify_source(repo: Path, approval: dict) -> None:
    """The published tag must peel to the approved checked-out commit/tree."""
    if _git(repo, "rev-parse", "--verify", "HEAD") != approval["commit"]:
        raise ValueError("HEAD differs from approved commit")
    if _git(repo, "rev-parse", "--verify", "HEAD^{tree}") != approval["tree"]:
        raise ValueError("source tree differs from approved tree")
    if _git(repo, "rev-parse", "--verify", "refs/tags/" + TAG + "^{commit}") != approval["commit"]:
        raise ValueError("release tag differs from approved commit")
    if _git(repo, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("tracked source differs from approved checkout")


def verify_assets(directory: Path, approval: dict) -> None:
    """Verify the wheel and sdist independently of the builder's own inventory."""
    for name in ASSETS:
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if actual != approval["assets"][name]:
            raise ValueError("asset bytes differ from approved SHA256: " + name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--approved-sha256", required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--directory", type=Path)
    args = parser.parse_args()
    approval = load_approval(args.manifest, args.approved_sha256)
    verify_source(args.repo, approval)
    if args.directory is not None:
        verify_assets(args.directory, approval)
    print("Approved v0.20.0 source" + (" and assets" if args.directory else "") + " verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
