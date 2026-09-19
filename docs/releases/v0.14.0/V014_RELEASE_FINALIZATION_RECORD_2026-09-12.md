# CNRS Scientific Toolkit v0.14.0 release finalization record

Release date: 2026-09-12

Status: GOVERNED MERGE GREEN; FINALIZATION CI PENDING

## Certified candidate

- pull request: #2;
- commit: `cd0d590818de3f2db615f2269276ede53527827d`;
- tree: `18e171d6a8e5a3a0b5a69614d05950fe0144f2ac`;
- Python/distribution run: `34733492839` — SUCCESS;
- Lean run: `34733492819` — SUCCESS, source identity plus six project builds;
- retained artifact: `10310278319`;
- independent re-audit: GREEN.

## Governed merge

- merge commit: `511526fdd60cfa2967d0307fe16ba4131785c0b3`;
- post-merge Python/distribution run: `34734237160` — SUCCESS;
- post-merge Lean run: `34734237144` — SUCCESS, seven jobs.

## Authorization

The governed merge of the certified candidate was explicitly authorized. The
release date `2026-09-12` was subsequently authorized for finalization.

## Remaining controls

The release-finalization commit must pass Python/distribution and seven-job Lean
CI. Its exact wheel and source distribution must be verified before tagging.
Tag creation, GitHub Release publication, asset attachment, and Zenodo
verification remain separate controlled actions. No Zenodo version DOI is
asserted by this record.
