# PORT-008 LC02 — Native coordinator binding

## Executive summary

Author authorized LC02 on 2026-10-09 at high reasoning effort. Bind existing
native leaves and UART reservations to the shared handover owners. This is a
private, off-bench integration tranche: no mode command, application API,
automatic SD transport, physical activation, or production change. Pause with
software/build evidence before preparing a separate bounded bench fixture.

LC02-A [x] — P4: use the sole UART/ISR core. Fence ordinary parser, keyboard
serializer and service producers immediately after block admission. Drain the
already queued ACK through the actual FIFO/shift register. Park only after
EMOS's held release request proves peer quiet and the parser/ring/FIFO are at a
boundary. Bind exact retained descriptor/buffer to native PARLIO; retain DMA
and callback lifetime on cleanup failure. Enforce deadlines through return;
restore only after local and reciprocal pad release. Preserve normal queued
keys; invalidate them only on fault/recovery. No unsolicited P4 request.

LC02-B [x] — EMOS: use its boot owner's actual handover, existing foreground
reservation, packet framer, bounded deadline/fuse, UART parking and assembly
payload loop. Exclude the boot monitor only while this foreground coordinator
owns entry/block/return. Permit reciprocal unpark only at the proven return
phase; retain the serializer reservation through matching completion status.
Reject nested/IRQ-disabled/unadmitted calls. Faults invalidate admission and
fence pads; no timed UART fallback. Keep native coordination private and
unregistered. A future qualification caller must separately negotiate/admit;
this tranche adds no supported bypass or formal ExExt commitment.

LC02-C [x] — Exercise actual coordinator and native/parking adapters with
modeled SDK/register boundaries, both directions and repeated blocks. Check
packet/shift-register delays, retained keys, exact bounds, wrong core, failed
SDK cleanup, cancellation, phase stalls/wrap and stale completion. Reuse paired
handover/control tests and actual linked eZ80 execution where applicable.
Record which physical inputs remain modeled. Do not claim electrical timing.

LC02-D [x] — Build complete ordinary/private firmware through maintained
wrappers, preserving all link inventories and 128 KiB ROM guards. If the
coordinator exceeds EMOS ROM, retain the refused map and stop before another
utility extraction or hardware activation. Record exact source/artifact hashes,
ROM accounting and monotonic host durations. Update parent and component-owner
records; pause for Author review. Preserve existing uncommitted emulator-coupled
work and unrelated checkout dirt.

## Research and implementation bounds

Reuse [LC01](LIVE-COORDINATOR-LC01-RESULTS.md), [handover](HANDOVER.md),
[block control](BLOCK-CONTROL.md), [native payload](NATIVE-PAYLOAD.md) and
[UART parking](UART-PARKING-RESULTS.md). Official GPIO documentation was
reviewed again; reference baseline remains agon-docs
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, MOS v3.0.2, VDP v2.16.0.
No new MOS/VDP wire contract is invented. Pinned IDF 5.5.5 remains the native
SDK authority. The installed ordinary pair and production selection remain
untouched. P4 buffer provisioning/receipt consumption belongs to a subsequent
private qualification caller; an unprovisioned P4 must reject offers.

## Resumed software validation — 2026-10-09

Author resumed the paused tranche. All A–D items pass within this off-bench
scope; [results](LIVE-COORDINATOR-LC02-RESULTS.md) and the portable index retain
exact evidence and limits. Both complete ordinary/private P4 and EMOS builds
pass. The private EMOS image uses 130473 ROM bytes, with 599 free. No physical
activation, production promotion, commit or push occurred. Stop for Author
review before a separate bounded private bench fixture.
