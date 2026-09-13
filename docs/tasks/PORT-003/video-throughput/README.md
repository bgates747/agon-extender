# Video-throughput continuation after Rally — 2026-09-13

The next bounded diagnosis of the remaining640×480 delivery limit is in
[LARGE-SURFACE.md](LARGE-SURFACE.md). It separates snapshot and socket-send
wall time before selecting another optimization, preserving the original
V01–V05 evidence and ordinary rendering/credit behavior.

The Author authorized unattended Extender backlog work after AgonArcade's
RALLY-22 full-game candidate meets its machine checks. Video speed comes first,
then the faithful VDP command PORT. Local experimental changes are permitted;
no experimental code may be pushed before Author review. Human emulator review
and commit approval remain separate. This is PORT-003 work, not a new upstream
renderer redesign or a resumption of the held paired QUAL-003 sprite test.

Preparation may overlap the final Rally SD transfer. Physical video experiments
begin only after that run returns to a proven CLI/SD recovery point. Preserve
accepted Rally, startup, P4/EMOS keyboard/SD, all rollback and concurrent remote
work. No pull/merge/rebase/push is part of this continuation.

## Bounded plan

1. [x] P003-V01: Record selected native backend, browser contract and installed
   baseline identities. Capture bounded browser delivery at an idle console
   without a firmware change. Respect the one-client contract; never evict an
   existing viewer. Record actual payload/sequence/presentation timing rather
   than treating the logical period field as achieved frame rate.
2. [x] P003-V02: Measure an ordinary VDU workload with a visible changing frame
   marker, then a representative existing game if admission is healthy. Keep
   rendering, snapshot production, network delivery and browser presentation
   distinct. Collect terminal receipts and return to Legacy CLI/SD. Fixture
   video modes are set by startup/CLI before invocation, never inside fixtures.
3. [x] P003-V03: Use evidence to isolate an Extender-owned bottleneck. Where
   necessary, add bounded optional probes at selected native worker/output or
   network boundaries. Do not infer native cost from the superseded generic
   frame service's counters. Define source bindings, error bounds and cleanup
   before any changed firmware is installed.
4. [x] P003-V04: Apply the smallest evidenced transport/scheduler/presentation
   correction while preserving retained VDP primitive algorithms and existing
   stock behavior. Run relevant host/lifetime/native-source and P4 closure
   checks. Keep any new fixture or firmware identity consistent with the
   project version policy and latest Author authorization.
5. [x] P003-V05: Repeat the same bounded cases, retain exact candidate/baseline
   artifacts and report observed rates/limits. Confirm Legacy keyboard and SD
   recovery. Leave changes local for Author review. Then select the next
   missing command family from the owning coverage tasks, without claiming
   general speed parity or silently correcting upstream defects.

## Focused source précis before implementation

1. The current ordinary console selects the original five depth classes through
   `vdp/video/extender/display/stock_runtime_controller.hpp`, not the earlier
   generic `LogicalFrameService`. PORT-003's stock-backend-r2 README and
   stock-backend-r3 deployment record describe the current integration.
2. `stock_p4_service.cpp` has an independent ESP timer, core0 drawing worker and
   core1 output worker. The timer coalesces opportunities. Drawing drains the
   retained FIFO without a primitive budget. Output services snapshot demand by
   preparing each native row under its guard, then normalizing into RGB222.
   Snapshot/network waits must never be added to the clock callback.
3. `stock_runtime_controller.hpp` guards one retained primitive/row/finite
   mutation, not a whole frame. Sprite decoration remains in the original
   scanline bodies. `stock_scanline.cpp` and binding verifiers constrain edits;
   apparent upstream quirks stay recorded unless a separately selected Extender
   boundary demonstrably activates them differently.
