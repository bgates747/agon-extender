# RESEARCH-008 — P4 output through Raspberry Pi Pico 2 and Cowbell

## Executive summary

Investigate Raspberry Pi Pico 2/RP2350 plus Adafruit PiCowbell HSTX DVI Output
as an independent external video-output option, primarily for P4-DevKit. It is
not part of the P4-PC indexed-framebuffer investigation: faster output through
P4-PC’s existing HDMI path may remove any reason to add this hardware there.

**State: recorded, not started.** Author clarified the separate scope on
2026-10-09. No implementation, wiring, transport selection or bench work is
authorized. “HDMI” here names the Cowbell connector; establish actual DVI/HDMI
signal and audio capabilities during research rather than assuming them.

## Scope and dependencies

1. P4 executes Extender VDP rendering; RP2350 receives an explicitly defined
   pixel/scanline stream and produces digital output through Cowbell. Assess
   indexed delivery and palette expansion as possibilities, not settled design.
2. [RESEARCH-007](RESEARCH-007.md) owns indexed storage and expansion for
   P4-PC’s existing HDMI path. Reuse findings without making this external
   output a prerequisite or expanding that task's implementation scope.
3. [RESEARCH-005](RESEARCH-005.md) owns the separate P4-DevKit RGB565
   resistor-ladder VGA lead. Neither proposal establishes a shared wiring plan.
4. [RESEARCH-006](RESEARCH-006.md) owns the distinct mainboard ESP32-PICO-D4
   source proposal. Reuse RP2350/HSTX/Cowbell research, but maintain separate
   source-processor pin, peripheral, performance and transport budgets.
5. Preserve EMOS mode/routing ownership and existing Agon behaviour. All
   reference checkouts remain read-only. No complete VDP port to RP2350 is
   selected; the candidate role is output and possibly scanline composition.

## Investigation subtasks

### R08-01 [ ] Establish need, baseline and reusable software

After authorization, pin current P4-DevKit/P4-PC capabilities and relevant
HSTX/Cowbell examples, drivers and licenses. Establish the benefit sought
relative to P4-PC HDMI and the independent VGA option. Refresh local hardware
records; do not assume parts on hand establish connectivity or available GPIOs.

### R08-02 [ ] Evaluate stream and palette formats

Compare indexed bytes plus synchronized palette records with RGB565 and RGB888.
Determine whether RP2350 HSTX/DMA can expand indices directly or needs CPU/PIO
work and intermediate encoded lines. Include palette-change timing, sprites,
Copper, cursor, logical geometry, scaling and double-buffer swaps. A small
lookup table does not establish sufficient conversion or scanout performance.

### R08-03 [ ] Budget transport, output and memory

Name the P4 transmitter, physical link, RP2350 receiver and output owners.
Evaluate existing drivers and available pins before inventing a protocol.
Calculate sustained/worst-case bandwidth, buffering, clock differences,
flow control, restart/full refresh and underflow recovery. Keep render,
transport, expansion and scanout costs separate. No wiring or transport choice
is made by the calculations alone.

### R08-04 [ ] Recommend and pause

Present retain-P4-PC-HDMI, external-Pico experiment or defer, with source-linked
feasibility and uncertainties. If worthwhile, propose a small existing-fixture
comparison and exact fidelity/performance criteria. Pause for approval before
building, connecting hardware or flashing either processor.
