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
3. Perform one retained warm-up excluded from comparison and five retained samples per length per
   route. Alternate route order between groups to expose order effects. Reset
   scene state and drain traffic outside each measurement.
4. Validate final state through an existing bounded query or retained capture
   outside timing. A capture failure must follow the current capture-failure
   protocol; do not confuse diagnostic interference with transport corruption.
5. No raw GPIO-speed benchmark or discard-only EDP sink in the initial suite:
   measure the actual ordinary application path first.

## Subtasks and gates

ST01 [x] — Review and freeze exact measurement points. Read official VDU
definitions and the existing PRT/fence implementation. Inspect both EMOS output
routes and the final parallel clock/cleanup boundaries. Record the selected
paired source commits, timer settings, compatible fence, actual payloads and
minimal patch inventory. Stop if a required boundary cannot be measured without
changing transport behavior materially; return that decision to the Author.

ST02 [x] — Build the minimal fixture and instrumentation. Keep the fixture,
result formatting and diagnostics in a MOSlet/application where possible.
EMOS contains only unavoidable private drain/timestamp hooks and bounded RAM
storage. EDP changes only if no existing compatible fence suffices. No printing,
SD writes, HTTP requests or per-byte instrumentation during measurement.
If per-block phase attribution is cheap, retain separate payload-loop and
handover totals using boundary reads; do not enlarge this into a profiling
framework. Explain every resident diagnostic hook and its removal condition.

ST03 [x] — Verify offline before deployment. Compile both component builds and
fixture; verify ROM fit, ownership, exact byte ordering and flush/fault cleanup.
Reuse emulator checks for EMOS/fixture correctness where supported, without
claiming emulated GPIO timing. Test timer saturation and the distinction between
enqueue, physical drain and receipt using existing host tests. Respect the
separate human approval gate for emulator changes. Freeze build/fixture hashes.

ST04 [x] — Prepare and execute the bounded physical comparison after approval
and bench acquisition. Read current local hardware and fixture constraints.
Verify exact installed bytes, input readiness and idle CLI before invocation.
Select the mode only in autoexec before the fixture; do not switch modes in the
fixture. Use the CLI to invoke tests, not startup-triggered repeated execution.
Run the four-length paired matrix and overhead controls. Stop on a transport or
readiness failure; retain informative evidence and do not replay uncertain runs.
Do not request analyzer relocation unless software measurements leave a specific
electrical/timing ambiguity that requires Author discussion.

ST05 [x] — Validate and report. Preserve raw samples, start/end duration,
firmware/fixture identities, payload hashes, timer calibration and error flags.
Tabulate UART and parallel side by side, worst slowdown first, showing median,
range, equivalent cycles/byte and percentage difference against UART for
comparable endpoints. Show M03 separately. State whether the evidence locates
cost in submission, payload transmission, handover or EDP/reply processing;
leave unmeasured attribution explicitly unresolved. These are not HDMI FPS.

ST06 [x] — Restore and hand back. Restore the exact retained UART firmware pair
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

The Author released the bench. ST01–ST05 are complete:
[physical results](STREAM-TIMING-R01-RESULTS.md) retain 48 fully byte-verified
samples, all timing endpoints, calibration, ranges and capture provenance.
ST06 exact UART restoration, complete ROM/P4/startup checks and input handback
are complete. The bench is released. The earlier broad goal remains
paused; no optimization, production promotion or firmware acceptance follows.


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


## Compiled checkpoint — ST01–ST03, 2026-10-11

The matched-stream MOSlet and private EMOS timing composition compile and pass
bounded offline checks. **No physical measurements or installations occurred.**
ST04 is blocked only on release of the current Author/fsim bench reservation;
ST05–ST06 remain unexecuted. The existing UART rollback pair remains installed.

| Artifact / check | Result and scope |
|---|---|
| Timing EMOS | `agon-emos-v0.1.24-b2026-10-11-19-00-57Z`, source `d7f25d8`; 131048 bytes, 24 ROM bytes free; mandatory build/link checks pass |
| Ordinary control | `agon-emos-v0.1.24-b2026-10-11-19-11-39Z`, source `5922583`; 130968 bytes, 104 free; complete image differs from preceding stream-r11 only in build identity |
| Instrumentation cost | 80 resident ROM bytes; shared native assembly body assembles probes out of ordinary builds; no EDP change |
| MOSlet | `port-008-stream-timing-r01-b2026-10-11-19-23-40Z`; linked at &B0000, within its 32 KiB application allocation |
| Actual linked EMOS checks | Both parallel directions, byte/edge order, guards, registers/stack/IFF; existing counted-output and VBlank checks; 9216 UART status/ownership/error cases pass |
| Evidence validator | Five host tests pass, including corruption, truncation, missing/extra/duplicate samples, warm-up exclusion, saturation and endpoint-order controls |
| Physical comparison | Not run; no speedup, dominant bottleneck, hardware byte-integrity or gameplay claim |