4. `docs/protocols/browser-video.md` owns EVF1: a32-byte header, one full frame
   per binary WebSocket message, current RGB222 pixel-format2 (00BBGGRR), one
   exact text `frame` credit at a time, and a single viewer. The old Phase-F
   RGB888-only/200ms limits are historical. Its description of an RGB888
   intermediate/three-byte allocation predates the accepted stock backend:
   current StockP4Service uses direct RGB222 snapshot storage. Reconcile that
   documentation with the existing accepted implementation, not a new behavior.
5. `wired_network_service.cpp` owns opaque sends and polls its worker at10ms.
   Complete-send/error/disconnect containment and physical-keyboard ownership
   are preserved. Polling latency is a candidate to measure, not a proven
   bottleneck. Browser reported FPS measures presentation calls, not scanout.
6. Existing headless Playwright helpers and the production browser decoder can
   be reused for bounded observation. Opening P4 USB serial resets the board;
   ordinary HTTP/video experiments must not open it. Do not change wiring;
   pinwalking is available if a later bus-level experiment actually needs it.

Installed private identities and transport addresses remain in ignored bench
records/HARDWARE.local.md. Source, firmware and protocol identity do not become
freshly verified merely because an old record exists. Record unexpected changes
and preserve them before selecting a new physical run.

## Baseline preparation findings

The old R2 binding verifier rejects the current selected source at
vgapalettedcontroller.cpp. Its token normalizer predates QUAL-003's later
AGON_GRAPHICS_TIMING include/scope hooks, which remain in the current console
flags. This is retained baseline drift, not a newly introduced failure from
this video increment. Do not call the current source R2-verified or strip those
changes from evidence without explicitly accounting for their exact bodies.
The timing-enabled scope can still acquire locks when duration collection is
off; existing QUAL-003 I004 already records that interference risk. Baseline
video must identify this build before comparing a separately bound no-timing
variant. No changed firmware has been built or installed here.

The role-named browser-video document now accurately describes the already
accepted direct RGB222 snapshot allocation/conversion; no runtime changed.
A bounded headless production-page observer is prepared in scripts/measure_video.py.
It records received header metadata, browser submission observations and first/last
frames, and exits rather than evicting another client or retrying after failure.

## Unchanged-firmware baseline

The exact production browser assets match served bytes. The installed r17
continues from the preserved BENCH-001 image; no flash/reset occurred. Bounded
20-second observations produce these received rates (not physical scanout):

| Host/path and consumer | Surface | Received FPS |
| --- | --- | --- |
| Linux laptop Wi-Fi, production presentation |640x480 RGB222|4.268|
| Linux laptop Wi-Fi, immediate credit/no presentation |640x480 RGB222|4.874|
| Wired Pi, immediate credit/no presentation |640x480 RGB222|14.667|
| Wired Pi repeat with packet capture |640x480 RGB222|14.683|
| Wired Pi, ExCom idle mode8, immediate credit |320x240 RGB222|31.214|

All report logical period16667us, which does not describe achieved delivery.
The receive-only mode intentionally bypasses browser presentation and is not
a production UI FPS claim. Different host/network paths are not a controlled
firmware comparison. The wired repeat captures130481packets with zero kernel
drops. TCP sequence-space bytes in flight peak at5760, matching the selected
SDK send-buffer default; this is evidence for a bounded transport experiment,
not complete attribution of latency. Payloads are large relative to that window.

An isolated draft r17 build variant changes only the SDK TCP send-buffer default
from5760 to32768. The renderer, graphics hooks, protocol and all other source
remain unchanged. It uses a fresh build timestamp, separate generated SDK config
and build directory, with exact input archive and retained r17 rollback. It is
not a new version/revision or a published/default configuration. No experiment
is flashed before baseline marker/CLI recovery and build checks are complete.

