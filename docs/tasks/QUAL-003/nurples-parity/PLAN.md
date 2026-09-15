# Nurples performance parity goal

## Executive summary

The Author authorizes unattended medium-effort work until Nurples renders as
fast on Extender with a connected streaming web client as on stock mainboard,
or meaningful progress becomes blocked. Stop on demonstrated parity. Necessary
bench flash/reset/SD/keyboard/diagnostic operations are authorized on the existing
wiring; preserve known-good recovery. Commit discrete steps locally; do not push
experimental changes. Voice on hardware for completion or necessary assistance;
spoken emulator fallback only if hardware cannot notify.

This goal supersedes the earlier audit-first sequence for work unrelated to the
Nurples workload. UC02–UC07 remain recorded; pull in only demonstrated blockers.
No Golem or unrelated backlog work. No destructive wiring experiments.

## Current correction — highest priority

AGENT-ASSIGNED, not separately Author-approved: r03 revealed stale NPRES.BIN.
MOS/EMOS SAVE uses FA_CREATE_NEW, and the fixture ignored its error. All later
copied game records lack fresh-run provenance; retract those game timing/state
comparisons. Independent output/packet measurements remain separately valid.
Stop the old sequence; no further NP01/NP03 comparison is accepted.

1. [x] N02g: Correct fixture output handling. Delete only its owned result/progress
   files, check every MOS load/save/delete result, and embed a newly staged8-byte
   per-run nonce plus fixture variant/capacity in the result. Host must reject
   nonce, format, variant, count, size or save-error mismatches. Preserve old
   evidence as invalid; reuse original game/assets without changes. First prove
   two distinct runs replace output with distinct expected nonces before restoring
   any gameplay-parity claim. Then rerun matched SW/HW and unfenced/sustained work.

Official reference: agon-mos src/mos.c mos_SAVE uses FA_CREATE_NEW; current
agon-emos src/mos.c retains that behavior. This needs no firmware alteration.

## Measurement contract

Use the same deterministic Nurples workload and assets on both routes in native
mode20 (512x384,64 colours,60Hz,single buffer). Pin original source and an isolated
fixture transformation. Preserve the dirty Nurples dev worktree: benchmark
copies and harness live here, no normal game changes without evidence.
Fix PRNG/input/simulation time so slower rendering cannot reduce the workload.
Record completed work using stock-compatible queue completion/query boundaries,
not submitted commands or browser refresh rate. Measure probe overhead against
unfenced controls; report timing limits. Retain actual frame/state counts and
warmup separately from timed runs. Keep web streaming active on P4, record its
independent delivery rate and errors, and compare with P4 output disabled.

Initial practical parity criterion: repeated matched runs have mean completed
frame time within5% of stock, with p95 no worse than stock plus one120Hz tick;
no increasing command backlog, missing workload, visual corruption or input
regression. Disclose tick quantization and any stricter/weaker conclusion the
data actually supports. Browser delivery is separate: a live stream is required,
but repeated snapshots are never counted as completed game frames. No quality,
resolution, sprite-count or gameplay reduction may be used to claim parity.

## Work checklist

1. [x] N01: Pin current game/assets/bench, inspect timing and deterministic seams;
   freeze a reproducible fixture with durable progress and completion outputs.
2. [ ] N02: Validate fixture workload/oracles, deploy/read back and run paired
   stock/P4 controls plus active web streaming. Retain timings and correctness.
3. [ ] N03: Identify the largest measured P4-specific cost; use bounded probes
   and code comparison to stock. Keep input/transport/render/output separate.
4. [ ] N04: Implement the smallest evidenced correction, commit/build/identify,
   flash/verify and rerun matched checks. Repeat only for unresolved bottlenecks;
   add granular documented experiments when new evidence changes the plan.
5. [ ] N05: Demonstrate repeated parity, restore usable production/CLI and startup,
   preserve results, hardware voice and stop. Human acceptance remains separate.

