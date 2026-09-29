# AUDIT-010 RP04 — EMOS raw SD write dispatch

## State

`A10-RP04-S01` [ ] Candidate and hardware-validation tooling complete; awaiting
commit-pinned physical execution and Author acceptance. A local candidate commit
is required to make the flashed source identity immutable; publication remains
outside this gate.

`A10-RP04-S02` [ ] Physical destructive-sector qualification remains pending.
Emulator success does not dispose it.

## Boundary and ownership

`A10-RP04-C01` [x] Official Agon API documentation commit
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` defines selector `0x73` as writing
`BC` blocks from the buffer at `DE`, with sector/unlock data at `HL` and status
in `A`.

`A10-RP04-C02` [x] Official MOS tag `v3.0.2`, commit
`8336409351ee5314e02801a7b72a4f1bb5282519`, and EMOS commit
`8f29bf811e4b989117e437a8e10afe2adbc77be7` both route
`sd_api_writeblocks` to `_SD_readBlocks_API`. The official checkouts were not
changed.

`A10-RP04-C03` [x] EMOS owns the one-call wrapper correction and its source and
linked-image guards. `mos-tests` owns the existing RST `0x73`, C-write control
and independent raw-image oracle. Extender records cross-component disposition
without duplicating the fixture.

## Candidate and regression manifest

`A10-RP04-R01` [x] Only `sd_api_writeblocks` now calls
`_SD_writeBlocks_API`. Selector, normalization, parameter stack, status return,
raw drivers, FatFS and `sdserve` remain unchanged.

`A10-RP04-R02` [x] Six focused EMOS ABI tests pass. They distinguish source
read/write targets, decode final linked `CALL` targets and include a negative
linked-image case that rejects the inherited dispatch.

`A10-RP04-R03` [x] A fresh candidate-specific prepared source tree and the EMOS
`firmware-check` wrapper pass all generic and product-linked checks. The
128,574-byte candidate `MOS.bin` has SHA-256
`fa5fd6a4ca71670acd1e9a5b338e6b2d00392dde9d21608d1b15ccbf05269174`.

`A10-RP04-R04` [x] The complete EMOS repository suite reports 126/134. All
eight failures reproduce unchanged from clean EMOS `8f29bf8` against the same
stale default prepared source tree. The fresh candidate-specific prepared tree
and product build pass, so the existing prepared-tree inconsistency is retained
as a baseline limit rather than attributed to RP04.

`A10-RP04-R05` [x] The `mos-tests` explicit-profile path required a narrow
uncommitted prerequisite: stock MOS/map hashes are asserted only for the
default profile; explicit profiles remain fail-closed against their own MOS,
map, VDP and emulator hashes. Test behavior and the raw-image oracle are
unchanged. The pinned stock profile's C `SD_writeBlocks` control still passes
both seeds after the harness correction.

`A10-RP04-R06` [x] Existing `sd_writeblocks.rst08.001` and
`SD_writeBlocks.c.001` cases pass two seeds each with no infrastructure error.
Independent image reads found sector two filled with 512 bytes of `0x6B` in all
four cases. The common sector hash is
`789a49fcfe20dccddb0f9266345989ae51c3333847df3bc45400d1b04033a565`.

`A10-RP04-R07` [x] The maintained two-command hardware workflow now separates
exact-commit flashing from testing. The test command consumes the verified flash
receipt, reruns the complete retained Extender regression manifest, and adds the
`a10-rp04-raw-sd-write` physical case. The fixture touches sector 2 only after
validating an MBR first-partition start beyond it, retains the preimage, verifies
the repaired API's effects, restores through the distinct C dispatch, and
independently verifies the exact restored bytes. Tool/fixture structural tests
and a target build pass; no physical write has yet run.

`A10-RP04-R08` [x] Frozen-tool dry runs rebuild EMOS commit
`19b8b6f9e9983190edb7b0beca95355e257b6851` from fresh EMOS and MOS-builder
snapshots. The identified 128,579-byte image has SHA-256
`2cf26c42ee956b95c6e4a732ddaebc108b4864ffb89c34bb02034ea17fe897e1`;
the exact-commit 10,288-byte physical fixture has SHA-256
`ebdaabf78ef01974df64d5744e34edea05d3c1231eb4a99e167077ee63baa6fd`.
The expanded retained closure at Extender commit `87d8eabb` passes all 55 cases
in 143.86 monotonic seconds with zero failure, infrastructure error, timeout or
blocked case. These are preparation gates, not physical RP04 acceptance.

## Acceptance boundary

`A10-RP04-A01` [x] The selected headless emulator cases passed. The Author then
clarified that emulator evidence is prerequisite evidence, not the required
per-repair hardware validation.

`A10-RP04-A02` [ ] Create local immutable candidate commits in the component
repositories, flash the exact EMOS commit with `flash_firmware_commit.py`, and
run `run_hardware_regression.py` against its receipt. Do not begin RP05 before
physical acceptance and the final RP04 disposition commit.

`A10-RP04-A03` [ ] Present the complete retained-suite and physical-case evidence
for Author acceptance. The prepared physical procedure fails closed unless the
card layout proves sector 2 pre-partition and exact restoration succeeds.
