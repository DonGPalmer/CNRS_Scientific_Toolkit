# Release evidence archive

This directory preserves version-specific governance, activation, checksum,
and closeout evidence without crowding the repository root. Release notes are
maintained separately in the reverse-chronological
[`RELEASE_NOTES.md`](../../RELEASE_NOTES.md) index.

## Archived releases

- [`v0.18.0`](v0.18.0/) — release-activation candidate record and checksum manifest.
- [`v0.17.0`](v0.17.0/) — activation record and release checksum manifest.
- [`v0.16.0`](v0.16.0/) — activation record and release checksum manifest.
- [`v0.15.0`](v0.15.0/) — freeze amendments, candidate evidence, manifests,
  release checksums, and finalization/closeout records.
- [`v0.14.1`](v0.14.1/) — preparation manifest, activation checklist,
  checksums, and closeout record.
- [`v0.14.0`](v0.14.0/) — freeze, audit-repair, activation, checksums, and
  finalization/closeout records.

Performance data associated with v0.14.0 is retained under
[`benchmark-results/v014`](../../benchmark-results/v014/).

## Preservation policy

The archived files are byte-for-byte relocations of their former root-level
counterparts. Their embedded paths and checksum entries record the repository
layout at the time of the corresponding release and are therefore preserved
unchanged. Verify those historical manifests against the matching Git tag or
release source snapshot.

Architecture-freeze and API-contract specifications that remain active inputs
to acceptance and claim guards stay at the repository root pending a separate,
governed specification-path migration.

Published tags, release assets, package artifacts, and Zenodo records are not
altered by this archive layout.