No completion claim from historical emulator FPS. Notify rather than guess if
an essential measurement/behavior contract needs human disposition. Source
porting remains minimal stock logic; recovery readiness is not a reason to
flash MOS needlessly. Existing r22 and both mainboard firmwares are baseline.

## Author steering and agent-assigned fixture details

Author explicitly selects the dirty `nurples-repair` working tree and generated
assets as the good reference. Preserve them; note bugs without unrelated fixes.
Author permits structured comparable-load stress fixtures and requests hardware
sprites in addition to the game's current software-sprite path. This supersedes
the initial older Nurples checkout selection. No old-checkout fixture was deployed.

AGENT-ASSIGNED (not separately Author-approved): start with a600-boundary pilot,
120-boundary warmup, fixed held-fire input, synthetic two-tick simulation clock,
stock pixel-query completion fence and per-boundary state/timing records. Use
independent SW/HW sprite variants; do not conflate their parity results. Pin
reference source/dirty asset hashes and keep generated copies in ignored storage.
If a query cannot observe scanline sprite decoration, report that limit and use
output captures for visibility; never count that query as hardware scanout proof.

N01: selected repair sources/dirty packed assets pinned in reference.json. Three
fixture variants assemble with ez80asm. A start receipt and fixed-size terminal
result are saved; timed frame records remain in RAM to avoid per-frame SD cost.
Source patching is isolated; reference worktree untouched. N02 validates the
pilot on hardware before it can support conclusions. Archive dirty reference
assets locally; do not rebuild them from older tracked art.

### N02 measurement-path clarification (agent-assigned, not separately Author-approved)

Source review confirms stock `sendScreenPixel` explicitly calls
`waitPlotCompletion(false)`. The downstream `processPrimitives` drains the queue
and calls `showSprites`; `readScreen` alone does neither. Thus the query is a
software-drawing completion boundary, not proof of hardware-sprite scanout.
Reference: official 2.16.0 `video/vdu_sys.h`, `video/agon_screen.h`, and FabGL
`displaycontroller.cpp`; corresponding port paths retain these calls.

The repair AGNB image loader requires RGBA2222, a supported hardware-sprite
format. The isolated HW variant enables the documented test flag and marks
sprites with command19 after normal initialization. Normal game source/assets
remain unchanged. Verify visibility in actual output before crediting the HW
variant; keep software and hardware comparisons separate.

The first pilot remains frozen. Before relying on its unfenced sibling for
probe-overhead conclusions, propagate the final-query failure into the terminal
record and make the analyzer's variant/scope explicit. Those are fixture issues,
not evidence of a VDP defect. Retain the original pilot identity/results.

Installed r22 includes `AGON_GRAPHICS_TIMING=1`. Dormant scopes still enter a
critical section. This is a candidate measurement cost, not yet a diagnosed
bottleneck; do not change firmware on that hypothesis alone.

Probe r02 propagates terminal-query failures and records variant flags in the
generated manifest. SW, HW and unfenced SW assemble successfully. This fixture
revision is agent-assigned under the unattended adjustment authorization; it
does not change or replace the in-flight r01 pilot. The r01 binary hashes remain
in fixture-builds.json; r02 hashes are in fixture-builds-r02.json.

N02 pilot checkpoints (agent-assigned subdivisions of the frozen paired work):

1. [ ] N02a: Legacy r01 SW pilot:600 records, no query error, live gameplay/PRNG
   progression; measured60.0 completedFPS. See results/README.md. Full staging
   and both readbacks passed; reuse assets for subsequent runs.
2. [ ] N02b: Same r01 SW binary on P4 without output, then with production web
   streaming. Compare state fingerprints before interpreting timing differences.
3. [ ] N02c: Hardware-sprite variant on both routes, with P4 output captures.
   Follow with corrected unfenced controls and repeats needed for conclusions.

