# AUDIT-010 RP04 — EMOS raw SD write dispatch

## State

`A10-RP04-S01` [x] Candidate and canonical paired-component hardware
qualification complete and accepted by the Author on 2026-09-30. Publication
remains governed by the audit-wide closeout gate.

`A10-RP04-S02` [x] Physical destructive-sector qualification passed against the
verified installed EMOS bytes. This disposes the execution gate but does not
substitute for Author acceptance.

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

`A10-RP04-R05` [x] The `mos-tests` explicit-profile path required narrow commit
`c7aab30`: stock MOS/map hashes are asserted only for the
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
and a target build pass.

`A10-RP04-R08` [x] Frozen-tool dry runs rebuild EMOS commit
`19b8b6f9e9983190edb7b0beca95355e257b6851` from fresh EMOS and MOS-builder
snapshots. The identified 128,579-byte image has SHA-256
`2cf26c42ee956b95c6e4a732ddaebc108b4864ffb89c34bb02034ea17fe897e1`;
the exact-commit 10,288-byte physical fixture has SHA-256
`ebdaabf78ef01974df64d5744e34edea05d3c1231eb4a99e167077ee63baa6fd`.
The expanded retained closure at Extender commit `87d8eabb` passes all 55 cases
in 143.86 monotonic seconds with zero failure, infrastructure error, timeout or
blocked case. These are preparation gates, not physical RP04 acceptance.

`A10-RP04-R09` [x] Exact EMOS commit
`8ecea5bc6cb4f9f563bc570316afbdaa08648632` was built, flashed and verified by
full 128 KiB ROM readback. The 128,579-byte artifact has SHA-256
`7c7ac79fcbdb4a9d67885aede552e808e0111bcc7e2d54b012c43add0305317a`;
the installed padded ROM has SHA-256
`4fab4a413ff3e7d163ee8bd605ef9390503ba25db116a5c9e6137e300932a729`.
Exact Extender runner commit
`1b79083038b83fc4a60265b3d05db1e554e51c15` then passed all 55 retained cases
in 150.491329 monotonic seconds and the physical case in 142.566509 seconds.
Sector 2 precedes the first partition at LBA 8192. The preimage and restored
CRC32 are both `b2aa7578`; the generated and independently observed pattern
CRC32 are both `3b3befd6`; test, restore and restoration-read statuses are all
zero. The fixture SHA-256 is
`9ed1064702f339ca8b6f3bb4ba852cdb9ccf724b59446ff4859b69eb85a47ce3`.
The runner restored the exact original startup, reset to a ready boot and sent
the accepted Legacy cue. The retained local summary under
`agents/hardware-validation/regression-2026-09-29-23-07-38Z-1b79083038b8/`
has SHA-256
`b3a2124ed85416e4788570b956a73dca8bb4239e35a3fdfe500d39f5ba9bf04a`.

`A10-RP04-R10` [x] Failed setup attempts remained fail-closed. The first
diagnostic fixture stopped at raw-SD initialization with status 2 and recorded
`write_attempted=0`. Disassembly then showed that AgonDev's `sd_writeblocks`
symbol uses MOS's C function table and therefore could not test RST selector
`0x73`; the corrected fixture binds RST `0x70`, `0x71` and `0x73` directly while
retaining the C write path only as its independent restoration control. Later
attempts stopped before fixture launch on an unsupported optional directory
operation, CLI-command timing and retained transfer-journal state; none
attempted a raw write. The maintained runner now serializes stale-result cleanup
in the one-shot startup and explicitly preserves/closes retained backups.

## Acceptance boundary

`A10-RP04-A01` [x] The selected headless emulator cases passed. The Author then
clarified that emulator evidence is prerequisite evidence, not the required
per-repair hardware validation.

`A10-RP04-A02` [x] Create local immutable candidate commits in the component
repositories, flash the exact EMOS commit with `flash_firmware_commit.py`, and
run `run_hardware_regression.py` against its receipt. Do not begin RP05 before
physical acceptance and the final RP04 disposition commit.

`A10-RP04-A03` [x] The Author accepted the complete evidence on 2026-09-30.
The canonical run passed both registered physical cases and all 17 required
checks. Sector 2 was before partition LBA 8192; write/read CRC32 `3b3befd6` and
preimage/restored CRC32 `b2aa7578` matched, with all fixture statuses zero. The
Author's subsequent manual Nurples run passed ExCom mode switching and gameplay
at an observed 25–29 frames per second.