Pinned local ESP-IDF Kconfig/lwipopts define TCP_SND_BUF from the setting. Its
Kconfig help still mentions TCP_SNDBUF, but the selected sockets headers expose
SO_SNDBUF as unimplemented and no TCP_SNDBUF implementation was found; use a
separate build configuration rather than relying on that stale help. Official
background: https://docs.espressif.com/projects/esp-idf/en/v5.3.1/esp32/api-guides/lwip.html .

The isolated32KiB build completes with unchanged maintained inputs and exactly
one effective SDK option delta (plus its compatibility alias). Full-frame send
containment passes. The RGB222 regression initially hit a stale generic fixture
calling executeFrameWork(8) after the accepted drawing-budget removal. Its three
calls now use executeFrameWork(); expectations are unchanged. The complete
publisher/pool/controller/network and real WebGL colour/stride/format/credit
checks then pass. This updates a test to the current API; no rendering code
was changed, and the distinct R2 source-verifier drift remains recorded.

A bounded ordinary-VDU marker is prepared in examples/video-marker. Stock Fab
shows complementary Gray-code rows and returns a terminal receipt. The initial
loop read time twice at its deadline and could emit one extra update; a single
elapsed-time read now gates each iteration. The separate physical baseline will
bind that corrected binary and its receipt. No mode switch is inside the app;
setup chooses mode8. It runs for20s and returns, with no private timing protocol.


## Ordinary-VDU physical baseline and isolated comparison

The corrected marker binary emits1200updates over2400raw MOS ticks, with
maximum scheduled gap1,36221VDU bytes and last frame1199. The terminal CSV was
read from the mainboard SD after returning to Legacy. Root startup hash remains
unchanged and the service exits to the CLI. No firmware change/reset precedes
this baseline. Wired immediate-credit delivery averages32.304FPS over30seconds,
including the final static marker. Within the changing interval, sampled marker
progress spans1194updates in19.9491seconds, with maximum sampled step5.959of972
received samples have complementary marker rows. Noncomplementary snapshots
are excluded from marker decoding; sequential ordinary rectangle commands do
not promise an atomic update of both rows. These are snapshot/receive results,
not a scanout or primitive-completion timing claim.

The next physical comparison is the isolated tcp32k draft build
uart-excom-console-r17-b2026-09-13-11-11-34Z, factory SHA256
12f57d5042c9a78b2ef10b8b8304e053b7b8233242c9e0b3e355c57b7a75b5dc.
Its partition table matches the retained baseline. The deploy helper preserves
all flash bytes it will overwrite (a2MiB prefix), verifies the existing app and
partition identities before writing, independently verifies the written image,
and observes native USB startup. This exploration does not confer qualified or
released status; maintained configuration remains unchanged pending comparison
and Author review. Private captures and deployment pointers stay under
agents/video-throughput.


## Real-game blocker found during comparison

The tcp32k variant passes marker receipt equality, native USB re-admission and
Legacy SD/startup readback. Wired640x480 received throughput is19.094FPS versus
14.683FPS in the baseline repeat; moving-marker320x240 is33.515FPS versus
32.304FPS. The latter is a small difference, not evidence of restored60FPS.
The completion text may overwrite one marker row depending on prior cursor
position, so decode only the changing interval; terminal invalid rows are not
counted as active rendering faults. One initial retained640x480 snapshot may
precede the newly selected320x240 surface.

A representative Rally full-game launch exposed a P4 reset. The first command
attempt omitted MOS RUN's address placeholder and never launched the game;
that case is excluded. Correct invocation is LOAD rally.bin then
RUN . oval mute. The received-frame observer detects no sustained game output,
and the keyboard epoch changes to a fresh unadmitted P4 startup. The normal
Rally build had already passed stock-onboard-VDP checks; this run exercises the
P4 port instead. No game source/data was changed.

The tcp32k crash partition was preserved through stable USB and decoded against
its exact ELF. processLoop fails in pthread_mutex_destroy while releasing a
shared BufferStream during bufferTransformData's destination-vector assignment,
VDP command41, buffer30007, transform30004, options78, format192, offset5,
stride8, limit4. This is a localization, not yet the cause. Both output/drawing
workers are separate from the faulting parser stack. No network-send frame is
on the failing stack.

