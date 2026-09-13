# Large-surface delivery diagnosis — 2026-09-13

This bounded continuation belongs to PORT-003, under the Author's unattended
RALLY-22/Extender sequence. It follows the completed V01–V05 increment and
faithful command checks. It does not resume held QUAL-003, redesign retained
VDP drawing, add browser-side rendering, or change the EVF1 credit contract.
All experimental changes remain local and uncommitted pending human review.

## Evidence and scope frozen before implementation

1. The previous combined DSP-cleanup/poll1/TCP32768 candidate receives roughly
   60 snapshots/s at320×240, but true640×480 mode0 receives19.634/s. Mode3 is
   640×240; its29.858/s observation is a separate geometry. These are wired
   immediate-credit measurements, not physical scanout or game-loop rates.
2. `stock_p4_service.cpp::publish` builds demanded RGB222 snapshots one row at
   a time, with the existing native row guard and output normalization. Its
   timer only wakes workers; it does not execute this construction. No current
   measurement separates complete snapshot wall time from transport wall time.
3. `wired_network_service.cpp::performQueuedSend` sends the owned opaque
   header/payload segments on the HTTP task using the existing complete-send
   adapter. Credit, lease release, error handling and the five-second send
   timeout must remain intact. Socket-call duration is not ACK time or browser
   receive completion; no inference of wire throughput from that duration alone.
4. Reuse `diagnostics/frame_recorder.hpp` for fixed-size, nonblocking timing
   aggregation. Use a separate recorder selected only by a new explicit
   `AGON_EXTENDER_VIDEO_TIMING` build flag. Do not enable the broad old frame
   timing composition or collect per-pixel/per-row times. Only snapshot and
   socket-send scopes are needed initially. Do not read/format counters inside
   measured paths, timer callbacks or ISRs.
5. The pinned SDK `components/esp_timer/include/esp_timer.h` defines boot-relative
   microseconds from esp_timer_get_time. Use unsigned32-bit duration subtraction
   only for bounded operations shorter than a wrap. Counters are lifetime
   diagnostic totals; use before/after deltas for one unchanged surface. Count
   lost/overlapping completions and reject invalid aggregates instead of
   silently assigning their time to another component.
6. Normal firmware must exclude the diagnostic endpoint, recorder and timestamp
   calls. Optional HTTP reading allocates/formats only on the HTTP task; it is
   not a production telemetry API. Read outside the timed browser window where
   possible. Compare the diagnostic build against the preserved uninstrumented
   candidate, and do not advertise its rates as production performance.

## Bounded plan

1. [x] P003-L01: Inspect current delivery/code/ownership and freeze the scope,
   diagnostic boundaries and recovery conditions above. Preserve the installed
   candidate, source identities, stock references and all previous evidence.
2. [x] P003-L02: Implement the optional two-boundary recorder and read-only HTTP
   report. Verify wall-time/units accounting, wrap, invalid/concurrent readings,
   and complete compile-out when disabled. Run existing network/lease/stock
   source checks appropriate to these call sites; do not silently fix baseline
   verifier drift or change renderer semantics to obtain a passing check.
3. [x] P003-L03: Build an isolated draft r17 diagnostic with DSP cleanup, poll1
   and TCP32768 held fixed. Archive exact inputs/outputs and check configuration
   differences, optional-hook selection and partition/rollback identity before
   considering a physical deployment. No revision increment or publication.
4. [ ] P003-L04: Revalidate physical admission and bench identity. If healthy,
   capture a bounded uninstrumented control, install the identified diagnostic,
   and measure the same320×240 and640×480 cases on the wired path. Retain browser
   headers and timing deltas, distinguish snapshot/send/remaining delays, and
   choose a further edit only if evidence identifies an Extender-owned cost.
   Do not increase TCP/clock/poll settings or change snapshot pacing blindly.
5. [x] P003-L05: Record the finding and any measured correction separately from
   production claims. Restore an identified uninstrumented candidate, prove
   Legacy keyboard/SD/startup recovery, stop all observers, and leave review
   gates explicit. Hardware intervention requiring the Author is deferred
   while independent work remains; no routine wake-up cue.

## Preserved boundaries

The accepted production app, full-game candidate, EMOS16, onboard stockVDP,
startup and wiring remain unchanged. CLI/mode changes use the already accepted
Extender keyboard pathway; fixture modes are selected outside app code. Physical
takeover ends ownership, never triggers automatic reacquisition. Every flash
uses the stable device identity, preserves overwritten bytes, checks the prior
application and partition, and independently verifies the replacement. Current
private admission/deployment state belongs to HARDWARE.local.md, not this file.

