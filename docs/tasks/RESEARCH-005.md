# RESEARCH-005 — Aspect-preserving video output and VGA pillarboxing

## State and authorization

Deferred future research, recorded at the Author’s request on 2026-09-20.
Covers possible mainboard VDP implementation and/or Extender output behavior.
No implementation, timing selection, firmware deployment or bench test is
approved by this record. This is not a prerequisite for current qualification.

## Supplied research and provenance

The Author supplied a web-agent investigation, preserved verbatim in
[SUPPLIED-RESEARCH.md](RESEARCH-005/SUPPLIED-RESEARCH.md), including its original
source links. It is a research lead, not independently verified source analysis
or hardware evidence. Its GitHub links are not commit-pinned and mix Agon VDP
with generic upstream FabGL; establish the actual Agon dependency before relying
on any claim. No source claims were independently revalidated in this filing.

Original attachment SHA-256: `d6f019aa4a6419aef8fb62fce65a2ab1189ce6eb1726ac4afd58d4cfec96077b`.

## Question and proposed direction

Can mainboard VDP emit a monitor-compatible wide VGA raster with black side
borders while preserving the game’s logical 4:3 image, framebuffer dimensions,
coordinates and rendering behavior? Separately, can the P4 output adapter retain
the same aspect ratio through HDMI/DSI without changing EDP rendering semantics?
Monitor scaling behavior must be measured rather than assumed.

The supplied investigation identifies these possible reuse points:

- FabGL viewport placement and DMA scanline descriptors may already supply
  side padding and repeated source rows.
- Paletted VGA controllers expand logical pixels into output scanline buffers;
  horizontal replication might belong there, leaving drawing code untouched.
- Logical framebuffer width and physical scanline width would need separating.
- Direct RGB222/64-color scanout follows a different path and cannot be assumed
  to inherit a paletted-controller solution.
- Its suggested experiment is 320×240 content enlarged 3× to 960×720, centered
  in a 1280×720 raster with 160-pixel side borders. This is a proposal, not a
  selected mode or demonstrated capability. A modeline’s presence does not
  establish achievable scanout, ISR budget or monitor compatibility.

For Extender, consult the [existing HDMI driver research](../hardware/esp32-p4-pc/HDMI-DRIVERS.md)
and [P4-PC task](P4PC-001.md). Mainboard VGA DMA techniques are not automatically
portable to P4 DSI/HDMI. Also retain the Author’s earlier preference to investigate
320×240 → 640×480 integer doubling at output time; do not silently select 720p.

## Future work

RESEARCH-005-R01 [ ] Verify the supplied claims against pinned official Agon VDP
and its actual FabGL fork, including supported color depths, viewport units,
multiscan interpretation, descriptor layout and sprite/Copper behavior.

RESEARCH-005-R02 [ ] Determine mainboard ESP32 scanout limits: pixel-clock
accuracy, temporary buffer requirements, ISR deadlines and impact on drawing,
sprites, Copper and sustained refresh. Prefer existing upstream mechanisms.

RESEARCH-005-R03 [ ] Independently assess P4 driver/hardware scaling and border
support, preserving logical framebuffer and rendering semantics; identify any
necessary output-adapter code and its cost.

RESEARCH-005-R04 [ ] Present a bounded proposal before implementation, including
monitor controls/EDID where relevant, integer scaling and pixel-aspect policy,
mode compatibility, rollback, and tests for geometry and sustained refresh.
Use a project-owned experimental checkout; official reference trees stay clean.

## Acceptance of future research

Report mainboard and Extender feasibility separately, with exact source revisions,
measured versus inferred limits and unresolved questions. Future physical tests
must demonstrate correct aspect ratio on actual displays and characterize
rendering/scanout performance separately. Filing this note makes no such claim.


## Deferred P4 VGA output lead — 2026-09-21

Author also proposes physical VGA from the current P4 as a possible interim
output while awaiting P4-PC HDMI hardware. This remains **deferred**, with no
wiring, implementation, build or bench authorization. It extends this research
bucket; it does not supersede HDMI as the intended primary output.

An existing implementation was located: [OulanB/P4VGA565](https://github.com/OulanB/P4VGA565),
source revision `6dfd8633e9df3d8e95a0e5b454c25694cf8d8ed3` inspected on 2026-09-21.
Its [example](https://github.com/OulanB/P4VGA565/blob/6dfd8633e9df3d8e95a0e5b454c25694cf8d8ed3/rgb_test/rgb_test.ino)
uses Espressif `esp_lcd_panel_rgb` for VGA, with RGB565 output and a Waveshare-specific
pin map; the repository also supplies hardware design files. The
[README](https://github.com/OulanB/P4VGA565/blob/6dfd8633e9df3d8e95a0e5b454c25694cf8d8ed3/README.md)
reports 640×480/60 Hz and 800×600/56 Hz. These are author-reported capabilities,
not independently measured timings or qualification on our Olimex board.
The README records USB-port interaction, GPIO supply/SDMMC voltage concerns,
and an eight-pixel scanline offset (reported corrected in newer IDF versions).
Do not copy its pin map or assume its timing labels and our toolchain are compatible.
License/reuse permission must also be established before vendoring implementation.

Preferred avenue to investigate: reuse P4-native LCD/DMA scanout machinery while
retaining the actual Agon VDP FabGL fork's image-generation algorithms. The
[existing composition/output audit](AUDIT-006/composition-output-review.md#real-seams-and-remaining-evidence)
distinguishes classic ESP32 I2S1 registers, DMA descriptors, clocks and interrupts
from portable row selection, palettes, sprite/Copper and cursor behavior.
Porting those physical bindings is required; replacing upstream graphics behavior
is not the objective. Existing P4 VGA software and reuse of VDP scanline code are
complementary possibilities, not mutually exclusive alternatives.

RESEARCH-005-R05 [ ] Deferred: establish available Olimex GPIOs without disturbing
UART/USB/Ethernet/storage, resistor-DAC electrical requirements, supported pixel
layout and driver/version licensing. Then assess rolling scanline buffers versus
full output buffers, DMA/cache ownership, sprite/Copper fidelity and sustained
refresh without blocking drawing or UART. Propose a bounded test only after
Author resumes this work; no 60 Hz gameplay guarantee follows from finding a demo.
