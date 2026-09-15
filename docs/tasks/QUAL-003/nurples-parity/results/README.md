# Nurples parity measurements

## Executive summary

Both software- and hardware-sprite pilots record600 successful boundaries on
mainboard and P4. Their gameplay fingerprints match. Fenced software drawing
completes at60FPS even with web output active, but the laptop browser receives
only about7–8FPS. Hardware sprites do not remove that visible-output gap.
This is not a parity success: output diagnosis, heavier loads and controls remain.
Hardware-sprite scanout is not certified by the pixel-query boundary.

## Pilot validation

Probe r01 SW binary hash is pinned in ../fixture-builds.json. Source and repair
assets are pinned in ../reference.json. Results: legacy-pilot.json; raw fixed-size
record retained in ignored bench evidence. All600 records show game_playing and
player_alive, with23 distinct PRNG states; this was not an idle menu. Shields
remain64. These compact records validate coarse state progression, not every
sprite, pixel or collision. More demanding loads may still be required.

The measured interval includes game work, query/return and ordinary vblank wait.
Stock's pixel query drains queued primitives and updates software sprites. It
does not prove hardware-sprite scanout. Tick quantization is8.333ms; no finer
instantaneous timing claim is made.

Initial asset/fixture staging with both staging and final readbacks took
**1636.1 seconds (27.27 minutes)**. This is deployment time, not gameplay time.
All files activated and read back successfully. Subsequent runs reuse the pinned
assets; do not repeat the large upload without a reason.

## First matched P4 control (no web output)

| Same r01 SW workload | Mainboard | P4, no web client | P4 elapsed difference |
|---|---:|---:|---:|
| Mean completed frame (ms) | 16.667 | 16.667 | 0.00% |
| Completed frames/s | 60.0 | 60.0 | 0.00% |
| p95 completed frame (ms) | 16.667 | 16.667 | 0.00% |

Both600-record fingerprints match exactly. Every479 post-warmup interval is two
clock ticks on each route. This does not measure spare CPU budget or establish
parity with web streaming/heavier sprite loads. Evidence: no-output-pair.json
and raw NPL1.BIN/NPE1.BIN.

Collector correction: after reset, use a fresh SD client state. The first host
collector reused its pre-reset state and correctly refused the changed service
identity. A fresh client retrieved the completed result without rerunning or
resetting the game. This was not a gameplay/firmware failure.

## Active web pilot: game work matches, viewing does not

The r01 P4 SW pilot with the production web client connected again records600
successful boundaries, the same state fingerprint, and60.0 completedFPS. The
browser remained connected through reset/loading/gameplay/terminal service,
without page errors or socket closure. Raw NPE2.BIN and web-pair.json retained.

| Output observation | Received FPS | Scope |
|---|---:|---|
| Production client, whole pilot observation | 7.79 | Includes loading and terminal surface |
| Production client, last10seconds | 7.66 | Window near gameplay end; not an exact game-only boundary |
| Static terminal surface, receive-only10s | 8.93 | Bypasses presentation, same512x384 RGB222 payload |

No parity success is claimed. Low visible delivery remains material despite
matched game completion. Output and then heavier/repeated workloads require
further work. Headless production observation and EVF captures remain in ignored
bench evidence, with served web assets and observer hashes. The terminal capture
shows Nurples scenery/HUD plus fixture/MOS completion text.

## Hardware-sprite pilot

Both routes complete600 boundaries without query failures. The479 post-warmup
intervals are all16.667ms, and both state fingerprints equal the SW pilot.
Evidence: hardware-sprite-pair.json and NPHL1.BIN/NPHE1.BIN. P4 production
web capture remains connected throughout both runs; its final10second delivery
is7.12FPS. The terminal output shows the expected same scene, plus test/MOS
text. A single terminal image is not a complete animation/scanout oracle.

These HW timestamps are command/drawing boundaries, not measured physical
hardware-sprite scanout; retain this distinction in summaries and comparisons.

## Wired host control, same static HW surface

| Consumer | Laptop Wi-Fi receivedFPS | Wired Pi receivedFPS |
|---|---:|---:|
| Production presentation | 7.12 (last10s of HW run) | 19.93 (static10s) |
| Immediate credit, no presentation | 8.93 (prior SW static surface) | 28.91 (HW static10s) |

The laptop/Pi comparison changes host and network; the left observations are not
identical static HW windows. It nevertheless rules out treating7–9FPS as an
intrinsic P4 drawing rate. The stronger paired Pi control uses the same static
HW surface and10second windows. Exact records/served assets remain in ignored
bench evidence. Both Pi captures report512x384 RGB222, no sequence gaps, and
no observer errors. This still does not achieve60FPS visible output.

## Drained output timings (r24 diagnostic, wired Pi)

| Client | Snapshot mean(ms) | Socket-send mean(ms) | Complete snapshot/send counts | ReceivedFPS |
|---|---:|---:|---:|---:|
| Production | 11.413 | 15.731 | 201/201 | 20.00 |
| Immediate credit | 11.439 | 15.824 | 297/297 | 29.70 |

All pixel/message unit totals match complete512x384 work; no loss/overlap/errors.
These socket times measure acceptance by complete-send calls, not network ACK
or monitor presentation. Credits were gated and the final granted frame drained
before reading counters and closing. This resolves the prior large-surface
incomplete-send accounting gap. Rates reproduce the uninstrumented wired
controls closely. Snapshot and send currently serialize; bounded lookahead is
the next agent-assigned experiment. No optimization success yet.

## First correction: bounded lookahead (r25 diagnostic)

| Wired client | r24 receivedFPS | r25 receivedFPS | FPS change |
|---|---:|---:|---:|
| Production | 20.00 | 24.64 | +23.22% |
| Immediate credit | 29.70 | 32.67 | +10.01% |

Drained accounting passes. In the receive-only window, snapshot time rises to
14.317ms and socket-send wall time to18.070ms while stages overlap. This suggests
shared-resource/scheduling costs limit the benefit; it does not identify their
individual CPU costs. The no-web Nurples HW pilot still completes600 boundaries
at60FPS with the identical state fingerprint. Active wired gameplay and heavier
loads remain required; this is provisional output progress, not goal completion.

Host orchestration needed two routine corrections: wait for actual keyboard
readiness after reset, and wait for a detached job's initial result file to exist.
Both resumed without rerunning/resetting the in-flight game.
