# Parallel block-boundary latency investigation

Identify why the extra byte after a full 4 KiB block can add tens of milliseconds.
The Author authorizes the investigation after reviewing the matched format 4
comparison, and requires this task to be committed/pushed before implementation.
Measure waiting and actual execution separately; do not explain the delay from
processor speed, name a culprit without evidence, or change transport policy to
hide it. Production selection remains unchanged.

## Scope and authority

1. Preserve the exact incoming EMOS/P4, listener, startup and mainboard VDP.
   Begin from the byte-verified restoration in the [matched results](RESUMPTION-RESULTS.md).
   Reuse the exact captured format 4 P4 source/image before adding any P4 probe.
2. EMOS owns routing, pin handover and ordinary VDU output. P4 owns its UART
   recognizer, native receiver, completed-buffer handoff and VDP parser task.
   UART1/Port C multiplexing remains the established electrical constraint.
3. No CRC, substitute checksum, software COMPLETE/ACK, new application packet,
   changed wiring, persistent UART shutdown, scheduling repair or renderer change.
   This is diagnostic attribution, not the next P08-D02 architectural code cut.
4. Use mode 0, single buffering and the same 256/4096/4097/8192 wire-byte commands.
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
   return. Current format 4 removes software completion exchanges. Its current
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

BL02 [x] — Compose canonical EMOS's existing phase profile with its unchanged
controller endpoint. Build through all mandatory ROM/link/baud/owner guards.
Rebuild the exact-bound MOSlet and independently validate the fourteen live
callsites, ROM match, register/stack/IFF, disabled hooks, timer and overflow.
Ordinary compositions must contain no active diagnostic calls or recorder.

BL03 [x] — Run the bounded four-length phase campaign against the exact preceding
format 4 P4 image. Retain all endpoint/phase rows and actual complete buffer-byte
proof. Attribute EMOS reservation, offer-to-admission, park, electrical entry,
payload, reciprocal return, polling/publication and unaccounted gaps without
adding overlapping intervals. Compare probe overhead with the retained ordinary
composition and report scheduling variation, not only medians.

BL04 [x] — If the largest interval still combines P4 readiness/parser work and
serial response, add a default-off, identified P4 diagnostic composition at the
same clean source. Record bounded RAM timestamps/event counts at the UART offer
recognizer, response enqueue/completion, native phase transitions, buffer return/
retirement and relevant parser/task-wait boundaries. No per-byte payload event stream,
logging, network requests or timing-dependent actions during measurement. The
BL04 refinement below permits aggregate native-mutex acquisition timing inside
a bounded adjustment scope; its per-lock observer cost must remain explicit. Link
records by block sequence/direction/length, using local clock differences; do not
subtract timestamps from unsynchronized processors. Dump only after completion.
Retain exact binary differences and clock/probe limits. Reuse existing compiled
owner boundaries and include-only diagnostics where feasible; no second renderer.

BL05 [x] — Run only the additional cases needed to discriminate the remaining
causes. Keep fixture payload, route, mode, fences and successful-path scheduling
unchanged. Preserve failed acquisitions and run required capture-absence controls.
If a new probe changes the symptom, report that perturbation and use a smaller
observation; do not call disappearance proof of a fix.

BL06 [x] — Restore complete incoming P4 flash/EMOS ROM byte for byte. Verify
startup/listener unchanged, original route/modes, cursor/text commands, ready
neutral input and actual CLI; release readers, transfer sessions and reset holds.
Preserve known incoming R25 wide-mode limits and mainboard VDP untouched.

BL07 [x] — Publish raw selected timings, phase/transaction mapping, complete-byte
proof, separate per-processor scopes, ranges, timer calibration/overhead limits,
restoration and a concrete location/cause conclusion. Distinguish a measured wait
from the reason it exists. Update task/log, commit/push and stop before any fix or
architectural change; propose the smallest correction supported by evidence.

## State and decision boundary

