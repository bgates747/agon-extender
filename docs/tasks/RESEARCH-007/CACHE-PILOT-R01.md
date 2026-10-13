# Indexed HDMI pre-writeback pilot — bounded preparation

## Executive summary

This default-off NP03 candidate removes one potentially redundant helper cache
operation from steady single-buffered Mode 20 indexed output. It does not remove
PPA palette expansion, change framebuffer ownership or establish a rendering
gain. The current RGB888 renderer remains the performance baseline. Offline
checks and individual target translation-unit compilation precede any complete
build, bench execution or acceptance.

Base: `a167e43ebe3a8ba2f51e000cf17a43a68443e273`. Preparation branch:
`codex/nurples-perf-cache-r01`. The frozen comparison checkout is unchanged.
This is one remedy within the [existing contract](NURPLES-PERFORMANCE-R01.md),
not a new task or an authorization to skip the static/scrolling comparison.

## Ownership and cache contract

1. The exact pinned PPA driver (`ppa_blend.c`, lines278–305 in the retained
   compilation inputs) writes back both inputs, then invalidates complete output
   rows before DMA. It does not write back CPU-modified output first. In Mode 20,
   that invalidation covers 787,968 bytes (684×384×3; 769.5 KiB), including both
   untouched 86-pixel sidebars. The CPU's initial black clear must reach memory
   before this invalidation. The SDK base remains commit
   `b774170ff46c393eeb5e495ea37936038d3f4f4f` with the existing pinned CLUT override.
   [Driver provenance](../../../vdp/compat/ppa_clut/README.md) and its recorded
   patch hashes remain unchanged.
2. The P4 output task waits for prior submission retirement before selecting its
   target. In the native indexed path, only a geometry clear writes that RGB888
   destination through the CPU; drawing uses a separate logical indexed image.
   PPA writes the active rectangle. Rolling scanout reads the RGB888 background
   and writes composed hardware sprites into separate SRAM strips.
3. An explicit per-plane eligibility record starts false. An attempt may omit
   the helper pre-C2M only when that plane previously completed PPA expansion,
   helper post-invalidation and successful panel submission in this mode, and
   no CPU clear or mode/path invalidation has occurred. Beginning the next
   attempt clears its record; refusal, cancellation or failure therefore forces
   the following attempt to retain writeback. Only successful submission restores
   eligibility. This record never replaces the existing DMA retirement wait.
4. A committed controller activation resets both records before its output task
   becomes active, after the old service has detached and joined. Same-size
   controller replacements are included. Cleanup, panel borrowing and an ordinary
   CPU row-expansion path also invalidate records. Eligibility is bounded to
   logical 512×384, carrier 684×384, single buffering and native indexed output.
   Other sizes, logical double buffering and scaled 320×240 retain writeback.
5. All driver input cache handling, driver output pre-invalidation, helper output
   post-invalidation, DPI submission and rolling-source cache operations remain
   unchanged. First use of both planes and every CPU clear retains pre-writeback.
   The helper's new trailing argument defaults to true for unchanged callers.

## Explicit build selection and measurement

Add `--indexed-output-cache-once` only to the existing explicit automatic
rolling normal-HDMI indexed/full-frame-snapshot composition. The builder and
action validator record `indexed_output_cache_once` in their manifests and
require the exact numeric compiler definition. Ordinary and comparison-control
selections omit it. Parallel handling is excluded. Omitting the option is the
complete source-level backout.

The six legacy timing phases and schema remain unchanged. Identical benchmark
builds expose an additive per-window `indexed_pre_c2m` counter containing actual
helper pre-writeback calls, elapsed microseconds, maximum and boundary drops.
This 16-window sidecar uses 256 bytes for counters and reports overflow explicitly. It is
statically absent without the existing render-benchmark definition. Driver
maintenance, blocking PPA and final panel writeback are excluded from this narrow
counter and remain covered by existing broader scopes.

A 787,968-byte cache range does not imply that many bytes are copied to PSRAM:
clean cache lines need no pixel writeback. The current SDK configuration executes
the writeback under its cache critical section; any output-wall or scheduling
benefit must be measured rather than inferred. Do not add overlapping counters
or present output-only savings as completed queued-rendering gains.
Refused software-sprite snapshots conservatively revoke eligibility too; actual
pre-writeback call counts may therefore exceed the two initial planes. A small
measured gain needs a probes-off confirmation because skipping this call also
skips its diagnostic scope overhead.

## Offline gates and remaining boundary

1. The maintained eligibility test covers both planes, first use, CPU clears,
   unchanged steady frames, identical-size mode replacement, other paths,
   invalid targets and abandoned attempts representing snapshot/PPA/submission
   failures.
2. The actual `HdmiPpaIndexed` helper is compiled and executed against an explicit
   CPU-cache/backing-memory model. It checks black sidebars, active pixels,
   retained input/output driver operations, unconditional default behaviour,
   two-plane steady omission and injected pre-writeback/PPA/post-invalidation
   failures. Address/undefined-behaviour sanitizers apply. This is a mocked cache
   and PPA model, not a silicon qualification.
3. Existing benchmark window and build-selection tests remain applicable.
   The new helper timing scope has window-boundary drops and feature-off
   preprocessing checks. Individual target translation units use the retained
   actual ESP-IDF configuration, CLUT headers and RISC-V compiler; both control
   and selected pilot must compile. A complete firmware build/link and validation
   are separate, unperformed preparation gates until requested.
4. Before adoption, compare same-source static bitmap and partial-scroll windows
   against indexed control and current RGB888, inspect this narrow cache cost,
   retain exact flags/raw evidence and verify both black sidebars, mode return,
   scanout counters and ordinary input. Do not claim repaired sprite visibility,
   a 25%/50% rendering gain or production acceptance from these offline checks.

## Prepared result

1. Sanitized eligibility and actual-helper cache/RAM-model checks pass, including
   window crossing, non-probe windows, bounded sidecar overflow/reset and static
   exclusion of the timing scope without the benchmark definition.
2. All 25 HDMI build-selection checks and existing benchmark-window checks pass.
   Individual P4 compilation passes for `hdmi_output.cpp`,
   `hdmi_ppa_indexed.cpp` and `stock_p4_service.cpp` in both control and selected
   pilot compositions. Numeric pilot `=0` preprocessing removes the eligibility
   state, lifecycle API and calls.
3. No full firmware build/link, hardware, network, mailbox, reset, flash or
   physical measurement was performed. Parent and independent second source review found no concrete ownership/cache
   blocker. Freeze the reviewed source before paired full builds. Local compile
   commands/logs and patch hashes stay in ignored records.
