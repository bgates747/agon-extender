# AUDIT-010 RP05 — Checked display allocations

## State

`A10-RP05-S01` [x] Candidate implementation, source qualification and automated
exact-commit hardware qualification complete. Manual loaded-asset validation
and Author acceptance remain required.

`A10-RP05-S02` [x] Accepted by the Author on 2026-09-30 after the exact
candidate passed the complete offline suite, full paired installed-system
qualification and manual loaded-asset Nurples validation. RP06 may proceed.

## Boundary and lineage

`A10-RP05-C01` [x] This item repairs only the lower allocation subset of
`AUDIT-010-F001`: viewport pools, drawing/visible row-pointer tables and the
paletted controller's prepared DMA rows. It does not prepare a replacement
controller beside the live controller, roll back a failed clock/worker attach,
or change official mode fallback. Those outer transaction concerns remain
`A10-RP06`.

`A10-RP05-C02` [x] The allocator body is inherited under `A10-LIN01` from the
bundled vdp-gl selected by official VDP tag `v2.16.0`, commit
`c7ac293d2aa81ddfa693390549bcd909069c8fc3`. Extender's P4 adaptation adds
memory-capability selection and internal-to-PSRAM retry. The local correction
is isolated in `checked_viewport_allocation.hpp`; the official Agon references
remain clean and read-only. Upstream publication is a separate decision.

`A10-RP05-C03` [x] No existing selected upstream function provides a checked
all-or-nothing viewport allocation. The project-owned helper replaces the
unsafe allocation body rather than creating a second runtime allocator. The
parallel nonrelease display family is unchanged.

## Regression manifest

`A10-RP05-R01` [x] A prepared viewport remains local until all framebuffer
pools and required drawing/visible row tables exist. Failure releases every
local allocation, preserves the requested geometry, returns false and leaves
all published viewport pointers empty.

`A10-RP05-R02` [x] The paletted controller initializes its persistent DMA-row
pointer table, checks each prepared scan-row allocation, unwinds earlier rows
on failure and releases the completed base viewport if row preparation fails.

`A10-RP05-R03` [x] The base and selected paletted controller stop resolution
setup when allocation fails. `agon_screen.h` returns the existing mode-memory
failure result before starting the P4 frame clock, enabling drawing or creating
a Canvas. This prevents the lower-allocation null dereference; retaining or
restoring the prior live display remains RP06.

`A10-RP05-R04` [x] `viewport_allocation_test.py` injects failure at every
allocation ordinal for single- and double-buffered multi-pool viewports and all
four prepared DMA rows. ASan/UBSan prove complete cleanup; assertions prove no
partial result publication and reject invalid or pool-exhausted requests.

`A10-RP05-R05` [x] The new fault-injection case is registered in the canonical
offline qualification manifest. Neighboring mode lifecycle, display profile,
browser capture, visible-text and native-build cases remain mandatory in the
complete clean-commit run.

`A10-RP05-R06` [x] A fresh unversioned `p4-console` build from exact candidate
commit `f5036ca210a3d2cb0291c4b405f4094b3a3d609f` passes native
source/definition/action validation and compilation. Its 1,706,304-byte factory
image has SHA-256
`1c84d9ff51f5e6444bb842163085b5a9eb16b07caba4575efbc2c35e8bb742cb`.
The build is development evidence only and is not deployable or a hardware
result.

`A10-RP05-R07` [x] The complete clean-commit offline suite passes all 56 cases
in 145.173471 monotonic seconds with no test failure, infrastructure error,
timeout or blocked case. The source closure remained clean and unchanged at
Extender `f5036ca2` and the frozen EMOS baseline `21a9ba27`. The retained local
summary under `agents/qualification-rp05-f5036ca2/summary.json` has SHA-256
`f571665881af9c99a79711790317cebbc284b0ff662c1584a15786d2e9cef29e`.

`A10-RP05-R08` [x] The exact candidate P4 image was flashed and independently
verified. Its 1,706,304-byte factory image has SHA-256
`ce61953b72cded8e7c7ce770987c679f8313aa4d598650112f0c63916f7937e9`;
the verified receipt under
`agents/hardware-validation/flash-p4-2026-09-30-02-55-05Z-f5036ca210a3/`
has SHA-256
`337284bf9a1e084607784fb7f0f8eb0a8044c4dc4ba3359f499043b960428949`.
The full paired installed-system qualification then passed both physical cases
and all 17 required checks in 232.798482 monotonic seconds against P4
`f5036ca2` and verified EMOS `8ecea5bc`. It verified browser reset, Legacy and
ExCom handoff, text and video capture, display status, SD service and round
trip, ordinary startup recovery, raw-sector write/read/restore and final
startup restoration. The retained summary under
`agents/hardware-validation/qualification-2026-09-30-03-14-25Z-8ecea5bc-f5036ca2/`
has SHA-256
`26f6962e70c93ddc5ed91992120455a8fe3cc8ef62c266be9ad0f34c5f328487`.

`A10-RP05-R09` [x] The Author manually ran the loaded-asset Nurples mode
transition on the exact installed candidate and reported the run successful.
This case remains intentionally outside automation. The observation completes
RP05's exact-candidate validation without expanding its scope into RP06.

## Acceptance boundary

`A10-RP05-A01` [x] Present exact commits, source and hardware evidence,
remaining RP06 boundary and manual observation to the Author. Stop for explicit
acceptance; do not begin RP06.
