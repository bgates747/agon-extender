# RESEARCH-006 — Mainboard VDP output through Pico 2 and DVI Cowbell

## Executive summary

Explore replacing mainboard VGA output with a Raspberry Pi Pico 2 and Adafruit
PiCowbell HSTX DVI Output connected to the mainboard ESP32-PICO-D4. Supported
Pico video-output software exists; transporting faithful finished video without
slowing mainboard VDP is unresolved. Header-only serial transport is plausible
for investigation, not a qualified 60 Hz replacement. Tapping digital VGA before
its resistor network is a separate alternative. A third architectural option is
to retain background rendering/storage on mainboard while Raspberry Pi Pico 2
composes sprites and Copper effects during digital scanout.

**State:** Initial assessment recorded; further research open. No implementation
or wiring selected. TRS-80 owns the shared bench. No bench access, reset, flash,
deployment or harness change is authorized by this task. This exploration does
not replace Extender's P4 HDMI/MIPI plan.

## Ownership and scope

Use **mainboard ESP32-PICO-D4** and **Raspberry Pi Pico 2 (RP2350)** explicitly
when ownership might be ambiguous. They are different processors.

Mainboard ESP32 continues to execute VDP and render background graphics.
Raspberry Pi Pico 2 receives video, optionally composes scanout effects under
the proposal below, and generates DVI through the Cowbell's HDMI connector. Mainboard
eZ80/MOS and applications should require no changes. P4 is not an intermediary.

Reuse upstream VDP behavior where possible. Do not substitute another VDU
interpreter on Pico without a separately reviewed scope change, or bypass EMOS
routing ownership. Future custom VDP work
belongs in a project-owned checkout; official references remain read-only.

## Initial assessment

R06-F01 — Adafruit provides RP2350 HSTX output examples, including 320×240 pixels
doubled to 640×480. This establishes an output starting point, not an incoming
video receiver or Agon compatibility. Cowbell is an output board, not a capture
device; DVI through an HDMI connector does not establish HDMI audio support.

R06-F02 — The examined Olimex AgonLight2 Rev B schematic exposes seven ESP32
signals: GPIO26, GPIO27 and GPIO35–39. Only GPIO26 and GPIO27 can transmit;
GPIO35–39 are input-only. The preliminary conversational count of five was
corrected by schematic inspection. Other eZ80 header signals do not provide
additional ESP32 outputs. Actual board revision and existing harness use must
be checked before assigning any pins.

R06-F03 — Header-only candidate: ESP32 supplies serial clock and data on its
two outputs; Pico returns readiness through an ESP32 input. ESP32 SPI/DMA and
Pico PIO/DMA are candidates, not selected implementations. Do not assume an
additional chip-select output: framing, restart and synchronization need an
explicit scheme. Peripheral availability, DMA memory, GPIO timing, wiring and
sustained throughput remain unverified.

R06-F04 — Alternative: capture digital RGB and sync before the VGA resistor
network. This might preserve effects already incorporated into scanout, but
requires connections beyond the expansion header. Accessible points, loading,
sampling phase, pixel-clock availability/reconstruction and mode detection all
need research. This does not mean connecting analog VGA directly to Pico GPIO.

R06-F05 — Identify where stock VDP produces finished pixels including sprites,
palette/Copper effects, cursor and buffer selection. A background framebuffer
copy alone does not demonstrate faithful output. Determine whether obtaining
finished video requires another composition pass, changes effect timing or
disrupts rendering. Do not assume disabling VGA leaves those mechanisms intact.

## Follow-up discussion — architecture alternatives

The Author's motivation is both community interest in this idea and having the
Pico/Cowbell parts already on hand. A useful bounded experiment need not become
a complete replacement VDP. Community discussion is motivation, not evidence of
an existing working implementation: review prior art before inventing a receiver
or renderer.

R06-F06 — Full rendering port remains a larger alternative, not the selected
scope. Either mainboard ESP32 interprets VDU and sends lower-level graphics
operations to RP2350, or RP2350 becomes the VDP interpreter/renderer. The former
needs a new graphics protocol and synchronized queries/readback; the latter
raises keyboard/audio/service ownership as well as the graphics port. Both
require examining ESP32-specific FabGL acceleration and timing assumptions.

R06-F07 — RP2350's 520 KiB SRAM does not rule out every double-buffered mode.
At one byte/pixel, two 320×240 buffers use 150 KiB, two 512×384 buffers use
384 KiB, and two 640×480 buffers use 600 KiB. These are buffer sizes alone,
not free-memory estimates: code/data, stacks, DMA and assets also need room.
Packed formats change the calculation. Asset-heavy VDP compatibility is a
separate concern from whether two small framebuffers fit.

R06-F08 — Scanline-compositor proposal:

**Mainboard background pixels → RP2350 line buffers → sprite/Copper composition
→ HSTX digital output.**

Mainboard ESP32 retains the background framebuffer(s), drawing operations and
buffer selection. RP2350 holds a bounded number of lines, required sprite image
assets/attributes and effect instructions instead of a whole background frame.
Double-buffered backgrounds can remain on mainboard; the source swap must take
effect at an agreed frame boundary. Sprite storage still needs a budget: line
buffers do not make arbitrary sprite populations or assets free.