The exact preceding r17 build has now been restored and independently verified.
The same corrected Rally launch also causes loss of HTTP then a fresh keyboard
epoch with no admission, before a game capture. Its crash partition is being
preserved for comparison. The reset is therefore reproducible without the TCP
buffer change. Hold real-game performance claims and further throughput edits
while isolating this port blocker. Preserve both dumps, sources and rollback;
keep baseline runtime configuration unchanged. This remains a local experiment,
not a release or a general fix to upstream VDP semantics.


The restored baseline dump confirms the same invalid mutex target/semaphore,
this time releasing MultiBufferStream at the nested buffered call boundary.
The common failing control block address is not itself proof of the first bad
write or failed allocation. The new examples/road-matrix-probe reduction keeps
Rally's startup protocol and80bounded section calls. Compute-only suppresses
just the final transformed PLOT calls; draw retains them. Native stock and
physical P4 runs will distinguish stream/matrix lifetime from primitive
execution. No speculative mutex/DSP/heap remedy is applied before this split.


Both compute-only and ordinary single-buffer draw reductions complete on stock
Fab and retain the same P4 keyboard epoch through bounded physical observation.
The native receipts are80submitted calls/960ticks for each; physical receipt
readback follows after the double-buffer case. The full-game failure therefore
needs a condition beyond this paced, asset-free matrix workload.

A failure-only mutex initialization probe is being built as a separate draft
variant with the baseline TCP setting. GCC14's selected shared_ptr mutex policy
calls __GTHREAD_MUTEX_INIT_FUNCTION without checking its result. The local SDK
pthread implementation can return allocation errors before storing the handle.
That is a hypothesis to test, not a diagnosis. The optional link wrapper preserves
successful calls, counts them, and on the first actual initialization error logs
its status plus free/largest internal heap and aborts at the origin. It sends no
VDP/MOS packet and makes no semantic repair. Ordinary console builds exclude it.
Exact source/build/rollback precede any deployment; preserved crash dumps remain
the authority until a new probe supplies evidence.


## First diagnosed failure boundary

The failure-only mutex probe catches pthread_mutex_init returning11 (EAGAIN)
on call23382 before the later invalid-handle destructor. Internal8-bit heap
has1215bytes free and largest block36bytes; total8-bit free remains30589179bytes.
The SDK allocates a FreeRTOS mutex semaphore from internal memory and returns
EAGAIN if that allocation fails. GCC14's shared_ptr mutex constructor ignores
that result, leaving a later invalid handle possible. The probe stack reaches
checkTransformBuffer/Context::drawBitmap while creating an inverse-matrix
BufferStream; allocation demand can fail at different sites after exhaustion.
This establishes internal-memory exhaustion as an earlier failure boundary,
not yet whether the memory is leaked, fragmented, or at legitimate peak use.

The8-second compute and mode136 draw receipts both read80/960ticks, and a manual
swap plus Legacy/SD recovery passes. The earlier mode8 draw CSV was overwritten
by the mode136 run; retain its output/epoch evidence without pretending its
terminal receipt was independently downloaded. Current baseline startup stays
unchanged. A second optional diagnostic also counts successful init/destroy
calls and stops on an actual destruction error to distinguish lifecycle loss
from peak demand. No fix or speed claim is inferred from the allocation probe.


## Internal allocation trace increment

The init/destroy-count variant records 23,384 successful initializations and
23,246 successful destructions before EAGAIN: 138 net counted live mutexes.
It reports internal free 991 bytes, largest block 36 bytes, and total free
30,588,871 bytes. No destruction error precedes it. This does not establish a
growing mutex leak; trace the other retained internal allocations before a fix.

