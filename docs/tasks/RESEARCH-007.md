# RESEARCH-007 — Indexed framebuffer and palette-expansion feasibility

## Executive summary

Investigate whether one-byte indexed storage could reduce Extender's drawing,
scrolling, sprite-background and output costs while preserving stock VDP
behaviour. The primary target is faster output through P4-PC’s existing HDMI
path. Compare P4 CPU palette expansion and supported PPA/display operations. The proposed benefit is
unproven: existing direct RGB888 rendering removed an expensive conversion
stage, and indexed storage could reintroduce it.

**State: R07-01 and R07-03 complete; bounded physical conversion comparison complete.**
On 2026-10-11 the Author requested detailed exploration
of indexed HDMI/PPA expansion, sample code and target compilation. The
[pipeline inventory](RESEARCH-007/PIPELINE-INVENTORY.md)
and [source baseline](RESEARCH-007/SOURCE-BASELINE.json) record R07-01;
the [capability report](RESEARCH-007/CAPABILITY-REPORT.md) and
[isolated example](RESEARCH-007/clut-example/README.md) record R07-03.
The Author subsequently requires a full runnable benchmark of CPU versus PPA
expansion. Its [bounded contract](RESEARCH-007/BENCHMARK-CONTRACT.md) authorized
offline implementation, target builds and packaging, with no bench access.
R07-B01–B04 now complete: [preparation results](RESEARCH-007/PREPARATION-RESULTS.md)
and [executable benchmark/recipe](RESEARCH-007/benchmark/README.md). The actual
firmware was built and packaged, then physically exercised under the Author’s
bench handover. R07-B05 now complete: [physical results](RESEARCH-007/PHYSICAL-RESULTS.md),
768 validated samples, all pixel/source/guard checks pass, exact ordinary P4
restored and bench released. PPA takes72–85% less conversion time than the old
CPU path, or53–59% less including signal-lane reorder, in this unloaded test.
R07-02 and R07-04–07 remain unstarted. This is isolated experimental work,
not product integration. The bounded deployment/run/restoration is complete; no
new mode, further deployment or bench action is authorized.
The machine-local reservation identifies the current bench owner;
PORT-008's separate matched-pair hardware comparison is not part of this task.

## Current tranche boundary — 2026-10-11

Latest Author direction: product integration was authorized, then paused before
implementation for discussion of stock VGA byte-lane ordering versus linear PPA
input. No integration changes or flashing occurred. The Author requested
[AUDIT-011](AUDIT-011.md) to investigate hardware fitness of upstream reuse
across the codebase; that task is prepared only, not started. Preserve stock
application behavior without assuming stock hardware layouts suit the P4.
Resolve the layout discussion before resuming integration; the earlier bounded
capability and benchmark contracts below remain evidence of their own scopes.

R07-01 is closed. The Author subsequently authorized R07-03's focused capability
research and an isolated compile-only example. Commit/push existing dirt first,
freeze this boundary, then pin relevant hardware and SDK sources. Establish
direct DSI indexed support versus memory-to-memory PPA expansion, silicon/SDK
constraints and possible small-strip output. Prefer upstream operations/code;
do not silently equate compile success with physical correctness or throughput.
Keep the current SDK, product renderer and firmware selection unchanged. Store
sample source in the task silo and generated build/tool evidence under ignored
agents storage. No flashing, serial/device access, SD/startup changes, bench
reservation or SDK replacement. Report evidence and unresolved hardware gates,
commit/push owned work and stop before product integration or hardware tests.

## Clarification — direct indexed HDMI versus PPA expansion

Author clarification on 2026-10-11: the specific question is whether P4-PC can
generate HDMI from a **one-byte-per-pixel programmable palette-index image**,
rather than merely store compact pixels internally. A previous unqualified
“yes” does not establish direct indexed scanout. Distinguish these mechanisms:

