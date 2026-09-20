# Displayed/drawing-page controls — 2026-09-20

## Executive summary

Both physical controls passed: mainboard VDP and P4 EDP matched all **153,600
pixels**, with zero differences. Both devices also matched the independent literal
image oracle. Hidden-page drawing leaves the red front page intact; swapping
exposes the completed green page. These are static correctness results, not
animation, frame-rate or swap-latency measurements.

| Control | Mainboard VDP | P4 EDP | Pixel differences |
|---|---|---|---:|
| PAGE_FRONT | Red background; white rectangle x40–79/y40–79 | Identical | 0 / 76,800 |
| PAGE_SWAP | Green background; white rectangle x120–159/y100–139 | Identical | 0 / 76,800 |

Actual geometry on both endpoints was **320×240, 64 colours, double buffered
(mode136)**. Each rectangle contains 1,600 white pixels; its remaining 75,200
background pixels are RGB(170,0,0) or RGB(0,170,0), respectively.

## Procedure and evidence

Executed the [frozen contract](CONTRACT.md), commit `269ebedf`, with immutable
existing scenes and player. Each mainboard capture followed a fresh ordinary
mainboard reset; each scene has two identical complete mainboard captures.
P4 snapshots came from separate generations (3/4 and 7/8), with identical pixels
within each pair. No Copper scenes or custom palettes were introduced.

Mainboard diagnostic `mainboard-image-capture-r02-b2026-09-16-12-41-20Z` taps the
visible scanout page, after composition. P4 retained its previously verified
`key-query-probe-r01-b2026-09-20-02-08-44Z` deployment; it was neither flashed nor
opened over serial solely to repeat identity checks. EMOS was unchanged. This
P4 candidate differs from the original first-pass campaign; do not imply that
all historical scenes were rerun on this candidate.

The official VDU system-command contract defines physical coordinates as
origin-at-top-left when logical scaling is disabled, and `VDU 23,0,&C3` as a
VSYNC page swap in double-buffered modes. Those contracts and the literal
fixture bytes define the independent oracle, rather than deriving expectations
from either captured image. The capture decoder's five tests and comparison
code's four tests also passed.

1. [Full-pixel results](evidence/results.json), including independent-oracle
   mismatch counts and distinct P4 generations.
2. [Artifact/restoration receipt](evidence/receipt.json), fixture hashes and
   firmware provenance.
3. [PAGE_FRONT images and captures](evidence/PAGE_FRONT/).
4. [PAGE_SWAP images and captures](evidence/PAGE_SWAP/).
5. [Evidence hashes](evidence/SHA256.json).

Run `QUAL-004-2026-09-20-23-20-57Z` took **145.514 host wall-clock seconds** for
reset, command entry, capture, comparison and returning to SD service. Backup,
diagnostic installation and final restoration are outside that interval. It is
an acquisition-duration observation, not isolated rendering time. No voice cue
was requested or sent.

The keyboard endpoint's `boot` field is an admission epoch: an ordinary Agon
reset deliberately increments it. The local adapter initially treated that
increment as a P4 restart and stopped before any scene; correcting that host
check required no firmware or fixture changes. Final prompt verification also
waited for settled readmission after the requested restoration reset; a stale
pre-reset admission was discarded without replaying pending keystrokes. No unexpected runtime resets
occurred in the completed run.

## Scope and closeout

These two controls raise cumulative retained coverage to **68 distinct static
scene pairs / 12,770,304 compared pixels**. Six other prepared low-depth/Copper
controls remain unqualified. Earlier sprite-scanout failures and the inherited
palette-deletion defect remain open; these passes do not resolve them.

The exact incoming startup and overwritten mainboard application sectors were
restored and independently verified. Serial acquisition, SD service and the
agent's video observer were closed; keyboard capture was released. Final MOS
prompt verification is recorded in the receipt. No P4/EMOS product code changed.
