# CNRS Scientific Toolkit v0.14.1 acceptance test plan

Status: FROZEN

## Required gates

| Gate | Requirement |
|---|---|
| A1 | `pyproject.toml`, `cnrs.__version__`, CLI output, tests, and `CITATION.cff` agree on `0.14.1` |
| A2 | Complete Python regression suite passes |
| A3 | The unchanged v0.14.0 streaming-division acceptance suite passes |
| A4 | Two clean builds from one commit produce byte-identical wheel files |
| A5 | Two clean builds from one commit produce byte-identical source distributions |
| A6 | Wheel and source distribution install cleanly and expose `0.14.1` |
| A7 | Release guard rejects a mismatched tag |
| A8 | Release guard rejects a missing or checksum-mismatched asset |
| A9 | Retained artifact records exact commit, tree, filenames, and SHA-256 values |
| A10 | Lean source identity and proof hygiene pass |
| A11 | All six vendored Lean projects build successfully |
| A12 | Independent audit confirms no arithmetic, API, Lean-source, or claim-boundary drift |

## Publication gates

1. Candidate CI and retained distributions are GREEN.
2. Independent audit identifies the exact candidate commit, tree, workflow
   runs, artifact, and distribution hashes.
3. Governed merge is explicitly authorized.
4. Post-merge CI is GREEN.
5. Actual release date is added to `CITATION.cff` before tagging.
6. Tag `v0.14.1` targets the certified finalization commit.
7. The release workflow attaches both Python distributions and verifies their
   public presence.
8. Zenodo publication and version DOI are verified and synchronized afterward.
