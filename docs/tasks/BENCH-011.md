# BENCH-011 — Remote consumer diagnostics without SD swaps

Extender provides remote deployment, invocation and durable log retrieval for
FSIM's loadable-renderer investigation. FSIM owns the game and instrumentation.
Establish mainboard VDP compatibility before running the candidate; preserve
ordinary startup and unrelated firmware, apps and assets.

## Current state

The bounded startup cohort is complete and the exact incoming mainboard flash
is restored. [Results and limits](BENCH-011/STARTUP-RESULTS.md) and
[portable evidence](BENCH-011/STARTUP-RESULTS.json) preserve all four attempts,
mode packets, pool samples and restoration. FSIM independently verifies the four retained attempts, all mode sequences,
all seven sets of raw pool samples and the temporary installation comparison.
The bounded task is complete; performance attribution remains separate
FSIM-owned work. No further bench execution is selected.

## Authority and state

1. The Author directly prioritizes this coordination in the FSIM conversation
   on 2026-11-01 and makes the bench available. Extender verified the original
   human message through the app's thread reader. HDMI diagnosis is stopped;
   a peer assertion alone would not authorize hardware changes.
2. Fresh HTTP evidence shows admitted neutral keyboard, valid USB F310, idle
   SD service and fault-free native mode 0. Complete private evidence and device
   identities belong in `HARDWARE.local.md` and `agents/fsim-diagnostics/`.
3. The recorded mainboard VDP is F060 app SHA256
   `58aadf642e465bbb15006a24d54e47a9bb68eeaf403295e35981e8b1166b2c27`.
   This is retained installation evidence, not a fresh flash readback. FSIM
   requires rows-r1 image SHA256
   `8d980025f891484cf7e6cc5f2992cf517cb80e0123ff7de712ae8d7f2dc1c807`.
   Compatibility was confirmed absent under F060. The Author selected the
   matching runtime temporarily; the exact incoming F060 is now restored.
4. EMOS v27/listener v0.3.0 retain checksum-free fast carrier2. Recovered P4 R25
   supports input/transfers, but its mode 96 scanout fault remains unresolved.
   FSIM uses mainboard Legacy output, not P4 rendering.
5. Requirements: mailbox message
   `2026-11-01_17-32-09_fsim-pingo_pingo066-priority-remote-diagnostics-one`.
   Extender's supported workflow reply:
   `2026-11-01_17-34-19_linux-extender_fsim-remote-workflow-boundary-one`.

## Executed bounded contract

1. Extender proves actual CLI with finite `EMOS sdserve --fast /`, startup read
   and acknowledged EXIT exchanges. Preserve 108-byte load-only startup. Never
   launch or resume tests through reset or autoexec.
2. Extender qualifies passive mainboard serial capture using the maintained
   joined DTR/RTS opener and printer-mirror sentinel. Preserve boot identity;
   disable mirroring after capture. Mirroring overhead is separate from baseline
   performance. P4 screen text cannot observe Legacy mainboard output.
3. Resolve D01 before any candidate RUN or firmware change. FSIM supplies exact
   image/source/partitions and rollback requirements for any necessary update;
   installation uses the controlling procedures and separately identified scope.
4. Extender stages only manifest-selected files in a separate
   `/extender/diagnostics/fsim` subtree. Use fast transfers and explicit host
   readback/hash where exact comparison requires it; no P4–EMOS checksums.
   Record transfer time separately. Listener EXIT precedes LOAD/RUN. A running
   ordinary app excludes foreground-listener transfers.
5. FSIM supplies finite invocation, Ready/exit semantics, durable per-attempt
   logs and terminal markers. Extender preserves baseline first attempt, then
   second RUN without reload only after proved return; archive logs before the
   next invocation. Never type into an unknown foreground state.
6. FSIM instruments a separate candidate: entry mode/dimensions, asset/work/LOAD
   stages, mode admission/reply/fence/settle and healthy failure cleanup. Keep
   executable/internal 8-bit/PSRAM free/largest fields distinct.
7. Not executed: successful-run ground/air/near/far stage timing is a separate
   later tranche requiring FSIM instrumentation. Its future contract separates
   eZ80 simulation, PREPARE and RENDER roundtrips, background composition,
   flip/fence and completed presentations versus host wall clock. FSIM retains
   physics, renderer ABI and controller compatibility; no P4 rendering port.
8. Extender restores entry mainboard mode/route, flashing cursor and actual CLI.
   Standing Agon-first recovery stops an interrupted sequence without replay.
   No wiring, P4/EMOS change, startup rewrite or production promotion is selected.

## Decision register

1. **D01 — Temporary mainboard update, accepted by Author 2026-11-01 and executed/restored.** FSIM's exact source comparison
   confirms F060 has built-in Pingo and no loadable runtime; rows-r1 has the
   generic runtime and removes built-in Pingo. Extender recommends a temporary
   rows-r1 diagnostic session followed by exact F060 sector rollback. This
   changes the extension interface used by the old flight program named in the
   unchanged load-only startup; do not run that old program during the session.
   The Author explicitly grants temporary installation, diagnostic execution and
   exact restoration after backup/verification. Actual backup/partition/active-slot
   proof remains a technical gate. Preserve P4, EMOS and autoexec; this is a
   temporary operational selection, not a permanent architectural change.
2. **D02 — Baseline attempt lifecycle, agreed with FSIM.** Preserve the unchanged
   seven runtime files. Host supplies a neutral Ready key and one bounded Escape
   within 120 host seconds, retaining terminal output and SD logs before the next
   RUN without reload. No optional verify.tst changes the baseline. Unknown
   foreground state stops dispatch. Diagnostic client must additionally supply
   unique attempt/stage logs and terminal markers before its own deployment.

## Preparation evidence

1. Two actual listener/startup-read/EXIT exchanges pass in 5.959 host-monotonic
   seconds; unchanged 108-byte load-only startup is retained. No game is invoked.
2. Maintained passive mainboard capture receives 183 bytes, including a unique
   printable sentinel and normal Legacy prompt, in 8.053 host-monotonic seconds.
   Mirror disable and cursor controls are submitted afterward. Input-admission
   epoch is unchanged; this does not independently measure electrical reset-pin
   or eZ80 RAM continuity. No reset is requested.
3. Five supplied firmware artifacts match their manifest size/SHA. Exact rows-r1
   application is 1,093,792 bytes; source pins 1056ee38/ac2dd598 and candidate app0
   offset 0x10000/capacity 0x140000 are recorded, subject to actual installed-table
   and active-image comparison. Do not write a bootloader or partition table.
4. Seven baseline files total 1,236,429 bytes. All seven pass separate fast2 upload plus explicit
   complete host readback. One interrupted host READ was resolved from its saved
   request; the activated upload was not repeated. Listener EXIT is acknowledged,
   startup remained unchanged before invocation. Subsequent explicit baseline
   and diagnostic pairs, temporary application-only installation and exact
   restoration are recorded in the linked result. Those terminal records
   supersede preparation state; frozen source/capture evidence remains retained.

## Controlling procedures

Follow the [mainboard SD guide](../mainboard-sd.md),
[serial capture](../serial-monitor.md), [SD layout](../sd-layout.md),
[test lifecycle](../procedures/test-appliances.md) and
[test execution](../procedures/test-execution.md). Selected firmware changes
also require installation/rollback/reset procedures. Production is unchanged.
