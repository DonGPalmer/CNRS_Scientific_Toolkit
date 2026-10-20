# v0.19.0 publication approval controls

Status: configured in the candidate workflow; no release approval or environment
configuration has been performed by preparing this change. Missing approval values
block publication. This closes audit finding C2's missing identity check.

The `publish-v0190-assets` job names the GitHub environment
`cnrs-v019-publication`. Before authorizing publication, configure that environment
with required reviewer protection and controlled configuration access, and verify
the actual protection settings. A YAML environment name alone does not establish
reviewer protection. Repository/environment administrators remain trusted; this is
an identity gate, not a cryptographic proof of human authorization.

After the separately approved activation merge, verify its parents/tree, successful
CI and actual wheel/sdist bytes. Prepare a UTF-8 JSON manifest with exactly these
fields (the placeholders below are not valid approval data):

```json
{
  "schema": 1,
  "version": "0.19.0",
  "tag": "v0.19.0",
  "commit": "FULL_FINAL_APPROVED_MERGE_COMMIT",
  "tree": "FULL_FINAL_APPROVED_MERGE_TREE",
  "assets": {
    "cnrs-0.19.0-py3-none-any.whl": "APPROVED_WHEEL_SHA256",
    "cnrs-0.19.0.tar.gz": "APPROVED_SDIST_SHA256"
  },
  "approval_record": "DURABLE_AUTHOR_PUBLICATION_AUTHORIZATION_RECORD"
}
```

Present those exact bytes and their SHA256 in the publication decision packet.
Only after explicit author publication approval, install the exact JSON string as
environment variable `CNRS_V019_APPROVED_MANIFEST_JSON` and its independently
recorded SHA256 as `CNRS_V019_APPROVED_MANIFEST_SHA256`. These are GitHub Actions
configuration variables (`vars`), not shell environment variables or repository
sidecars. Do not automatically calculate/set the trusted digest in the release job.
Preserve the exact UTF-8 bytes, including any final newline, when entering JSON.
Approval data must not fall back to repository-level variables: keep both names
exclusive to this environment and verify no same-named repository/organization
variables exist before activation. Restrict changes to the environment/configuration
to the governed publication procedure.

The job checks manifest digest/schema, checkout commit/tree, peeled release tag,
and tracked-source cleanliness before building. It checks built distributions
against approved hashes before upload, and checks the downloaded public assets
against the same approval manifest. Upload replacement remains disabled. The old
v0.18 publication job is unchanged. Release-service calls are still downstream of
these checks, and a reviewer pause is effective only once protections are configured.

The manifest identifies the final merge, not the pre-merge candidate. The builder
uses the commit timestamp as `SOURCE_DATE_EPOCH`; identical source trees at different
commits may have different archive bytes. If a rebuilt distribution differs because
of build tooling or any other cause, stop and investigate; do not regenerate approval
to make the check pass. Prepare a new reviewed decision packet if identities change.

CI tests source/tag mismatches, missing approval/digest, malformed manifests,
manifest edits, and changed wheel/sdist bytes with regenerated checksum files.
Publication is not authorized by passing those tests. No v0.19 tag, release, DOI,
publication date, environment configuration, or official Lean adoption is introduced.