The next isolated draft enables the selected ESP-IDF standalone heap tracer,
frame pointers and eight caller frames, with 32,768 records and its hash map in
PSRAM. It starts at the 512th mutex initialization, after early startup, and
stops on the first actual mutex error. A serial dump copies and prints only
live internal records without holding the SDK dump helper's long critical
section. Freed records are removed; capacity, high water and overflow are
reported. No record pointer is dereferenced. Starting late omits earlier
allocations and PSRAM record storage omits ISR allocations. Tracing perturbs
timing and memory usage; no performance result can come from this build.

Pinned SDK sources are components/heap/{Kconfig,heap_trace_standalone.c,
include/esp_heap_trace.h} and components/esp_system/Kconfig. Official context:
https://docs.espressif.com/projects/esp-idf/en/v5.5.1/esp32p4/api-reference/system/heap_debug.html .
The local SDK is the implementation authority. Preserve the preceding core
before flashing; archive all maintained inputs before building, verify their
hashes afterward, verify expected installed app/partitions before deployment,
and retain serial evidence through exactly one admitted Rally launch. Restore
CLI/SD through the established Pi reset if the P4 aborts. Keep baseline TCP5760
and ordinary configurations unchanged. This remains within P003-V03.

The trace application compiles with unchanged maintained inputs. Enabling
frame pointers also grows the SDK bootloader to 26,288 bytes, beyond the
24,576-byte space before the partition table. The merger rejects that overlap;
no overlapping image is deployed. The diagnostic package instead retains the
preceding independently verified 24,448-byte bootloader and identical entire
128KiB boot/partition prefix, and places only the new application at0x20000.
Effective SDK differences are heap tracing and the backtrace/frame-pointer
choice; there is no flash/PSRAM/security/partition protocol difference. The
rejected generated bootloader and packaging hashes remain in the manifest.
This is a diagnostic packaging exception, not a layout change or release.

The first heap trace completes without overflow: 9,360 live internal task
allocations, 318,700 payload bytes, dominated by paired 32/36-byte allocations.
Two serial rows interleave with network logging and are excluded from detailed
parsing (68 bytes); aggregate firmware counts remain intact. Allocation stacks
stop at the prebuilt libstdc++ operator new, whose library lacks frame pointers.
The next optional trace wraps ordinary scalar/array new with default malloc
and immediate abort on allocation failure, solely to expose caller stacks.
Successful allocation behavior is retained; new_handler/exception behavior on
failure is intentionally absent in this diagnostic and cannot ship. No fix is
selected yet. Preserve the complete original trace and its parsing exclusions.


## Confirmed DSP dependency lifetime defect and bounded correction

The caller-visible physical trace locates the paired allocations in
ESP-DSP1.8.0 Mat::det, reached via adjoint/inverse/checkTransformBuffer while
Rally draws transformed bitmaps. It completes without trace overflow:
9,359 internal records,318,664 payload bytes. One32-byte record interleaves
with network logging and is excluded from detailed parsing. The remaining
32/36-byte pair sites account for316,508bytes. The selected upstream component
commit is196825deaa4848b2c8e87b6126491cd7fc87e5bf; mat.cpp SHA256 is
6dd88f0ff7e22769bbcc579fb8449693f7eaf4021bf723ee227ce34d5cb01864.
Mat::det allocates temp, then returns zero at a zero pivot without deleting it.
Cofactors of valid invertible transforms can be singular, so this does not
require an invalid game transform. A host build of that exact upstream source
passes numerical assertions but AddressSanitizer reports82,688leaked bytes in
2,176allocations after the bounded inverse/determinant exercise.

P003-V04 now tests a one-statement lifetime correction at that return. The
Extender build will generate an exact-source-bound mat.cpp derivative in its
private build directory and substitute only that translation unit. Keep the
managed package and read-only official references untouched. An explicit
experimental environment selection enables it; ordinary configuration remains
unchanged pending review. No matrix arithmetic, VDP command, rendering, FIFO,
clock, input or network behavior is intentionally changed. This repairs a
selected P4 dependency lifetime needed by the port, not upstream VDP features.
The patch must fail closed if the component source changes, retain provenance
and Apache notice, and be removed once a selected upstream release supplies the
equivalent cleanup. No upstream/public report or push is authorized here.

