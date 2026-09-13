# CNRS Scientific Toolkit v0.14.1 maintenance scope

Status: FROZEN FOR IMPLEMENTATION AND VALIDATION

## Objective

Close the published v0.14.0 governance record and make the Toolkit release
process reproducible, auditable, and resistant to missing distribution assets.

## Included

1. Synchronize package, runtime, command-line, citation, release-note, status,
   provenance, and source-index version metadata to `0.14.1`.
2. Record the closed v0.14.0 GitHub identity and Zenodo version DOI
   `10.5281/zenodo.22731846`.
3. Build the wheel and source distribution twice with a commit-derived
   `SOURCE_DATE_EPOCH` and require byte equality.
4. Generate exact SHA-256, commit, and tree records for retained CI artifacts.
5. Use `actions/upload-artifact@v7`.
6. On publication of `v0.14.1`, build and validate the exact tag, attach the
   wheel and source distribution, and verify both are publicly listed.

## Excluded

- arithmetic or serialization changes;
- public API additions or removals;
- changes to streaming-division or witness semantics;
- changes to vendored Lean source;
- new mathematical, performance, convergence, scientific, or formal claims;
- streaming multiplication, caching, batching, or CLI expansion.

Those feature proposals remain candidates for v0.15.0 and later releases.

## Release rule

`date-released` remains absent from `CITATION.cff` until the actual governed
release date is authorized. No tag or public release may precede a GREEN audit
of the immutable candidate and its retained distributions.
