# QUAL-004 coverage ledger

## Executive summary

Acquisition and deployment are in progress. No whole-image pass is claimed yet.
The first tranche is62 static scenes at512×384×64 colours: calibration,39 retained
finite cases, and22 additional existing shape pages. Each needs paired physical
captures; preparing a command file does not constitute testing it.

| Family | Planned source scenes | Current classification |
|---|---|---|
| Primitive line endpoints, patterns, thickness | SHP01–05 | Awaiting hardware run |
| Triangles, rectangles, parallelograms | SHP06–08 | Awaiting hardware run |
| Circles, ellipses, arcs, segments/sectors | SHP09–12 | Awaiting hardware run |
| Line/flood/path fills | SHP13–15 | Awaiting hardware run; path semantics experimental upstream |
| Paint variants and eight GCOL operations | SHP16–17 | Awaiting hardware run |
| Colour mapping and palette reset | SHP18 | Awaiting hardware run in64-colour mode |
| Origins, logical/physical coordinates | SHP19, BSP07/21 | Awaiting hardware run |
| Viewports, clears, clipped bitmap plotting | SHP20–23, BSP07 | Awaiting hardware run |
| Copy/move/scroll and single-row viewport | SHP22, SCROLL/CLIPROW/COMBINED | Awaiting hardware run |
| Default text and graphics text | SHP headings, SHP23 | Awaiting hardware run |
| Buffered calls, saved contexts, transforms | SHP24, BSP29 | Awaiting hardware run |
| Alpha and bitmap cutouts | BSP03 | Awaiting hardware run |
| Software sprite movement/update/layers | BSP21/22/25 | Awaiting hardware run |
| Hardware and mixed sprites | BSP26/27 | Awaiting composed scanout comparison |
| Custom font creation/selection variants | No additional scene selected yet | Not covered yet; not labelled unimplemented |
| All bitmap storage formats and conversions | Partial existing scenes | Coverage gaps to enumerate after first tranche |
| Lower-depth palette modes, static Copper | Capture tap extension needed | Not covered yet; not labelled unimplemented |
| Double buffering/displayed versus drawing page | Additional mode136 scene needed | Not covered yet; not labelled unimplemented |
| Time-varying Copper/animated scenes | Coherent full-frame acquisition needed | Deferred; stitched static rows cannot qualify |
| Sprite population stress page BSP30 | Prior mainboard timeout evidence | Deferred from first tranche; no implied pass |
| Audio synthesis, physical LCD/MIPI output | Outside graphics-image scope | Not implemented/output roadmap as previously recorded; no work here |

Missing API functionality discovered during source review or execution must be
marked **not implemented**, with its command and evidence. Do not equate a
missing test or unsupported capture mode with a missing API implementation.
Existing hardware-overlay format restrictions require comparison to stock;
a format unsupported by both devices is not automatically a port defect.
