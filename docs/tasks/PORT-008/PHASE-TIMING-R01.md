# PORT-008 — Attribute ordinary parallel block costs, r01

## Executive summary

Author approved phase attribution on 2026-10-11. Measure the existing EMOS/EDP
path before changing it: the completed matched-stream comparison identifies
large residual-block and reply costs but does not separate their causes.
Reuse its four exact payloads, PRT clock and full-buffer proof. This tranche
covers instrumentation, offline correctness, a bounded hardware comparison and
verified restoration. Persistent UART shutdown and circuitry remain later work.
PT01–PT06 are complete: 24 selected samples/full 196,608-byte proof and exact
UART restoration. [Results](PHASE-TIMING-R01-RESULTS.md) retain phase attribution,
provenance and limits. The broader eight-hour ExExt goal remains paused;
production stays unchanged. Author subsequently requires removal of ExExt CRC;
P08-P05/D01/D02 below own that next implementation boundary.

## Contract and boundaries

PT01 [x] — Freeze phase definitions and a minimal probe design. Inspect actual
reservation/offer, UART park, native byte runner, UART restore, completion/release,
VBlank service, return poll/fetch and packet publication. Record caller context,
clock scope, nesting and probe overhead. No per-byte probes or logging in timed
intervals. Prefer MOSlet RAM storage/formatting; retain only unavoidable resident
hooks in an explicit diagnostic profile. Stop for discussion if ROM fit requires
removing product behavior or if a safe observation cannot preserve semantics.

PT02 [x] — Implement the frozen probes and fixture. Reuse buffered 5/&C2
streams of 256, 4096, 4097 and 8192 bytes, one warm-up and five measured samples
per length. Keep P4 stream-r14 unchanged if eZ80 observations suffice; do not
substitute source HEAD, an uninstalled candidate or the old UART-only partner.
Record forward and reverse blocks, repeated polls, ISR work and nested intervals
without double-counting totals. Explicitly drain partial batches through EMOS.
No private application GPIO or transport ownership bypass.

PT03 [x] — Compile and run instruction-model/host checks. Verify ROM fit,
probe register/stack/IFF preservation, disabled-hook behavior, overflow refusal,
record capacity and interval interpretation. Compare the ordinary composition
with retained pre-probe bytes apart from build identity. Bind the MOSlet to the
exact diagnostic ELF and full ROM fingerprint. Commit controlled inputs before
hardware. These are CPU-model checks, not physical timing or emulator UI proof.

PT04 [x] — Acquire the free bench only for deployment/execution. Read current
local identity, installed receipts and bench constraints. Verify the exact paired
images and fixture by readback. Preserve mainboard fsim VDP, original startup,
all wiring and games. Select mode 3 only in temporary autoexec; no startup test.
Invoke each group explicitly from the admitted CLI. No browser video or active
HTTP monitoring during timed intervals. Collect byte dumps outside timing.
One complete group per length, with fresh completed-case repeats only for missing
integrity evidence. Never replay uncertain work. Compare endpoint times against
the preceding instrumented campaign as an overhead/context check, not an
identical-build causal experiment.

PT05 [x] — Validate all selected samples and report. Retain timestamps, callsite
identity, repeat origins, full 8192-byte proof, saturated/overflowed exclusions,
start/end and firmware hashes. Use the preceding integrity-only chronological
selection rule when a USB dump is incomplete. Show phase median/range in µs
and share of a clearly defined enclosing interval; distinguish inclusive/nested
intervals and unobserved time. Separate forward drain, receipt and query/reply.
Do not call elapsed cycles CPU utilization, payload-loop speed raw bandwidth,
or query completion render/scanout completion. Select the next optimization
from measurements and pause for Author discussion before implementing it.

PT06 [x] — Restore and independently verify the exact original UART pair and
38-byte startup, resolve known temporary sibling files, demonstrate CLI/input,
close collectors/listeners and release the bench. Preserve the documented
mixed-pair admission limitation and restore through a compatible pair if needed.
No new version tag or production promotion follows diagnostic results.

## Research précis and measurement design

1. Official read-only references: agon-docs commit
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
   [RST18 contract](../../../../../agon-docs/docs/mos/API.md),
   [GPIO mapping](../../../../../agon-docs/docs/GPIO.md);
   clean agon-mos v3.0.2 and agon-vdp v2.16.0. This work introduces no VDU API.
