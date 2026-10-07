# ADR-0025 — Bounded RGB888 rendering experiment

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-05
- Related task: RGB-001

## Decision

The Author authorizes a CPU-only experiment comparing direct RGB888 logical
storage with the retained native renderer, using existing mode20/8 workloads
and a bounded mode136 follow-up. Ordinary builds retain mode-native storage.
Only an explicitly selected experimental P4-PC HDMI benchmark build substitutes
RGB888 storage for the selected64-colour geometries.

The first implementation reuses common Canvas/rasterizers and preservesRGB222
colour quantization, GCOL operations, public bitmap formats and sprite background
semantics. The P4 CPU expands plotted bitmap/software-sprite pixels when drawing;
it composes hardware sprites into the presentation image before DSI DMA.
Definition-time expansion caches and PPA acceleration remain deferred.

The Author's subsequent direction selects LCD-owned720p buffers as the renderer's
pixel storage. Logical row descriptors address the centered viewport with the
physical720p stride. Ordinary presentation performs cache writeback/selection,
without a framebuffer copy. Stock colour/asset semantics and the independent
nominal60Hz hardware frame clock remain intact.

An application-requested double swap is staged before the upcoming DMA boundary.
A separate core1 task submits the completed back while the drawing executor
waits under native exclusion. The DMA acknowledgment releases the old front;
only then may the ordinary swap notification authorize drawing into it. This
task must not require the exclusion held by its caller. Teardown cancels an
unsubmitted request and joins a submitted buffer's physical release.

The CPU composes overlays into panel storage with saved background rows. It
restores backgrounds before drawing/readback or recycling an old front. Double
overlays are completed on the back at application swaps; independent overlay
updates without those swaps are outside this experiment's qualified scope.

## Rationale and boundary

The initial separate RGB888 planes isolated the renderer change and retained a
presentation copy. Static controls then measured23.19ms preparation at512×384,
including19.41ms row copy/composition. The Author directs removal of that copy.
Its builds, evidence and earlier decision remain traceable in RGB-001.

On IDF5.5.5/pre-v3 P4, the callback follows DMA selection. Releasing the old front
at logical pointer exchange would race scanout. Waiting until a hardware edge
to begin staging would instead introduce two-edge pacing. Early staging plus
actual DMA acknowledgment addresses both constraints. Scrolling must copy pixel
contents because DMA cannot follow logical row-pointer rotations.

No measured performance claim follows the new design alone. EMOS routing,
existing fixture bytes, fixed HDMI timing and production selection remain
unchanged. Expanded asset caches and PPA remain deferred.
