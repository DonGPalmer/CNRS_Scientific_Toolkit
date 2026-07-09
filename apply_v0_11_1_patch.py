"""Apply the v0.11.1 patch overlay to a complete v0.11.0 repository tree.

Run from the root of the extracted patch package:
    python apply_v0_11_1_patch.py /path/to/CNRS_Scientific_Toolkit
"""
from __future__ import annotations

from pathlib import Path
import re
import shutil
import sys

PATCH_ROOT = Path(__file__).resolve().parent


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    new, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"expected one match in {path}, found {count}")
    path.write_text(new, encoding="utf-8")


def prepend_if_missing(path: Path, heading: str, body: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if heading not in text:
        path.write_text(body.rstrip() + "\n\n" + text, encoding="utf-8")


def main(repo_arg: str) -> None:
    repo = Path(repo_arg).resolve()
    if not (repo / "cnrs" / "division.py").exists():
        raise SystemExit("target is not a complete CNRS Toolkit v0.11.0 tree")

    for rel in [
        "cnrs/cnrs_division_status.py",
        "tests/test_division_status_v080.py",
        "tests/test_division_api_consistency_v0111.py",
    ]:
        src = PATCH_ROOT / rel
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    replace_once(
        repo / "pyproject.toml",
        r'(?m)^version\s*=\s*"0\.11\.0"\s*$',
        'version = "0.11.1"',
    )
    replace_once(
        repo / "cnrs" / "__init__.py",
        r'__version__\s*=\s*"0\.11\.0"',
        '__version__ = "0.11.1"',
    )

    citation = repo / "CITATION.cff"
    if citation.exists():
        replace_once(citation, r'(?m)^version:\s*["\']?0\.11\.0["\']?\s*$', 'version: "0.11.1"')

    release = (PATCH_ROOT / "RELEASE_NOTES_V0.11.1.md").read_text(encoding="utf-8")
    prepend_if_missing(repo / "RELEASE_NOTES.md", "# v0.11.1", release)

    test_status = (PATCH_ROOT / "docs/TEST_STATUS_V0.11.1.md").read_text(encoding="utf-8")
    prepend_if_missing(repo / "docs" / "TEST_STATUS.md", "# Test Status — v0.11.1", test_status)

    note_dst = repo / "docs" / "release" / "V0.11.0_POST_RELEASE_NOTE.md"
    note_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_ROOT / "docs/release/V0.11.0_POST_RELEASE_NOTE.md", note_dst)

    github_release_dst = repo / "docs" / "release" / "V0.11.1_GITHUB_RELEASE.md"
    shutil.copy2(PATCH_ROOT / "V0.11.1_GITHUB_RELEASE.md", github_release_dst)

    readme = repo / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        text = text.replace(
            "## v0.11.0: Rational Expansion and Scientific Workflow Validation",
            "## v0.11.1: Division Classification Consistency Patch\n\n"
            "v0.11.1 corrects the retained legacy division classifier so it agrees "
            "with the numerator-aware Gaussian-rational termination theorem. "
            "See `RELEASE_NOTES.md`.\n\n"
            "## v0.11.0: Rational Expansion and Scientific Workflow Validation",
            1,
        )
        readme.write_text(text, encoding="utf-8")

    print(f"Applied v0.11.1 patch to {repo}")
    print("Next: run pytest, build, twine check, then replace validation placeholders.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python apply_v0_11_1_patch.py /path/to/repository")
    main(sys.argv[1])