Contract frozen/pushed as `fcf2dca0` before source edits. Recorder/validator
source `542b245a` accepts current fourteen-callsite format4 and refuses incomplete
or unknown schemas while retaining historical sixteen-callsite interpretation.
Eleven host evidence checks pass. Canonical EMOS `2fc7b26` composes existing phase
hooks/controller endpoint; build `agon-emos-v0.1.27-b2026-11-02-04-23-34Z` is
128,881 bytes, 2,191 free, raw SHA256
`89558bb1aae2ffafe1c916b3ba349e66ba7ebf509f3e5ad856c5b6615b4c722c`.
All wrapper/link/baud checks pass. Exact-bound fixture
`port-008-phase-timing-r01-b2026-11-02-04-24-47Z`, SHA256
`604955cfaba60af4f95b4e8a68850fc4bd5722a65db0211688297c07619b2522`,
passes fourteen final-CALL bindings, 3,072 ROM/RAM register/IFF/overflow cases and
actual MOSlet/ZDS ABI checks. Fresh CLI, staging/readback and full incoming ROM
proof pass. Exact diagnostic EMOS identity is observed after one FLASH; matched
unchanged P4 application installation/verification and all four phase cases
complete. Integrity-only selection retains 24 full byte proofs (22 original,
two labeled repeats); all 36 original/repeat CSV rows have zero flags. The
256/4096 capture-absence controls both finish six rows and positive CLI without
panic. All work uses Pi/bench; the Author takes Oryx offline for the night.
Existing capture/restoration bytes remain retained locally. The Author's bench authorization
continues for this bounded investigation; establish fresh actual CLI/input and
startup evidence before installation. P08-D02 remains open. No newly selected
carrier/session/scheduling design, production promotion or version tag follows.


## P4 observation gate — first measured case

The first current 4097-byte phase case completes all six zero-flag rows and
full buffer proof. The next offer-to-admission interval is 46.35–47.15 ms in
four measured rows; in the fifth it is 1.15 ms and the following seven-byte
query offer takes 46.53 ms. One-byte native payload is 0.125–0.139 ms.
The combined offer interval, rather than pin switching or that byte's native
runner, owns the delay. This satisfies BL04's gate for a P4 observation.

Source review identifies one possible obstruction: `vdu_buffered.h` takes
`AGON_STOCK_NATIVE_GUARD` separately for every inline operand's target-byte
write. This is not proof of mutex waiting. The isolated default-off P4 diagnostic
will measure whole buffer-adjustment elapsed time, native-lock wait total/max/
count within that scope, and offer recognition/acceptance. Preserve the same
mutex calls and byte loop. Reuse the existing native-wait observation pattern;
do not remove/coarsen locks or infer CPU time by subtracting unsynchronized clocks.
Retain bounded records in RAM and read them only after explicit case completion
and Legacy handback. No payload-per-byte timestamp stream or USB logging is added.
P4/eZ80 local intervals and their block/request ordering must explain the wait;
observational overhead and remaining preemption ambiguity stay explicit.

The first 4096-byte case completes and saves its endpoint/phase rows, but its
sixth USB dump is short. Preserve it as an incomplete acquisition, not transport
corruption. Agon-first reset plus actual CLI succeeds before independent cases.
Its later capture-absence control completes six zero-flag rows and positive CLI without panic; the incomplete acquisition remains retained.


### BL04 instrumentation refinement

The first phase records justify measuring the native mutex candidate. Use the
existing native-wait pattern to accumulate wait total/max/count around actual
native mutex acquisitions only while the parser executes a target-buffer
adjustment. This adds local clock reads per lock (the inline operand loop locks
per byte), rather than allocating/logging an event per payload byte. Record that
observer cost and compare the unchanged payload/fences with the preceding P4.
A large individual wait is elapsed blocking/preemption, not a CPU instruction
count. Aggregate lock time may include acquisition overhead and preemption;
subtracting it from the enclosing command does not measure retired CPU work.
The P4 diagnostic must keep actual lock/unlock semantics unchanged, publish
bounded completed records safely, and refuse an unfrozen/incomplete readout.

### Observer bring-up correction

The first observer source `fb867f5f` passes offline checks and exact installation,
but fails native receiver arm on the first 43-byte CLI packet in three setup-only
ExExt entries. No timing application is invoked on that image. P4 continues
running with fault-free mode 0 scanout; one Agon reset restores actual CLI each
time. The ordinary serial capture identifies native arm, not a P4 panic.

