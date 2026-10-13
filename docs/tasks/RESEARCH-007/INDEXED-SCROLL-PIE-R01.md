# Indexed partial-scroll row-copy pilot

This bounded NP03 continuation reuses the existing default-off `--scroll-fast`
selection for indexed P4 storage. Base source is
`832fb5bce0e7c2375aab80cddde5adc7891fee56`. The
[Nurples performance contract](NURPLES-PERFORMANCE-R01.md) governs comparison;
this preparation neither establishes a speedup nor changes production.

Offline preparation passed actual-controller ASAN/UBSAN, existing indexed
saved-sprite/native goldens (including 1,200 alias cases), the bounded vector-copy
model and 27 build-selection tests. Twelve actual P4 controller/runtime/output
objects compiled across all four independent selector combinations; the three
selected assembly compositions retain identical 84-byte kernel code. Full
firmware linking, target execution and performance/visual qualification remain
pending. Local commands, logs, source hashes and patch identity are retained in
the owning agent's ignored preparation receipt.

## Preserved contracts

1. Official `VDU 23,7` scrolling retains the selected viewport, direction and
   pixel movement. The retained FabGL `genericVScroll` copy/fill overload still
   erases software sprites, orders row copies to preserve unread sources and
   fills exposed rows with the brush colour. No VDU or bitmap ABI changes.
2. `P4Color64Controller::rawCopyRow` already calculates the physical span using
   `kP4ColorBytes`: one byte for indexed storage, three for BGR. Partial indexed
   vertical scrolling already uses this helper. Distinct row allocations remain
   disjoint even when visible descriptors rotate. Full-width indexed scrolling
   retains pointer rotation; horizontal scrolling retains `memmove`.
3. The builder requires explicit P4 colour storage and normal HDMI; indexed
   selection additionally requires automatic rolling output and excludes
   parallel handling, matching this bounded video-only qualification. Snapshot PIE and
   scroll PIE remain independent callers of one compiled assembly source. Their
   omission retains the original `memcpy` paths. No new selector is introduced.
4. The assembly, bounded scalar heads/tails, native exclusion, task-context
   handling, ISR fallback, silicon bounds, cache and output ownership are
   unchanged. The existing target one-shot qualification adds the exact
   256-byte Nurples field width across all source/destination alignments.

## Bounded validation

1. Extend the existing actual-controller snapshot fixture with indexed partial
   scrolling in both directions, small/full-height amounts, odd X/widths and
   the 95/96-byte kernel cutoff. Fragmented/permuted source rows cover all
   alignments; compare every pixel, fixed border, row descriptor and canary.
   Verify that full-width scrolling still rotates descriptors correctly.
2. Reuse the indexed renderer/native goldens for saved-background sprites,
   overlapping erase/restore, clipping and partial scrolling. Host sanitizers
   qualify controller semantics and bounds, not execution of the P4 ISA.
3. Verify builder selections and exactly one assembly source when both flags
   are selected. Compile actual P4 controller/actions from the retained pinned
   build commands; confirm the unchanged kernel bytes and selected call sites.
4. Full firmware linking, target self-test, matched-source measurements and
   visual/input checks remain separate gates. The existing IDF `memcpy` may
   already be competitive at 256 bytes; no gain follows from instruction counts.

## Reference scope

The official VDP command reference is
`agon-docs/docs/vdp/VDU-Commands.md`, section `VDU 23,7`. Implementation scope is
the retained stock rasterizer contract in the project-owned vendored
`vdp/vendor/vdp-gl/src/displaycontroller.h::genericVScroll`, the project-owned
copy helper, and the already reviewed ESP-DL-derived PIE kernel. This pilot
does not fix upstream oversized-scroll behavior or alter its qualification
domain; tests use amounts no greater than the selected region height.