### Output-gap investigation — AGENT-ASSIGNED, not separately Author-approved

The first P4 SW run with the production browser connected also completes60FPS,
with the identical600-record state fingerprint. However, browser delivery is
only7.79FPS across the run, about7.66FPS over its last10seconds. A static
receive-only control gives8.93FPS. These are clearly insufficient viewing
performance even though the initial completed-work criterion is satisfied.
Do NOT declare the goal achieved from this pilot. Investigate snapshot/send/
client presentation costs under N03; preserve the separate game-work metric.
Hardware-sprite comparison and heavier/repeated loads remain required.

Start with existing static output and receive-only controls, source review and
host-side network timing if available. Only add/flash bounded snapshot/send
probes if existing evidence cannot isolate the cost. Keep all such additions
agent-assigned, retain r22 rollback, and never change stock drawing semantics
just to make output easier. No EMOS change is currently justified: the P4
no-output and active-output completed-work pilot both match mainboard.

N02b complete: SW600-record fingerprints and measured60FPS match on both P4
controls. N02c hardware pair also completes with the same fingerprint; corrected
unfenced controls, heavier workload validation and repeats remain outstanding.

### N03 bounded output investigation (AGENT-ASSIGNED, not separately Author-approved)

1. [x] N03a: Separate host/network/presentation controls without firmware changes.
   Wired Pi static HW surface:19.93FPS production,28.91FPS receive-only; laptop
   Wi-Fi:about7–9FPS. Do not attribute the whole gap to P4 rendering. Retained
   prior video-throughput research already documents the same host-path effect.
2. [x] N03b: Build an isolated r23 diagnostic variant of the exact installed r22
   source, enabling only the existing bounded `AGON_EXTENDER_VIDEO_TIMING`
   snapshot/send recorder. Pin source/config/tool/output hashes; preserve r22
   rollback. Flash/verify through the established deployment helper. Collect
   snapshot/send deltas on a static512x384 surface over wired production and
   receive-only clients. Compare observable output rates to the uninstrumented
   controls; do not silently subtract probe cost.
3. [x] N03c: Use those durations and stock/output contracts to choose one bounded
   correction. The current browser returns credit after RAF presentation; the
   producer then waits for demand at a logical frame boundary before capture,
   and sends the full frame. Serial waits are a hypothesis, not a completed
   diagnosis. Any lookahead/credit experiment must retain bounded storage,
   correct ownership/disconnection/mode-change handling and no starvation of
   parser/network tasks; historical RGB-4 continuous-output starvation remains
   a regression constraint. No drawing-algorithm rewrite is authorized by this
   hypothesis. Freeze the selected change before implementation.

Host packet capture was unavailable without a password; no privilege or wiring
change is needed. Use the existing wired Pi and bounded timing hooks instead.
Do not request the sleeping Author's attention for this optional diagnostic.

N03b reuses the prior LARGE-SURFACE.md investigation rather than repeating its
implementation. Its640x480 snapshot mean was16.660ms, but socket accounting
was invalidated by closing with an in-flight response. The new observer MUST
stop granting credits, receive/drain the last granted response, and read final
counters while still connected before closing. Use the same quiescent boundary
before the timed window. Reject lost/overlapping/incomplete or mixed-layout
counts. This closes that existing measurement gap on current512x384 Nurples;
it is not a claim of discovering those timing hooks anew.

N03b correction: r23 source archive predates the optional output hooks; enabling
the flag alone yielded a healthy firmware with no timing endpoint (404). No
timing conclusion is drawn. The reviewed parent-to-maintained delta in exactly
two source files is only the optional scopes/endpoint; transplant those and the
existing video_timing.hpp into isolated r24. Require both endpoint bytes and
videoRecorder symbol in the final image before deployment. No drawing/transport
algorithm delta is present. This correction is agent-assigned, not separately
Author-approved. r23 and its rollback evidence remain identified locally.