This split requires intercepting background pixels before mainboard applies the
same effects, or explicitly assigning each effect to one processor. Otherwise
sprites/Copper could be applied twice. Palette effects may require indices and
palette state rather than already-resolved RGB. Address/scroll-changing Copper
operations may require mainboard cooperation. Classify actual upstream effects;
do not assume all Copper behavior is a local pixel transformation.

RP2350 must finish each output line before its display deadline. Several queued
lines absorb short stalls, not indefinite source delays. Specify underflow,
frame/line synchronization, sprite-state latching and source/output clock drift.
The proposal reduces RP2350 framebuffer storage, not the background pixel traffic.
No full-frame-free implementation or timing fidelity is established yet.

R06-F09 — Two outputs permit serial communication. Illustrative, unapproved
assignment: mainboard GPIO26 supplies SPI clock, GPIO27 supplies data, and an
input-only mainboard GPIO receives RP2350 readiness. No final pin assignment is
made. A continuously selected PIO receiver with explicit stream framing is one
option when no third output is available for chip-select. Investigate SPI/DMA
and receiver timing rather than assuming a particular clock rate is sustainable.

I²C also uses two suitable bidirectional pins, but the documented ESP32 limit of
400 kHz is far below the pixel payload rates below. It is not a suitable primary
pixel transport here. Any control-only use would need its own pin/resource plan;
it cannot be assumed to operate independently on pins already carrying SPI.

## Traffic lower bounds

Calculated active-image payload at 60 new frames/s, decimal Mbit/s. Excludes
framing, blanking, processing, transfer gaps and return traffic. These are
requirements, not measured link rates.

| Logical image | One byte/pixel | Packed six bits/pixel |
|---|---:|---:|
| 320×240 | 36.864 Mbit/s | 27.648 Mbit/s |
| 640×480 | 147.456 Mbit/s | 110.592 Mbit/s |

Packing adds processing and is not assumed supported by the selected library.
Scaling on Pico avoids sending duplicated pixels. A steady 60 Hz output does
not establish reception of 60 distinct frames/s. Budget RAM, buffering, tearing
and source/output clock mismatch separately. Compression is not a guaranteed
solution for worst-case traffic. Start the assessment with 320×240.

## Bounded follow-up

R06-01 [x] Record initial assessment, corrected GPIO count, sources and scope.

R06-02 [ ] Audit exact mainboard revision, exposed signals and existing pin use.
Produce a proposed electrical/pin budget, distinguishing header-only wiring
from soldered video taps. No wiring yet.

R06-03 [ ] Trace stock VDP/FabGL through finished scanlines. Record source
revisions and ownership of sprites, Copper, cursor, buffer swaps and timing.
Identify the minimum reusable output boundary and a possible pre-composition
boundary for the RP2350 scanline proposal. Classify which Copper operations
can move and which require mainboard cooperation.

R06-04 [ ] Review maintained Pico HSTX output and PIO/DMA receiver examples.
Budget RAM, capture/output clocks, conversion, scaling and storage. Check
licenses and exact Cowbell pin use. Search community prior art; distinguish
working code from proposals and output-only demos.

R06-05 [ ] Compare both transports for sustained/worst-case bandwidth, CPU/DMA
cost, synchronization and recovery. Compare finished-pixel forwarding with
split scanline composition, including sprite storage and underflow behavior.
Do not extrapolate one mode to all modes.

R06-06 [ ] Present a go/no-go recommendation and one small experiment for Author
review. Define fidelity and mainboard-performance pass criteria before coding
or separately authorized bench work.

## Sources

1. [Olimex Rev B schematic](https://github.com/OLIMEX/AgonLight2/blob/main/HARDWARE/AgonLight2_Rev_B/AgonLight2_Rev_B.pdf).
   Local checkout inspected at b7f2a21c282813efd8cdf26573eb5126876432a8;
   relevant sheets: Extension.sch and ESP32-PICO-D4.sch.
2. [Agon GPIO documentation](https://agonplatform.github.io/agon-docs/GPIO/).
   Do not substitute Console 8's header layout.
3. [Espressif GPIO documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gpio.html).
   GPIO34–39 are input-only.
4. [ESP32 SPI master driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/spi_master.html).
   Review the actual VDP toolchain's driver version and resource use before
   implementation; current documentation is not a measured transport result.
5. [Cowbell 6363](https://www.adafruit.com/product/6363) and
   [pinouts](https://learn.adafruit.com/adafruit-picowbell-hstx-dvi-output/pinouts).
   HSTX uses Pico GPIO12–19; review additional Cowbell connections too.
6. [Raspberry Pi HSTX example](https://github.com/raspberrypi/pico-examples/tree/master/hstx/dvi_out_hstx_encoder).
   Output example, not an Agon receiver.
7. [Earlier purchasing notes](P4PC-001/PURCHASING.md) and
   [HDMI research](RESEARCH-004/RESULTS.md) provide context, not qualification
   of this mainboard-source proposal.

8. [ESP32 I²C driver](https://docs.espressif.com/projects/esp-idf/en/v5.2.8/esp32/api-reference/peripherals/i2c.html).
   Documented standard/fast modes up to 400 kHz.

Recorded September 28 UTC, 2026, from the preceding read-only exploration.
No builds, benchmarks, board connections or hardware tests were performed.
