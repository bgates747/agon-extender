# Test Runs

Decision-bearing build, deployment, experiment, and qualification evidence
lives in `<RUN-ID>/`, beginning with a copy of `TEMPLATE/manifest.yaml`.

The run directory and manifest `run_id` must match
`<TASK-ID>-YYYY-MM-DD-HH-MM-SSZ`. Store evidence with relative filenames and
full SHA-256 values. Keep private bench topology and specimen mappings in the
ignored local hardware record; tracked manifests use short aliases.

After completion, a run manifest is append-only except for an explicit dated
entry in `corrections` explaining what was changed and why.

## Qualification sequence

Qualified testing begins from a clean commit containing every controlled input,
including the test procedure and artifact identities. Build from that commit,
record `dirty: false`, conduct the run, and only then commit its manifest and
evidence. A passing run may be followed by a separate qualification/baseline
commit or release tag.

Do not repair or edit a candidate during a qualified run. Preserve the failed
evidence, commit the correction, assign a new build and run ID, and rerun. Dirty
working-tree tests are exploratory and cannot qualify an artifact.
