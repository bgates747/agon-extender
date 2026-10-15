# SCROLL-001 — Pattern-based scrolling qualification

Measure actual completed scrolling on mainboard VDP and Extender while using the
approved mode-specific pattern as the moving image. Begin with single-buffered,
240-line, 4:3 modes. Full-screen means every pixel moves, preserving stock's
full-width/full-screen optimized paths. Timing must describe VDP execution, not
merely eZ80 command transmission. This records the Author's evolving design;
offline implementation is in progress. The eight-case eZ80 program builds and
its independent pixel-model checks pass. No firmware has been installed and no
physical test has been invoked for this task.

## Agreed scope

1. One eZ80 program contains eight cases: full-screen up/down/left/right and
   partial-region up/down/left/right. Advance one logical pixel per vblank.
2. Begin with 4:3 modes; wide Extender variants follow later. Initial 320×240
   geometry: vertical partial region256×240, centered with32pixel sidebars;
   horizontal partial region320×176, centered with32pixel top/bottom margins.
   Larger-mode geometry is not yet selected; the builder accepts explicit width,
   height and margin rather than extrapolating silently.
3. Wrap at the tested region's own opposing boundary. Partial cases leave the
   surrounding image unchanged. Full-screen cases move the entire image,
   including identification embedded in the pattern; no reserved fixed banner.
4. Use each mode's approved palette-quantized pattern. Preserve original image
   identity/phase and clear case announcements between measured runs.
5. Vblank paces drawing updates. Exclude intentional vblank waiting from rendering
   timing. Record overload/backlog rather than disguise missed pacing slots.
6. The Author requests time spent by the VDP executing the full rendering work.
   Distinguish scroll primitive execution, exposed-edge wrap restoration and
   completed scroll-plus-wrap rendering. eZ80 submission/return latency is not
   an acceptable substitute for actual VDP rendering time.
7. Compare mainboard versus Extender at equal mode/geometry/work, and compare
   directions/full versus partial within each processor. State dimensions and
   scope; do not normalize away the differing region areas.
8. Double-buffered tile-scroller game mechanics remain deferred in DBUF-001;
   they are not an added case or dependency here. Frozen prior suites/results
   remain historical evidence, not editable test definitions.

## Source review and timing investigation

1. Official VDP v2.16.0 Context::scrollRegion in
   ../../../../agon-vdp/video/context/graphics.h routes public VDU23,7 to Canvas
   scrolling. Official command contract:
   ../../../../agon-docs/docs/vdp/VDU-Commands.md section VDU23,7.
2. Project-retained upstream-shaped VGA64Controller::VScroll uses generic
   row-pointer swapping with sidebar copying when the region is narrower than
   the viewport. Full-width scrolling avoids sidebar copies. HScroll contains
   specialized aligned packed-byte/word shift paths for one-pixel scrolling.
   Locations: vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp and
   vdp/vendor/vdp-gl/src/displaycontroller.h. Establish the immutable upstream
   library revision before treating a full audit as complete. Verified release
   baseline: official VDP v2.16.0/c7ac293d2aa81ddfa693390549bcd909069c8fc3,
   linked vdp-gl all-the-plots/ac2dd5986daf496c43ae8e7fe41836274aec54a0.
   Both reference worktrees are clean. Official documentation inspected at
   f9806bd3cbff6ed5d1c08bef1d51fed11764b86b.
   MOS reference is clean official v3.0.2 at
   8336409351ee5314e02801a7b72a4f1bb5282519.
3. P4 alternative controller: vdp/video/extender/display/p4_rgb888_controller.cpp.
   Full-width vertical row-pointer rotation is retained for owned rows. Borrowed
   panel storage uses stock's copy/fill overload because DMA row addresses cannot
   rotate. Narrow linear-byte vertical regions also select that copy/fill path.
   Horizontal scrolling is rewritten as row-wise memmove plus exposed fill;
   upstream's packed VGA lane-shift specialization is not retained there.
4. Audit the exact selected source/controller/format in each mode before building
   the fixture. Root working tree and retained experimental source can differ;
   no source selection or firmware repair is implied by these initial findings.