The observer accidentally reserves approximately 6 KiB of internal static RAM.
Source `74006a51` moves its bounded records to explicitly allocated PSRAM before
admission, retaining only the small live accumulator internally. This follows
the existing native-wait observer and preserves scarce DMA-capable memory.
Entry recovers and free internal RAM rises by 6192 bytes, consistent with memory
pressure; the old exact allocation-failure stage remains unproved. Failure-only
receiver diagnostics now identify SDK/allocation stages in the repaired build.
No native transport, lock or scheduling policy is changed. Nineteen profile
checks and address/undefined-behavior host controls pass (LeakSanitizer disabled
inside the ptrace sandbox). The identified native build passes and is installed
and read back exactly. Entry and the six-row 4097-byte case now complete.
Five measured dumps match all 8192 bytes; the warm-up dump is short. All six
timed block groups and adjustment scopes are present, but later CLI teardown
fills 128 offer slots and drops 41 events. The complete required prefix ends
at slot 55. The whole-session trace and whole-acquisition pass remain refused;
retain both failures. A bounded prefix validator proves every required block's
length/direction/sequence, recognition/acceptance/retirement and matching eZ80
phase order before using those scopes. It neither selects by elapsed time nor
supplies missing events.

Five measured adjustment scopes take 48.336–52.526 ms with 4086 original native
acquisitions each. Their aggregate acquisition elapsed is 18.919–20.594 ms;
individual maxima are 0.215–0.313 ms. The parser does not recognize the following
offer during that byte-update work; recognition-to-acceptance is small once
service resumes. One early tail admission moves the delay to the next query,
as in the baseline. The cause is serialization of admission behind the parser's
inline update, not a single long native-mutex block or electrical setup. The
instrumentation's per-lock timer overhead and remaining command/preemption time
are explicit; do not claim an exact uninstrumented mutex or CPU cost.

The new marked acquisition requires its own post-campaign control. Use the
exact retained matching product implementation with both capture-body code and
boundary observations absent. Report those diagnostic/binary differences; this
control cannot distinguish which observer caused a short USB acquisition. No
second P4 case or speculative fix is needed for this attribution.

### Bounded control and next proposal

The marked 4097 observer case passes its own 60-second control using the exact
retained product implementation without either the USB debug body or the P4
boundary observer. Six rows have zero flags, positive CLI and no panic/restart.
Its fourteen-callsite phase records reproduce 45.597–47.556 ms tail offers; the
fifth row instead moves 46.389 ms to the query. This reproduces the admission
symptom with both P4 observations absent. It neither supplies missing bytes nor
identifies which observer caused the short USB acquisition. One control setup
stops before RUN when the CLI receives MOS STATUS without its leading `E`; one
Agon reset, actual CLI proof and 1 s postclear settling precede its first actualRUN.
The lost character's exact cause is unproved.

Recommend next discussing bounded I/O progress by the existing P4 owner while
the parser still has queued bytes, admitting only what its existing 8 KiB queue
can hold. Preserve EMOS routing/offer/pin ownership. Check reentrancy and phase
deadlines before implementing. This can remove an artificial admission wait;
it does not remove the inline command's processing cost or qualify generic
file/bitmap throughput. Chunked native guards/bulk input are a separate parser
change. No correction or P08-D02 decision is implemented in this tranche.

BL04's implemented observation is narrower than its original inventory: P4
recognition/admission/retirement plus adjustment/native-acquisition scopes,
combined with eZ80 native phases, locate the long interval before recognition.
Separate P4 UART enqueue/drain and every native-phase timestamp were not added
and are not claimed. The complete measurement prefix suffices for attribution;
whole-session collector reuse remains unqualified because of later overflow.
No recurring diagnostic or production adoption is selected.

## Closeout — 2026-11-02

BL01–BL07 complete within this bounded attribution. The linked
[results](BOUNDARY-LATENCY-RESULTS.md) and
[portable evidence](BOUNDARY-LATENCY-EVIDENCE.json) retain the selected 24 baseline
buffers, five measured observer buffers, complete timed prefix, partial-capture
and teardown-capacity refusals, required controls and all clock/probe limits.
Complete incoming P4 flash `006397a5` and EMOS ROM `84da2c5a` are restored byte for byte;
startup/listener unchanged, mainboard VDP never flashed, both mode 0 settings and
actual Legacy CLI verified, cursor controls submitted to both displays. Readers,
transfer sessions and reset holders released; Pi/bench only throughout.
The publication closes this diagnostic contract, not PORT-008, the warm-reset
issue, P08-D02 or a production release. No transport fix is implemented.
