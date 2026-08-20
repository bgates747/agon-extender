# SETUP-002 Review Guide

SETUP-002 was approved by the Author on 2026-08-20. The accepted review covered
these decisions:

1. **Vocabulary and grammar:** versions for software/protocols, revisions for
   controlled physical/test artifacts, UTC timestamped builds and runs.
2. **Authority:** the Author approves artifact IDs and version/revision
   increments; tooling assigns build/run timestamps.
3. **Lifecycle:** draft, experimental, candidate, qualified, released,
   deprecated, and rejected remain separate from compatibility.
4. **Compatibility:** consumers declare exact, one-of, or semantic-version
   range requirements; physical revisions never use inferred ranges.
5. **Initial registry:** confirm the artifact lineages in `artifacts.yaml`, the
   rejected r01 canary/profile, and the deliberately unassigned draft entries.
6. **Evidence model:** builds, baselines, and runs use the supplied YAML
   templates; run evidence is append-only and tracked.
7. **Firmware application:** after approval, SETUP-001 creates canary r02,
   embeds its generated build ID in diagnostics, emits a build manifest, and
   opens a run manifest before reflashing.
8. **Privacy:** tracked records use aliases and exclude private topology,
   credentials, and specimen identifiers.

This approval closed SETUP-002 and authorized applying the policy to subsequent
work. Future policy changes require a new tracked task and the next registry or
document revision where applicable.