N03b passes on r24 with drained counters: production201 snapshots/sends and
receive-only297 snapshots/sends, all complete units; no recorder loss/overlap.
Means are11.4ms snapshot and15.8ms socket send. Wired received20.0FPS production,
29.7FPS immediate-credit. The diagnostic rates reproduce uninstrumented controls.
N03c selects overlap of these currently sequential stages as the next experiment.

### N04 first correction contract — AGENT-ASSIGNED, not separately Author-approved

1. [x] N04a: Add opt-in, one-frame snapshot lookahead to the project-owned pool.
   A successful consumer lease may arm one future snapshot only if no producer
   is already active. Repeated polls with an existing lease cannot rearm it.
   Keep fixed slot allocation, immutable leased bytes, monotonic generations,
   mode/detach ownership and logical-boundary capture. If credit stops or the
   client disconnects, at most the already-armed future capture may finish;
   there must be no continuous no-demand composition/starvation. Existing pool
   defaults remain unchanged; only an explicit experimental stock-service build
   flag enables lookahead. No stock primitive/scanline algorithm or wire-format
   changes, extra browser credits, or resolution/quality reductions.
2. [x] N04b: Exercise lease immutability, bounded demand, producer overlap and
   default behavior on the host. Build an isolated r25 comparison atop current
   r24 diagnostics, preserve rollback, deploy/verify, rerun the same wired output
   windows and Nurples workload. Retain raw timings and frame/state records.
3. [x] N04c: Evaluate the measured improvement and remaining gap before any
   further change. Browser-credit timing is a separate possible next experiment,
   not part of this one. Stop/restore if input, rendering, lifecycle, or output
   correctness regresses. Performance success does not waive heavier/repeated
   gameplay and unfenced controls or human acceptance.

N04a implemented behind the explicit lookahead option/build flag. Sanitized host
checks pass for default demand behavior, held-byte immutability,100 repeated
blocked polls without rearming, disconnect/reconnect during production, bounded
three-slot storage and unchanged legacy snapshot-pool regressions. No hardware
performance claim yet. r25 build will enable the option only for comparison.

N04b/c scoped results: r25 output improves to24.64FPS production/32.67 immediate
credit. Complete accounting and no-web600-boundary60FPS/state equality pass.
The goal still requires active wired gameplay, heavier loads, unfenced controls
and repeats; static output progress alone is insufficient.

### Next bounded correction — AGENT-ASSIGNED, not separately Author-approved

1. [x] N04d: Optimize only the P4-owned RGB222 row normalization, currently one
   scalar read/XOR/mask/store per pixel. For aligned four-byte groups, swap the
   two16-bit halves and mask each byte's high two bits using alias-safe memcpy.
   This must reproduce `out[x]=signal[x^2]&63` exactly, preserve supported row
   bounds, and fall back safely for unaligned addresses. Runtime alignment must
   be checked before compiler alignment assumptions. No stock scanline body,
   palette, sprite, framebuffer, resolution or wire-format changes. Keep this
   separately opt-in for comparison; retain r25 lookahead and diagnostics.
2. [x] N04e: Host-check byte equality across colours, row widths and alignment
   offsets, with canaries/sanitizers; inspect target compilation as useful. Build
   and identify the isolated r26 variant, preserve/verify rollback, repeat the
   same drained wired measurements and workload. If snapshot cost does not
   materially improve, do not claim this loop caused the gap. Evaluate before
   choosing further pipeline/client changes.

N04d implemented as a separately selected output-adapter helper.65,792 sanitized
scalar-equivalence cases pass over native row widths, byte patterns and16 source/
destination alignment combinations, preserving canaries and input bytes. Target
GCC assembly confirms aligned LW/SW accesses and halfword swap/mask; the unaligned
path retains byte accesses. Stock scanline bodies remain unchanged. Hardware
snapshot-cost attribution still awaits the r26 comparison.

