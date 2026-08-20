# Baselines

A baseline is a tracked, named combination of exact artifact identities and
external dependencies approved for a stated purpose. Copy `TEMPLATE.yaml` to
`<baseline-id>.yaml`; the filename omits the revision because the baseline ID
already includes it, for example `p4-light2-bringup-r01.yaml`.

Never edit an accepted baseline to select new artifacts. Create the next
baseline revision, preserve the old file, and record qualification run IDs.
`qualified` applies only to the compatibility scope stated in that file.
