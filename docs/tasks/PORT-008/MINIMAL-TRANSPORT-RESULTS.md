# PORT-008 — Minimum transport review results

## Executive summary

The candidate does substantially more than replace UART with parallel bytes.
Stock MOS hands bytes to UART and receives packets through its receive interrupt.
Our candidate adds transactional blocks, repeated UART control exchanges and
VBlank-driven transmission/reception. CRC is removable outright. A separate
completion-message round trip is a strong removal candidate because the physical
handover already waits for native completion, DMA cleanup and reciprocal pad
release. Length, direction, receiver readiness and electrical ownership remain
necessary for the current fixed-count, shared-wire implementation.

CRC removal alone will not establish stock behavior. The candidate delays partial
output until VBlank, publishes at most one key event per VBlank and refuses output
with interrupts disabled. Those are observable software departures. Preserve
stock parsing/effects and correct these scheduling/admission differences in
separately bounded code cuts. First recommend removing ExExt transport CRC in
both owners while retaining the tested electrical path; then remove the redundant
software completion exchange. No product source, firmware or bench state changed
in this review. No speedup is claimed. Author discussion precedes implementation.

## Scope and exact source baseline

The [review contract](MINIMAL-TRANSPORT-REVIEW.md) TR01–TR04 is complete. This
is a source review of clean trees, not a rebuilt or installed-firmware test.

| Reference | Selected identity |
|---|---|
| Official documentation | agon-docs `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` |
| Official MOS | v3.0.2, `8336409351ee5314e02801a7b72a4f1bb5282519` |
| Official VDP | v2.16.0, `c7ac293d2aa81ddfa693390549bcd909069c8fc3` |
| Maintained EMOS | `a3a03c3790a8d7459f71a06ba44e007e01a999a2` |
| Maintained Extender | `2e895961db551199e964fb7faeb8cb333abe6779` — frozen review contract |

Official MOS/VDP references remained clean at their release tags. The experimental
EMOS profile selects `emos_exext.c` and excludes the obsolete `emos_parallel.c`
and `emos_parallel_engine.c`; the latter files are not this candidate's live
output path. These source revisions are not asserted to reproduce the retained
stream-r14 measurement image, whose original dirty source identity is preserved
in the [measurement evidence](STREAM-TIMING-R01-RESULTS.md).

## Stock paths to preserve

1. **eZ80 output:** stock `src_startup/vectors16.asm` RST10 calls
   `UART0_serial_PUTCH`; RST18 loops over the caller's bytes or delimiter and calls
   the same leaf. `src/serial.asm` checks UART enable, optional CTS and transmitter
   holding-register readiness, then writes the byte. The holding-register wait
   can retry; this is readiness polling, not payload retransmission. There is no
   block envelope, sequence, CRC, receiver receipt or VBlank flush. Return does
   not prove the last byte has left the physical UART or that VDP has executed it.
2. **VDP input/output:** stock `VDUStreamProcessor` uses a `Stream` for reads and
   writes. UART setup provides a 256-byte RX ring and hardware flow control.
   `readByte_t` can wait up to the configured 200 ms for an operand. `send_packet`
   emits `command|0x80`, one-byte length and body, then invokes the stock sent
   callback. Preserve packet/event order and callbacks; transport return does
   not by itself mean the display has refreshed.
3. **eZ80 receive:** stock `_uart0_handler` reads a byte and invokes
   `vdp_protocol` with interrupts masked. That parser retains partial packet
   state and dispatches the stock handlers on completion. KEY invokes
   `user_kbvector` before sysvar/keymap effects. Stock VBlank updates the MOS
   clock; it does not negotiate graphics blocks or fetch keyboard packets.
4. **Physical distinction:** stock UART has independent transmit/receive paths.
   Our eight data wires carry one direction at a time and overlap UART pins.
   P4 must not drive them while eZ80 drives them. EMOS owns CLOCK/VALID in both
   directions; P4 owns READY. A reverse opportunity and direction handshake
   therefore have a physical justification. Their present software envelopes,
   transaction identities and frame-rate scheduling do not follow from stock.