3. [ ] N04f (agent-assigned): Run the deterministic game with the wired production
   client active before mainboard reset and throughout gameplay. The laptop's
   slow Wi-Fi stream cannot exercise the faster output candidate adequately.
   Add an optional first-frame readiness receipt to the reusable headless
   observer; default observation behavior remains unchanged. Stage/verify the
   fixture first, wait for that receipt, then issue exactly one reset. Retain
   browser connection/errors, game timings/state and run durations separately.
   A completed no-web pilot/static output test does not substitute for this run.

N04e complete: r26 snapshot mean9.163ms/production29.69FPS and
10.180ms/immediate-credit33.45FPS. Accounting passes and no-web HW pilot
retains60Hz/state equality. Snapshot cost fell but is not the entire bottleneck.
N04f active wired gameplay is next; no parity claim.

N04f complete: both SW and HW retain60Hz/all479 measured intervals at two
ticks and matching fingerprints, with the wired production observer active
before reset through terminal service. Browser receipt remains below60FPS.

### Remaining output gap — AGENT-ASSIGNED, not separately Author-approved

1. [x] N04g: Capture a bounded header-only TCP trace on the wired Pi during the
   existing drained static output control. Reuse prior packet accounting; retain
   browser timing separately. Inspect frame-start/end, credit and ACK timing to
   distinguish wire occupancy from idle time before selecting another firmware
   change. No source, baud, quality or transport-contract change in this step.

N04g: wired trace retained69,785packets with zero kernel drops. Median frame
payload span17.10ms, last payload to next EVF7.19ms, browser credit0.80ms after
payload tail, next EVF6.30ms after credit. Two-byte next-message WS headers are
excluded from the preceding payload tail. Host offload coalesces some packets.
The diagnostic HTTP totals were rejected because one historical lost completion
was already present; this does not invalidate the independent packet timestamps.