5. Canvas.waitCompletion exists internally, but waitCompletion(false) actively
   processes primitives immediately and therefore changes normal scheduling;
   Canvas.getPixel itself is not a universal completion barrier. Do not time
   either wrapper and call that normal-worker scroll execution.
6. Inspect/reuse retained operation timing at the actual normal primitive
   execution boundary, with matched mainboard/P4 scope and monotonic clocks.
   Include wrap drawing and final render housekeeping in a separate complete
   update measure. Retain queue wait separately, no forced synchronous execution
   merely to simplify timing. See docs/testing/game-timing.md and existing
   render operation instrumentation in displaycontroller.cpp.
7. Establish a bounded diagnostic record/terminal protocol compatible with EMOS;
   no private keyboard completion carrier or unproved stock-poll fence. Prove
   operation ordering, measurement overhead, missing records and timeout behavior
   before claiming actual completed rendering measurements.

## Remaining gates

1. Finish the stock-versus-port path audit, including actual linked upstream
   revision, selected controller, full-width optimizers and partial-region
   algorithms. Record retained versus rewritten behavior without assuming a
   rewrite is beneficial.
2. Agree the precise primary timing interval and normal-worker instrumentation,
   clock calibration, controls and record retrieval before implementation.
3. Select initial mode/colour matrix, per-case duration/repeats, overload policy
   and how current case identity stays accessible without changing full-screen
   scroll semantics. Do not assume additional resolved choices.
4. Build a new revision, validate region/wrap correctness and timing independently,
   then stage under the normal readiness protocol. No flash/reset/run authorization
   comes from this planning record.

## Offline implementation — 2026-10-14

1. Maintained source: `tests/fixtures/display-pattern/pattern-wide.svg` preserves
   the approved artwork. `tests/fixtures/scroll/build.py` renders the4:3crop,
   embeds mode/case identification, draws native swatch indices and quantizes
   every pixel to the selected default palette. Generated assets are not source
   dependencies. Width, height, margin, palette, mode, steps and result path are
   explicit inputs. The eZ80 program reads configuration without recompilation.
2. `geometry.py` defines the eight regions and wrapped source/destination strips.
   Independent pixel checks exercise complete phase cycles on320×240and other
   non-square grids, asserting stationary pixels outside every partial region.
   Public PLOT&ED installs graphics clipping; direct bitmap draw does not install
   it, so the fixture deliberately uses PLOT for the one-pixel restore.
3. Draft first package defaults: mode8/320×240/64colours,600updates per case.
   These are configurable preparation defaults, not expanded Author acceptance
   or a measured runtime estimate. Modes9–11can reuse the same executable with
   their matching patterns/configurations. Wide modes and another resolution
   remain subsequent qualification scope.
4. Matched private diagnostic counters use the existing admitted16-byte QTG
   reply envelope. Operation11probes the extension before any measured work.
   Counter reads9/10report scroll sum/calls and maximum/boundary crossings;
   11/12report bitmap equivalents. Existing1–8retain their meanings.
   Default-off `--graphics-timing` is selectable through the native P4 builder;
   the stock-derived mainboard builder selects `--scrolling`. No production
   firmware or new general callback ABI is selected by these changes.
5. Primary scope is summed normal-worker primitive execution plus final sprite
   housekeeping, in local ESP monotonicµs. Scroll and bitmap are separately
   reported subsets; never add them again. Vblank, queue and native-lock waits
   are excluded. Parser/submission/SD work and scanout are separate scopes.
   These are elapsed operation intervals including preemption and measurement
   overhead, not exclusive CPU cycles. No foreground flush/pixel query is used.
6. Per-case wall duration and final drain remain secondary diagnostics. Timer
   pairs are measured outside capture and retained without subtraction. Pacing
   uses the real mainboard VBlank/MOS clock (2units per edge, nominal120units/s
   at60Hz), including during Extender runs; phase alignment to P4 HDMI is not
   claimed. Missed slots describe application submission, not demonstrated
   completion of each update at scanout. Per-update completion percentiles are
   not available from these aggregate counters.
