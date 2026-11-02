# P4 admission progress while buffered bytes remain

The Author authorizes the fix after the boundary investigation identifies P4
admission serialized behind its inline byte-update loop. Service the existing
P4 I/O owner at bounded read intervals while buffered bytes remain. Preserve
EMOS ownership, ordered bytes and physical handover; measure earlier data
admission separately from the command's remaining processing/reply cost.
Pi5/bench only; Oryx remains offline. Restore the complete incoming pair after
qualification. This is experimental development, not production acceptance.

## Scope and decision register

1. AP-D01 — Accepted by “proceed with the fix”, 2026-11-02: keep the existing
   P4 parser/I/O task and its I/O-only progress entry. No additional task, ISR,
   wire command, carrier/version change, queue growth or EMOS source change.
   This applies the ownership already selected in ADR-0026; it introduces no
   new architectural owner or authority. P08-D02 remains partial/open.
2. Initially service after at most 64 queued bytes, and immediately on empty
   input or pending physical ownership. This is a byte-work bound, not a
   calibrated wall-clock deadline. No clock call or logging per payload byte.
3. While an admitted native block owns the pins or completed staging has not
   retired, progress that same owner and withhold parser consumption. Reuse
   existing deadlines and idle/pending behavior; never infer release from time.
4. Nested progress never enters processNext, VDU mode changes, application
   callbacks or another transport writer. Defer ordinary console transitions
   until the outer parser boundary. Preserve queued control envelopes and
   normal EMOS STOP/exit fencing. Refuse reentrant reads from progress itself.
5. Preserve the 8 KiB RX/TX queues, provisional data lifetime, backpressure,
   split reads, setup/peek ordering, cancellation, Legacy/ExCom behavior and
   mainboard VDP. No native-guard coarsening, buffer-adjustment optimization,
   DMA changes, new checksum/CRC, autoexec edit or SD unmount.

## Bounded research precis

