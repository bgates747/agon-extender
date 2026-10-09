# PORT-008 — Private native qualification caller

## Scope and authorization

Author authorized continuation on 2026-10-09 after committing/pushing the LC02
software checkpoint. Work one bounded increment at a time. This increment
prepares the missing qualification callers and checks complete firmware; pause
before physical installation and execution. It does not enable formal ExExt,
ordinary parallel VDU routing, SD transport or a public raw-pin API.

LC03-A [ ] — Prepare a private, explicitly selected two-way qualification pair.
EMOS must own reservation, capability negotiation, exact block admission, native
coordination, status and release. The diagnostic MOSlet owns patterns, checks
and reporting, not GPIO, UART registers, interrupt vectors or resident function
addresses. Reuse API 51h's existing Legacy/MOSlet/busy admission and bounded
`ext.uartdiag` adapter; a private operation is absent from ordinary firmware.
P4 supplies bounded storage and consumes only matched successful receipts on
its existing UART owner. Keep diagnostics out of resident code wherever
possible. No autonomous P4 transfer request or production selection change.

LC03-A1 [ ] — Add the smallest private EMOS service needed to perform one
bounded block on behalf of the MOSlet. Validate direction, nonzero length at
most4096, complete MOSlet buffer bounds and caller policy before mutation.
Generate fresh control identity in EMOS and retain the negotiated state there.
Refused acquisition changes no pins; uncertain admitted work fences/invalidate
and stops the diagnostic. Do not retry a possibly delivered block.

LC03-A2 [ ] — Add a private P4 qualification storage/receipt adapter with
4096-byte capacity and deterministic patterns. Before acknowledging an offer,
P4 prepares TX bytes or poisons RX storage; P4 checks RX only after successful
receipt. Log descriptor, direction, length, integrity and duration via USB
serial after UART return. No byte-by-byte logging or payload callback overhead.

LC03-A3 [ ] — Build a MOSlet for lengths1,2,255,256,4096 in both directions,
repeated with different patterns. Check every reverse byte and both guard
regions; retain durable results under `/agents/extender/results`. Select any
video mode in autoexec only. The MOSlet must stop on failure, return a nonzero
status and distinguish provisional data from a completed block. Report host
and MOS clock units/limits honestly; throughput awaits actual hardware.

LC03-A4 [ ] — Exercise actual service/pattern/receipt code with existing paired
coordinator and linked instruction fixtures where possible. Include refused
direction/bounds, busy ownership, wrong/stale receipt and data corruption.
Build complete ordinary/native/probe EMOS compositions with unchanged ROM and
GPIO/baud guards and profile-specific activation-caller inventory. If the
private probe exceeds131072 ROM bytes, retain the refused map and stop before
another extraction. Compile the selected full P4 probe and verify source and
artifact closure. Update parent/component docs and pause with readiness limits.

LC03-B [ ] — Subsequent separately reviewed hardware tranche: refresh bench
ownership/topology, freeze exact installable identities and restoration files,
install/verify the private pair and MOSlet, prove boot release before payload,
then run the small two-way cases and verify UART keyboard recovery. First/last
byte alignment, VALID pulse capture and electrical output release remain
unproved until then. F03 reset/fault recovery and throughput may require further
bounded cases; a clean block suite alone does not close F03.

## Research and fixed dependencies

Reuse [LC02 results](LIVE-COORDINATOR-LC02-RESULTS.md),
[block control](BLOCK-CONTROL.md), [native payload](NATIVE-PAYLOAD.md),
[handover](HANDOVER.md) and the current diagnostic MOSlet gateway. Official
agon-docs baseline remains `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`;
[GPIO](../../../../../agon-docs/docs/GPIO.md) and
[MOS API](../../../../../agon-docs/docs/mos/API.md) supply stock boundaries.
Official MOS v3.0.2 / VDP v2.16.0 references remain read-only. No official
API, architecture or wiring change is selected. Pinned ESP-IDF5.5.5 remains
the native driver authority. Private EMOS starts at130473 ROM bytes /599 free;
ordinary128739 /2333 free. Diagnostic-only orchestration must not conceal ROM
pressure by changing the linker limit or bypassing EMOS ownership.

The test extension is a fixed private composition, not a supported facility for
ordinary applications. Its build/link checks must distinguish it from the
unactivated native composition. Deployment must not infer permission from an
unversioned compile image. Machine-specific bench state stays in ignored local
records. No installed firmware or SD file changes during LC03-A.
