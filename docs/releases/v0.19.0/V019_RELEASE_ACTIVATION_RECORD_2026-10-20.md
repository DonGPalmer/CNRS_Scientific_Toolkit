# CNRS Scientific Toolkit v0.19.0 activation record

Status: RELEASE-ACTIVATION CANDIDATE; not merged, tagged or published.
Preparation date: 2026-10-20. This is not a publication date.

## Verified implementation baseline

PR #20: `https://github.com/DonGPalmer/CNRS_Scientific_Toolkit/pull/20`.
Normal merge: `f04c856064e82fc8e059af693d65392bff9ad843`.
Audited/merged tree: `a651d1e1c450782411056463fa17b18edbdfa809`.
Approved implementation head: `57d788b69b7d6c615d99a405536755826ee94856`.
Frozen formal subtree: `d3ee7c7fd6648812966f3aaa4f700acbc40e223f`.
Post-merge tests/distribution run `39442596713` and six-project Lean run
`39442596695`: SUCCESS. Merge closeout package SHA-256:
`9ef57517565440b4467fa64eeefacf11613bf5fda7f69325d6dbd49afd0a87bb`.

## Activation scope

Synchronize package/runtime/citation metadata, current release documentation,
consolidated notes, build/distribution tooling and the 0.19 publication path.
Add metadata/asset release checks and update the exact source index.
No executable mathematical implementation, table certificate, validation
oracle, historical acceptance packet or certified Lean source is changed.

The new publication job is bound to tag v0.19.0 and does not overwrite
existing assets. It verifies fresh isolated wheel/sdist imports and compares
attached bytes with approved build hashes. It is not invoked by candidate
push/PR validation. The historical v0.18 publication job remains unchanged.

CITATION.cff retains the concept DOI and omits date-released while this is a
candidate. No v0.19 version DOI is invented. Existing v0.18.0 tag/assets and
historical notes remain intact. Candidate distributions are not replacement
v0.18.0 release assets.

## Verification and remaining gates

Exact candidate head/tree and CI/artifact hashes are recorded in the draft
PR and external activation dossier, avoiding self-referential commit hashes.

1. Complete activation-head regression, historical acceptance and claim
   guards, certificate gate, source inventory, metadata checks, reproducible
   builds and isolated wheel/sdist verification.
2. Retain exact-head Python/distribution and frozen Lean CI plus actual
   distribution artifact identities; verify publication workflow statically
   without creating a release.
3. Audit the exact activation candidate and artifacts.
4. Obtain separate author authorization to mark ready and merge.
5. Verify actual activation merge parents/tree and post-merge CI/artifacts.
6. Obtain separate tag/publication authorization; then verify public assets,
   actual release date and Zenodo version DOI and record additive closeout.

The candidate does not authorize official Lean/E2 adoption or enlarge the
formal proof boundary. Python remains independently implemented.
