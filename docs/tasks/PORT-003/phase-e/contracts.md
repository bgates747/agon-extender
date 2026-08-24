# PORT-003 Phase E contracts

These contracts freeze Phase E before production implementation. They bind the
official `v2.16.0` screen facade and mode lifecycle to the accepted P4 display
backend without defining transport, operating-mode, physical-input, or output-
consumer policy.

## Authority and oracle order

1. Official Agon documentation for `VDU 22`, screen modes, context reset,
   buffer swapping, mode packets, callbacks, and Teletext.
2. Exact official VDP `v2.16.0` source spans and unchanged function bodies.
3. Independent source-derived fixtures generated without production code or
   output.
4. Production host output under sanitizers and clean P4 compile/link closure.

## Facade ownership

1. The official source path, globals, function names, mode switch, and public
   behavior remain recognizable and authoritative.
2. One stable project-owned `P4DisplayController` replaces all five classic
   physical VGA controller classes. The official `_VGAController` name remains
   the owning global.
3. The P4 facade adapter parses visible width, height, and nominal refresh from
   official retained modelines; it does not implement VGA electrical timings.
4. Requested configuration maps 2/4/8/16/64 colors to the retained
   PALETTE2/4/8/16/SBGR2222 native formats and preserves the official error
   distinction between invalid depth/mode and unavailable storage/service.
5. Controller storage configuration remains transactional. The adapter stops
   and restarts the controller-owned logical frame service; a failed request
   restores cadence for the still-valid previous mode before reporting failure.
6. Palette, Copper, Canvas, dimensions, logical scaling, rectangular-pixel
   detection, Teletext, completion waits, and swaps retain their official
   facade call sites and behavior.

## Frame and cursor seams

1. Official context code continues to read and assign
   `_VGAController->frameCounter` directly. A project-owned atomic-compatible
   register proxy supplies that exact source expression while P4 frame
   progression advances the same modulo-2^32 value.
2. The display-facing cursor adapter may bind the active P4 controller, update
   mode bounds, and position its mouse-cursor overlay. It owns no physical
   acquisition, event queue, packet, variable, callback, keyboard, or
   operating-mode behavior.
3. PORT-005 remains responsible for processed input injection and the retained
   official input semantics. Phase E supplies only the cursor-position endpoint
   that its eventual adapter can call.

## Official VDU 22 lifecycle

1. The handler clears and waits on the old display, disables Teletext, removes
   all VSYNC callbacks, and attempts the requested mode.
2. Failure retries the prior mode and then mode 1. The resulting valid mode,
   not the failed request, determines subsequent metadata.
3. Every result resets all contexts. A double-buffered result swaps once and
   clears the new drawing side so both planes begin cleared.
4. A previously visible cursor is restored, the input-owned cursor positioner
   is rebound to the new dimensions, and visible mouse variables are refreshed.
5. The mode-change callback runs before the eight-byte mode packet is sent.
   The packet contains little-endian pixel width and height, one-byte normalized
   character width and height, color depth, and selected mode.

## Teletext

1. Mode 7 first configures the official 640x480, 16-color bitmapped Canvas and
   then initializes the retained Teletext implementation.
2. Successful initialization sets `ttxtMode`; a subsequent mode request clears
   it before attempting the new mode.
3. No vdp-gl textual physical controller is selected. Teletext remains Canvas
   drawing over the common P4 bitmapped backend.

No target build, visible image, implementation self-comparison, or extracted
source body alone is a compatibility oracle.
