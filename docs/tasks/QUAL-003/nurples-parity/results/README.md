# Nurples parity measurements

## Executive summary

The first stock-mainboard software-sprite pilot completes all600 boundaries with
no query error. After120 warmup boundaries, all479 measured intervals are two
120Hz ticks: **16.667ms / 60.0 completed frames per second**. This establishes a
scoped pilot baseline, not a parity result. P4 comparisons remain in progress.

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
