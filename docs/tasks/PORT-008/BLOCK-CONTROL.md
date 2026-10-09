# PORT-008 — Bounded block control transactions

The Author authorized continuation on 2026-10-09. This off-bench increment
closes the offer/result transaction layer within F02c2; it does not enable
ExExt, grant GPIO ownership or qualify native payload timing. Preserve the
preceding uncommitted ROM-fit work and unrelated EMOS checkout work.

BC01 [x] — Extend the existing F7 version-2 owner with exact block ACK and
completion matching. EMOS retains its admitted descriptor and UART reservation;
P4 retains one descriptor and a caller-owned bounded buffer. Reject nested,
stale, malformed and out-of-order work without publishing provisional bytes.
Reuse the existing console ISR, CRC and bounded exchange, not a second parser.

BC02 [x] — Require a completed physical return to UART and both processors'
payload results before publishing success. Give P4 a per-phase and result-wait
deadline with unsigned wrap handling. Cancellation invalidates capability and
requests physical release; no timeout may restore pins or manufacture release.
No ordinary startup or native payload activation changes in this increment.

BC03 [x] — Run the maintained EMOS foreground/ISR and P4 owner together with
scripted physical phase completions. Exercise both directions, bounds,
sequential blocks, descriptor/CRC mutations, missing/stale/duplicate results,
payload failures, wrap/stall deadlines, cancellation and queued key packets.
Build the actual complete EMOS images, retaining ROM accounting and mandatory
link checks. If the new image does not fit, preserve the measured refusal and
stop before further extraction; do not silently enlarge this contract.

BC04 [x] — Record results, source/build identities, checks and remaining
physical coordinator gates. No bench, network-device request, flash/reset,
SD write, production promotion or commit of emulator-coupled code this tranche.

## Bounded research and wire contract

The reference baseline remains agon-docs
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, MOS v3.0.2 and VDP v2.16.0.
Read-only official [system commands](../../../../../agon-docs/docs/vdp/System-Commands.md)
describe VDU 23,0 and the return packet envelope; the project's
[console protocol](../../protocols/excom-console.md),
[admission](PARALLEL-ADMISSION.md) and [handover](HANDOVER.md) own this
private extension. It is not a stock MOS/VDP API.

Version 2 keeps the fixed 16-byte body. Offer/ACK are 02h/82h. Completion
request/reply are 04h/84h, distinguishable from version-1 console operations.
Offsets 4–12 must match the retained admitted descriptor exactly: session,
sequence, length and direction. Offset 13 is zero for success or one for
payload failure; other values are invalid. Offsets 14–15 retain the existing
CRC. ACK always requires status zero. EMOS sends its local payload status only
after reciprocal UART recovery. P4 replies only after its own physical return
and local payload result; either failure prevents publication and invalidates
the session. Uncertain delivery is not permission to retry the old sequence.
For a matched payload failure after clean physical return, P4 invalidates the
capability while retaining UART so its failure reply can drain. A physical
fault instead requests release recovery and cannot claim clean return.

P4 requires a provisioned buffer of sufficient capacity before acknowledging
an offer. Its caller keeps the buffer alive and TX contents immutable through
DMA cleanup and completion. RX contents remain provisional until the owner
publishes a successful receipt. A receipt must be taken before admitting the
next block, preventing reuse of a still-published buffer. P4's 2,000 ms deadline
applies separately to each observed physical phase and to waiting for the
completion request after return. A deadline begins release recovery and cannot
prove electrical cleanup. EMOS reuses the existing clock/fuse bounded wait.

The boot release monitor and block handover currently have separate state
objects. Joining those objects, fencing/draining the actual UART owner, calling
the native payload leaves and protecting return from reset monitoring remain
required follow-up within F02c2/F02c3. Do not fake a UART-state proof to enable
this transaction layer on ordinary startup. Native EMOS currently has only
309 ROM bytes free; compilation decides whether this increment fits.

## Result

The bounded transaction increment is complete; the combined native image is
refused at 190 bytes over ROM capacity. No live activation or SD deployment.
See [results](BLOCK-CONTROL-RESULTS.md) for checks and remaining gates.