Sources: official [MOS API](../../../../../agon-docs/docs/mos/API.md),
[packet contract](../../../../../agon-docs/docs/vdp/System-Commands.md),
[RST handlers](../../../../../agon-mos/src_startup/vectors16.asm) lines 120–155,
[serial](../../../../../agon-mos/src/serial.asm) lines 78–110 and 204–215,
[receive/VBlank](../../../../../agon-mos/src/interrupts.asm) lines 43–80,
[packet parser/effects](../../../../../agon-mos/src/vdp_protocol.asm) lines 70–201,
[VDP Stream](../../../../../agon-vdp/video/vdu_stream_processor.h) lines 262–290,
337–350 and 516–529, [UART setup](../../../../../agon-vdp/video/vdp_protocol.h).

## Candidate paths and the block boundary

1. **Entry:** `emos.c` prepares/commits the existing console route, including its
   version-1 activation controls. `emos_exext_start` then negotiates a second
   parallel session and sends START. The second session carries a transaction,
   challenge/nonce and sequence. Entry therefore contains both existing display
   activation and extra transport activation, not just a peripheral selection.
2. **Forward:** `serial.asm` preserves the public register ABI and routes to
   `emos_exext.c`. Bytes append to 4096-byte RAM storage. Full storage flushes
   synchronously; a partial batch normally waits for VBlank. `transfer` reserves
   the UART owner, constructs/seals OFFER, waits for its ACK and enters the native
   coordinator. The coordinator drains/parks UART, performs the electrical
   handover, clocks bytes, releases/restores pins and exchanges COMPLETE/ACK.
3. **P4 forward publication:** the P4 coordinator arms fixed-count PARLIO DMA
   before granting READY. Native completion stops the peripheral and releases
   pads. Even after electrical handback, `ParallelControl` keeps the buffer
   provisional until the separate COMPLETE request; only then can
   `ParallelVduStream::retire` append it to the parser's RX ring. The retained
   VDP parser still consumes ordinary command bytes through `ConsoleStream`.
4. **Reverse:** stock-shaped P4 packet writes append to an 8192-byte TX ring.
   EMOS sends POLL, obtains the pending length, caps the fetch to 256 bytes and
   performs another full OFFER/native/COMPLETE cycle. EMOS stages up to 512 bytes,
   gathers complete logical packets and feeds the existing keyboard/console
   handlers in a real VBlank interrupt. Publication stops when one KEY event
   changes `keycount`; any following packet waits for another VBlank.
5. **4096→4097:** exactly 4096 bytes takes one immediate full-block flush. 4097
   bytes also leaves one byte queued for a later partial flush; an ordered query
   also needs its tail delivered and a reverse fetch. Both block overhead and
   VBlank scheduling matter. Source confirms these mechanisms; it does not assign
   the measured additional ~33–35 ms to a particular processor or instruction.
6. **Parser progress and input:** P4 `ConsoleStream` services link progress during
   operand/block reads without reentering command execution. That is necessary
   to avoid deadlocking a command split across transfers. The outer P4 loop
   suppresses USB pumping/key intake while a block is pending, which currently
   spans the software receipt wait as well as physical exclusivity. Retain pad
   ownership; do not treat the whole receipt lifetime as inherently input-exclusive.

The current two block-control exchanges add 38 request and 36 reply bytes per
block, before the separate 37-byte POLL exchange: each request is a three-byte
carrier plus sixteen bytes; each reply is a two-byte packet header plus sixteen
bytes. These are counts from code, not measured duration or predicted speedup.

## Removal and retention matrix

Order below prioritizes the requested stock-behavior boundary and actionable
removals. Measured performance ranking remains in the frozen phase report;
these rows are not independently measured cost shares.