Run identical host numerical/lifetime checks on unmodified and generated source;
require baseline leak detection and clean corrected exit. Verify the CMake
substitution, source hashes, selected ELF and unchanged TCP/default SDK. Build
the physical correction with all optional mutex/heap/new diagnostics excluded.
After rollback and installed-image verification, repeat the same Rally launch,
observe beyond the previous failure, measure browser delivery only once stable,
then recover Legacy keyboard/SD/startup readback. Human review remains pending.


## Lifetime correction physical result

Local draft uart-excom-console-r17-b2026-09-13-12-35-10Z, factory SHA256
83355c5368e5d5338a83525c4a8d2255b6e1195359143a85d018f3e3c5abf34e, passes
independent flash verification and native USB startup. Normal SDK options are
unchanged, including TCP5760; optional mutex/heap/new probes are absent from the
ELF. Exactly one matrix translation unit is compiled, with derivative SHA256
827afa8ffff61251981f9318b94e3b98583ff0e341d23f4d208e0091da9cde58.
The original managed source hash is unchanged.

The same Rally full-game candidate now runs beyond the earlier failure. A
120-second post-launch observation contains234healthy keyboard-status samples,
no epoch change/error and no loss of native admission. The180-second normal
serial capture contains no abort/panic. Its later free8bit-minus-freePSRAM
observations stay approximately374–377KB instead of exhausting internal RAM.
This difference is a sampled heap observation, not an atomic heap accounting
proof. A30-second wired immediate-credit capture receives897snapshots at
29.8515FPS, median31.2ms, maximum75.8ms, zero sequence gaps. Decoded320x240
frames show Rally's attract text, car and road. This is browser delivery and
agent image inspection, not hardware scanout FPS or Author visual acceptance.
The browser's final close produces a normal trailing failed-header/disconnect
log; no failure was reported in the measured observer window.

Escape quits the game. Keyboard commands select Legacy, load/start sdserve,
and mainboard startup readback matches its prior hash; the service exits to
CLI. Accepted production files/startup, EMOS and onboardVDP were not changed.
P003-V02's workload/recovery collection is machine-complete. V03–V05 continue
for video throughput; the lifetime blocker is resolved within this bounded
local candidate, pending Author review. No commits or publication occurred.

To build this experimental correction, set AGON_EXTENDER_DSP_LIFETIME_FIX=1
for the ordinary p4-console build invocation. The default selection deliberately
stays unchanged until review; omitting the selection builds the original DSP
source. The ignored source/archive/build manifest is authoritative for the
observed candidate. Do not accidentally describe a later default build as fixed.


## Next transport experiment: idle wait between snapshot checks

With the lifetime correction fixed across both cases, collect an ordinary
marker/control run, then compare only the network worker's10ms polling wait
against1ms in an isolated opt-in build. The worker already wakes on a browser
credit but receives no wakeup when the separate stock output worker publishes
a newly requested snapshot. That source boundary can add avoidable waiting;
it is not yet established as the dominant cost. Keep TCP5760, renderer, clock,
credit/lease rules and all retained APIs unchanged. A source constant selected
only by an experimental compile flag bounds this comparison. Do not replace
normal defaults, introduce producer-side network waits or claim rendering
speedup from browser delivery. Compare the same wired observer, marker receipt
and Rally, then perform the established Legacy/SD recovery. If shorter polling
helps, consider a separately bounded publication notification to remove the
extra wakes; do not assume that design is required before measuring.