2. Reuse [completed measurement contract](STREAM-TIMING-R01.md),
   [physical results](STREAM-TIMING-R01-RESULTS.md) and
   [fixture](../../../tests/performance/stream_timing/README.md).
   PRT1 /256 gives nominal 72,000 counts/s, 13.889 µs/count and a 0.9102-second
   single-pass limit. MOS increments two coarse units per VBlank (~120/s here).
   Keep ordinary interrupts and clock source/divisor unchanged.
3. EMOS-owned implementation: `agon-emos/src/emos_exext.c` (queue, reservation,
   offer, VBlank service and publication), `emos_parallel_coordinator.c`
   (park/payload/unpark/completion), `emos_parallel_native_body.inc` (bounded
   byte runner). Calls can execute inside the real VBlank service as well as
   foreground output. Actual publication remains in real ISR context.
4. Use boundary probes with bounded RAM storage; no SD, USB or network output
   during timed intervals. An explicitly diagnostic-only hook may dispatch
   into exact-bound MOSlet RAM, armed only while that fixture owns PRT1 and its
   record storage. Preserve all registers/flags/IFF and disarm before saving or
   returning. Ordinary builds must contain no hook or diagnostic dispatch.
   Freeze actual sites and addressing once compile feasibility is established.
5. Retain probe/read controls; do not subtract an assumed constant overhead.
   If eZ80 intervals identify time waiting for EDP but not its internal cause,
   report that remaining boundary and propose a separate bounded P4 experiment.
   Do not silently enlarge this into a profiling framework.

## Following steps — not this tranche

P08-P02 [ ] — After phase results, CRC removal and Author discussion, consider UART shutdown
once at ExExt entry/restoration at exit. Both EMOS and EDP must preserve direction
ownership, bounded keyboard/query return opportunities and reset recovery. An
accepted contract/architecture amendment must precede that behavior change.

P08-P03 [ ] — After an approved implementation, repeat byte-verified comparisons,
then use existing finite Nurples, Rally and Aginvadors fixtures. No game change
or performance acceptance is implied by the current instrumentation approval.

P08-P04 [ ] — Author requested review after this tranche: remove the operator's
intermediate Legacy step when switching ExCom ↔ ExExt if EMOS can safely perform
that handover itself. Review the existing transition guard, both processors'
ownership/release ordering and failure recovery before proposing a change.
This review is queued; phase acquisition must not change mode-switch behavior.

P08-P05 [ ] — Author requires no CRC in ExExt (2026-10-11). Prepare the next
bounded implementation contract to remove CRC generation and validation from
both EMOS and EDP's ExExt transport control exchanges. Do not substitute a faster
CRC or another per-block checksum. Preserve physical ownership/handshakes,
length/direction interpretation and required packet framing. Byte checking in
the host qualification fixture remains outside transport timing. Resolve paired
wire-format/version compatibility before deployment, compile both components,
then reuse these exact byte-verified streams. Current phase instrumentation
measures the preceding CRC-bearing candidate, not this accepted future design.
No implementation starts in the phase tranche; pause for Author discussion.

## Accepted decision and remaining design boundary

P08-D01 [x] — No CRC in the ExExt transport. Author explicitly rejected the
agent's recommendation to accelerate the existing CRC routine. Remove the
transport CRC work instead. Recorded in ADR-0026 and the normative architecture.
This is a design requirement; no CRC-free firmware has been built or tested.

P08-D02 [ ] — Define the paired CRC-free control envelope/version handling.
Resolve how EMOS/EDP reject or avoid mixed protocol pairs and how the unused
trailing CRC fields are treated or removed. Do not add an alternative checksum.
This does not authorize unrelated changes to ExCom or SD file verification.

P08-H01 remains deferred in the parent task: external latches/transceiver/FIFO
investigation follows a concrete operation/cost to replace, not a chip-first guess.

## PT01 probe definition — frozen before physical execution

Sixteen unique probe aliases share one guarded ROM leaf. C call boundaries
record caller PCs; the fixture builder derives their names from original object
relocations and verifies each final CALL byte. The RAM jump vector is &B0020
in the diagnostic MOSlet header padding, armed through one reset-zero EMOS byte.
No hook executes before admission/fingerprint checks or after results saving begins.
The RAM recorder masks only its bounded append, preserving all registers, flags
and IFF. Each record retains raw PRT1, caller PC and current offer length/direction.
Overflow disarms acquisition and invalidates the sample. No native per-byte probe.

