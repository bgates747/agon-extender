# Plain low-depth graphics results — 2026-09-20

## Executive summary

Both plain low-depth fixtures passed on physical mainboard VDP and P4 EDP.
**153,600 complete-image pixels matched with zero differences.** All nine
independent literal tiles and their untouched borders passed on each device in
each mode. No unexpected reset or incomplete capture occurred. Copper was not
executed and no product firmware correction was made.

| Fixture | Mode / geometry / colours | Mainboard repeat | P4 fresh generations | Pixel differences |
|---|---|---|---|---:|
| PAL4 | 10 / 320×240 / 4 | Identical | 15 and 16, identical | 0 / 76,800 |
| PAL2 | 11 / 320×240 / 2 | Identical | 19 and 20, identical | 0 / 76,800 |

The additional independent checks cover 539 pixels per device per mode (2,156
checks total), including palette remapping, RGBA8888/RGBA2222/monochrome bitmaps,
transparent pixels, screen capture, bitmap aliases, XOR drawing and an ignored
invalid physical-colour value. This is scoped static correctness, not exhaustive
API coverage, animation or performance qualification.

## Method and provenance

Executed [contract](CONTRACT.md), frozen in `161cfd7a`, with unchanged PAL4/PAL2
bytes and barrier sidecars from [the frozen input manifest](../fixtures/SCENES.json).
The deployed player and both scenes were read back and hash-verified. Video
modes were selected only by temporary startup, for both mainboard and Extender.
Each of the two mainboard captures per scene followed an ordinary fresh reset.
The last two of four P4 snapshots had distinct generations and matching pixels.
All 76,800 pixels per image were compared without masks, resizing or tolerance.

Mainboard diagnostic `mainboard-image-capture-r02-b2026-09-16-12-41-20Z` captures
visible scanout pixels after palette expansion and composition. P4 retained
`key-query-probe-r01-b2026-09-20-02-08-44Z`, identified by the preceding verified
deployment; no new P4 flash/readback was performed. EMOS remained unchanged.
Exact artifact hashes and that provenance limitation are in the receipt.

The retained literal oracles were created independently of captured images.
The two-colour oracle already accounts for stock HSV colour matching: saturated
blue selects the light palette entry in the original black/white mapping.
That established expectation was not changed to fit this run. Both image
checks used scale1. The five capture-decoder and four comparator tests passed.

1. [Full comparisons and independent checks](evidence/results.json).
2. [Firmware, fixture and restoration receipt](evidence/receipt.json).
3. [PAL4 images and captures](evidence/PAL4/).
4. [PAL2 images and captures](evidence/PAL2/).
5. [Mode10 oracle](evidence/mode10-oracle.json) and
   [mode11 oracle](evidence/mode11-oracle.json).
6. [Evidence hashes](evidence/SHA256.json).

Run `QUAL-004-2026-09-20-23-32-47Z` took **151.764 host wall-clock seconds** for
startup/reset, command entry, acquisition, comparison, mode-startup replacement
and returning to SD service. Backup, diagnostic installation and final
restoration are outside that interval. It is not isolated rendering time.

## Closeout and remaining scope

Cumulative retained coverage is now **70 distinct static scene pairs /
12,923,904 compared pixels** across the separately identified campaigns. Four
prepared Copper controls remain unqualified: COP16_REPLACE, COP16_RESET,
COP4_SETUP and COP2_SETUP. Existing crash findings remain open.

Original startup and overwritten mainboard application sectors were restored
and independently verified. Final keyboard/SD/serial/video state and MOS prompt
verification are retained in the receipt and final image. No P4/EMOS code or
production application changed; no notification was requested.
