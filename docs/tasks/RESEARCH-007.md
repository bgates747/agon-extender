# RESEARCH-007 — Indexed framebuffer and palette-expansion feasibility

## Executive summary

Investigate whether one-byte indexed storage could reduce Extender's drawing,
scrolling, sprite-background and output costs while preserving stock VDP
behaviour. The primary target is faster output through P4-PC’s existing HDMI
path. Compare P4 CPU palette expansion and supported PPA/display operations. The proposed benefit is
unproven: existing direct RGB888 rendering removed an expensive conversion
stage, and indexed storage could reintroduce it.

**State: recorded, not started.** Author requested filing the supplied web-agent
feedback on 2026-10-09 while network topology changes. No investigation,
implementation, benchmark, new mode, deployment or bench action is authorized
by this record. PORT-008 coordinator work remains paused independently.

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

### R07-01 [ ] Pin contracts and inventory the current pipeline

Review official Agon documentation first, then tagged VDP/MOS sources where
implementation detail is needed. Pin exact project, reference, SDK and output
library revisions when research begins. Map framebuffer/row tables, asset
formats, saved backgrounds, rolling composition buffers, palette state and
final scanout ownership. Explain which current modes already use one-byte
storage and which use direct RGB888. Prepare a bounded source-linked précis;
do not reconstruct the pipeline from this feedback alone.

### R07-02 [ ] Establish semantic feasibility

Map each relevant VDU operation and sprite/Copper/palette path to proposed
indexed storage. Distinguish identity RGB222 encoding from a programmable
index lookup. Determine whether indices must survive to scanout for palette
changes to affect existing pixels. Describe exact support, incompatibilities
and any true-colour fallback. Treat custom 256 colours as a separate unaccepted
feature, not a prerequisite for investigating stock 16/64-colour modes.

### R07-03 [ ] Verify P4 PPA and display-peripheral capabilities

Read pinned Espressif documentation, headers and driver/source for the selected
P4 silicon and SDK. Verify whether L8 is supported in the relevant operation,
whether it means luminance or indexed colour, and whether an arbitrary CLUT
exists. Check destination formats, stride/alignment, cache coherence, overlap,
DMA-accessible memory, synchronization and output-controller capabilities.
State clearly whether expansion can share an existing scale/composition pass,
requires another pass, or is unsupported. Unsupported PPA expansion is a valid
finding; do not silently substitute a different interpretation of L8.

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