7. The fixture requires expected scroll/bitmap counts and no reported boundary
   crossings. It refuses existing result files, preserves partial failures,
   records whole-suite start/end/duration, and displays terminal status on both
   routes through EMOS display-preserving switching, finishing in Legacy.
   These physical behaviors still require bounded verification.
8. Remaining readiness work: independently verify installation/rollback,
   validate empty and pacing-only controls and a bounded wrap smoke, deploy and
   read back fixtures/configuration, confirm input/CLI and fresh card handoff.
   The Author's stop-before-full-suite-invocation boundary remains active.

### Built preparation artifacts

1. Mainboard image: `scroll-mainboard-timing-r01-b2026-10-15-02-56-21Z`,
   firmware SHA256
   `61bdfedea437199565646b07e91589eea67a3a8bd70a7c5b68be933ec2e0fb4a`.
   Stock VDP/GL commits above, root preparation commit f5f20d54, native ARM64
   toolchain and pinned PlatformIO6.1.18. Built successfully; not installed.
2. P4 image: `indexed-hdmi-r09-b2026-10-15-02-54-12Z`, diagnostic source
   28514129dda88a13b411c2655749506a7e662b0c based on tested c233ac8e.
   Retains indexed frame snapshot, bitmap fast path, overlay ordering, visible
   software-sprite snapshot and normal rolling HDMI selections from that
   baseline. The only source changes are execution diagnostics and explicit
   native build/validation selection. Native build/action validation passes.
   This is a separately pinned experimental derivative, not the fsim prototype
   currently last verified on the bench and not a production selection.
3. Offline320×240and512×384packages produced identical eZ80 executable bytes
   before the final notification refinement, confirming that dimensions and
   geometry are runtime configuration. That512×384package is an offline
   portability check, not another authorized physical test or selected geometry.
4. Local receipts, exact binaries, generated patterns and installation planning
   remain ignored under the active task's machine-local evidence directory.
   No device access, flash, reset, fixture deployment or invocation occurred.

### SD staging — 2026-10-14

The Author subsequently returned the Agon card to the host and authorized copying.
The fixture, eight patterns, configuration/launcher, readable instructions,
manifest and both diagnostic firmware installation inputs are staged at
`/extender/scroll-r01`. All18files were verified; ordinary startup is unchanged
and the card was left mounted. This supersedes the earlier no-deployment state.
Firmware installation, bounded controls, input readiness and actual invocation
remain unperformed. The suite is staged on SD, not ready to start.

### Individually callable tests — Author direction

The Author requires each test to be independently callable, with batch dispatch
calling those same tests. Fixture revision `pattern-scroll-r02` accepts a named
case or explicit `all`; omitted/invalid selection executes no test. All paths use
the same `run_case` function, with identical rendering/timing code. The batch
stops on its first failed case. Individual launchers and the batch launcher use
the documented MOS `RUN &040000 <parameters>` interface. No test changes mode.

Result filenames append the observed route (`mb` or `ext`), selection and optional
run label to the configured base. A single-case run therefore cannot collide
with an all-case run; repeat labels preserve earlier results. The existing
refusal to overwrite remains. Completion is announced after the selected test
or complete batch, with EMOS retaining both display cues and finishing Legacy.

The updated eZ80 program builds. Sanitized host checks verify each single-case
selection, batch order, first-failure stopping and invalid selections/labels.
Physical readiness gates and the stop-before-full-batch boundary remain unchanged.

### Source audit limits

1. The P4 64-colour alternative uses owned row rotation for full-width vertical
   scroll, stock copy/fill for fixed panel rows or narrow indexed regions, and
   rewritten horizontal memmove/fill. The320×240mode8experiment selects this
   alternative when direct RGB888/indexed experiments are enabled.
2. The ordinary2/4/16-colour P4 controllers select stock-shaped packed VGA
   implementations. Their exact algorithm/compiled baseline audit is still
   needed before those modes enter the first comparison matrix. Do not apply
   mode8findings to all colours or infer performance from source alone.
