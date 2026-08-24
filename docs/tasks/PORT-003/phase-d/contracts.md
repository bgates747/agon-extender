# PORT-003 Phase D contracts

These contracts freeze Phase D behavior before production implementation.
They extend the qualified logical renderer/frame service without defining an
official mode facade, a durable consumer lease, or a physical output sink.

## Palette state

1. `PALETTE2`, `PALETTE4`, `PALETTE8`, and `PALETTE16` have 2, 4, 8, and 16
   entries. `SBGR2222` is fixed direct RGB222 and has no mutable/Copper palette.
2. Palette ID 0 always exists. Deleting ID 0 has no effect. Deleting ID 65535
   deletes every secondary palette but preserves palette 0.
3. Creating a secondary 16-bit palette ID copies palette 0 as it exists at that
   call. Recreating an existing ID recopies palette 0. Failed allocation leaves
   all old state valid.
4. Setting an entry wraps its index modulo the active palette size, creates a
   missing secondary palette when allocation succeeds, and quantizes RGB888 to
   the stock RGB222 output space by retaining each channel's two high bits.
5. Palette-0 mutation does not implicitly rebuild drawing quantization. The
   explicit LUT update uses the retained HSV-distance rule and higher-index
   tie preference, matching the upstream call boundary.
6. A successful mode reconfiguration resets secondary palettes, signal-list
   state, palette 0 to the depth's controller defaults, and the drawing LUT.
   Failed reconfiguration preserves the complete old state.

## Copper signal list

1. Each raw entry is an unsigned 16-bit row count followed by a 16-bit palette
   ID. Row counts accumulate from output row zero.
2. An ID absent when the list is installed resolves to palette 0 and does not
   later retarget merely because that ID is created.
3. Deleting a referenced palette retargets those spans to palette 0.
4. The last installed span applies to every remaining output row. Entries
   beyond the composed height have no effect. Zero-row entries advance no rows
   and therefore allow the next entry to take effect at the same boundary.
5. The canonical reset list is one `(0, 0)` entry, which selects palette 0 for
   every row. An empty update preserves the current first span, matching the
   reachable upstream implementation boundary rather than inventing an error.
6. Copper affects only presentation. Logical bytes, ordinary screen readback,
   native bitmap saves, and palette-0 drawing lookup remain unchanged.

## Presentation compositor

1. A composition call receives one explicit native plane view, matching mode
   descriptor, palette/Copper state, requested origin-and-size region, destination
   RGB888 storage, and ordered overlay inputs. It performs no allocation.
2. Base pixels are decoded with `NativePixelCodec`. Paletted values select the
   Copper-resolved row palette; `SBGR2222` expands directly to RGB888.
3. Invalid dimensions, region, plane size/stride, destination capacity, pixel
   format, or overlay metadata returns a typed failure without partial access
   outside either buffer.
4. Composition never writes logical storage. `readScreen()` and native saves
   continue to use palette 0 and exclude hardware overlays.
5. The Phase D controller seam is synchronous and valid only while its caller
   has established quiescent state: either the logical frame service is
   stopped, or controller background execution is disabled/suspended and the
   caller retains that state until the call returns. The caller also owns all
   palette and overlay mutation for that interval. An unsuspended call while
   the service runs returns `NotQuiescent` before borrowing frame state.
6. Only RGB888 destination values leave the call. It is
   qualification/integration machinery, not permission for a sink to retain a
   plane, palette, bitmap, sprite, or cursor pointer or block the frame
   service. Phase F owns the bounded generation/lease mechanism.

## Overlay semantics

1. Unchanged common code owns software sprites and their background
   save/draw/restore behavior. Phase D does not duplicate that path.
2. Presentation overlays are applied in stock order: visible text cursor,
   visible/allowed hardware sprites in ascending active index order, then the
   visible mouse cursor.
3. RGBA8888 and RGBA2222 pixels with zero alpha are transparent. Any nonzero
   alpha is opaque; no blending is performed.
4. RGBA8888 channels are quantized to RGB222 before output. RGBA2222 carries
   RGB222 directly.
5. RGBA2222 with `PaintMode::XOR` XORs its six color bits with the already
   composed RGB222 base/overlay pixel. Other supported hardware-overlay paint
   modes overwrite, matching the old scanline routine.
6. Overlay positions may be negative or outside the viewport. Safe clipping
   must preserve the exact visible intersection and source offsets.
7. Copper recolors logical/software-sprite indices before overlays. It never
   recolors separately composed hardware sprite or cursor RGB values.

## Oracle and qualification order

1. Official Copper documentation and exact official VDP/vdp-gl source spans.
2. Independent source-derived fixture model that does not consume production
   code or output.
3. Production host output under ASan/UBSan and explicit allocation accounting.
4. Clean pinned P4 compile/link closure.

No visible image, production self-comparison, or target compile alone is a
compatibility oracle.
