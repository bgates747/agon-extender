# Approved numeric guard validation

## Executive summary

N02–N06 are implemented and pass focused host checks and a full P4 build.
Hardware r22 matches stock on342/342 valid samples and passes570/570 rejection
checks. Startup restoration and the final unmuted Rally smoke are pending.
The initial stock run exposed a fixture palette mistake, corrected in r02.
No game benchmark, mainboard firmware change or experimental push is included.

## Implementation and host evidence

| Check | Result | Scope |
|---|---:|---|
| Actual parser bodies, N02/N03/N06 | 65,931 passing cases | Undefined/float-cast-overflow sanitizers |
| Actual guarded renderer bodies, N04/N05 | 146 passing cases | Address/undefined/float-cast-overflow sanitizers |
| Defined stock-branch renderer controls | 36 passing cases | Same valid sampling hash12193972632595109770 |
| Existing fixed conversion regression | 65,764 passing cases | Sanitized |
| Existing audio framing regression | 15,120 passing cases | Stock dispatcher/source guard also passes |
| P4 target build | Pass | 123.00seconds including preparation |

Tests extract retained source bodies rather than duplicating helper logic.
Checks preserve stock valid-input truncation/order and are P4-only. Invalid
corners skip publication/drawing; dynamically owned matrices are released once.
N06 retains the existing clear-old-bitmap-at-entry behavior, so rejection does
not promise preservation of the old bitmap. NaN fails positive source-coordinate
bounds before source pointer calculation in all three bitmap formats.

## Hardware identity and evidence limits

See [build.json](build.json) for r22 hashes and source selection. The candidate
retains the archived installed-source parent and its UART/output configuration,
plus the accepted earlier fixes; this is a controlled exploratory derivative,
not a clean-parent release qualification. Mainboard VDP remains official2.16.0
and EMOS remains v0.1.16-b2026-09-13-07-31-36Z. P4 flashing independently verified
in47.83seconds. Fixture r02 source checkpoint is5f53bd8.

Stock receives defined valid inputs only. P4 receives separate rejection cases;
undefined stock conversions have no portable reference result. Host checks
cover infinities, boundaries and ownership beyond the physical fixture. The
existing readFloatArguments positive-infinity timeout sentinel is unchanged;
this work does not claim general malformed-stream resynchronization. Existing
integer geometry overflow and N07/N08/dormant findings remain outside scope.

## Fixture correction and timing

The first stock run finished342 queries in10,772 raw120Hz ticks (89.77seconds).
Its six failures were mask foreground expectations: default logical palette63
is RGB255,255,170, while15 is white, as official v2.16.0 agon_palette.h specifies.
r02 selects15. MOS EXEC stops on nonzero program return, so that run never
reached ExCom or its terminal SD service. Direct CLI service launch retrieved
the completed CSV without reset. This was a fixture correction, not a firmware
repair. The first-run wait is not fixture runtime.

Elapsed fixture ticks include SD writes, queries and command transport. They
are correctness-suite durations, not renderer throughput or application FPS.

## Completed paired hardware run

| Correctness section | Stock mainboard VDP | P4 r22 |
|---|---:|---:|
| Valid samples |342/342 pass |342/342 pass |
| Differences from stock | Baseline |0 |
| Rejection samples | Intentionally not run |570/570 pass |
| Valid-section elapsed (120Hz raw ticks) |10,802 |10,902 |
| Valid-section elapsed (seconds) |90.02 |90.85 |
| Rejection-section elapsed (seconds) | — |152.60 |

These durations include command/query transport and SD writes; the0.93% valid
section duration difference is not rendering performance. The three fixture
sections total333.47seconds. Boot through completed retrieval took386.30seconds.
Allow roughly7minutes for this correctness run including retrieval; setup and
voice are additional. Two bounded browser observations were made during the
P4 sections, so these are not output-free performance measurements.

Fixture r02:13,054bytes, SHA256
`d5d02f864d495830e312136d1538d2f2b11b14acd7744ce3aeee4661ad56f3e4`.
Corrected fixture/startup staging and verification took36.90seconds. Exact
pixel rows and terminal records are retained here with hardware.json. Run
started2026-09-15T07:16:54Z and collection ended07:23:20Z.