2. [x] N04h: Add opt-in bounded credit-to-ready and ready-to-socket dispatch
   durations to the existing output recorder. No routing/credit/drawing changes.
   Inspect actual ELF (not CMake's incomplete compile database): current network
   worker wait is1tick/1ms and packed-row loop uses word accesses. Measure where
   the observed post-credit delay occurs before choosing another correction.
   Preserve rollback, build/verify, drain clean windows and reject incomplete
   accounting; production builds must retain zero probe state/cost when disabled.

N04h completed: r27 validates deployment/input/SD/HW pilot and clean four-phase
windows. Immediate-credit means: credit-to-ready3.905ms, ready-to-send0.219ms,
snapshot10.171ms, socket18.022ms,32.15receivedFPS. Production varies to23.79FPS
with9.247ms capture,18.940ms send,0.589ms credit-to-ready,0.105ms dispatch.
HTTP work-queue dispatch is not the dominant delay; more queue optimizations
are not justified. Preserve this distinction and run remaining workload controls
before expanding output contracts.

### Remaining matched workload controls — AGENT-ASSIGNED, not separately Author-approved

1. [ ] N02d: Deploy the existing corrected r02 unfenced SW fixture under a new
   filename, verify both readbacks, run on mainboard and P4 with wired production
   output. Use explicit unfenced timing labels and compare deterministic state
   with fenced pilots. Ordinary vblank remains; matching60Hz can bound an effect
   at that pacing, not prove zero CPU probe overhead.
2. [ ] N02e: Extend only the isolated fixture to a bounded2400-boundary workload,
   allowing substantially more enemy/game progression. End with an explicit
   reason before interactive game-over rather than hanging on synthetic time.
   Preserve native gameplay updates/assets; record completed count/state and
   refuse a heavy-load claim if progression is insufficient. Use matched SW/HW
   routes, a longer bounded browser observer and retained output captures.

N02e fixture detail: r03 adds a terminal-reason byte and read-only native
live-sprite count (20allocated records) per boundary. This instrumentation adds
eZ80 work equally to both routes; it is not normal-game CPU cost. It stops
before interactive game-over/victory and records that reason. Both SW/HW
variants assemble. NP03 records include capacity/count and are analyzed
separately from NP01; no sustained hardware result is claimed yet.

N02d complete: corrected r02 unfenced SW control on both routes records
600boundaries, all479 measured intervals two ticks, and the same fingerprint
as fenced pilots. Terminal fences pass and P4 wired web remains connected.
This finds no pacing change at60Hz; it does not measure zero probe CPU cost.

3. [ ] N02f (agent-assigned): Resolve the white headless screenshot limitation
   with a direct WebGL readback of the retained EVF, using unchanged served
   production parser/presenter assets. Compare all pixels after present, before
   drawing-buffer discard; report this as an offline renderer check, not physical
   display or FPS. Run on the wired observer host only after gameplay measurements
   have released its CPU; do not contend with a timing run.

N02g repair checkpoint:

1. [x] N02g-i: NP04 checked-I/O and nonce/variant/capacity validation pass host
   rejection checks and two consecutive P4 runs. Nonces differ, both contain
   2400records and the same deterministic state fingerprint. Means29.5718 and
   29.5654 fencedFPS; p95 33.333ms/max50ms. Live sprites peak13.
2. [x] N02g-ii: Fresh mainboard/P4 SW, unfenced and HW comparisons completed.
   All six variants match the same 2400-record state fingerprint; expected
   unique nonces and checked saves validate provenance. See verified-r27-cases.json.

### Qualified UART changes absent from the running baseline

AGENT-ASSIGNED, not separately Author-approved. Fresh NP04 measurements now
show a real scoped gap: stock58.7624 fencedFPS, P4 repeat29.5718/29.5654FPS,
with identical2400-record workload state and13 live sprites maximum. Inspecting
actual archived P4 source reveals that r22–r27 still contain the pre-E07P
console owner/stream: unconditional delay(1), old RX timeout/default Stream
block reads, old reply admission/refill policy. Maintained source contains the
previously qualified stock-aligned changes, but the restored running baseline
did not. Installed EMOS is also the earlier restored image; E07P qualified
v0.1.17 profiles were restored away. See agon-emos INTEG-014/E07P-results/README.md
and machine-local restoration records. Do not mistake these for new discoveries
about optimal UART algorithms or blindly import unrelated maintained changes.

1. [x] N03i: Finish the current immutable r27 matched controls. In parallel, build
   an isolated r28 comparison which transplants ONLY the maintained, previously
   qualified console_hardware.inc/console_stream.hpp UART changes into r27's
   selected source composition. Record hashes/diff; keep all current output
   options and mainboard firmwares fixed. Build-time identity and sanity checks
   must prove the selected image actually contains this change.
2. [x] N04j: After the active matrix releases the bench, restore safe startup,
   preserve r27 full rollback, flash/verify r28, verify native input/SD and rerun
   the same nonce-verified workload with wired output. Compare before making a
   new rendering or MOS change. Firmware recovery remains available, not a
   reason to flash MOS speculatively. No experimental push.

### Control-service recovery before N04j (AGENT-ASSIGNED, not separately Author-approved)

The r27 matched matrix completed and all result bytes were retrieved. The next
controller stopped before any flash: P4 responds to ICMP but HTTP status times
out from both bench hosts. No pending SD mutation or observer remains.

1. [x] N04j-R1: Perform one identified P4-only USB reset with firmware unchanged,
   capture its startup, and re-establish HTTP/SD ownership. Do not reset MOS or
   overwrite autoexec while its child SD service is executing. If recovery
   succeeds, resume the already frozen safe-startup restoration and r28 pipeline.
2. [x] N04j-R2: Preserve this unresolved HTTP failure as a separate reliability
   observation; do not attribute it to a UART or graphics defect without evidence.

Recovery observation: the one P4 reset restored HTTP and SD immediately, but
keyboard admission was lost (ready=false, locale0) because EMOS had not repeated
its startup handshake. Child SD exit succeeded before this was discovered.
Allow one mainboard reset to replay the retained terminal-returning autoexec;
this is recovery, not a new timed comparison. Wait for its terminal SD service,
then exit it and restore startup through a directly launched service. Do not
use the rerun result as fresh benchmark evidence. No MOS flash is involved.

The recovery reset completed the game, then COPY correctly refused the existing
archived destination and aborted autoexec at line11. A decoded EVF capture
showed the saved-result message, access-denied error and responsive ExCom MOS
prompt. This explains absent terminal SD service; it is not a hung game.
Native CLI now selects Legacy and launches SD directly. Future recovery must
expect COPY's create-new behavior too; never classify missing SD alone as hang.

Recovery checkpoint: native CLI/SD admission and exact original startup readback
passed. P4-only r28 deployment has resumed with preserved r27 rollback. The
HTTP stall remains unresolved; no throughput result depends on its recovery
replay. N03i build/identity checks and complete fresh baseline are now done.

### N04k — Separate output contention from remaining transport cost

AGENT-ASSIGNED, not separately Author-approved. The first fresh r28 SW result
is30.0066 fencedFPS versus r27's29.5718. The maintained P4 UART changes alone
have not explained the gap. Finish the immutable three-case streaming matrix.

1. [x] N04k-i: If streaming controls still miss parity, run the same NP04 SW/HW
   fenced workload with no browser connected, fresh nonces and result names,
   unchanged P4/EMOS/assets. Read drained output-recorder counters before/after
   and require no snapshot/socket work during the game. This diagnostic does
   not satisfy the goal's active-streaming requirement. No MOS flash yet.
2. [x] N04k-ii: Compare the fresh output-off records to matched streaming records.
   A remaining gap directs investigation toward EMOS/command/render timing; a
   disappearing gap directs investigation toward snapshot/render contention.
   Freeze the next correction only after this distinction is measured.

N04j completed: r28 streaming SW30.0066FPS, unfenced34.0319 boundaries/s,
HW30.7696FPS. All expected nonces and2400-record gameplay states match. No
parity; output-off controls now own the bench. The wired-host offline WebGL
readback also passes every pixel with zero GL errors using retained EVF data;
that validates decoding/presentation pixels, not physical display cadence.

### N04l — Reapply the qualified EMOS UART profile

AGENT-ASSIGNED, not separately Author-approved. Fresh r28 SW output-off measures
32.6504FPS with no output-counter increments; streaming measures30.0066FPS.
Most of the gap persists without output. Installed EMOS remains the restored
pre-E07P image. Reuse the exact already-qualified ordinary E07P image, not a new
MOS implementation: agon-emos INTEG-014/E07P-results/README.md, ordinary profile
v0.1.17-b2026-09-14-16-10-16Z,130936bytes, SHA256
429f85ebb413bf3eed779307a71126b6cafb7bf884ad1824c6673e1814718b61.
The earlier qualification proves bulk transport only; fresh game tests are needed.

1. [x] N04l-i: Finish output-off HW control. Exit child SD, launch SD directly,
   restore/read back original safe startup. SAVE current full128KiB ROM to an
   absent destination and retrieve it. Require exact preserved baseline match.
   Verify candidate bytes on SD and existing rollback bytes before flashing.
   Preserve r28 P4 rollback and maintained ZDI recovery readiness.
2. [x] N04l-ii: Invoke FLASH exactly once through accepted native CLI, then one
   mainboard reset and fresh keyboard admission. SAVE/read back entire ROM to
   another absent name and compare candidate prefix byte-exactly. Do not call
   an emitted command a successful flash. No mainboard VDP/source changes.
3. [ ] N04l-iii: With P4 r28 fixed, repeat nonce-verified SW/HW streaming cases
   and matching mainboard controls under the same EMOS image. Compare before
   selecting any additional implementation. If no material gain, preserve the
   result and investigate command/render latency rather than rewriting MOS.

N04k results: zero output-counter increments and matching nonce-verified state
for both SW32.6504FPS and HW32.1968FPS. Streaming costs some throughput, but
the large mainboard gap persists without it. N04l ROM-preservation/comparison
therefore proceeds; no new MOS source changes are selected.

### N04l-R — Recover failed ordinary FLASH attempt

AGENT-ASSIGNED, not separately Author-approved; recovery use is within the
Author's unattended hot-bench goal authorization. Baseline full ROM matched
1cd65eac21780a8a7c82e14209737c38796e24f32300524e58a93e5c44e096d8 before
FLASH. After one FLASH and reset, no fresh keyboard admission appeared; a
bounded CLI probe lost admission with reason6 and emitted only its first event.
No test ran. This does not prove a candidate logic defect. The controller's
three-second post-command delay did not prove flash completion before reset;
retain that as a possible procedural cause, not an established diagnosis.

1. [x] N04l-R1: Reuse the verified maintained connected-harness recovery image,
   bound to the exact saved pre-run131072-byte known-good ROM. Preserve current
   r28 P4 flash, verify programmer deployment, capture complete pre-erase ROM
   and target identity, restore baseline once with independent byte readback.
   Use docs/mos-recovery.md unchanged. No automatic retry or wiring change.
2. [x] N04l-R2: Restore/verify P4 r28 before one controlled mainboard reset.
   Prove fresh native input and SD access with original safe startup. Inspect
   failed-ROM bytes to distinguish incomplete programming from a valid image
   failing to boot. Freeze a new step before any further EMOS installation;
   never repeat a blind delay-and-reset FLASH sequence.

N04l-R1: complete failed-ROM capture shows exact42316-byte candidate prefix,
remaining88756bytes all FF. Recovery restored the exact known-good full ROM;
P4 r28 restored/readback. This supports premature controller reset as cause.
The ordinary updater's automatic reboot is now the completion guard documented
in maintained recovery guidance. Physical input/SD readmission remains pending.

### N04l-R3 — Corrected updater completion (AGENT-ASSIGNED, not separately Author-approved)

Known-good ROM/P4/native keyboard/SD/original startup all restored and verified.
The failed image is an exact candidate prefix followed by erased bytes, so the
corrective experiment changes controller completion handling only.

1. [x] N04l-R3a: Invoke the same already-verified on-card candidate once. Wait
   up to120seconds for the updater's own fresh EMOS keyboard admission. Never
   issue an external reset during this wait. Lost keyboard session at reboot is
   expected; it is not grounds to resend FLASH. If no fresh boot, stop/inspect.
2. [x] N04l-R3b: After automatic reboot, save to a new ROM-dump filename and
   compare full ROM against candidate plus erased padding. Verify safe startup
   and native CLI/SD, then release the queued matched game comparisons.

N04l-R3a: updater automatic reboot produced fresh keyboard admission after
19.286seconds, with no external reset. The prior roughly seven-second reset
was premature. First post-boot SAVE did not create its file, while following
LOAD/RUN established SD service; input admission alone did not prove startup
commands had finished. Exit that proven direct service and repeat only the
ROM SAVE/readback with a fresh name; do not repeat FLASH or reset.

N04l-R3b: full131072-byte installed ROM equals qualified ordinary candidate
plus erased padding; SHA256f9229e93cd178de4f1045d4464d1173eee2fb0086157a391b72bfa816a569618.
Safe startup and native CLI/SD verified. The same candidate boots when allowed
to finish programming; the earlier failure was the premature-reset procedure.
P4 r28 remains fixed. Four fresh route/sprite comparisons now own the bench.