This plan freezes a local experiment before source edits. Existing human
emulator-validation/commit requirements and the Author's no-experimental-push
instruction keep all affected source and documentation uncommitted.

## Local implementation and build checks

The new `diagnostics/video_timing.hpp` supplies separate snapshot/socket scopes
and an optional `/diagnostics/video-timing` report. Snapshot units are completed
construction pixels; socket units are complete message bytes accepted by the
socket calls. Early exits/failures record zero units. The reader rejects lost,
overlapping, incomplete or mixed-layout intervals rather than interpreting them
as lower cost. Snapshot completion still has the existing pool publication
semantics; it does not prove monitor presentation.

Host sanitizer checks pass for units, time wrap, cancellation, duplicate finish,
overlap and busy-reader loss. The reused recorder's concurrent100,000-completion
test also passes. Disabled builds contain no new recorder, report or timestamp
symbols. Sixteen network feature combinations pass short-send and registration/
failed-stop containment. Existing publisher/pool/controller/network and real
WebGL RGB222 checks pass. Retained stock scanline source is byte-identical.

Isolated build `uart-excom-console-r17-b2026-09-13-16-01-22Z` succeeds with only
the two instrumented boundary source files and new header differing from the
installed candidate's source set. SDK configuration, partitions and DSP
derivative match exactly. Private inputs, source archive, ELF and build checks
remain under agents/video-throughput; this is not yet physical evidence.

Build inspection clarifies an inherited condition: the existing console
composition already enables FRAME_TIMING through `video/CMakeLists.txt`, as well
as GRAPHICS_TIMING. The initial absence assertion was therefore wrong. Both
prior and new images contain that existing recorder; this experiment neither
enables nor removes it. The additional output recorder remains separately
selected. CMake's compile database does not by itself describe the selected
SCons object compilation. The actual snapshot and network objects, plus the
final ELF, all contain the new recorder; those are checked directly. The
CMake response file contains architecture options, not this opt-in selection.

## Physical results and Author-requested pause

The existing image's fresh wired controls reproduce59.487FPS at320×240 and
19.689FPS at640×480. The diagnostic image was independently written/verified,
with native USB startup, Pi mainboard reset, fresh keyboard admission, unchanged
root startup readback and SD-service exit. The Author connected their web viewer
during the first warmup; the observer received1013/video client busy and exited
without evicting it. The Author then disconnected and released testing.

| Case | Browser received FPS | Snapshot mean wall time | Socket evidence |
| --- | ---: | ---: | --- |
| Diagnostic320×240 |59.379 |4.907ms |5.234ms, complete units accounting |
| Diagnostic640×480 |19.599 |16.660ms,460 complete constructions |Strict complete-send accounting rejected |

Both browser windows have one settled layout, zero sequence gaps and no page
errors. The larger aggregate contains461 socket attempts but only460 complete
message equivalents; all recorder-loss/overlap counters remain zero. This is
consistent with an in-flight send aborted when the observer closes, but that
cause has not been isolated. Preserve the failed check. Its26.045ms mean across
all attempts must not be presented as a clean successful-send average. Snapshot
units do match every construction, so that narrowly scoped mean is usable.

Timing deltas bracket browser setup/teardown as well as its20-second received
sample window; they are not exactly the same population. Old latest snapshots
can appear in geometry warmup, as already documented. No production scanout,
game FPS improvement, isolated depth-versus-size cost or optimization success
is claimed. No rendering or transport algorithm was changed in this increment.

The next measurement needs to stop issuing credits, drain the final response,
collect counters and then close the observer. P003-L04 stays incomplete until
that boundary is qualified and the same large case passes accounting. The
Author asked to pause at a good stopping point; no new experiment was started.

The exact pre-test image uart-excom-console-r17-b2026-09-13-13-07-24Z was restored,
factory SHA256
`5bddd14bc5611c99c6b1e90b18fc0f2ed7167298a499199c6248dd8b1fbb489c`.
Independent flash verification, native USB startup, one Pi mainboard reset,
neutral/released keyboard admission, unchanged root startup readback and
SD-service exit all pass. The new timing endpoint returns404 after restoration.
Mainboard is at Legacy EMOS CLI; observers are closed. Existing FRAME_TIMING /
GRAPHICS_TIMING in the prior composition remain exactly as before this test.

Exact build/deployment/rollback records, raw before/after counters, browser
captures, comparison.json and final-recovery.json remain in ignored
agents/video-throughput/large-surface and the identified build directories.
Work is paused for Author discussion, with all changes uncommitted/unpushed.
