# PORT-008 — Stock behavior with minimum parallel transport

## Executive summary

Author authorizes this bounded review on 2026-10-11. Compare stock MOS/VDP byte
transport with the current ExExt candidate and produce a concrete removal list.
The first pass must preserve stock behavior above transport; all ExExt CRC must
go. Current construction/offer/completion consumes 70.3–80.7% of measured ordered
reply time, so review that wrapper before changing the native byte runner.
This tranche ends with a source-backed minimal path and an implementation order.
It does not implement or deploy the removal, resume the paused eight-hour goal,
or select permanent UART shutdown. TR01–TR04 are complete; the
[source-backed result](MINIMAL-TRANSPORT-RESULTS.md) contains the removal matrix
and proposed code cuts. Stop for discussion before implementation.

## Authority and scope

1. Parent: [PORT-008](../PORT-008.md), P08-P05 and accepted P08-D01/D03 in the
   [phase contract](PHASE-TIMING-R01.md). The remaining minimum-control decision
   is P08-D02. [ADR-0026](../../decisions/ADR-0026-four-lane-exext-transport.md)
   and [architecture](../../architecture.md) own accepted design.
2. EMOS owns the eZ80 output route, receive integration, GPIO, flow control and
   committed mode. P4 EDP owns the receiving/sending peripheral and byte-stream
   endpoint. Applications retain their stock calls and command/reply bytes.
3. Preserve parsing, command execution, packet formats, callbacks, sysvars and
   interrupt semantics. Physical transfer timing may differ. Keep the electrical
   ownership/release, byte sampling and backpressure that the shared wiring and
   peripheral actually require; do not infer a need from existing software.
4. No CRC, substitute checksum, speculative retries, new application protocol,
   upstream bug fixes, renderer changes, game changes or wiring changes. Host
   qualification can still compare exact received bytes outside timed intervals.
5. Work is offline source review only. Do not reserve the bench, connect to a
   device, reset, flash, run a physical fixture or change an emulator profile.
   No product source, build configuration or frozen result is changed here.

## Work items

TR01 [x] — Establish the stock path. Read official MOS RST10/RST18, packet and
keyboard callback documentation before source. Trace actual MOS serial send,
receive ISR/parser and VDP Stream read/write. Record tags/commits and exact
source locations, flow-control behavior, blocking and interrupt context.

TR02 [x] — Map the candidate end to end. Trace ordinary ExExt output, full and
partial batches, query replies, keyboard packets and real VBlank service through
EMOS and P4. Identify each CRC, offer/ACK, completion, poll, session, buffer and
UART handover. Separate existing byte semantics from added link machinery and
name both processor owners. Include the 4096→4097 boundary and reverse traffic.

TR03 [x] — Produce the removal/retention matrix. For every added operation,
classify remove, retain for physical necessity, simplify, or unresolved. Cite
the concrete electrical/peripheral or stock-behavior requirement for retention.
Identify callers and affected tests; retain only the minimum data needed for
direction, byte count, ownership and backpressure. Treat permanent UART shutdown
as a later alternative, not a prerequisite for this review.

TR04 [x] — Write the smallest viable path and implementation sequence. Distinguish
immediate CRC removal from control simplifications needing a paired protocol
change or Author decision. State compile/offline checks and reuse the existing
256/4096/4097/8192-byte comparison matrix for later hardware validation. Report
risks and unresolved owner/ordering facts without inventing solutions. Update
current task/handoff and stop for discussion before source edits or deployment.

## Bounded research précis

1. Official read-only baseline: agon-docs
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
   [MOS API](../../../../../agon-docs/docs/mos/API.md),
   [VDP system/protocol commands](../../../../../agon-docs/docs/vdp/System-Commands.md).
   Stock MOS v3.0.2 `8336409351ee5314e02801a7b72a4f1bb5282519` and stock VDP
   v2.16.0 `c7ac293d2aa81ddfa693390549bcd909069c8fc3` are clean references.
   [MOS serial](../../../../../agon-mos/src/serial.asm) and
   [MOS VDP protocol](../../../../../agon-mos/src/vdp_protocol.asm) define actual
   transport/parser boundaries. Consult VDP source only for material detail.
2. Maintained candidate: EMOS `src/emos_exext.c`, parallel coordinator,
   native byte runner, session/control and UART ownership code in the sibling
   owner checkout; P4 endpoint/control/Stream adapters under
   `vdp/video/extender/transport`. Record exact working source commits in results;
   do not claim these trees equal a retained installed measurement build.
3. Reuse [phase results](PHASE-TIMING-R01-RESULTS.md) and
   [matched stream results](STREAM-TIMING-R01-RESULTS.md). Construction/offer/
   completion is an inclusive measured scope, not proof that every constituent
   operation is independently slow or removable. Post-full-block offers add
   ~33–35 ms; the EMOS/P4 share remains unresolved. No new speedup estimate.
4. The original UART pair/startup was restored and verified. Production remains
   unchanged. Unrelated agon-dev-env work belongs to another agent and must not
   be staged as part of this contract or review.

## Deliverable and acceptance boundary

One source-backed result document beside this contract contains the stock and
candidate path maps, removal matrix, minimum-path sketch and proposed next code
tranche. Review checks are source trace completeness, correct link targets and
clean diffs; no physical or performance acceptance is claimed. Author review
precedes implementation. Preserve all earlier measurement evidence unchanged.
