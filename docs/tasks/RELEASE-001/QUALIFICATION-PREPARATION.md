# Combined native release qualification preparation

## Executive summary

The retained accepted P4 and EMOS images need no firmware rebuild. The old
qualification runner is incompatible with current startup rules and HDMI
output. Preparation must remove those assumptions, preserve exact installation
provenance and leave all physical validation pending while the bench is occupied.
The actionable sequence remains in the parent task, not this research note.

## Bounded contracts and source findings

1. Official documentation baseline: agon-docs commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
   `docs/vdp/System-Commands.md` (screen information, `VDU 23,0,&86`),
   `docs/vdp/Screen-Modes.md` (mode selection and double-buffer visibility),
   and `docs/mos/API.md` (ordinary counted VDU output and mode sysvars).
   Official MOS v3.0.2 (`8336409351ee5314e02801a7b72a4f1bb5282519`) and VDP
   v2.16.0 (`c7ac293d2aa81ddfa693390549bcd909069c8fc3`) reference checkouts are clean tagged
   references; no upstream source modification is needed. Fresh mode responses
   are required; cached MOS sysvars alone cannot prove the selected target.
2. `qualification/run.py` previously uploaded a one-shot `/autoexec.txt`, then
   reset into the raw-SD test. The EMOS-owned fixture additionally overwrote
   startup inside `arm_recovery()`. Both conflict with the current appliance
   lifecycle. The fixture must return through an explicit RUN, not arm boot.
   A historical source snapshot must not silently supply that obsolete fixture.
3. `vdp/video/extender/network/http_video_service.cpp` excludes `/video` for
   `AGON_EXTENDER_HDMI`. `display_status.hpp` exposes committed render geometry,
   actual HDMI carrier, DMA frame-complete count and rolling fault counters.
   Those permit a native automated progress/fault check, not a visual pixel,
   aspect, colour or loaded-asset proof. Browser-video builds retain their
   decoded-frame checks. Native qualification needs separately recorded Author
   visual review on the exact final pair.
4. `scripts/sdcard.py` negotiates protocol 2 without transport checksums when
   called with `require_fast=True`; the old qualification helper allowed
   fallback. Fail before HELLO for a checked/unsupported listener. Existing
   raw-sector CRCs summarize local SD test buffers; they are not checksums on
   processor communications. Byte comparisons remain the actual SD oracle.
5. Current EMOS v27 was built from base
   `9844ecf38fde59d157b9006da2ca74ea59348710` plus its archived uncommitted patch.
   Retain that truth, the full source inventory/archive and exact 128-KiB
   installed readback. Do not claim that base commit alone reproduces v27 or
   require a new firmware merely to obtain a clean-source receipt. The new
   independently built fixture has its own source pin and ABI compatibility
   review; it need not be rebuilt from the older firmware snapshot.
6. Current reset bridge configuration and Pi GPIO actuator need fresh physical
   verification before reuse. Historical USB reset evidence is separate.
   No new reset wiring, actuator result or foreground state can be established
   offline. The runner must stop on changed boot identity during a workload,
   uncertain raw I/O, unsupported entry-mode cleanup or missing command handback.

## Scope limits

No physical access, reset, flash, serial open, SD deployment or application
invocation is permitted in this preparation tranche. A host simulation, source
archive verification or successful fixture link is not a physical qualification
pass. Current production selection and immutable accepted archives stay intact.

## Exact reference links and reuse limits

1. [Official mode information](../../../../../agon-docs/docs/vdp/System-Commands.md),
   [mode and buffer semantics](../../../../../agon-docs/docs/vdp/Screen-Modes.md),
   and [MOS API](../../../../../agon-docs/docs/mos/API.md) define the query,
   sysvar, file and low-level SD contracts. Raw SD selectors 0x70/71/73 retain
   their destination/unlock/sector-buffer/count layouts. The independent
   C-dispatch restore is retained unchanged.
2. [Accepted counted-output binding](../../../tests/fixtures/controller/mos_io.asm)
   is reused by QSTATE. Pinned EMOS returns A=0 for counted output on either
   route; do not interpret this helper as a universal stock MOS return contract.
3. [Source preparation](../../../qualification/build_fixtures.py) copies and
   hashes exact app inputs separately from resident firmware. The new QSTATE
   entry contract rejects double-buffered modes; the Pi can restore an arbitrary
   supported single-buffered mode without hard-coding the entry mode number.
4. [Installation evidence adapter](../../../qualification/installation.py)
   verifies whole archives in memory without extracting or executing them.
   Local archive/readback paths remain outside tracked reports. Future live
   identity/actuator/cue-file evidence cannot be manufactured from these checks.

## Live preparation contract clarification — 2026-10-30

The Author's ready-bench handoff establishes idle CLI availability; the host
then obtains actual listener/read/EXIT evidence rather than asking for duplicate
confirmation. The 128-KiB EMOS ROM and P4 application/bootloader/partition ranges
can be compared read-only, without reflashing the accepted components.

Ordinary filesystem command completion must not be inferred from acknowledged
keyboard events. Cleanup now uses a separate explicit MOS EXEC command file,
queues the fast listener after all owned-file deletions, and independently
checks absence. The retained command file lives in results evidence; it is not
deleted while MOS holds it open. Official
[star commands](../../../../../agon-docs/docs/mos/Star-Commands.md#delete)
document `DELETE -f`; pinned installed `agon-emos/src/mos.c` also automatically
forces literal single-file deletion. Therefore confirmation is not established
as the cause of the observed handback gap. Explicit `-f` makes the reviewed
noninteractive intent clear; synchronous batch completion is the actual host
coordination correction. Keep the unresolved failure evidence until diagnosed.
