# AUDIT-010 RP05 — Checked display allocations

## State

`A10-RP05-S01` [ ] Candidate implementation and source qualification complete.
Exact-commit hardware qualification and Author acceptance remain required.

`A10-RP05-S02` [ ] RP05 accepted. RP06 remains unauthorized until this box is
accepted and the final RP05 disposition is committed.

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

`A10-RP05-R06` [x] A fresh unversioned `p4-console` build passes the native
source/definition/action validation and compilation. The build is development
evidence only and is not deployable or a hardware result.

`A10-RP05-R07` [ ] The complete clean-commit offline suite passes and records
the exact candidate identity and durable summary.

`A10-RP05-R08` [ ] The exact candidate P4 image is flashed and independently
verified, then the full paired installed-system qualification passes against
verified P4 and EMOS receipts. A manual loaded-asset Nurples mode transition is
required because that case remains intentionally outside automation.

## Acceptance boundary

`A10-RP05-A01` [ ] Present exact commits, source and hardware evidence,
remaining RP06 boundary and manual observation to the Author. Stop for explicit
acceptance; do not begin RP06.
