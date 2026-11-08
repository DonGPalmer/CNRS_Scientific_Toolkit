#!/usr/bin/env python3
"""Offline, non-publishing rehearsal of the v0.20 identity and asset gate.

Only creates a synthetic git tag inside a temporary repository. There are no
network requests, GitHub release actions, environment writes, or source tags.
The real author-approved release manifest must never be fabricated here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from tools.check_v020_release_approval import (
    ASSETS, TAG, load_approval, verify_source, verify_assets,
)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def rehearse(directory: Path) -> None:
    for name in ASSETS:
        if not (directory / name).is_file():
            raise FileNotFoundError(directory / name)
    with tempfile.TemporaryDirectory(prefix="cnrs-v020-offline-rehearsal-") as tmp:
        tmpdir = Path(tmp)
        repo = tmpdir / "synthetic-repository"
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "Synthetic Gate Test")
        git(repo, "config", "user.email", "synthetic@example.invalid")
        (repo / "synthetic.txt").write_text("REHEARSAL ONLY\n", encoding="utf-8")
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "synthetic-only")
        git(repo, "tag", TAG)
        manifest = {
            "schema": 1, "version": "0.20.0", "tag": TAG,
            "commit": git(repo, "rev-parse", "HEAD"),
            "tree": git(repo, "rev-parse", "HEAD^{tree}"),
            "assets": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                       for name in ASSETS},
            "approval_record": "SYNTHETIC OFFLINE REHEARSAL — NOT AUTHOR APPROVAL",
        }
        raw = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
        manifest_file = tmpdir / "synthetic-only.json"
        manifest_file.write_bytes(raw)
        trusted_digest = hashlib.sha256(raw).hexdigest()

        positive = load_approval(manifest_file, trusted_digest)
        verify_source(repo, positive)
        verify_assets(directory, positive)

        # These must fail closed. Synthetic positive checks do not create trust.
        rejected = 0
        for bad in ("", "0" * 64):
            try:
                load_approval(manifest_file, bad)
            except ValueError:
                rejected += 1
        tamper = tmpdir / "altered"
        tamper.mkdir()
        for name in ASSETS:
            shutil.copyfile(directory / name, tamper / name)
        (tamper / ASSETS[0]).write_bytes((tamper / ASSETS[0]).read_bytes() + b"x")
        try:
            verify_assets(tamper, positive)
        except ValueError:
            rejected += 1
        try:
            verify_source(repo, {**positive, "commit": "a" * 40})
        except ValueError:
            rejected += 1
        if rejected != 4:
            raise AssertionError(f"expected four negative-control rejections, got {rejected}")
    print("OFFLINE REHEARSAL PASS: positive source/assets and 4 negative gates")
    print("NO RELEASE, NO LIVE TAG, NO ENVIRONMENT WRITE, NO PUBLICATION")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("dist"))
    args = parser.parse_args()
    rehearse(args.directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
