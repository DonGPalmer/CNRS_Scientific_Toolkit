#!/usr/bin/env python3
"""Validate CNRS release tag, distributions, and checksum inventory."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def expected_assets(version: str) -> tuple[str, str]:
    return (f"cnrs-{version}-py3-none-any.whl", f"cnrs-{version}.tar.gz")


def validate(version: str, tag: str, directory: Path) -> dict[str, str]:
    if tag != f"v{version}":
        raise ValueError(f"tag {tag!r} does not match version {version!r}")
    hashes: dict[str, str] = {}
    for name in expected_assets(version):
        path = directory / name
        if not path.is_file():
            raise FileNotFoundError(path)
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    inventory = directory / "SHA256SUMS.txt"
    expected = "".join(f"{hashes[name]}  {name}\n" for name in expected_assets(version))
    if not inventory.is_file() or inventory.read_text(encoding="utf-8") != expected:
        raise ValueError("SHA256SUMS.txt does not exactly match the required assets")
    return hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--directory", type=Path, default=Path("dist"))
    args = parser.parse_args()
    validate(args.version, args.tag, args.directory)
    print(f"release assets validated for {args.tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
