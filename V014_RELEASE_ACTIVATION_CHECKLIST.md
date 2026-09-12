# v0.14.0 release activation checklist

Status: NOT AUTHORIZED FOR RELEASE  
Use only after implementation and acceptance are complete.

## Documents supplied in this package

- README.md
- RELEASE_NOTES.md
- RELEASE_NOTES_v0.14.0.md
- CITATION.cff
- SOURCE_INDEX.txt
- synchronized architecture, API, division, claim, test, theorem-alignment,
  Lean-alignment, acceptance, and performance documents under docs/

## Non-document release files to update from the final candidate

- pyproject.toml: set project version to 0.14.0;
- cnrs/__init__.py: set __version__ to 0.14.0 and export approved new APIs;
- default regression tests that assert the package version;
- distribution metadata generated from the final tree;
- SOURCE_INDEX.txt regenerated from git ls-files.

## Evidence that cannot be prepared honestly in advance

- final Python passed/skipped/warning counts;
- GitHub Actions run and job identities;
- candidate commit and tree;
- wheel and source-distribution names, sizes, and SHA-256 values;
- installed-wheel smoke-test result;
- performance JSON/CSV results and reviewed comparisons;
- GitHub Release URL and Zenodo version DOI.

These values must be added only after they exist. No bracketed INSERT markers
are used in the supplied documents; pending evidence is stated explicitly.

## Release sequence

1. Implement the frozen APIs.
2. Make the acceptance and regression suites GREEN.
3. Run all six Lean jobs and the alignment guard.
4. Execute and review the frozen performance protocol.
5. Build and install-test the wheel and source distribution.
6. Regenerate SOURCE_INDEX.txt and synchronize all exact counts and identities.
7. Obtain an independent audit of the immutable candidate.
8. Governed merge, tag, GitHub Release, and Zenodo publication.
