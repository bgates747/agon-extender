# PORT-008 — Matched UART and parallel stream timing, r01

## Executive summary

Measure how long the eZ80 spends submitting and transmitting identical VDU
bytes to EDP through ExCom/UART and ExExt/parallel. Separate those costs from
EDP processing and reply delivery. Reuse the existing PRT timing code and
ordinary transport implementations; do not optimize either implementation
during this investigation. The Author approved execution after reviewing the buffer-upload proposal.
Implementation and bounded validation are authorized; respect current bench ownership.
The previous eight-hour goal is paused.

## Scope and baseline

1. The eZ80 fixture sends a retained, hashed RAM-resident stream through ordinary
   EMOS-owned VDU output. EMOS selects ExCom or ExExt; applications never access
   GPIO, UART or the parallel coordinator directly.
2. Both routes terminate at the same P4 EDP parser, renderer and output
   configuration. Keep browser streaming disabled for the primary comparison.
   Keep video mode, scene, physical wiring and keyboard conditions identical.
3. Preserve the currently restored UART pair. It is the recovery baseline,
   not a source of ExExt performance results: the new comparison needs one
   explicitly identified compatible experimental pair supporting both routes.
   Select exact source/configuration identities before building. Do not silently
   install the untested split-upload candidate or other pending changes.
4. The mainboard VDP is the fsim custom build, **not stock**. Retain it unchanged
   and record its exact identity: its VBlank timing still influences EMOS.
5. The question is transport cost. No game modifications, rendering fixes,
   scheduling redesign, new wiring, throughput optimization, production
   promotion or resumed broad game campaign belongs in this tranche.

## Measurement contract

Use an otherwise-unused eZ80 PRT1 with the existing timer source unchanged.
Keep normal interrupts enabled. Report raw ticks, divisor, nominal clock,
elapsed microseconds and equivalent eZ80 clock cycles. Equivalent clock cycles
include interrupt service and waiting; they are **not retired instructions**
and cannot alone identify CPU utilization. Never subtract clocks from different
processors.

| ID | eZ80 observation | Meaning and limits |
|---|---|---|
| M01 | Immediately before first ordinary output call to final output-call return | Application submission duration; may leave queued bytes |
| M02 | Same start to transmission of the final payload byte | Sender wire-drain duration, including earlier waits and handovers; excludes later completion receipt |
| M03 | Same start to successful normal completion of the final parallel block | Parallel protocol completion; includes post-payload release/receipt; UART has no equivalent block receipt |
| M04 | Same start to receipt of the identified EDP processing-fence reply | End-to-end processing/reply duration; not display scanout completion |

M02 requires an actual observation point, not an assumption that output return
means transmission complete. For UART, review the correct transmitter-empty
status, including the shift register, and preserve receive-error handling when
reading UART status. For parallel, timestamp the actual final-byte clock
boundary before cleanup/receipt; record instruction/read overhead. M02 may
precede M01 when the final write itself blocks. Store independent timestamps;
do not assume their numerical order.

Drain preceding traffic and establish empty EMOS queues before each sample.
After M01, explicitly flush any ExExt residual batch through an EMOS-owned test
entry point if no existing suitable entry exists. Keep the natural VBlank
service enabled and include its effects. This explicit-drain experiment is not
a claim about natural gameplay batching latency. Place the EDP fence after
payload drain; account separately for its command/reply bytes. Verify its
contract before calling it rendering completion.

The fixture selects its own timer range before each sample. If the interval
cannot fit, use an established wider-range method or shorten the workload;
do not introduce an overflow ISR merely to instrument the existing ISR problem.
Reject saturation, missing replies, transport faults and incomplete streams.
Calibrate timer-read overhead with an immediate-read control. Use retained MOS
time as a coarse cross-check, with its resolution stated.

## Bounded workload

1. Construct one deterministic buffer-upload stream family using buffered command
   5, operation &C2 (set multiple targets from inline operands), at offset zero
   in a buffer allocated before timing. Command 0 would allocate a fresh block
   on each sample, so command 5 preserves the agreed allocation-free interval. Retain the bytes, length and hash for each member. ExCom and ExExt use
   exactly the same payload and ordinary output-call pattern.
2. Use four payload lengths: a small stream, exactly one current 4096-byte batch,
   just beyond that boundary, and two batches. Prefer 256, 4096, 4097 and 8192
   bytes if legal command padding allows; otherwise record the closest valid
   command-complete lengths before freezing the fixture. Never end inside a
   command or upload body.
3. Perform one unmeasured warm-up and five retained samples per length per
   route. Alternate route order between groups to expose order effects. Reset
   scene state and drain traffic outside each measurement.
4. Validate final state through an existing bounded query or retained capture
   outside timing. A capture failure must follow the current capture-failure
   protocol; do not confuse diagnostic interference with transport corruption.
5. No raw GPIO-speed benchmark or discard-only EDP sink in the initial suite:
   measure the actual ordinary application path first.

## Subtasks and gates

ST01 [ ] — Review and freeze exact measurement points. Read official VDU
definitions and the existing PRT/fence implementation. Inspect both EMOS output
routes and the final parallel clock/cleanup boundaries. Record the selected
paired source commits, timer settings, compatible fence, actual payloads and
minimal patch inventory. Stop if a required boundary cannot be measured without
changing transport behavior materially; return that decision to the Author.

ST02 [ ] — Build the minimal fixture and instrumentation. Keep the fixture,
result formatting and diagnostics in a MOSlet/application where possible.
EMOS contains only unavoidable private drain/timestamp hooks and bounded RAM
storage. EDP changes only if no existing compatible fence suffices. No printing,
SD writes, HTTP requests or per-byte instrumentation during measurement.
If per-block phase attribution is cheap, retain separate payload-loop and
handover totals using boundary reads; do not enlarge this into a profiling
framework. Explain every resident diagnostic hook and its removal condition.

