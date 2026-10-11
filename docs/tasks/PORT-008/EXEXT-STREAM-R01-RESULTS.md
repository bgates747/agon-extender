# Ordinary ExExt — bounded results

Ordinary parallel VDU/reply routing now passes two focused physical fixtures.
Three warm resets pass on the earlier held-prefix pair, but later resets into
ExExt fail admission and require paired recovery. Cached keyboard input now
passes physically; larger sprite-stream traffic faults before completion. Full
transition/gameplay qualification remains incomplete. Production remains unchanged.
[Work contract](EXEXT-STREAM-R01.md) owns the remaining implementation/tests.

## Firmware and physical scope

| Pair | P4 build | EMOS build | Installed verification |
|---|---|---|---|
| Earlier held-prefix comparison | `port-008-stream-r04-b2026-10-11-12-24-35Z` | `agon-emos-v0.1.24-b2026-10-11-12-31-04Z` | All four P4 segments; complete128KiB EMOS ROM |
| IRQ teardown/cached-input comparison | `port-008-stream-r06-b2026-10-11-13-07-17Z` | `agon-emos-v0.1.24-b2026-10-11-12-47-24Z` | All four P4 segments; same verified EMOS image |
| Latency/partial-return comparison | `port-008-stream-r05-b2026-10-11-12-47-10Z` | `agon-emos-v0.1.24-b2026-10-11-12-47-24Z` | All four P4 segments; complete128KiB EMOS ROM |

All use P4-PC, normal full HDMI, existing renderer, no private payload probe,
and the unchanged eleven-signal resistor harness. Mainboard VDP is the preceding
consumer's custom build, **not official stock**. Browser video is disconnected.
Exact private receipts/raw results are retained in the ignored run silo.

## Focused physical results

Worst completion latency first; ranking is the newer pair's median whole-update
pixel-query completion. Each accepted run has120ordered rows, no fault/abort.
PRT nominal18.432MHz/256 gives72,000counts/s; one60Hz budget is1,200counts.
MOS nominal120clock units/s advances in steps of2. These calibrated assumptions
are not a precision wall-clock or HDMI-FPS measurement.

| Fixture | Earlier pair median completion (ms) | Newer pair median completion (ms) | Newer / earlier change | Newer application updates/s | Newer median active submission (ms) |
|---|---:|---:|---:|---:|---:|
| T03 single-scanline clipped tile upload | Not run: CLI invocation failed | 50.056 | Not comparable | 16.438 | 0.069 |
| T01 static tiny pixel query | 67.000 | 50.042 | −25.31% latency | 16.628 | 0.000 |

T01's newer median completion is300.25% of one60Hz budget. This includes
batching, handover, parser/query and reverse-reply scheduling; it is not raw
parallel bandwidth or a renderer-only duration. HDMI scanout remains about
60.07Hz. Application cycle rate, framebuffer submission and scanout are separate.

## Correctness/recovery boundaries

| Check | Evidence/result | Limit |
|---|---|---|
| Agon-only warm reset | Three consecutive stable ready/neutral admissions on stream-r04/EMOS-r06; first automatic post-FLASH startup also succeeds | Reset during payload/power loss not established |
| Partial returned VDP packet |4,096 actual EMOS-owner boundary/body/STOP cases pass, including257-byte packets | Host transport leaves are modeled |
| Keyboard ISR/callback ABI | Actual linked eZ80 VBlank, nested/non-nested delivery, primary/alternate/IX/IY/SP/IFF pass | Does not alone prove physical idle/game input |
| P4 native coordinator |319 ordinary/diagnostic paired cases pass;754 actual boot-pad cases separate | Not an electrical performance measurement |
| Cached-map physical input | Five seconds with no hot-loop MOS/VDU calls: six exact a/Shift/B down/up callbacks and six matching cached-map changes on stream-r06/EMOS-r07 | Bounded idle-input proof, not gameplay responsiveness |
| HDMI mode transition | Captured shared-IRQ load fault at DW-GDMA status0x50081030; original startup restored after recovery | [FWBUG-015](../../firmware-bugs.md) source-derived teardown remedy passes host negative/positive controls; first previously crashing transition and input run pass; broader repeat pending |

The earlier T03 invocation lost its leading RUN character. A stale completion
message was rejected by missing durable evidence. The revised runner clears
prior completion and verifies preparation/errors/result identity; the newer
T03 pass has its own complete saved record.

## Larger-stream and reset failures — subsequent control

1. Stream-r06/EMOS-r07 passes the five-second cached-input fixture. MOS cached
   key-map bit positions are stock BBC physical-key mappings (a65, b100,
   Shift3), not FabGL virtual-key indices. Exact packets and map sequence match.
2. Preparing T07/T08/T09 succeeds, but the following Agon-only reset does not
   restore readiness. A second Agon-only reset also fails. P4 stays running
   with clean60Hz HDMI counters; paired P4/Agon reset recovers without reflashing.
   Earlier original-startup warm-reset passes do not establish this case.
3. T07 then starts once and faults before a result: normal USB log reports
   native completion failure, native result5. T08/T09 are not invoked. No saved
   rows or sprite/gameplay pass claimed. A fresh paired reset recovers. Original
   startup and all three configs are restored and verified; bench released.
4. Extend only the existing failed-leaf USB message with direction, admitted
   length, completed bytes/callback flags and current control levels. No private
   probe, successful per-byte instrumentation or EMOS diagnostic ROM growth.
   These facts distinguish callback rejection, TX backend failure and timeout
   before choosing a remedy; do not infer new electrical corruption.