1. Timing EMOS image SHA256:
   `74c3b1f438c06d8107f151e26e32187f0b50f7d3c831dae5db3f38e43f52e3c4`.
   Exact ELF SHA256:
   `82e8949dc11d3ec02ab67ac7f75c44a9868c7e3d23325bb1bc71189c0d76db5c`.
2. MOSlet SHA256:
   `4571393391bf964e48a712cba5c403e8b97683e58aa7953ed75f175f03dbc5d8`.
   Its builder binds private symbols to that exact ELF and adds a full-ROM
   fingerprint refusal. These are temporary diagnostic bindings, not a public
   MOS ABI or supported application GPIO access.
3. [Fixture source, build and bench instructions](../../../tests/performance/stream_timing/README.md)
   own the reproducible procedure. Exact binaries, manifests, linked checks and
   normal-build isolation evidence are retained in the ignored local
   `agents/stream-timing-r01/` silo. No emulator profile/module/deployment changed;
   CPU-model checks prove modeled instruction/I/O correctness, not Fab behavior
   or physical clocks.
4. Parallel M02 reads the counter after the final rising edge and loop-exit
   bookkeeping. UART M02 observes TEMT in software. Both include observation
   delay and possible interrupt preemption; neither is an exact analyzer edge.
   M03−M02 measures only the final block tail/receipt, not earlier handovers.
5. EDP executes ordinary per-byte buffer updates during sending; receiver
   backpressure remains included. This is the real application path rather
   than isolated electrical bandwidth. Full 8192-byte poisoned/updated target
   contents must match after every sample before accepting any comparison.
6. The fixture uses a separate 120-second coarse timeout for verbose USB buffer
   dumps outside timing. Ordinary reply waits remain four seconds; a measured
   interval reaching PRT saturation is rejected. Neither timeout authorizes
   resetting an uncertain running application. Actual suite runtime is unknown
   until a comparable physical run is retained.
7. Remove timing-only firmware hooks/profile from later production selection
   after the transport investigation; keep the shared ordinary native body,
   correctness tests and fixture source reusable. No production bundle/tag or
   broader ExExt goal continuation is authorized by this checkpoint.


## ST04 admission and fixture ABI correction — 2026-10-11

Author releases the bench for execution. The first timing EMOS FLASH submission
is followed by missing listener readiness with the older data-r20 P4. Complete
the planned stream-r14 partner installation (all four segments independently
verify), then verify the full timing EMOS ROM before any fixture invocation.
No uncertain test is replayed; none has run at this checkpoint.

Predeployment review catches a MOSlet ABI error: the private resident ZDS C
writer returns byte status in A and may use IY, whereas AgonDev expects its
return in HL and preserved IY. A MOSlet assembly bridge now supplies null/zero
arguments, preserves IX/IY and converts status to HL. No EMOS image change.
Actual linked bridge tests pass empty drain, four refusals and five timestamp
values with stack/register/IFF preservation. Prior fixture build remains frozen
preparation evidence and must not be deployed. Selected replacement:
`port-008-stream-timing-r01-b2026-10-11-19-32-51Z`, SHA256
`b20f3845d6d9e22494aa63c920afbc1b6dd03bcfd793c22e36e0ff241987e24f`. Its exact EMOS bindings are unchanged.

ST04 setup correction: MOS RUN parses this address as `&B0000`; the bare
`B0000` invocation is rejected as Invalid parameter before application entry.
LOAD likewise requires `&B0000`: its bare-address parse silently falls back
to the default load address, leaving the old listener at &B0000. Both corrected
before the timing fixture entered; no transport sample from either attempt;
ordinary setup capture discarded under the bench evidence retention policy.

## ST04 capture selection clarification — 2026-10-11

Individual verbose USB dumps can lose bytes even when the fixture saves six
fault-free rows and returns to the CLI. Do not qualify an incomplete sample.
Complete the independent cases, then make fresh completed-case invocations.
For each route, length and original repeat index 0–5, select the first
chronological invocation with zero flags and a complete, exact 8192-byte dump.
Use a later original row only when that index lacks complete earlier evidence.
Never renumber a row or substitute individual timing fields. Preserve all
original CSVs/logs, source hashes, selected row/chunk origins and exclusions.
Selection depends only on integrity, not elapsed time; the unchanged validator
must accept all 24 selected rows and complete dumps per route. This preserves
the warm-up exclusion and five fully verified comparison samples per length.

Clock clarification: stock MOS adds two coarse units per VBlank. The measured
60 Hz cadence therefore gives about 120 units/s. The frozen fixture's 7200/240
unit dump/reply bounds are approximately 60/two seconds here, rather than the
120/four-second descriptions in the preparation checkpoint above. PRT1 timing,
timeout constants and frozen bytes are unchanged; keep the raw calibration.
