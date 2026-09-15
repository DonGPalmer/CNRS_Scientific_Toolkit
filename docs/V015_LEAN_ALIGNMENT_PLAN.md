# CNRS Scientific Toolkit v0.15.0 Lean-alignment plan

Status: FROZEN BEFORE IMPLEMENTATION

## Target mathematical bridge

The intended bridge is finite-support convolution multiplication: coefficient convolution represents multiplication of evaluated finite Laurent/polynomial expressions over the applicable Gaussian-integer/CNRS carrier.

## Required theorem map

Before any theorem-backed release claim, record:

- Lean repository and project;
- theorem names and complete statements;
- hypotheses, carrier, support convention, offset convention, and evaluation map;
- Lean/toolchain and dependency revisions;
- certified commit, Git tree, workflow run/job, artifact identity, and source checksums;
- a field-by-field mapping from Lean objects to Python types and operations.

## Synchronization rule

The Toolkit may import a Lean result only after that result has completed its own independent audit and governed promotion. The exact certified sources must be vendored or checksum-linked using the existing source-identity mechanism. Development snapshots may guide tests but cannot support release claims.

## Python/Lean boundary

Lean proves the identified finite mathematical proposition in its formal carrier. Python remains independently implemented. Toolkit tests verify representative and property-based correspondence; they do not convert the Python runtime into formally verified or Lean-extracted software.

## Mismatch handling

Differences in trimming, zero representation, coefficient order, Laurent offsets, normalization, or resource-limit behavior must be resolved explicitly. An adapter may bridge representations only if it is documented and tested as value preserving. A mismatch cannot be hidden by weakening release language after implementation.

## Fallback release posture

If the formal P3-L1 result is not certified in time, v0.15.0 may release the finite exact Python feature as computationally validated, provided all theorem-backed language is removed and the provenance records the formal alignment as pending. No provisional theorem identity may be cited.
