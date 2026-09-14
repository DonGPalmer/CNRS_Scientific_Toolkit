# CNRS Scientific Toolkit v0.14.1 release activation checklist

Status: RELEASE PUBLISHED; POST-RELEASE CLOSEOUT AUDIT PENDING

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
- [x] Lean source identity plus six project builds: run `34770773970`.
- [x] Exact source index and checksum inventory prepared and locally verified.
- [x] Immutable public candidate CI and retained artifact `10321763058`.
- [ ] Independent GREEN audit.

## Governed publication

- [x] Publication commit fixed on `main`.
- [x] Python/distribution and Lean CI succeeded at the publication commit.
- [x] Actual release date `2026-09-14` added to `CITATION.cff` in closeout synchronization.
- [x] Exact distributions verified by release-assets workflow `34848995514`.
- [x] Tag `v0.14.1` created at commit `a1ac3e1273ef9492c7b4a1aaeba08f078ce1d56a`.
- [x] GitHub Release published with approved title and notes.
- [x] Automated workflow attached both certified distributions.
- [x] Zenodo version DOI `10.5281/zenodo.22750622` recorded.
- [ ] Independent post-release closeout audit.