ST03 [ ] — Verify offline before deployment. Compile both component builds and
fixture; verify ROM fit, ownership, exact byte ordering and flush/fault cleanup.
Reuse emulator checks for EMOS/fixture correctness where supported, without
claiming emulated GPIO timing. Test timer saturation and the distinction between
enqueue, physical drain and receipt using existing host tests. Respect the
separate human approval gate for emulator changes. Freeze build/fixture hashes.

ST04 [ ] — Prepare and execute the bounded physical comparison after approval
and bench acquisition. Read current local hardware and fixture constraints.
Verify exact installed bytes, input readiness and idle CLI before invocation.
Select the mode only in autoexec before the fixture; do not switch modes in the
fixture. Use the CLI to invoke tests, not startup-triggered repeated execution.
Run the four-length paired matrix and overhead controls. Stop on a transport or
readiness failure; retain informative evidence and do not replay uncertain runs.
Do not request analyzer relocation unless software measurements leave a specific
electrical/timing ambiguity that requires Author discussion.

ST05 [ ] — Validate and report. Preserve raw samples, start/end duration,
firmware/fixture identities, payload hashes, timer calibration and error flags.
Tabulate UART and parallel side by side, worst slowdown first, showing median,
range, equivalent cycles/byte and percentage difference against UART for
comparable endpoints. Show M03 separately. State whether the evidence locates
cost in submission, payload transmission, handover or EDP/reply processing;
leave unmeasured attribution explicitly unresolved. These are not HDMI FPS.

ST06 [ ] — Restore and hand back. Restore the exact retained UART firmware pair
and startup unless the Author explicitly accepts leaving the timing candidate.
Verify usable CLI/input, released reset and no running listener/collector/test.
Release the bench, update the parent task/results and stop for discussion before
optimization. Passing timing acquisition is not acceptance of ExExt performance.

## Research and retained evidence

1. [Official VDU commands](../../../../../agon-docs/docs/vdp/VDU-Commands.md):
   authority for the payload and query semantics. ST01 must select exact commands
   and record the reference revision; no upstream reference edits.
2. [Existing game timing](../../testing/game-timing.md): PRT1 read order, source
   preservation, divisors, calibration, overflow handling and fence limitations.
   Its historical runner has explicit reuse restrictions; reuse reviewed timer
   code, not an obsolete deployment procedure.
3. [Ordinary stream contract](EXEXT-STREAM-R01.md) and
   [results](EXEXT-STREAM-R01-RESULTS.md): failed game performance, ISR ownership,
   exact rollback identities and uninstalled candidate boundaries.
4. EMOS owner sources: `agon-emos/src/emos_exext.c`, `src/uart.c`, `src/uart.h`,
   and the parallel coordinator/clock helpers in the sibling checkout. The
   current UART header defines TEMT separately from THRE; reading LSR can
   acknowledge receive errors. ST01 must review the actual access path.
5. [Capture protocol](../../qualification/capture-failure-protocol.md),
   [bench constraints](../../qualification/bench-constraints.md) and
   [SD layout](../../sd-layout.md) apply to any later execution/deployment.

## Current disposition

Execution approved by the Author; implementation begins with ST01. Hardware
execution awaits release of the newer fsim/Author bench reservation recorded
in HARDWARE.local.md. No hardware operations while that reservation stands.
The paused goal and existing regression rollback remain in force. No new
architectural decision or firmware acceptance is implied.


## ST01 frozen implementation selection

1. Official references: agon-docs `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
   MOS v3.0.2 `8336409351ee5314e02801a7b72a4f1bb5282519`, VDP v2.16.0
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. MOS/VDP references are clean.
   Buffered-Commands-API commands 0/2/5 and System-Commands pixel query &84
   define the stream and ordered parser-completion observation.
2. Use target buffer &E100, clear and allocate 8192 bytes outside timing. Each
   measured stream is `23,0,&A0,0,&E1,5,&C2,0,0,count_lo,count_hi,data...`: an
   eleven-byte header followed by 245/4085/4086/8181 bytes. Total wire lengths
   are exactly 256/4096/4097/8192. Inline data cycles deterministically through
   all byte values. Poison the target before every upload.
3. Use the ordinary seven-byte pixel query after drain as an ordered parser
   completion reply. Buffer adjustment runs synchronously before the parser
   reaches that query. This proves preceding command processing, not renderer
   worker completion or HDMI presentation. General poll is startup-only per
   official documentation and will not be repurposed by the fixture.
4. Reuse exact retained P4 stream-r14 bytes; do not include uninstalled r15.
   No EDP source changes are planned. EMOS starts from maintained `56d78ef`
   with the same stream implementation, under a separate timing-only profile.
   Unavoidable resident hooks: guarded residual flush, guarded UART drain
   observation preserving receive errors, and one final-forward-byte timestamp
   per block. Fixture/results/timer control remain outside firmware.
5. PRT1 /256 gives nominal 72,000 counts/s and a 0.9102-second single-pass
   range at 18.432 MHz. Saturation invalidates a sample, never wraps silently.
   M02 stores the raw counter immediately after the final forward clock pair
   and loop-exit bookkeeping. Exact instruction offset is retained; no per-byte
   probes. Private symbol bindings are generated from the exact linked EMOS
   image, never installed as a stable application ABI or raw GPIO entry.
6. Buffer command &80 serial debug dump can verify all bytes after the timed
   interval using existing EDP output. Its logging is outside capture; bind
   exact retained bytes before accepting correctness. Reject missing/truncated
   evidence. No newly invented network diagnostics are required.