| ID | Candidate operation | Disposition | Specific reason / affected owner |
|---|---|---|---|
| MT01 | CRC generation/checks, including shared `exchange` and ACK validation | Remove | No stock counterpart or physical ownership function. EMOS `emos_console.c`, parallel headers and `emos_exext.c`; P4 parallel headers/handover/Stream request. Do not replace with another integrity algorithm. |
| MT02 | VBlank-only partial output flush and long synchronous VBlank transfer service | Change | Stock output hands bytes to transport during the call. Frame-clock gating is software policy; the shared wires do not require it. EMOS queue/service must stop imposing a frame barrier. |
| MT03 | One-key-per-VBlank publication | Change with receive scheduling | Stock dispatches received packets in its receive ISR. Current policy was a workaround for bundling down/up into one interrupt and MOS's latest-event latch. Removing the cap while still bundling events would recreate that failure; provide stock-shaped receive opportunities instead. |
| MT04 | Refusal of output when caller IFF is off | Resolve before stock-equivalence claim | `route_write_byte/stream` rejects `!irq`; stock PUTCH does not require enabled interrupts to load the UART. Current control replies require UART ISR progress. This is a dependency introduced by this design, not a general GPIO requirement. |
| MT05 | COMPLETE/ACK and delayed parser publication | Remove software round trip after preserving local completion order | P4 native completion, DMA cleanup, pad release and reciprocal UART return already precede `payloadReturned`. Retire successful storage once those actual facts hold. Failure must remain fenced; never manufacture success from a timeout. No need for a second software receipt solely to re-prove completed transfer. |
| MT06 | OFFER/ACK with entire mirrored identity | Simplify | Current fixed-count DMA requires byte count/direction and available storage before clocks. Receiver-ready confirmation is necessary. Sixteen-byte descriptor echo, nonce and sequence are not intrinsic to those requirements. Keep the existing electrical handshake until its replacement is tested. |
| MT07 | Transaction/challenge/nonce, sequence and wrap renegotiation | Remove from minimal link design after preserving reset/drain ordering | Stock stream has no transaction/replay protocol. Local ownership, empty queues and the accepted physical reset-release fence must replace dependence on these fields; do not merely delete comparisons while retaining stale queued control. |
| MT08 | Full POLL request/reply on every serviced VBlank | Simplify; reverse availability remains necessary | P4 cannot send unclocked parallel data. EMOS needs a reverse opportunity even while foreground is idle. Pending length can share a necessary control reply; an idle request mechanism still needs definition. No unsupported claim that RAM flags communicate peer state. |
| MT09 | Physical UART drain/park, direction/release/arm and restoration | Retain for current phase-based link | UART and parallel share conductors. Exact UART-empty, pad release and DMA stop/arm facts prevent simultaneous driving. Permanent UART shutdown is a separate later choice, not selected here. |
| MT10 | Byte count, DMA bounds, queue space and READY/backpressure | Retain | These govern byte delivery and hardware storage, not payload correctness checks. P4 must arm before EMOS clocks; EMOS clocks reverse bytes only after P4 grants readiness. |
| MT11 | eZ80 GPIO byte loop, atomic Port-D writes, P4 retained DMA units/filter and board power setup | Retain in first code cuts | These implement the working physical link and processor-specific peripheral requirements. Existing native runner is a small measured share. Inactive synchronization clocks remain until separately proved unnecessary. |
| MT12 | RX/TX storage and copies | Retain necessary storage; simplify lifetime/copies later | UART also buffers bytes, and DMA storage cannot disappear while hardware owns it. Exact 4096/8192/512 sizes and duplicate copies are implementation choices. Removing completion staging should not require rewriting VDP or reallocating buffers per transfer. |
| MT13 | Complete-packet staging and `need_more` before shared parser | Simplify only with separate control/data parser state | Stock packet parser already handles partial bytes. Current UART control and logical reply bytes share receive state; feeding a partial logical packet then a control ACK would corrupt it. Separate link recognition from logical parsing before eliminating this workaround. |
| MT14 | STOP/drain and key-arrival race handling | Retain the ordering requirement; simplify envelope | A key can arrive between pending-count observation and exit. EMOS/P4 must finish or explicitly preserve queued return bytes before changing transport. Stock packet/effect order must survive. |

