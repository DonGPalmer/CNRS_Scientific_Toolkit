# CNRS Scientific Toolkit v0.14.1 release activation checklist

Status: PREPARATION COMPLETE; VALIDATION PENDING

## Preparation

- [x] Version synchronized to `0.14.1`.
- [x] v0.14.0 GitHub and Zenodo closeout identities recorded.
- [x] Maintenance scope and claim boundary frozen.
- [x] Reproducible double-build script added.
- [x] Release asset validation guard added.
- [x] Artifact upload updated to `actions/upload-artifact@v7`.
- [x] Release-publication asset workflow added.
- [x] `date-released` omitted while candidate status applies.

## Candidate validation

- [x] Complete Python regression suite locally: `1221 passed`.
- [x] v0.14.0 acceptance suite locally: `19 passed`.
- [x] Reproducible wheel and source-distribution comparison locally.
- [x] Clean installation from both distributions locally.
- [ ] Lean source identity plus six project builds.
- [x] Exact source index and checksum inventory prepared and locally verified.
- [ ] Immutable public candidate CI and retained artifact.
- [ ] Independent GREEN audit.

## Governed publication

- [ ] Explicit merge authorization.
- [ ] Governed merge and post-merge CI.
- [ ] Actual release date added to `CITATION.cff`.
- [ ] Finalization CI and exact distributions verified.
- [ ] Tag `v0.14.1` created at the verified commit.
- [ ] GitHub Release published with approved title and notes.
- [ ] Automated workflow attaches both certified distributions.
- [ ] Zenodo record, publication date, and version DOI verified.
