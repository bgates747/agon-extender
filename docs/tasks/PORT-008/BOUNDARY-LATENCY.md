# Parallel block-boundary latency investigation

Identify why the extra byte after a full 4 KiB block can add tens of milliseconds.
The Author authorizes the investigation after reviewing the matched format4
comparison, and requires this task to be committed/pushed before implementation.
Measure waiting and actual execution separately; do not explain the delay from
processor speed, name a culprit without evidence, or change transport policy to
hide it. Production selection remains unchanged.

## Scope and authority

1. Preserve the exact incoming EMOS/P4, listener, startup and mainboard VDP.
   Begin from the byte-verified restoration in the [matched results](RESUMPTION-RESULTS.md).
   Reuse the exact captured format4 P4 source/image before adding any P4 probe.
2. EMOS owns routing, pin handover and ordinary VDU output. P4 owns its UART
   recognizer, native receiver, completed-buffer handoff and VDP parser task.
   UART1/Port C multiplexing remains the established electrical constraint.
3. No CRC, substitute checksum, software COMPLETE/ACK, new application packet,
   changed wiring, persistent UART shutdown, scheduling repair or renderer change.
   This is diagnostic attribution, not the next P08-D02 architectural code cut.
4. Use mode0, single buffering and the same 256/4096/4097/8192 wire-byte commands.
   Each count includes the 11-byte buffered-update header. Preserve one warm-up,
   five measured rows, explicit tail flush and the ordered reply boundary.
5. Follow current test-appliance, execution, capture-failure, reset, installation,
   rollback and SD-layout procedures. The Pi owns explicit CLI invocation,
   original route/mode capture, fresh mode confirmation, >=1 second settling,
   retrieval and final restoration. Never modify autoexec or launch from reset.

## Bounded research precis

1. Official references: agon-docs `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`,
   MOS v3.0.2 `8336409351ee5314e02801a7b72a4f1bb5282519`, VDP v2.16.0
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`; remain read-only. Consult
   `docs/mos/API.md` and `docs/vdp/Buffered-Commands-API.md` in agon-docs for
   ordinary byte output, inline buffer adjustment and USB debug dump contracts.
2. Canonical EMOS `src/emos_exext.c` batches 4096 bytes, flushes a full batch,
   and exposes a measurement-only foreground tail flush. Ordinary partial
   batches also have a real-VBlank service path. Explicit flush means a blanket
   attribution to waiting for VBlank is invalid.
3. EMOS `src/emos_console.c` performs an offer/reply exchange before each block;
   `src/emos_parallel_coordinator.c` owns drain/park, native payload and reciprocal
   return. Current format4 removes software completion exchanges. Its current
   source has fourteen phase callsites, versus sixteen in the historical
   CRC/completion-bearing campaign. Refresh linked-callsite validation explicitly.
4. P4 `vdp/video/extender/transport/parallel_control.hpp` retains one native
   buffer until local completion consumption. `parallel_vdu_stream.hpp` copies
   completed bytes into its receive queue; `console_hardware.inc` and
   `console_stream.hpp` share one parser/I/O-progress owner. Trace admission,
   buffer retirement and task waits if EMOS-side timestamps leave them combined.
5. Existing `tests/performance/stream_timing/{build.py,phase.asm,main.cpp}` binds
   the exact ROM/ELF, verifies original-object relocation-to-final-CALL mapping,
   records phases in MOSlet RAM and saves after measurement. Preserve its
   register/IFF/capacity checks, overflow refusal and mode/cursor lifecycle.
6. Historical [phase results](PHASE-TIMING-R01-RESULTS.md) locate a post-full-block
   offer delay on an older composition. They motivate boundaries, not attribution
   of current format4 latency. Current [matched evidence](RESUMPTION-EVIDENCE.json)
   retains the 4097-byte 20.8–66.7 ms range and all original/repeat provenance.

## Work items and validation

BL01 [x] — Freeze this contract, link it from the authoritative task/TODO and
commit/push before code changes. Current state below records the implementation.

BL02 [ ] — Compose canonical EMOS's existing phase profile with its unchanged
controller endpoint. Build through all mandatory ROM/link/baud/owner guards.
Rebuild the exact-bound MOSlet and independently validate the fourteen live
callsites, ROM match, register/stack/IFF, disabled hooks, timer and overflow.
Ordinary compositions must contain no active diagnostic calls or recorder.

BL03 [ ] — Run the bounded four-length phase campaign against the exact preceding
format4 P4 image. Retain all endpoint/phase rows and actual complete buffer-byte
proof. Attribute EMOS reservation, offer-to-admission, park, electrical entry,
payload, reciprocal return, polling/publication and unaccounted gaps without
adding overlapping intervals. Compare probe overhead with the retained ordinary
composition and report scheduling variation, not only medians.

BL04 [ ] — If the largest interval still combines P4 readiness/parser work and
serial response, add a default-off, identified P4 diagnostic composition at the
same clean source. Record bounded RAM timestamps/event counts at the UART offer
recognizer, response enqueue/completion, native phase transitions, buffer return/
retirement and relevant parser/task-wait boundaries. No per-byte instrumentation,
logging, network requests or timing-dependent actions during measurement. Link
records by block sequence/direction/length, using local clock differences; do not
subtract timestamps from unsynchronized processors. Dump only after completion.
Retain exact binary differences and clock/probe limits. Reuse existing compiled
owner boundaries and include-only diagnostics where feasible; no second renderer.

BL05 [ ] — Run only the additional cases needed to discriminate the remaining
causes. Keep fixture payload, route, mode, fences and successful-path scheduling
unchanged. Preserve failed acquisitions and run required capture-absence controls.
If a new probe changes the symptom, report that perturbation and use a smaller
observation; do not call disappearance proof of a fix.

BL06 [ ] — Restore complete incoming P4 flash/EMOS ROM byte for byte. Verify
startup/listener unchanged, original route/modes, cursor/text commands, ready
neutral input and actual CLI; release readers, transfer sessions and reset holds.
Preserve known incoming R25 wide-mode limits and mainboard VDP untouched.

BL07 [ ] — Publish raw selected timings, phase/transaction mapping, complete-byte
proof, separate per-processor scopes, ranges, timer calibration/overhead limits,
restoration and a concrete location/cause conclusion. Distinguish a measured wait
from the reason it exists. Update task/log, commit/push and stop before any fix or
architectural change; propose the smallest correction supported by evidence.

## State and decision boundary

Contract prepared; no diagnostic source edit or bench operation yet. Existing
capture/restoration bytes are retained locally. The Author's bench authorization
continues for this bounded investigation; establish fresh actual CLI/input and
startup evidence before installation. P08-D02 remains open. No newly selected
carrier/session/scheduling design, production promotion or version tag follows.
