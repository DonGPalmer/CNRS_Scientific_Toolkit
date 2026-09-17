# CNRS Scientific Toolkit v0.15.0 release closeout record

**Status:** GitHub and Zenodo publication complete; independent post-release
audit PASS WITH ADMINISTRATIVE CORRECTIONS; corrections installed additively
on `main` after the immutable release tag

**Release date:** 2026-09-17

## Published identity

- repository: `DonGPalmer/CNRS_Scientific_Toolkit`;
- tag: `v0.15.0`;
- commit: `5051885402a054807f9ae460448204439fff2196`;
- tree: `457da71d84c6893e747b9666878cfbe29b8c4c77`;
- GitHub release ID: `390681109`;
- GitHub publication time: `2026-09-17T12:09:28Z`.

The published tag remains fixed. This additive closeout synchronization on
`main` does not move or recreate the tag and does not replace either published
distribution.

## CI and retained artifact

- post-merge Python/distribution workflow `35149485108`: SUCCESS;
- post-merge Lean workflow `35149485142`: SUCCESS;
- Lean jobs: source identity plus six project builds, 7/7 SUCCESS;
- retained distribution artifact `10468791616`;
- artifact name:
  `cnrs-v0.15.0-distributions-5051885402a054807f9ae460448204439fff2196`;
- artifact digest:
  `sha256:11c23b6b1b77c4f76b9c84f9c6db0d4d09499081e0fb912f441c7499fb517b9a`.

## Published distributions

Release-assets workflow `35219537009` completed successfully and attached:

- `cnrs-0.15.0-py3-none-any.whl`
  - size: 264,724 bytes;
  - SHA-256:
    `30348eb34e3b7a837881dc8f38c532282d387450f01166ffc2718c1d514b0c44`;
- `cnrs-0.15.0.tar.gz`
  - size: 331,088 bytes;
  - SHA-256:
    `6f4195c2bf3c4fc136f909de151200931e04363b651a098c67ae68889bc04166`.

Both assets were downloaded and independently rebuilt from the public tag.
The rebuilt files matched the published hashes exactly. Earlier hashes obtained
from the local pre-publication commit are not release-asset identities.

## Zenodo identity

- version DOI: `10.5281/zenodo.22812232`;
- concept DOI: `10.5281/zenodo.20574852`;
- Zenodo record ID: `22812232`;
- publication date: `2026-09-17`;
- deposited file:
  `DonGPalmer/CNRS_Scientific_Toolkit-v0.15.0.zip`;
- deposited size: 2,567,626 bytes;
- deposited MD5: `af43e39e87f3322ce9ef6cefcf9e175d`.

The Zenodo archive was independently compared with the exact public tag:
476/476 files matched, with no missing, extra, or changed files.

## Administrative corrections

The post-release audit found no implementation, tag, asset, deposited-source,
or DOI-identity defect. It found only these administrative items:

1. replace pre-publication future-tense DOI language with the issued version
   DOI;
2. align `CITATION.cff`'s release date to the actual GitHub and Zenodo
   publication date, 2026-09-17;
3. retain the concept DOI while adding the exact v0.15.0 version DOI;
4. record the actual tag-derived distribution hashes above;
5. distinguish the release body's audited implementation-test snapshot from
   the three release-engineering tests added during finalization.

The release body's published validation counts remain the certified
implementation-audit snapshot: 1,278 passed and 4 optional-pandas skips in the
standard environment, or 1,282 passed with optional pandas. The finalization
tree adds three release-engineering tests; this closeout does not recast the
historical audit snapshot as the final-tag full-suite total.

## Scope and claim boundary

This closeout changes metadata and governance records only. It changes no
arithmetic algorithm, public Python API, vendored Lean source, theorem boundary,
published tag, release asset, or Zenodo deposited file.