The corrected-DSP/poll10 marker control emits the same1,200updates/2,400ticks
and36,221VDU bytes; terminal receipt and Legacy/SD recovery pass. Wired delivery
is32.6130FPS over30seconds with zero sequence gaps. The observer begins after
marker startup and includes its final static state; this is not a20-second
end-to-end observation of every update.

The selected SDK runs FreeRTOS at1,000Hz, so1ms is one blocking tick, not a
zero-tick busy loop. Exact executable DWARF and worker disassembly verify10ticks
in the control and1tick in the experimental build. CMake's compile_commands
alone omits some final PlatformIO/SCons flags; executable inspection is the
validation authority for this comparison. Full opaque-write and failed-stop
network containment regressions pass with the unchanged protocol.


## One-tick polling physical comparison

The opt-in poll1 build uart-excom-console-r17-b2026-09-13-12-49-15Z (factory
SHA256dbaf939f5e75b5ddd31ac0bd79f195a556fbc7f904027f1e4d1add59d67f9d1d)
passes flash verification, native keyboard admission, Rally output, later
60-second status observation and Legacy/SD recovery. Root startup is unchanged.
Both builds use the exact same DSP derivative and otherwise identical SDK.
Serial capture/readout timing was not aligned between the two later browser
runs; ordinary logging/readout timing is not an exact controlled variable for
that Rally comparison. Do not attribute a sub-percent difference to polling.

| Wired immediate-credit workload |10ms poll|1ms poll|
|---|---:|---:|
| Rally30-second received FPS |29.8515|30.0071|
| Marker30-second received FPS |32.6130|58.1482|
| Marker valid snapshots/s in changing interval |31.1200|55.9479|
| Marker changing interval observed |14.2352s|14.3169s|

Each30-second measurement has zero sequence gaps. Marker median receive interval
improves30->17ms; maximum86->74.5ms. The complete received-window result includes
the final static marker, so it overstates the rate of valid changing-marker
observations. Complement validation excludes intermediate ordinary rectangle
updates; it is not a framebuffer-atomicity test. Both terminal receipts are
identical:1,200updates/2,400ticks/maxgap1/36,221VDUbytes/last1199.

Shorter polling demonstrably removes delivery delay on the light workload.
Rally still has another limiting stage, which this experiment does not locate.
P003-V03/V04's bounded diagnosis/correction checks are machine-complete; Author
acceptance/commit/publication remain pending. The ordinary polling default stays
10ms. Continue V05 with a640x480 comparison before selecting further work.

For the next isolated640x480 comparison, keep poll1 and the DSP derivative
fixed, and repeat the previously evidenced TCP send-buffer experiment at32KiB
versus5760. The earlier independent TCP case improved the large frame while
leaving the tiny poll wait unresolved. Combining those already bounded changes
is a new candidate, not an assumed additive gain. Build/archive while the
current read-only observer runs; do not flash until it closes and Legacy/SD
recovery is proven. Compare actual headers/dimensions, the changing marker and
Rally, with one viewer and unchanged normal SDK/source defaults.

Correction after the header audit: poll1/TCP5760 delivers28.7625FPS at
640×240, not640×480 (20seconds,577frames including one older320×240 snapshot),
median33.2ms, max86.3ms, zero gaps. The command was VDU22 3 in normal numbering.
Earlier poll10/TCP5760's14.6827FPS was640×480, so those two rates are not a
same-layout comparison. The subsequent combined run below also uses640×240,
making its direct comparison with this poll1 control valid at that size only.
The exact header audit and correction sidecars preserve the original raw runs.

The combined draft is uart-excom-console-r17-b2026-09-13-13-07-24Z, factory
SHA2565bddd14bc5611c99c6b1e90b18fc0f2ed7167298a499199c6248dd8b1fbb489c.
Effective SDK differences versus the poll1 control are only TCP_SND_BUF_DEFAULT
and its LWIP compatibility spelling,5760->32768. The matrix derivative matches
and ELF reports the same1ms worker wait. Baseline CLI/SD recovery passes before
this candidate's deployment. Mainboard firmware/startup/accepted game untouched.
Rally already targets30draws/s; its browser snapshot rate is a separate quantity,
so do not infer a universal30Hz port limit or a requirement for60distinct game
frames from these delivery observations.

