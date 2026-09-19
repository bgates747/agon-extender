# Pair-RLE — Nurples results

## Executive summary

The codec works, but **do not enable it by default for Nurples**. Pair-RLE produced about52KB/frame versus39KB for RLE2 and did not improve measured output. Automatic selection chose RLE2 throughout. Keep the implementation and experiment; the final browser default retains the previous RLE2/packed selection without the extra pair-RLE pass.

| Path | Browser submissions fps | Change vs prior | Mean packet bytes | Format | Application cycles fps |
|---|---:|---:|---:|---|---:|
| prior | 21.07 | +0.0% | 38956 | EVR1 | 60.00 |
| pair | 20.03 | -4.9% | 52357 | EVQ1 | 60.00 |
| auto | 20.15 | -4.4% | 39093 | EVR1 | 60.00 |

## Findings and limits

1. Four-bit count version, explicitly confirmed by the Author: each little-endian token repeats its two RGB222 pixels1–16 times. The literal-flag variant was never flashed. The payload never expands beyond one byte per original pixel, including an odd tail. Header size is unchanged.
2.64 host round trips cover random pixels, flat fields, alternating pairs, odd runs, odd tails, run limits and large raster sizes. Eight malformed inputs rejected; exact worst-case size and invalid input checks passed. Every measured pair-only Nurples frame used EVQ1. No browser errors or fixture vblank timeout occurred.
3. All three trials used the unchanged1800-cycle single-vblank Nurples fixture and fresh starts. Browser reporting uses a20-second interior window ending five seconds before the last capture, excluding asset loading and termination. These are headless Chromium submissions, not physical monitor scanout. Approximately45seconds per fixture invocation including launch/collection.
4. Prior is the previous selection policy on the same experimental firmware; automatic adds pair-RLE eligibility. Small fps differences from single sequential trials do not prove a regression. Absolute fps differ from the previous six-bit experiment, so do not compare those runs as a controlled firmware benchmark. The larger pair-RLE payload and lack of selection are decisive here.
5. A pair may span rows. Pair alignment and maximum32-pixel repeated spans limit compression of long same-colour regions compared with RLE2. Alternating AB patterns can favour this codec, but Nurples as tested does not. No claim is made for other games.
6. Original firmware artifacts, source overlays and evidence remain intact. The experimental default-pair image is preserved separately from the final default-restored build. Mainboard firmware and production games are unchanged.
7. The final interactive review uses existing /test/nurples/nurples.bin (two-vblank pacing), unchanged. Pair-only remains available through explicit pair=1 protocol negotiation; ordinary browser startup retains rle2=1&packed=2. Refresh the web client after flashing.

## Final installed-image check

The default-restored build served exact expected assets and completed a fresh
Nurples run:1,279 observed EVR1 frames, no browser errors, no vblank timeout.
The first smoke reached MOS but its SAVE command refused to overwrite the
previous trace; rerun with unique output filenames passed. A stale host SD
session was rejected before execution and replaced with a fresh session. These
were fixture bookkeeping errors, not codec failures. SMOKE.json records success.
