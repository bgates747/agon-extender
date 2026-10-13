# Indexed snapshot row-copy pilot — bounded preparation

This default-off NP03 candidate targets the measured cost of copying the logical
indexed image into its private publication snapshot. It reuses the existing P4
PIE row-copy kernel and bypasses the ordinary row helper's unconditional 880-byte
temporary stack frame. It does not remove the snapshot, change its timing or
establish a performance gain. The [Nurples performance contract](NURPLES-PERFORMANCE-R01.md)
continues to govern comparison and acceptance.

Base: `5444b8f345fc79439a382411c780dda7bd427397`. Preparation branch:
`codex/nurples-indexed-copy-r01`. Frozen comparison checkouts remain unchanged.

## Selection and preserved behavior

1. `--indexed-snapshot-pie` selects the numeric definition
   `AGON_EXTENDER_INDEXED_SNAPSHOT_PIE=1`. The builder requires the existing
   indexed PPA, complete-frame snapshot and automatic normal rolling HDMI
   composition, excludes parallel handling, and records the selector in both
   build and action-validation manifests. Omission or explicit numeric zero
   removes the candidate controller entry point and calls. Cache-once is not a
   dependency; matching comparisons must choose that independent option equally.
2. The P4 output task uses the candidate only for the existing undecorated
   512×384 single-buffer indexed snapshot. It copies each authoritative visible
   row descriptor separately, for exactly the logical row width. Stock scrolling
   may rotate descriptors and the allocator may use separate pools, so this
   candidate never flattens or coalesces source allocations. Other dimensions,
   double buffering and decorated rows retain `copyLinearRow` unchanged.
3. The existing native guard still excludes drawing for the complete copy and
   matching scene capture. Software-sprite visibility refusal precedes any copy,
   and the original stopping check remains before every row. Snapshot allocation,
   prior-submission retirement wait, target selection, cache operations, PPA,
   output submission, task notification and mode/lifecycle ownership are unchanged.
4. Kernel availability is separate from call-site selection. The snapshot flag
   enables only `copyIndexedSnapshotRow`; renderer `copyScrollRow` still requires
   its own `SCROLL_FAST` selector. The separately selected
   [indexed scrolling pilot](INDEXED-SCROLL-PIE-R01.md) permits both explicit
   selections to share one compiled kernel. Neither selector enables its peer.

## Kernel, bounds and execution context

1. The existing assembly instructions and ABI are unchanged. Only the assembly
   inclusion guard accepts the new independent selector. Its preprocessed text
   and extracted 84-byte instruction section are byte-identical to the base
   kernel selected by `SCROLL_FAST`; section SHA-256 is
   `c76bcebc3e19e82232c38828e8c2f250ba50f44ecfcc221228d3bd988547c98e`.
2. The existing wrapper copies a bounded scalar head and tail. Its aligned vector
   loads, source splicing and read-ahead remain inside the requested row span;
   source and destination are disjoint. No source-pool padding is assumed. ISR
   calls retain scalar `memcpy`; the actual output caller is a FreeRTOS task.
3. The reviewed target boundary remains ESP32-P4 RV32, XEspPIE enabled, silicon
   revision v1.0 or newer, using the pinned IDF task context handling for q0–q2
   and SAR_BYTES. No global PIE CFG, interrupt mask or peripheral state changes
   are added. The builder confines the PIE ISA to the existing controller object
   and assembly, keeping the remaining renderer/control objects unchanged.
4. Benchmark builds execute the existing one-shot heap/canary target self-test
   through the selected snapshot wrapper before measured rendering. Its 1,536
   cases include every source/destination alignment and the exact 256-byte
   scrolling span and 512-byte row. Failure aborts before a benchmark; host tests
   do not qualify the ISA.

## Offline evidence and remaining gate

1. Actual stock-controller ASAN/UBSAN checks pass with the selector absent, zero
   and one. They cover fragmented/misaligned rows, identity/rotated/reversed
   descriptors, all sixteen destination alignments, exact pixels, untouched
   source/canaries, cancellation, actual partial viewport scrolling and actual
   full-width row rotation. Fallback checks include 320×240, 640×480, double
   buffering and decoration; the decorated test has no active overlay.
2. The existing bounded vector-load model passes alignment, guard-page and
   partial-scrolling checks. All 27 HDMI build-selection tests pass, including
   selector isolation, numeric zero, prerequisites and unsupported composition.
3. Six actual P4 translation units compile: control and pilot versions of the
   controller, runtime adapter and HDMI output. Disassembly shows the snapshot
   entry point calling the proven kernel with a 32-byte stack frame, while
   renderer scrolling still calls ordinary `memcpy`. The ordinary copy helper
   remains the unchanged fallback. Logs, objects and command/source receipts are
   retained in ignored local preparation records.
4. A full firmware link, on-device one-shot test, same-source paired benchmarks,
   HDMI/input verification and acceptance remain unperformed. The copy may be
   memory-bound or have enough call/head/tail overhead to erase the expected
   benefit. Measure snapshot exclusion, native wait, queued rendering, rolling
   output and correctness separately; do not infer a 25%/50% rendering win from
   smaller stack use or byte-identical assembly.
