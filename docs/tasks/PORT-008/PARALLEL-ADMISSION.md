# PORT-008 — Private parallel block admission candidate

## Executive summary

F02c2b1 adds a private wire-admission gate in front of each existing handover
sequencer. It does not install a UART parser, negotiate a session, change boot
pins or expose ExExt. The gate checks a coordinator-owned ExExt mode, a trusted
session, a strictly next block number and an exact bounded descriptor; EMOS also
checks P4's matching acknowledgement before starting handover. This is the first
bounded part of c2b, not a complete coordinator.

## Research and scope

The official `agon-docs/docs/vdp/System-Commands.md` (documentation commit
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`) reserves VDU 23,0 for VDP commands.
The retained official VDP v2.16.0 (`c7ac293d2aa81ddfa693390549bcd909069c8fc3`)
namespace and this project's maintained
[console protocol](../../protocols/excom-console.md) establish F7 as an existing
Extender-local fixed 16-byte control body. Reuse that carrier; do not introduce
an independent byte scanner or touch the official reference checkouts. Old
console version 1 must reject version 2 after consuming the same 16 bytes.

The current console challenge is not automatically parallel permission. The
future coordinator must establish a fresh, nonzero P4-issued session through
an explicit capability exchange, bind it to EMOS admission, and invalidate it
on reset, timeout, cancellation, uncertain delivery or mode exit. That exchange
and actual serializer/boot binding remain c2b work. The present functions accept
already-established private state; no running code populates it or calls them.

## Candidate block envelope

EMOS sends `23,0,F7h` plus 16 bytes. P4 responds `FFh,16` plus 16 bytes. No
bytes are emitted by this increment. The following is a private candidate,
not a published MOS API or assigned upstream command.

| Offset | Meaning |
|---|---|
| 0–1 | `EX` |
| 2 | Version 2, distinct from compatible-console version 1 |
| 3 | Block offer 2; successful acknowledgement 82h |
| 4–7 | Nonzero session identity, exact match to the coordinator's trusted state |
| 8–9 | Block sequence, little endian, starting at 1; no wrap or skipped number |
| 10–11 | Payload length, little endian, 1–4096 bytes inclusive |
| 12 | Direction: 0 EMOS→P4, 1 P4→EMOS |
| 13 | Zero; other status/reserved values cannot grant handover |
| 14–15 | Existing console CRC-16/CCITT over offsets 0–13, little endian |

The coordinator must supply two complete 16-byte bodies to the EMOS gate,
and one complete body plus a writable 16-byte ACK buffer to P4. These private
leaf signatures do not parse partial UART packets; their future parser caller
must enforce the fixed body length and timeout before invocation.

Both processors retain six bytes: four session bytes and the last admitted
sequence. An all-zero session is invalid. The session authority, not a received
block offer, initializes those bytes after the future capability exchange.
Successful admission consumes a sequence before handover begins. After 65535,
require a fresh session; never reuse zero. The gate never changes state on a
malformed, stale, out-of-order, wrong-mode or busy request.

EMOS requires both a valid offer and a valid P4 acknowledgement matching every
descriptor byte (apart from the opcode reply bit and recalculated CRC). P4
checks the offer before admitting and constructing its acknowledgement. A
consumed offer cannot be replayed after the handover returns to UART.

The acknowledgement grants only entry to drain/release phases. It is neither
peer-quiescence proof nor successful payload completion. P4's coordinator must
finish serializing the entire acknowledgement before parking; EMOS must fence
ordinary submissions before transmitting the offer. Existing queued key packets
must remain ordered. A failed/uncertain exchange must invalidate admission and
recover release; it must not retry a payload on the old sequence. The remaining
coordinator supplies deadlines and exact descriptor/buffer lifetime, and cannot
publish success until matching post-payload integrity/status completes.

## Reset boundary

P08-F-D03 requires the future parallel-capable pair to complete reciprocal
physical release before UART startup. No peer, old peer or expired timer grants
ownership. Mainboard keyboard/MOS may continue with Extender I/O unavailable.
This gate cannot enforce a boot GPIO fence; current UART-only startup remains
unchanged until that separate integration is implemented and tested.

## Validation scope

Run each maintained gate with its real sequencer. Cover both directions, all
legal lengths, altered descriptor/CRC fields, wrong modes, zero/stale session,
sequence zero/skip/replay/exhaustion, rejected legacy envelopes and invalid
acknowledgements. Check non-mutation on failure and single consumption on
success. Execute the compiled EMOS gate in the pinned eZ80 interpreter, build
both targets and report ROM growth. No hardware, SD or installed image changes.

[Development results](PARALLEL-ADMISSION-RESULTS.md) retain validation and limits.