| Boundaries | Interval scope |
|---|---|
| reserve_begin → reserve_end | EMOS keyboard/UART serializer reservation |
| reserve_end → offer_begin | Offer construction and optional session renewal |
| offer_begin → coordinate_begin | UART offer/ACK plus coordinator admission guards |
| coordinate_begin → park_end | Coordinator setup and successful UART drain/park, including pending polls |
| park_end → payload_begin | Electrical entry/release/arm handshake |
| payload_begin → payload_end | Guarded native runner, including preclocks, byte loop and EOF cleanup; not isolated raw byte-loop bandwidth |
| payload_end → unpark_end | Electrical return handshake plus UART restoration |
| unpark_end → completion_begin | Remaining handover steps before matched receipt |
| completion_begin → completion_end | Matched completion exchange |
| poll_begin → poll_end | Return-availability UART control exchange and reservation/release |
| service_begin → service_end | Inclusive real VBlank synchronous service; nested block/poll work must not be added twice |
| publish_begin → publish_end | Actual buffered packet publication in the real VBlank handler |

Post-completion owner release/queue handling and time outside these intervals
remain visible as gaps in enclosing endpoint timing. Exact wire-drain M02 stays
in the preceding frozen campaign; this profile measures native runner completion,
not its last electrical edge. Return blocks have the same phase probes as forward
blocks, distinguished by the admitted offer at offer_begin.

## Offline checkpoint

The diagnostic EMOS compiles at 131,063 bytes (9 free), with all mandatory
link/baud/owner checks. Source 291ac9e; P4 unchanged. Its ordinary control
compiles at 130,968 bytes and matches the retained preceding ordinary image
apart from six timestamp bytes. Thus the diagnostic profile costs 95 resident
ROM bytes; no product function is removed. The exact-bound MOSlet/recorder
compiles within 32 KiB at &B0000. Three thousand seventy-two actual linked
probe cases cover all AF flags, SP/registers/IFF, disabled no-read behavior,
low/high PRT latch, saturation values, final capacity slot and overflow disarm.
Existing native/output/real-VBlank checks and eight host tests pass.
This was the pre-hardware checkpoint; the completed physical results above
supersede its acquisition boundary. No speedup or production acceptance.

PT04 setup correction: ExCom→ExExt is intentionally rejected by
`emos_request_mode`; the new runner initially omitted the intermediate Legacy
request after mode-3 preparation. Zero fixture invocations occurred. Corrected
the runner to enter Legacy before ExExt; ordinary setup-only bundle discarded.
No firmware, reset or protocol change and no uncertain test replay.

The corrected transition succeeded, but the runner initially rejected retained
old error text under `--keep-display`. Fresh cleared STATUS confirms ExExt.
Moved the assertion to that fresh authoritative STATUS; still zero fixture
invocations before correction and no firmware change/reset.

Subsequent setup-only assertion encountered a wrapped CLI command at the long
fixture-directory prompt. Changed to the root before fresh STATUS/CD checks;
zero invocations in that discarded setup attempt. No reset or firmware change.

## Physical closeout

Five completed invocations save 30 original zero-flag endpoint/phase rows.
Two USB dumps are incomplete; one matching fresh-repeat sample supplies missing
proof under the frozen integrity-only rule. All 24 selected rows/full buffers
validate. EMOS CRC/construction/offer/completion control intervals dominate;
the next offer after a full block also takes an extra ~33–35 ms. These probes
do not isolate that interval's EMOS/P4 share. Park/restore alone is small.

Author rejects CRC optimization and requires no CRC in ExExt. Stock MOS/VDP
ordinary UART has no such check; the project introduced it in custom control
packets. This measured candidate retains those checks; no CRC-free image is
claimed. Keep required electrical ownership/handshakes and host byte proof.

Exact original data-r20 P4/all four segments and old EMOS/full 128 KiB ROM
verify, original 38-byte startup readback restored, actual Legacy CLI and five
seconds of stable input pass. Listener/collector/test stopped, reset released;
bench released 2026-10-11T21:30:45Z. Mainboard fsim VDP, wiring, games and
production unchanged. Old P4 lacks the newer pad-release log marker; waiting
for it was an installer setup mistake, not a product failure. No extra reset
or flash was needed. Stop for next-tranche discussion.
