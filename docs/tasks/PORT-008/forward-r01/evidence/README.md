# PORT-008 post-run prototype source snapshots

Status: **Historical evidence — not maintained source, build provenance, or a
deployable candidate**

These binary Git patches preserve the exact live tracked-source deltas found in
the two owning repositories after the failed PORT-008 investigations. They
prevent later repair work from making the only copies of those deltas disappear
while the actual source remains governed by its owning repository.

| Evidence patch | Owning repository and base | SHA-256 | Boundary |
|---|---|---|---|
| `agon-extender-post-run-prototype.patch` | `agon-extender` at `45c45d5ef02285a737969a11b29dcc011aa4ef9b` | `e381b4c944bf72eda30efb4277bac9c7b9b3a47aac2157a0a039b41b5d8e0c7b` | P4 direction-control source plus its task-local validator; current fixed-purpose prototype only |
| `agon-emos-post-run-prototype.patch` | `agon-emos` at `0e24b06abdb322fdb4e681a21242ccfebfc8ea65` | `98510188b5e9912f35c9780005bf4ec95077eca028f3ee17e9699ba2cb997e25` | EMOS length-width and sender-cadence source/checks; current fixed-purpose prototype only |

The Extender patch covers only:

1. `vdp/video/extender/transport/forward_parallel_stream.cpp`;
2. `vdp/video/extender/transport/forward_parallel_stream.hpp`; and
3. `docs/tasks/PORT-008/forward-r01/scripts/validate-forward-build.py`.

The EMOS patch covers only:

1. `src/serial.asm`;
2. `projects/port008-forward/verify.py`; and
3. `tests/test_port008_forward.py`.

The snapshots do not retroactively make any run clean. The run manifests
correctly retain the cited base commit and `dirty: true` state. F007 also means
that a later source snapshot cannot prove which object bytes were built.
Specifically, run `PORT-008-2026-09-01-02-10-50Z` used the intermediate EMOS
length correction before the cadence change, so the combined current EMOS
patch is not its exact source delta. That run remains identified by its binary
hash and bounded physical evidence only.

The ignored local build tree presently retains the located dirty diagnostic
binaries at SHA-256 `7984048405e327e7e3fc6e1dc227d697b0bc7a032bcbeff631b4ecead48275c1`,
`8f659845c24a9b328f6791a7ac75a2b820df254bc601517d1b2741ed7999987b`,
and `37f1dd65d76666d0fa46a05defb47544a93dc31bd9d31ef0283cf692bde2c967`.
Those generated binaries are not tracked by this evidence record.

Do not apply either patch as a product update. The P4 snapshot retains F005,
F013, R001, and the pre-activation corrective-action boundary. The EMOS
snapshot has not passed the repository's required post-correction graphical
emulator gate. Any maintained correction must be implemented and reviewed in
the owning repository, receive a clean identity, and satisfy the applicable
REMED-002 and PORT-008 gates.
