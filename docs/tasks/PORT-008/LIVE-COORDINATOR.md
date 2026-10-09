# PORT-008 — Live coordinator integration

## Executive summary

Author authorized continuation on 2026-10-09 after ordinary diagnostic ROM
recovery passed on hardware. Proceed one bounded subtask at a time. First join
P4 boot recovery and block control to one physical handover owner; do not let
boot monitoring cancel normal block controls or let ordinary UART work run
while that owner is outside UART. No flash or live payload is part of LC01.
The existing tested bench combination remains installed.

LC01 [x] — Make the private P4 console's boot/recovery adapter reference the
same handover object as its `ParallelControl`. During admitted entry/payload/
return phases, boot polling yields without sampling reset controls, writing
GPIO, running recovery deadlines or admitting ordinary UART work. Explicit
cancellation must start a fresh fence and invalidate old transport state; a
completed return to UART must resume monitoring. Preserve core ownership and
all existing release/cleanup refusal behavior. Exercise actual adapters and
control owner together, including admission after real boot recovery, normal
block controls, cancellation during a block, failed fencing and wrong core.
Compile the affected complete ordinary/private P4 targets. Record evidence and
pause for discussion before LC02.

LC02 [x] — Bind the actual UART packet/serializer/shift-register drain and
parking owner, native PARLIO leaves and reciprocal return/status completion to
that shared P4 owner. Wire the corresponding EMOS foreground coordinator and
exclude normal parking from its boot reset monitor. Preserve real deadlines,
IRQ/keyboard ownership, exact descriptors, DMA lifetime and provisional RX.
Build full paired firmware within ROM guards; use existing paired CPU/SDK
fixtures before requesting bounded hardware activation. Detailed implementation
contract follows LC01 review; no new mode, raw GPIO API or SD transport here.

## Bounded research and authoritative dependencies

Reuse [native leaves](NATIVE-PAYLOAD.md), [block control](BLOCK-CONTROL.md),
[P4 runtime recovery](P4-RUNTIME-RECOVERY.md), [handover](HANDOVER.md) and
[physical diagnostic results](DIAGNOSTIC-ROM-RECOVERY-HARDWARE.md).
The official baseline remains agon-docs
`f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, MOS v3.0.2 and VDP v2.16.0,
read-only. [MOS GPIO ownership](../../../../../agon-docs/docs/GPIO.md) and the
pinned IDF 5.5.5 driver conclusions in those contracts remain unchanged.
This subtask changes private orchestration, not a stock API or wire format.

LC01 finding (resolved): `P4BootStartup` previously contained a private
handover while `ConsoleStream::parallel` contained another. Boot completion
therefore did not authorize block admission on the control owner, and its live
monitor interpreted legitimate entry CLOCK/VALID levels as reset withdrawal.
Constructor injection now shares one lifetime and UART process owner, without
manufacturing a UART phase or completed release bit.

LC01 only suppresses the boot adapter while a later block coordinator owns the
phase. It does not advance an unbound block, stop native DMA, restore UART or
publish received data. The shared block owner must continue enforcing its own
deadlines in LC02. Ordinary builds retain their existing UART path.

LC01 completed off-bench: [results](LIVE-COORDINATOR-LC01-RESULTS.md).
LC02 authorized and completed off-bench on 2026-10-09:
[contract](LIVE-COORDINATOR-LC02.md), [results](LIVE-COORDINATOR-LC02-RESULTS.md).
The network-change pause checkpoint is retained separately; software/build
verification has now resumed and passed. No hardware activation caller is
installed. Stop for review before a bounded physical fixture; F03 qualification
and formal ExExt/application/SD integration remain open.
