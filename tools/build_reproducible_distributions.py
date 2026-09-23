#!/usr/bin/env python3
"""Build byte-identical CNRS wheel and source distributions twice."""

from __future__ import annotations

import hashlib
import gzip
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.18.0"
ASSETS = (
    f"cnrs-{VERSION}-py3-none-any.whl",
    f"cnrs-{VERSION}.tar.gz",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_date_epoch() -> str:
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%ct", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def build(outdir: Path, epoch: str) -> None:
    env = os.environ.copy()
    env.update({"SOURCE_DATE_EPOCH": epoch, "PYTHONHASHSEED": "0"})
    subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(outdir)],
        cwd=ROOT,
        env=env,
        check=True,
    )
    normalize_sdist(outdir / f"cnrs-{VERSION}.tar.gz", int(epoch))


def normalize_sdist(path: Path, epoch: int) -> None:
    """Rewrite an sdist with stable ordering, ownership, mtimes, and gzip header."""
    with tempfile.TemporaryDirectory() as temporary:
        raw_tar = Path(temporary) / "normalized.tar"
        with tarfile.open(path, "r:gz") as source, tarfile.open(
            raw_tar, "w", format=tarfile.PAX_FORMAT
        ) as target:
            for member in sorted(source.getmembers(), key=lambda item: item.name):
                member.mtime = epoch
                member.uid = member.gid = 0
                member.uname = member.gname = ""
                member.pax_headers = {}
                payload = source.extractfile(member) if member.isfile() else None
                target.addfile(member, payload)
        with raw_tar.open("rb") as source, path.open("wb") as destination:
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=destination, mtime=epoch
            ) as compressed:
                shutil.copyfileobj(source, compressed)


def main() -> int:
    work = ROOT / ".release-build"
    dist = ROOT / "dist"
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(dist, ignore_errors=True)
    first, second = work / "first", work / "second"
    first.mkdir(parents=True)
    second.mkdir(parents=True)

    epoch = source_date_epoch()
    build(first, epoch)
    build(second, epoch)

    dist.mkdir()
    lines: list[str] = []
    for name in ASSETS:
        left, right = first / name, second / name
        if not left.is_file() or not right.is_file():
            raise RuntimeError(f"missing distribution: {name}")
        left_hash, right_hash = sha256(left), sha256(right)
        if left_hash != right_hash:
            raise RuntimeError(
                f"non-reproducible distribution {name}: {left_hash} != {right_hash}"
            )
        shutil.copy2(left, dist / name)
        lines.append(f"{left_hash}  {name}\n")

    (dist / "SHA256SUMS.txt").write_text("".join(lines), encoding="utf-8")
    (dist / "CANDIDATE_COMMIT.txt").write_text(
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True),
        encoding="utf-8",
    )
    (dist / "CANDIDATE_TREE.txt").write_text(
        subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True),
        encoding="utf-8",
    )
    print(f"Reproducible CNRS {VERSION} distributions verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
