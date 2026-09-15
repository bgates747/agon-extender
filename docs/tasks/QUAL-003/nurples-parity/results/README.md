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