## Combined candidate and bounded closeout

The combined candidate passes native admission, a 60-second Rally status watch
(116 healthy samples, no epoch change/error), decoded attract output, Escape,
Legacy CLI, SD startup readback and service exit. The accepted production game,
startup, EMOS and onboard VDP remain unchanged. All observers and serial
captures have closed. Exact private deployment/current foreground is recorded
in HARDWARE.local.md. No human acceptance, commit or publication is claimed.

| Wired immediate-credit observation | Poll1 / TCP5760 | Poll1 / TCP32768 |
| --- | ---: | ---: |
| Idle 640×240, 20 seconds | 28.7625 FPS | 29.8581 FPS |
| Marker, 30-second received window | 58.1482 FPS | 59.6935 FPS |
| Valid marker observations in changing interval | 55.9479/s | 58.5155/s |
| Changing interval observed | 14.3169 seconds | 14.1501 seconds |
| Rally, 30-second received window | 30.0071 FPS | 30.7136 FPS |

All listed windows have zero sequence gaps. The repeated combined marker has
median 16.9 ms / maximum 31.7 ms receive intervals and the unchanged terminal
receipt: 1,200 updates, 2,400 ticks, maximum submission gap 1, 36,221 VDU bytes,
last frame 1199. The first combined marker observer started late and includes
only its final 2.9 seconds of changing output; retain it as a timing/setup limit,
but use repeat02 for the comparison above. Delayed/static snapshots, incomplete
ordinary VDU updates and browser submission remain distinct from rendering.
One initial retained640×240 snapshot precedes320×240 in the late marker run.
The header audit and retained mode table resolve this as the prior mode3
surface, not mixed or corrupt metadata. The initial research prose incorrectly
assumed mode3 was640×480. Actual normal mode0 is640×480/16colours; mode3 is
640×240/64colours. No snapshot implementation change follows from that mistake.

The larger send buffer adds a modest delivery gain after the polling correction.
These single runs do not establish sub-percent timing or gameplay improvement.
The DSP cleanup is the evidenced stability repair; one-tick polling is the
large light-workload delivery improvement. Keep both polling and TCP tuning
experimental, including the combined image, until Author review. The ordinary
source default remains 10 ms and the ordinary SDK remains TCP5760. The DSP
selection also remains explicitly opt-in as documented above.

P003-V01–V05 are machine-complete within this scope. General speed parity,
graphics-hook overhead and the held paired
QUAL-003 timing work are not resolved. The next faithful coverage slice is
font creation/selection/property/deletion/copy and its visible rendering, under
PORT-008's ordinary command expansion. The accepted VDU disposition inventory
retains those commands; the old qualification matrix is still a superseded
mode candidate and must not be promoted by these observations.

An additional mode0 observation now checks true640×480 after the resolution
correction. The observer prints counts for every actual header layout so an
informal run label cannot silently substitute for pixel dimensions. This is a
host evidence change only; the same physical firmware stays installed.

The actual mode0 run receives395frames in20seconds, including one older
320×240 snapshot and394frames at640×480. Full-window delivery is19.6244FPS;
the settled640×480 interval is19.6339FPS, median50ms/max63.8ms, zero gaps.
The earlier TCP32768/poll10 result at the same dimensions was19.0936FPS, so
short polling adds only a small gain for this large surface. That earlier image
predates the DSP lifetime correction; idle console output does not exercise
its inverse-transform path. Do not reuse the invalid640×240-versus640×480
comparison to claim a doubled large-surface rate. The light marker improvement
and Rally observations retain their independently verified320×240 layouts.