Ordinary ExCom activation currently uses the same CRC helper. Do not globally
delete that helper and silently alter unrelated ExCom/SD contracts. The first
code cut must explicitly distinguish the parallel transport branch, including
all its entry/poll/stop/error exchanges. Existing console activation remains
an identified setup dependency; retaining it does not make ExExt setup identical
to stock or wholly free of project activation machinery.

## Minimum-path sketch and proposed code order

The target data path is:

```text
Application's unchanged MOS output call
  → EMOS transport leaf
  → minimum count/direction/receiver-ready admission
  → existing electrical handover and native byte delivery
  → local completion and storage publication
  → unchanged VDP Stream/parser

Unchanged VDP packet production
  → bounded P4 return storage and reverse-availability indication
  → EMOS-owned reverse clocking at a receive opportunity
  → unchanged logical packet parsing/effects in the proper interrupt context
```

There is no CRC, retransmission protocol, per-block challenge or separate
software completion receipt in that target. DMA count and ownership facts remain.
This is the proposed endpoint, not a claim that deleting four calls achieves it.

1. **First code cut — CRC removal:** remove parallel CRC work in both owners,
   including shared send/reply paths. Preserve current electrical phases and
   buffer lifetimes to isolate the change. Recommend initially retaining the
   fixed carrier width with the former CRC slots reserved/zero, then removing
   those slots when the control carrier is shortened. This costs two padding
   bytes, not CRC work, and avoids editing every shared fixed-length recognizer
   in the same cut. Distinguish the paired format using its existing version
   discriminator; no new negotiation service. Exact protocol identity and
   deployment compatibility belong to P08-D02 before implementation/deployment.
2. **Second code cut — completion:** publish/retire successful storage at the
   existing proved physical return boundary and remove COMPLETE/ACK from EMOS
   and P4. Keep actual failure/cleanup ordering, not the receipt state machine.
   This also shortens the interval during which P4 suppresses key ingestion.
3. **Following bounded cut — link admission:** reduce offer metadata to what
   fixed-count DMA and direction/readiness need; collapse duplicate session
   negotiation into committed mode/physical ownership. Explicitly drain/reset
   old controls and queues. Consider return-pending metadata in an already
   necessary reply instead of an extra poll. Preserve an idle return opportunity.
4. **Stock-behavior completion:** replace VBlank-driven transfer waits and bundled
   publication with a concrete receive schedule that preserves real interrupt
   context, stock packet effects and caller IFF behavior. Existing source does
   not establish an available asynchronous GPIO interrupt mechanism; do not
   assume one or silently repurpose VBlank/another application's timer. That
   scheduling choice remains part of P08-P05/D02 discussion. CRC-free timing
   can be measured earlier, but must not be labelled full stock equivalence.

No permanent UART shutdown, mainboard VDP modification, game modification or
new electrical circuit is required to execute the first two proposed code cuts.

## Reuse of existing validation

1. EMOS full builds/link gates must cover ordinary and experimental profiles,
   ROM size, output ABI/register preservation and boot ownership. Update the
   paired host/linked control tests where they currently demand CRC rejection;
   do not retain that behavior merely to keep a historical test passing.
2. Reuse [paired control tests](../../../tests/parallel_control_test.py),
   [block controls](../../../tests/parallel_block_control_test.py),
   [P4 Stream](../../../tests/parallel_vdu_stream_test.py),
   [native coordinator](../../../tests/parallel_native_coordinator_test.py)
   and EMOS `test_exext_stream.py` plus linked `exext_output`/`exext_irq` tests.
   Exercise full/residual boundaries, reverse fragments, callback edits,
   down/up order, idle input, missing peer and reset/direction recovery.
   Existing tests intentionally encode one-key-per-tick/nested-output refusal;
   passing them does not establish stock-equivalent scheduling.
