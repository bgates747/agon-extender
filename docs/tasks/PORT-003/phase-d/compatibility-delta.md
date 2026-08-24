# PORT-003 Phase D compatibility delta

Phase D adds mutable palette/Copper state and sink-neutral composed RGB888
presentation to the qualified Phase C logical renderer. Exact upstream spans
and dispositions are generated in `evidence/presentation-provenance.yaml`;
host results and target inclusion are generated in the other Phase D evidence
records and the canonical dependency graph.

## Retained behavior

1. Palette 0 remains the drawing palette and the source of logical readback and
   native-save conversion. Secondary palettes and Copper affect presentation,
   not stored logical pixels.
2. Palette IDs remain 16-bit. Palette 0 cannot be deleted; creation copies
   palette 0; indexed writes wrap to the active palette size; unknown Copper
   palette IDs resolve to palette 0; and the last Copper span extends through
   the remaining rows.
3. RGB888-to-palette lookup remains an explicit operation using the upstream
   integer-truncated HSV-distance rule. Fixed 64-color modes use direct RGB222.
4. Common software sprites remain in the unchanged upstream framebuffer path.
   Composed-only overlays retain the order text cursor, ascending hardware
   sprites, then mouse cursor, with upstream clipping, transparency, overwrite,
   and RGBA2222 XOR semantics.
5. Single- and double-buffer drawing/visible-plane identities remain those
   qualified in Phases B and C. Logical readback observes the drawing plane;
   composed presentation observes the visible plane.

## Project-owned physical replacements

1. `PaletteState` replaces the classic VGA controller's packed DMA signal maps
   and linked palette/signal objects with allocator-injected palette nodes and
   compact row spans. The old structures contain VGA sync bytes and cannot be
   consumed by the ESP32-P4 presentation path; observable palette/Copper rules
   are retained separately from that physical representation.
2. `PresentationCompositor` replaces scanline-time VGA palette lookup and
   hardware-overlay injection with a pure logical-plane-to-RGB888 row/region
   operation. It owns no output hardware, framebuffer, task, transport, or
   sink lifetime.
3. `P4DisplayController::composeVisibleRegionQuiescent()` is a bounded Phase D
   qualification seam. Its caller must stop or suspend frame execution and all
   presentation-state mutation until copied RGB888 output is returned. It is
   not the Phase F frame-consumer or lease contract.

No upstream or vendored source byte is patched. The replacements are required
because the excluded VGA GPIO/I2S/DMA/VSYNC implementation has no ESP32-P4
equivalent, not to improve application-visible behavior.

## Deferred or excluded

Phase D does not implement or claim the official `agon_screen.h` facade, mode
table/fallback, context/callback lifecycle, Teletext, VDU parsing, MOS/EMOS,
EDU/VDU routing, transports, network/browser or physical display sinks, audio,
input drivers, storage, updater behavior, or a durable frame-consumer API.
The `p4-presentation` binary is compile/link evidence only and has no artifact
identity, deployment, or physical qualification.