1. **Direct indexed scanout: no support established.** The P4 DSI output path
   inspected in the selected ESP-IDF 5.5.5 exposes no arbitrary palette/CLUT
   expansion stage. Its `mipi_dsi_brg_ll_set_input_color_format` in
   `components/hal/esp32p4/include/hal/mipi_dsi_brg_ll.h` selects physical RGB/YUV
   formats (with grayscale in the newer-silicon branch), not programmable
   indices. The external LT8912B bridge receives the DSI video stream; no indexed
   expansion capability there has been established either. This is the bounded
   finding for the inspected path, not proof that every undocumented hardware
   arrangement is impossible. Eight-bit grayscale is not indexed palette colour.
2. **PPA hardware palette expansion: documented in newer SDK documentation.**
   Espressif's [PPA CLUT documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/peripherals/ppa.html#color-look-up-table-clut)
   explicitly describes indexed L8/L4 input and a programmable table of up to
   256 ARGB8888 colours, configured through `ppa_set_color_lookup_table`.
   The documented L8 blend input uses eight-bit indices, not luminance. PPA
   produces expanded output pixels in a destination buffer; this is a hardware
   conversion operation, not the DSI scanout engine reading indices directly.
   Palette replacement must not overlap transactions using the same CLUT.
3. **Current SDK limitation: the inspected 5.5.5 API does not enable this path.**
   At pinned IDF commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`,
   `components/hal/include/hal/ppa_types.h` comments out L8/L4 with a TODO for
   CLUT support, and `components/hal/esp32p4/include/hal/ppa_ll.h` comments out
   those formats in its support checks. That same low-level header contains
   CLUT register helpers. Thus missing public driver support must not be
   reported as proof that the PPA hardware lacks a CLUT. Newer documentation
   does not by itself qualify our silicon, installed driver or firmware.
4. **Promising but unproven: indexed PSRAM image → PPA → RGB scanout strips.**
   The P4 could potentially ask PPA to expand successive indexed blocks into
   small RGB buffers, then have DSI DMA scan those buffers through LT8912B to
   HDMI. If feasible, the P4 CPU would not expand individual pixels and a full
   expanded RGB image might be unnecessary. R07-03–05 must establish actual
   silicon/driver support, destination-memory access, completion/cache ownership,
   palette consistency, sprite/Copper integration and refill deadlines before
   claiming this works. No performance or compatibility benefit is yet measured.

This clarification originally recorded preliminary leads only. The later
bounded R07-03 authorization above permitted isolated example compilation and
upstream-derived driver overrides. Its completed report confirms v1.3 silicon
CLUT support and records actual target compilation; it does not authorize a
product SDK upgrade, renderer integration or deployment. The online `latest`
documentation remains mutable; pinned source and PDF identities bound the
completed findings.

## Origin and boundaries

1. [Supplied feedback](RESEARCH-007/WEB-FEEDBACK.md) preserves the proposal and
   attribution. Its hardware/API/performance assertions are research leads,
   not verified findings or an accepted architecture. Earlier optimization
   results remain valid evidence for their tested compositions.
2. Assess a common eight-bit storage width with three proposed palette
   configurations: stock Agon 16 colours, stock Agon 64 colours, and a
   programmable 256-entry RGB palette. Do not assume these share stock colour
   semantics, or that the 256-entry extension already has an API.
3. Distinguish a palette index, grayscale L8, packed RGB222/RGB332, bitmap
   RGBA2222 and output RGB565/RGB888. An eight-bit input format alone does not
   establish arbitrary CLUT expansion. Determine the actual selected P4
   peripheral/SDK support before proposing a PPA conversion.
4. Preserve stock VDU colour selection, logical/physical palette mapping,
   drawing/plot operations, colour readback, transparent text/bitmaps, software
   and hardware sprites, Copper, cursor, clipping, buffering and completion
   ordering. Reuse upstream code where possible; no upstream bug fixes in a
   first faithful port. EMOS continues to own ordinary VDU routing and modes.
5. Retain a true-colour alternative where indexed storage cannot reproduce
   required behaviour. Identify precisely which operations need it and whether
   they are stock or project extensions; do not assume either universal
   quantization or universal true-colour compatibility.
6. Resistor-ladder RGB565 VGA and Raspberry Pi Pico 2/Cowbell output are
   separate investigations, primarily alternatives for P4-DevKit. They are
   neither a dependency nor an output implementation within this task. See
   [RESEARCH-005](RESEARCH-005.md) for the VGA lead and
   [RESEARCH-008](RESEARCH-008.md) for P4-to-Pico output. Existing mainboard
   ESP32-to-Pico research remains [RESEARCH-006](RESEARCH-006.md).

## Memory hypothesis

These are arithmetic payload sizes for tightly packed 320×240 pixels, excluding
stride, alignment, palettes, saved sprite backgrounds, DMA strips, staging,
assets and any additional logical/output buffers. KiB means 1024 bytes.

| Format | Bytes/pixel | One image, bytes | One image, KiB |
|---|---:|---:|---:|
| RGB888 | 3 | 230400 | 225 |
| RGB565 | 2 | 153600 | 150 |
| Eight-bit indexed | 1 | 76800 | 75 |

An indexed image is one third the RGB888 pixel payload and half the RGB565
payload. These ratios do not predict frame rate or total allocation savings.
A 256-entry RGB888 palette alone adds 768 bytes. Determine whether palette updates
require output recomposition, transfer, cache maintenance or synchronized
scanout publication before calling palette animation cheap end to end.

## Investigation subtasks

### R07-01 [x] Pin contracts and inventory the current pipeline

Review official Agon documentation first, then tagged VDP/MOS sources where
implementation detail is needed. Pin exact project, reference, SDK and output
library revisions when research begins. Map framebuffer/row tables, asset
formats, saved backgrounds, rolling composition buffers, palette state and
final scanout ownership. Explain which current modes already use one-byte
storage and which use direct RGB888. Prepare a bounded source-linked précis;
do not reconstruct the pipeline from this feedback alone.

Completed 2026-10-11: official contracts and exact local tags reviewed; 5,501
retained r17 source hashes match the inspected checkout. The report separates
packed/indexed stock controllers, one-byte physical RGB222, selected three-byte
HDMI drawing storage, one-byte software-sprite saved areas, output strips/images,
PPA staging and the allocated but bypassed browser snapshot pool. Current HDMI
source, retained build and approved production are explicitly distinguished.
No new compilation, measurements or device access; pause before R07-02.

### R07-02 [ ] Establish semantic feasibility

Map each relevant VDU operation and sprite/Copper/palette path to proposed
indexed storage. Distinguish identity RGB222 encoding from a programmable
index lookup. Determine whether indices must survive to scanout for palette
changes to affect existing pixels. Describe exact support, incompatibilities
and any true-colour fallback. Treat custom 256 colours as a separate unaccepted
feature, not a prerequisite for investigating stock 16/64-colour modes.

### R07-03 [x] Verify P4 PPA and display-peripheral capabilities

Read pinned Espressif documentation, headers and driver/source for the selected
P4 silicon and SDK. Verify whether L8 is supported in the relevant operation,
whether it means luminance or indexed colour, and whether an arbitrary CLUT
exists. Check destination formats, stride/alignment, cache coherence, overlap,
DMA-accessible memory, synchronization and output-controller capabilities.
State clearly whether expansion can share an existing scale/composition pass,
requires another pass, or is unsupported. Unsupported PPA expansion is a valid
finding; do not silently substitute a different interpretation of L8.

The 2026-10-11 authorization includes these bounded implementation checks:

1. **R07-03A [x]** Pin primary hardware/SDK evidence and identify the precise
   public-driver gap, supported operations and silicon constraints.
2. **R07-03B [x]** Write an isolated target example using verified palette
   expansion operations, reusing upstream definitions/helpers where possible.
   Explain any necessary low-level access beside the code. The example must
   not initialize DSI/HDMI, keyboard, network, SD or product services.
3. **R07-03C [x]** Cross-compile/link for ESP32-P4 with retained tool identities.
   Record exact configuration, source and artifact hashes, compile failures
   that reveal genuine API constraints, and limits of compile-only validation.
4. **R07-03D [x]** Report direct-scanout and strip-conversion conclusions with
   sources. Leave physical correctness, deadline/performance and renderer
   integration unverified; stop without device access.

Completed 2026-10-11: the v1.3 TRM explicitly documents programmable BLEND L8/L4
CLUT expansion; DSI/LT8912B expose no documented programmable-index scanout.
The isolated `ppa-clut-example-r05` target compiles/links actual upstream-derived
CLUT calls with unchanged base SDK and product sources. The unmodified SDK
control demonstrates its missing public API. See the capability report for
exact build/hash evidence, preparation corrections and ISR, two-input, scaling,
palette and strip-deadline limits. No physical correctness, throughput, gameplay
or product-integration result; pause before remaining subtasks.

### R07-04 [ ] Compare CPU and output-stage alternatives

Evaluate CPU lookup expansion by scanline/rolling strip versus full-image
conversion, and retaining direct RGB888/RGB565 for selected modes. Account for
read/write traffic, setup and synchronization, sprite/Copper composition and
palette updates. Include Nurples's partial vertical scroll and many sprites
as the principal performance target. A smaller stored image is insufficient
if the additional expansion jeopardizes scanout deadlines or input response.

### R07-05 [ ] Assess buffer and palette publication lifetimes

Account for total live memory on P4-PC: logical framebuffers, saved backgrounds,
assets, palette tables, output strips/images and DMA storage. Trace when drawing,
palette changes, sprite composition and scanout observe each version. Determine
whether indexed storage can avoid a full RGB output image without introducing
tearing, stale palettes or missed scanout deadlines. Check PSRAM traffic and
cache synchronization, rather than inferring contention from storage size.

### R07-06 [ ] Propose a small discriminating test plan

Reuse existing rendering-load, colour/palette, sprite and deterministic Nurples
fixtures wherever applicable. Propose at most five workload classes: static
palette changes, partial scrolling, scrolling plus loaded sprites, bitmap/
transparency correctness, and the necessary true-colour fallback control.
Compare against exact existing renderer identities at matching geometry,
content, buffering and output timing. Separate drawing/scrolling, expansion,
composition, cache/DMA handoff, scanout. Include total
memory, real work/wait headroom, input response and visible corruption/tearing.
Prepare the proposal only; execution needs a subsequent reviewed contract.

### R07-07 [ ] Report and pause for an architecture decision

Produce a compact comparison table of feasible paths, semantic coverage,
measured versus inferred costs, upstream reuse, complexity and uncertainties.
Recommend retain-current, bounded indexed experiment, or defer. State which
potential gains apply to P4-PC HDMI and which could also apply to LCD.
Update related task links and the dated log. Pause before code changes, new
commands, peripheral/transport selection, measurements or deployment. If the
Author selects a material design change, follow the normal task/ADR/mainline
architecture process; this investigation itself changes no architecture.

## Dependencies and non-duplication

1. [RGB-001](RGB-001.md): direct RGB888 drawing and prior conversion tradeoffs.
2. [SCAN-001](SCAN-001.md): partial vertical scrolling and retained remedies.
3. [SPRITE-001](SPRITE-001.md): rolling sprite composition and buffer lifetimes.
4. [PPA-001](PPA-001.md): broader drawing acceleration, independently deferred.
   Share capability findings; do not restart its broader assessment here.
5. [HDMI-002](HDMI-002.md) and [LCD-001](LCD-001.md): output formats/timings and
   geometry constraints. No timing changes to confound a storage comparison.
6. [RESEARCH-005](RESEARCH-005.md), [RESEARCH-006](RESEARCH-006.md) and
   [RESEARCH-008](RESEARCH-008.md): independent resistor-ladder VGA,
   mainboard-to-Pico and P4-to-Pico investigations; no dependency on them.
7. [BENCH-009](BENCH-009.md) and [render-load guide](../testing/render-load.md):
   existing comparable fixtures, timing scopes and retained evidence.

## Decision register

### R07-D01 [ ] Storage architecture — unresolved

Recommendation: make no storage change until R07-01–07 establish compatibility
and the cost of expansion. Alternatives are retaining current storage,
indexed stock-colour paths with output-stage expansion, or mixed indexed/
true-colour storage. The Author decides after the report.

### R07-D02 [ ] Custom palette scope — unresolved

Recommendation: evaluate custom 256 colours as a separate possibility without
making it a dependency of stock 16/64-colour storage research. Its API and
implementation require separate approval after feasibility is established.