3. Rebuild exact-ROM-bound timing fixtures for changed images. Reuse the
   [matched four-payload fixture](../../../tests/performance/stream_timing/README.md)
   unchanged in workload: 256/4096/4097/8192 total stream bytes, PRT timing,
   ordered query/reply and full-buffer host comparison outside measured intervals.
   Compare original UART and each accepted code cut without combining different
   rendering or output workloads. Phase probes are optional diagnostics, not
   product firmware requirements.
4. Hardware execution is later, under a frozen code/deployment contract and a
   free bench. Preserve current verified UART rollback and restore it after
   the bounded matrix. Gameplay comparisons follow transport correctness/timing.
   This review ran no builds, executable tests, emulator or physical tests;
   only source/reference/link/diff checks apply to its deliverable.

## Maintained source map

Paths are relative workspace links; line locations refer to the clean source
baseline above. No machine-specific filesystem or device mapping is included.

| Owner / concern | Source and relevant locations |
|---|---|
| EMOS selected profile | [exext-stream-candidate.mk](../../../../agon-emos/port/exext-stream-candidate.mk), source filters |
| EMOS byte/stream ABI | [serial.asm](../../../../agon-emos/src/serial.asm), 282–410 |
| EMOS queues, transfer, reverse and VBlank | [emos_exext.c](../../../../agon-emos/src/emos_exext.c), transfer 52, flush 80, fetch 85, poll 103, start/stop 114/130, writers 154/176, publish 193, tick/service 217/239 |
| EMOS CRC/control | [emos_console.c](../../../../agon-emos/src/emos_console.c), exchange 57, reply 82, admission 205, session 246, offer 266, complete 275, stream 289; [wire](../../../../agon-emos/src/emos_parallel_wire.h), [session](../../../../agon-emos/src/emos_parallel_session.h) |
| EMOS physical coordinator/bytes | [coordinator](../../../../agon-emos/src/emos_parallel_coordinator.c), 16–96; [native assembly](../../../../agon-emos/src/emos_parallel_native_body.inc) |
| EMOS receive/context | [keyboard](../../../../agon-emos/src/emos_keyboard.c), publish 51, tick 108, dispatch 148, reserve/park/unpark/release 372–415; [service bridge](../../../../agon-emos/src/emos_exext_io.asm), [interrupts](../../../../agon-emos/src/interrupts.asm) |
| P4 block control/publication | [parallel_control.hpp](../../../vdp/video/extender/transport/parallel_control.hpp), request 21, returned 64, takeCompleted 70; [parallel_vdu_stream.hpp](../../../vdp/video/extender/transport/parallel_vdu_stream.hpp), request 35, canOffer 57, accepted 62, retire 68 |
| P4 physical phases/native DMA | [coordinator](../../../vdp/video/extender/transport/p4_block_coordinator.cpp), [handover](../../../vdp/video/extender/transport/p4_parallel_handover.cpp), [native payload](../../../vdp/video/extender/transport/p4_native_payload.cpp), arm 44, TX 104, RX 153, finish 296 |
| P4 retained parser integration/input | [ConsoleStream](../../../vdp/video/extender/transport/console_stream.hpp), [single owner](../../../vdp/video/extender/transport/console_hardware.inc), control 83, step 288, retire 338, pending gate 381, UART recognizer 450, input/parser 491–501 |

## Review boundary

P08-D02 remains open for the paired carrier/version and minimal control choice.
The receive-scheduling issue is material to the requested stock behavior and is
recorded here under P08-P05; it is not silently waived as a timing difference.
Review findings change no accepted architecture by themselves. Discuss the
recommended first code cut before implementation. The bench remains released,
the installed UART pair/startup unchanged, and production unchanged.
