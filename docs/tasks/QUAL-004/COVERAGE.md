# QUAL-004 coverage ledger

## Executive summary

First pass stopped at the frozen reliability gate: all63 mode20 scenes and three
mode9 controls have exact paired physical images. Eight prepared mode controls
remain unqualified after a second P4 mode-transition restart. No API implementation
was added. Static image parity does not qualify live resource mutation or transitions.

| Family | Planned source scenes | Current classification |
|---|---|---|
| Primitive line endpoints, patterns, thickness | SHP01–05 | Passed static image parity |
| Triangles, rectangles, parallelograms | SHP06–08 | Passed static image parity |
| Circles, ellipses, arcs, segments/sectors | SHP09–12 | Passed static image parity |
| Line/flood/path fills | SHP13–15 | Passed static image parity; path semantics experimental upstream |
| Paint variants and eight GCOL operations | SHP16–17 | Passed static image parity |
| Colour mapping and palette reset | SHP18 | Passed static image parity in64-colour mode |
| Origins, logical/physical coordinates | SHP19, BSP07/21 | Passed static image parity |
| Viewports, clears, clipped bitmap plotting | SHP20–23, BSP07 | Passed static image parity |
| Copy/move/scroll and single-row viewport | SHP22, SCROLL/CLIPROW/COMBINED | Passed static image parity |
| Default text and graphics text | SHP headings, SHP23 | Passed static image parity |
| Buffered calls, saved contexts, transforms | SHP24, BSP29 | Passed static image parity |
| Alpha and bitmap cutouts | BSP03 | Passed static image parity |
| Software sprite movement/update/layers | BSP21/22/25 | Passed static image parity |
| Hardware and mixed sprites | BSP26/27 | Passed static composed image parity |
| Custom font creation/selection/mutation/deletion | FONT01, retained PORT-008 case | Passed static image parity |
| All bitmap storage formats and conversions | Partial existing scenes | Coverage gaps to enumerate after first tranche |
| Lower-depth palette modes, static Copper | PAL16, COP16_SETUP, COP16_EDIT | Passed mode9 parity; [plain mode10/11 palettes also passed](low-depth/RESULTS.md). Four Copper controls deferred |
| Double buffering/displayed versus drawing page | PAGE_FRONT/PAGE_SWAP | [Passed both physical controls](page-controls/RESULTS.md), 2026-09-20; static images only |
| Time-varying Copper/animated scenes | Coherent full-frame acquisition needed | Deferred; stitched static rows cannot qualify |
| Sprite population stress page BSP30 | Prior mainboard timeout evidence | Deferred from first tranche; no implied pass |
| Audio synthesis, physical LCD/MIPI output | Outside graphics-image scope | Not implemented/output roadmap as previously recorded; no work here |

Missing API functionality discovered during source review or execution must be
marked **not implemented**, with its command and evidence. Do not equate a
missing test or unsupported capture mode with a missing API implementation.
Existing hardware-overlay format restrictions require comparison to stock;
a format unsupported by both devices is not automatically a port defect.

## Explicit second-pass implementation boundary

| Feature | Classification | Source evidence / disposition |
|---|---|---|
| Physical mouse cursor creation/display, including bitmap cursor command `23,27,&40` | **Not implemented** in the retained unavailable-input adapter | `makeMouseCursor()` is empty; `showMouseCursor()` leaves `mouseVisible=false` in `vdp/video/extender/input/unavailable_input_adapter.hpp`. Existing command-consumption inventory also records this. No implementation in QUAL-004. |
| Audio synthesis | **Not implemented**, outside graphics-image scope | Existing unavailable audio backend and PORT-004 framing work; correct byte consumption does not imply sound generation. No work here. |
| Native LCD/MIPI output | **Not implemented** in this selected web-output configuration | Output roadmap, not a framebuffer parity claim or a test failure. No work here. |

This is an explicit known-gap list, not an exhaustive declaration that every
other API is implemented. Runtime evidence below will classify tested operations;
missing coverage and acquisition failures remain separate from missing features.

## Coverage still unqualified

1. Feature-gated tile engine/layers and teletext mode7: not exercised here; this
   is missing coverage, not a declaration of missing implementation.
2. Mode9 Copper replace/reset, mode10 COP4_SETUP and mode11 COP2_SETUP:
   four Copper controls prepared and preserved, not qualified. Plain PAL4/PAL2
   [passed subsequently](low-depth/RESULTS.md), as did mode136
   [PAGE_FRONT/PAGE_SWAP](page-controls/RESULTS.md).
3. PAL16 exercises public bitmap storage formats0/1/2 in its selected cases;
   exhaustive conversions, modes and reserved/internal format combinations remain
   outside this finite corpus.
4. Static software/hardware sprite images passed; three mainboard crashes and two
   P4 setup restarts leave resource lifetime and mode transitions unqualified.
5. Dynamic Copper, coherent animated frames, BSP30 population stress, physical
   scanout timing and browser output timing require separate qualification.
