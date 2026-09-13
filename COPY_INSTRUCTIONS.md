# CNRS Scientific Toolkit v0.14.1 copy instructions

This archive contains the complete 28-file v0.14.1 maintenance-preparation
update in the existing GitHub repository folder structure.

## Installation

1. Start from a clean local clone synchronized with GitHub `main` at the closed
   v0.14.0 release.
2. Extract this archive at the repository root.
3. Allow the 16 existing files to be replaced and the 12 new files to be added.
4. Do not copy `COPY_INSTRUCTIONS.md` into the repository; it is packaging
   guidance only.
5. In GitHub Desktop, confirm that exactly 28 changed repository files appear.
6. Commit the changes to a new v0.14.1 candidate branch, not directly to
   `main`.

## Before public candidate submission

Run:

```bash
python -m pytest -q
python -m pytest -q acceptance/v014
python -m pip install build
python tools/build_reproducible_distributions.py
python tools/check_release_assets.py --version 0.14.1 --tag v0.14.1 --directory dist
sha256sum -c V0141_SHA256SUMS.txt
```

`CITATION.cff` intentionally has no `date-released` field while v0.14.1 is a
candidate. The actual governed date is added only after merge and immediately
before the final tag.

The package does not alter arithmetic behavior, public APIs, vendored Lean
source, or theorem boundaries.
