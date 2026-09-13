# Stock UART alignment — bounded unattended contract

Owner: PORT-008. Authorized by the Author on 2026-09-13, after reviewing
QUAL-003's framebuffer and upload findings. This plan is frozen before code
changes. The Author is away for several hours and explicitly authorized granular
local commits without waiting for plan review. No experimental push is authorized.

## Prime directive

If stock VDP code compiles for P4, use it. If it cannot compile, make the barest
platform adaptation while retaining its logic. Do not improve stock algorithms,
fix upstream bugs, change wire commands or invent transport semantics. Record
unrelated bugs for follow-up. EMOS owns routing; preserve keyboard, SD, return
packet framing, mode leases and recovery. Parallel transport and gameplay are
out of scope. Read this plan before each numbered step and after failures; change
it only when a recorded discovery invalidates an assumption or requires a step.

## Measurement contract

1. Establish stock and current EDP forward/return paths, including actual library
   methods, timeouts, baud, buffers, task roles and flow control. Legacy scripts
   and results are references only: their buffered wiring, pins and divergent
   protocols cannot be reused as current authority.
2. First measure pure data without bitmap creation or drawing. Prefer ordinary
   stock buffer/echo/readback APIs where they prove exact correctness. If those
   are insufficient, freeze a minimal paired diagnostic fixture before using it;
   isolate instrumentation and keep production UART framing unchanged.
3. Measure eZ80-to-display and display-to-eZ80 separately, then concurrent traffic
   where stock semantics permit. Use identical deterministic payloads including
   zero/all-one, alternating and pseudorandom patterns; lengths around chunk and
   ring boundaries, then sustained large transfers. Verify exact lengths and
   bytes/checksums outside timed portions. Record no-op/control overhead without
   blindly subtracting it, errors/timeouts/overruns, and endpoint recovery.
4. Use equal baud and corresponding route APIs. Report payload bytes, useful
   bytes/s, elapsed milliseconds and EDP/mainboard percentage changes. Separate
   host SD collection, submission, endpoint processing and completion. The 8N1
   nominal ceiling at 1,152,000 baud is 115,200 bytes/s per direction; protocol
   wrappers and scheduling reduce useful throughput. Target comparable stock
   rates with zero errors, not an invented universal pass threshold.
5. Only after pure transport is understood and correctness passes, repeat with
   bitmap creation plus plotting, then bounded sustained rendering using the
   retained renderer. Keep browser/video output absent initially. Test actual
   hardware-sprite composition only as a separately bounded output workload.
6. If meaningful gaps persist after stock alignment, use documented pinwalking
   and captures on the four UART TX/RX/RTS/CTS wires. Do not reuse historical pin
   maps. Do not change wiring unattended. Digital captures diagnose timing,
   handshake/framing; analogue signal integrity may require Author/scope help.
7. Preserve actual installed image/startup identities and working rollback before
   flashing. Use existing guarded flashing, reset, CLI and SD workflows. Finish
   with known working firmware, neutral keyboard and verified SD/CLI recovery.
   No unsolicited emulator attention cue while the Author is at dinner; hardware
   alert when review is ready, emulator fallback only if hardware is unavailable.

## Granular execution steps

- [x] U01 Preserve current graphics/transport findings in a separate local commit (09583fd).
- [x] U02 Freeze this plan, task priority and the Author's no-drift directive in a local commit.
- [x] U03 Inspect legacy UART scripts, evidence and pinwalking; record reusable techniques and incompatible contracts.
- [x] U04 Complete current-versus-stock forward/return API and scheduling précis; select exact minimal changes and test boundaries.
- [x] U05 Freeze a reproducible pure-transfer fixture/procedure, correctness oracle, controls, source identities and recovery plan.
- [ ] U06 Run baseline pure-data measurements on stock mainboard and existing EDP; preserve raw results and exact configurations.
- [ ] U07 Make the smallest stock-alignment change for forward bulk reception; verify stream semantics and build, then commit.
- [ ] U08 Run identical pure-forward transfer checks on the candidate, compare rates/correctness and recovery; commit evidence.
- [ ] U09 Align the return path only where U04/U06 evidence shows divergence; verify framing, flow-control stalls and recovery; commit separately.
- [ ] U10 Repeat forward/return and permitted concurrent pure transfers on the combined candidate; require no corruption before adding load.
- [ ] U11 Run paired bitmap upload/create/plot measurements and bounded rendering load; preserve independent transport/render scopes and commit results.
- [ ] U12 If gaps remain, capture existing UART/handshake wiring after channel verification; attribute or bound remaining causes without circuit changes.
- [ ] U13 Restore/finalize the reviewed recoverable bench state, verify keyboard/SD/startup, summarize tabular evidence and unresolved limits, commit and stop for Author review.

Each completed step gets a local commit recording its evidence and disposition.
A conditional step may close as not required with evidence; it is not permission
to invent extra implementation. Source, procedure and identity precede physical
measurement commits. Existing emulator-related changes retain their explicit
human validation gate; use non-emulator tests where appropriate, and leave new
emulator changes uncommitted unless already authorized and validated.

## Discovery amendments

U06 preflight amendment: prior graphics diagnostics documented burst-reply loss.
Run both forward matrices before either return matrix, so a return-path failure
cannot prevent the independent EDP forward baseline. This changes fixture order
only; no production path or payload change. First app and both images build;
rebuild app for the committed order before hardware. No results discarded.

## Current cursor

U06 next: build/smoke the frozen fixture and isolated baseline images, then run physical pure data. PROCEDURE.md owns exact boundaries. No production transport change yet. Prior mainboard VDP restored;
P4 remains the measured r17 13:07:24Z image. Detailed private bench identities
and admission are in HARDWARE.local.md and existing ignored run journals.