1. Read-only official references remain agon-docs
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, MOS v3.0.2
   `8336409351ee5314e02801a7b72a4f1bb5282519`, VDP v2.16.0
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`.
   agon-docs [Buffered commands](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Buffered-Commands-API.md) command 5 specifies per-byte
   multi-target/operand ordering; [MOS API](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md) RST10/RST18 specify the
   unchanged byte/stream output contract. Do not replace those semantics.
2. [Boundary results](BOUNDARY-LATENCY-RESULTS.md) and its portable evidence
   retain exact baseline sources/bytes, phase binding and observer limits.
   The long interval occurs before recognition of the next offer. Once P4
   recognizes it, observed acceptance takes0.073–0.200 ms. Removing both P4
   observers reproduces45.597–47.556 ms waits. This fix does not remove all
   command-processing work or establish generic bulk/file-transfer throughput.
3. `console_stream.hpp::read()` currently calls progress only on empty RX;
   `readBytes()` has an existing pending-native/no-idle-sleep path. Reuse both
   through one byte-budget mechanism rather than a second transport engine.
4. `console_hardware.inc::runConsole()` already has `step(false)`: coordinator,
   serializer and control recognition without processNext. Inspect nested
   consoleControl calls as ordinary PREPARE can reset the VDP context; defer
   those transitions until `step(true)` rather than reentering a command.
5. `ParallelControl::uartTransitionAllowed()` requires UART phase and neither
   pending nor unretired completion. `ParallelVduStream::retire()` publishes
   only physically returned bytes. `canOffer()` owns existing capacity checks.
   Do not grant publication/read access from a descriptor or native callback.
6. Maintained root P4 display sources differ from the exact tested R25
   composition. Implement transport changes in maintained `vdp/`; apply only
   that frozen delta to a clean project-owned checkout of source
   `03e428f3bb87951bd4f296ccb36ef677ef1db617`. Native build/review must preserve
   pinned R25 display, SDK, board, compiler, USB hosts and dependency inputs.
   No renderer rebase or new production selection by Git HEAD assumption.

## Work and gates

AP01 [x] — Freeze/push task/TODO before implementation. Verify source ownership,
reference identities and current bench reservation. Retain all prior evidence.

AP02 [x] — Add bounded progress and ownership gating in the actual Stream availability, read,
peek and bulk paths; defer nonparallel console transitions during nested I/O.
Run real-source host checks with SDK boundaries faked, including queued-data
admission, physical-return gating, exact order, full queues, split/cache/prefix,
wrap/cancel/fault/timeout, reentrant callback refusal and unchanged UART builds.
Demonstrate the previous empty-only policy fails the new admission regression.

AP03 [x] — Freeze source and build an identified native P4-PC candidate from the
exact matched composition. No boundary observer/per-lock timers. Validate full
native graph/options, changed source closure, ROM/ABI-bound unchanged phase
fixture and the existing mandatory ownership/coordinator regressions. Record
source/build/artifact hashes; no uncommitted identified input or generated-source
edit. Experimental stream r18 identifies the initial progress change; r19 adds the
required availability integration gate before the four-case comparison.

AP04 [x] — Establish fresh actual CLI and unchanged load-only startup, install
and independently verify the paired candidate with the exact retained phase
EMOS/fixture. Execute four separately invocable mode 0 cases256/4096/4097/8192,
one warm-up plus five measured records each. Explicit RUN only; preserve entry
routes/modes, settling and cursor cleanup. No HTTP during timed work. Keep full
actual buffer-byte proof and all failed acquisitions; recover independently
and run required marked-case controls with capture routines absent.

AP05 [x] — Compare retained baseline and candidate side by side: next-offer
latency, data-block local completion, native payload/handback and ordered reply
separately. Define units, scope, percentage and ranking; retain all samples,
calibration/probe limits and actual decoded bytes. A shorter sender wait alone
is not faster command execution. Verify queued-byte/native exclusivity with
no replay, corruption, queue overflow or ownership failure.

AP06 [x] — Restore exact incoming full P4 flash/EMOS ROM and largest changed
application erase span. Independently verify startup/listener unchanged,
mainboard VDP untouched, both original modes, Legacy/input/actual CLI and cursor
controls. Release readers/transfers/reset holds. Update task/TODO/log and publish
source/evidence. Stop before broader games, canonical all-mode qualification,
production selection/tag or unrelated parser/locking optimization.

## State

Task frozen/pushed as 3e5bd59d before implementation. Real-source admission and
mutation regressions pass under ASan/UBSan, together with split-upload/no-idle-
sleep, UART-owner/reset, mode lifecycle, actual queue/backpressure, admission,
physical handover/coordinator and native-build-selection checks. The read/peek/
bulk paths share a 64-byte consumed-queue budget and native/staging gate; nested
reads cannot reenter. Nested dispatch defers console lease version1 while keeping
controller version2 and parallel format4 I/O serviceable. No wire/EMOS change.

Author authorization includes monitored
bench qualification, standing recovery and exact restoration. It does not
select a production version or accept firmware before review. Use current
installation/reset/rollback/test/SD procedures and fresh local output identities;
previous task helpers are evidence and must be adapted before any reuse.

## Integration gotcha before larger cases

The retained parser converts its top-level nonblocking read directly to uint8_t
when available() reported input. Gating only read() could therefore turn a
pending native transfer's temporary -1 into VDU255. The first r18 256-byte case
passes six exact buffers, but source review identifies this uncovered edge
before the larger cases. Add the same owner/progress gate to available(); only
the owning task can admit a block, so a positive availability result and its
following nonblocking read stay consistent. The actual-source regression runs
both caller forms and proves that removing just this gate fails the top-level
parser assertion. Callback-recursive availability also reports zero. R18's
bounded result is retained separately; repeat the full four-case comparison on
r19. EMOS/fixture remain byte-identical. No renderer or wire change is added.

## Completion — 2026-11-02

AP01–AP06 are complete. [Results](ADMISSION-PROGRESS-RESULTS.md) and
[portable evidence](ADMISSION-PROGRESS-EVIDENCE.json) retain the matched R19
source/artifacts, exact bytes, raw phases, integrity-only selection, all failed
acquisitions and required no-dump control. Following-offer medians after a full
block fall from 46–47 ms to 1.6–1.9 ms. Local data completion falls from 83.00 to
38.36 ms at 8192 bytes and from 66.96 to 22.36 ms at 4097 bytes; ordered reply
medians remain essentially unchanged. No CPU/parser or rendering speedup follows.

Thirty-six R19 rows have zero flags; 24 selected rows have complete actual
8192-byte proof. Original and first-repeat 4097 repeat 2 dumps are short and stay
failed whole acquisitions. Only that selected index uses the last labeled
acquisition's corresponding row/phases, selected by integrity alone. Its matching
60-second control has the entire debug body absent and passes six zero-flag
rows/no panic/actual CLI; it does not qualify bytes or pixels or prove a cause.

Complete incoming 16 MiB P4 flash and 131072-byte EMOS ROM are independently
restored exactly. Startup/listener and mainboard VDP are unchanged; both mode 0
settings, Legacy, input, cursor controls and actual CLI handback pass. Fresh
resource audit finds both serial devices unowned and all four reset holders
released/exited. Bench released. Source changes and isolated control are
published; no production promotion/tag. Stop before another transport cut,
parser/native-lock optimization, games or all-mode qualification. P08-D02,
warm-reset reliability and original R25 wide-mode limitations remain open.

## Reference closure

1. Official VDP v2.16.0 [buffer adjustment implementation](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h)
   retains per-byte operation/operand order. Its [stream processor](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_stream_processor.h)
   distinguishes retrying parameter reads from nonblocking command reads after
   availability. The latter requires the availability gate described above.
2. Maintained [Stream adapter](../../../vdp/video/extender/transport/console_stream.hpp)
   and [sole parser/I/O owner](../../../vdp/video/extender/transport/console_hardware.inc)
   implement bounded service and nested dispatch. The unchanged
   [physical control](../../../vdp/video/extender/transport/parallel_control.hpp)
   and [VDU queue](../../../vdp/video/extender/transport/parallel_vdu_stream.hpp)
   own UART-return/completion and provisional-data retirement contracts.
