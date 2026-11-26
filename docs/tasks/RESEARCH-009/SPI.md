# RESEARCH-009 — Hardware SPI feasibility

Hardware SPI is a credible reliability candidate for the Olimex eZ80–P4
payload path. Its measured file throughput on the P4 remains open. An
earlier AgonLight2/WROOM campaign already reproduced and corrected both
shared-SD interference and a receiver arming race. Apply those lessons to a
bounded eZ80-controller/P4-peripheral prototype, with hardware isolation of
the P4 branch and UART left available. The earlier campaign does not qualify
this P4-PC wiring, the reverse direction, or the current EMOS firmware fit.

## Silicon and current ownership

| Component | Source finding | Implication |
| --- | --- | --- |
| eZ80F92, Rev B AgonLight2 | One hardware SPI block. PB3 is SCK, PB7 MOSI, PB6 MISO and PB2 the hardware slave-select input. The board connects PB3/PB7/PB6 to the microSD and UEXT. PB4 is the microSD's software select. PB5 is an exposed separate GPIO with a timer alternate function. | Keep eZ80 as the sole controller. Hold PB2 high in controller mode. Use PB5 for P4 select. Changing controller role or using PB2 as an external select can break SD operation. |
| Production EMOS | `_init_spi` owns the PB mux, holds PB2 and PB4 high, and selects controller mode 0 with divisor 3. `src/sd.asm` owns PB4 and its idle clocks. The byte helpers poll SPIF, and their timeout fall-through does not expose a clean transport error to a caller. | Keep agreed mode/divisor fixed for both devices if possible. Use a separate bounded EMOS burst with checked SPIF/MODF/WCOL. Do not call FatFS, change the SD mux, or toggle either select from an interrupt during that burst. |
| ESP32-P4, Rev C P4-PC | GP-SPI2 and GP-SPI3 are routable via GPIO matrix. SPI2 has native GPIO7/8/9/10 functions, which the commissioned header/profile cannot simply repurpose. SPI0/1 serve memory. The P4's own microSD uses SDMMC, a different peripheral and card. | Candidate owns one GP-SPI peripheral, DMA channel resources and one bounded high-priority service task. Use SPI2 routed to EXT1 if the exact component link/map and initialization show it unclaimed. Verify P4 onboard storage, HDMI and USB/keyboard coexistence in the candidate composition. |
| P4 SDK v5.5.5 | Slave mode supports bounded CPU transfers to 64 bytes and longer DMA packets. CS and SCK determine actual received bit count. If the controller clocks past the configured capacity, `trans_len` clips. DMA imposes word-size RX length, aligned DMA-capable buffers and the target's actual DMA/cache alignment. The driver installs the next transfer, enables it in hardware, then calls `post_setup_cb`. | Arm a receive capacity larger than the exact expected padded wire length. Compare actual bits, then expose only logical payload bytes. Use SDK-aligned internal buffers with word-multiple lengths and verify 1-, 3- and 511-byte tails. Assert READY only after actual hardware setup and release it in `post_trans_cb`. Reap/requeue promptly and keep diagnostics off the hot path. |

Sources are Zilog PS015317-0120, printed pp.130–139, and the [Olimex AgonLight2
Rev B schematic](https://github.com/OLIMEX/AgonLight2/blob/b7f2a21c282813efd8cdf26573eb5126876432a8/HARDWARE/AgonLight2_Rev_B/AgonLight2_Rev_B.pdf).
The Olimex tree also retains a manufacturer [eZ80F92 datasheet copy](https://github.com/OLIMEX/AgonLight2/blob/b7f2a21c282813efd8cdf26573eb5126876432a8/DOCUMENTATION/EZ80F92.pdf).
The software basis is [EMOS SPI at abefa2f](https://github.com/bgates747/agon-emos/blob/abefa2f943eb3089c08d85bf39e48ebb4938f4bd/src/spi.asm),
[EMOS SD at that commit](https://github.com/bgates747/agon-emos/blob/abefa2f943eb3089c08d85bf39e48ebb4938f4bd/src/sd.asm),
[production pins and source identities](../../../production/bundles/olimex-parlio-v0.3.0/bundle.yaml),
[ESP-IDF 5.5.5 SPI slave guide](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/peripherals/spi_slave.html),
and [SPI slave driver source at the project's pinned IDF commit](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_driver_spi/src/gpspi/spi_slave.c).
The P4 hardware basis is the [Rev C source index](../../hardware/esp32-p4-pc/README.md),
[P4-PC board profile](../../../vdp/build/boards/p4-pc.json) and
[reported harness assignments](../../../hardware/designs/light2-p4pc-harness-draft/README.md).

## Earlier shared-bus trouble and what fixed it

1. With the classic ESP32 WROOM MISO wired, MOS lost access to the SD card.
   Disconnecting MISO preserved SD access and still let the WROOM receive.
   Separate CS lines were already present. A separate eZ80 software bug
   left the WROOM's SPI mode/divisor in force through FatFS calls. Keeping
   the configuration change inside each burst restored SD operation in
   that test. Software gating of WROOM MISO helped but did not fully
   eliminate corruption. The physically installed 74HC125 gated WROOM
   MISO by the WROOM's CS and removed the output contention. The report's
   suggestion that the card fell out of SPI mode was not independently
   proved. Keep the SD driver's existing deselect/idle clocks and verify
   continued card operation instead of counting dummy clocks as recovery.
   [Sharing notes](https://github.com/bgates747/agon-hardware/blob/45e0f4ffce5b84cc0956d017e0a5198da5ef83bf/first_steps/stream_agm/spi-bus-sharing-notes.md)
   · [Hardware and fault narrative](https://github.com/bgates747/agon-hardware/blob/45e0f4ffce5b84cc0956d017e0a5198da5ef83bf/first_steps/stream_agm/problems_and_proposals.md)

2. The buffer left a second failure visible. Under HTTP traffic, the
   classic ESP32 missed or entered otherwise byte-exact MOSI transactions
   late. The loaded test retained a partial record matching a known
   sequence at bit offset 164, plus a whole missing completion for an
   exact wire window. The successful WROOM design separated descriptor
   reaping from logging and exposed hardware-armed READY. Its loaded
   `SPI-DMA-15c` run matched all 20,000 1,024-byte records, with all CS
   assertions armed and every expected re-arm interval visible. This
   supplies an implementation pattern and controls for the P4 prototype.
   The tested receiver, traffic direction and network load were WROOM
   Agon-SD-to-WROOM with one HTTP worker.
   [15c result](https://github.com/bgates747/agon-hardware/blob/45e0f4ffce5b84cc0956d017e0a5198da5ef83bf/first_steps/stream_agm/tests/runs/2026-08-08_spi-dma-15c_hardware-ready-http1_run02/run.md)

The historical failure combines real ownership bugs with the innate
limitation that one hardware SPI shifter serves two physical destinations.
The failures above have bounded remedies. The serialization cost remains.

## Proposed signal assignment

This is a candidate for a future isolated harness. The current PARLIO data,
clock and valid conductors sharing the listed P4 contacts must be disconnected
before those contacts are reassigned. The four existing UART conductors on
Agon PC0–PC3 and their corresponding P4 GPIOs 17–20 stay connected. Keep the
P4's local SD and pUEXT functions.

| Signal | AgonLight2 Rev B | P4-PC Rev C | Driver and condition |
| --- | --- | --- | --- |
| SCK | UEXT pin 9, PB3 | EXT1 pin 8, GPIO14 | eZ80 → P4. Remove prior PD5 connection on EXT1.8. |
| MOSI | UEXT pin 8, PB7 | EXT1 pin 16, GPIO33 | eZ80 → P4. Remove prior PC5 connection on EXT1.16. |
| MISO | UEXT pin 7, PB6 | EXT1 pin 15, GPIO32 | P4 → eZ80 through select/power-gated high-Z output. Remove prior PC4 wire and verify the optional external-power-sensing link is disconnected. |
| P4_CS_N | 34-pin Agon GPIO header pin 26, PB5 | EXT1 pin 10, GPIO16 | eZ80 → P4. Qualify PB5 ownership versus T5_OUT/user GPIO. Pull high at idle. Remove prior PD7 connection on EXT1.10. |
| READY_N | 34-pin Agon GPIO header pin 13, PD4 | EXT1 pin 9, GPIO15 | P4 → eZ80. Reuse this wire with isolated open-drain ownership and Agon-side bias. Release at reset/absence and between arms. |
| GND | 34-pin GPIO pin 33 or UEXT pin 2 | EXT1 pin 3 | Common reference. Separate positive rails. |

The table avoids boot strap GPIO36 and the GPIO46 SD/LDO4 I/O-bank dependency.
UEXT pin 10 is PC2 on this board and belongs to existing UART flow control.
The board's regular PB4 card select remains local; PB2 /SS stays high. These are
source-based assignments. Confirm switchable sense links, connector orientation,
actual pad power banks and connected harness before any wiring.

Provide hardware MISO disable whenever P4 select is high, the board is
unpowered or reset, or the link is disabled. Put fail-open partial-power-down
isolation on the P4 branch, including SCK/MOSI/CS and READY, so unequal power
does not back-feed or falsely assert a handshake. A 74HC125-type select gate
explains the historical correction, but its previous success alone does not
qualify powered-off protection. Specify and test the candidate gate's
power-off leakage and worst-case 3.3 V timing. Always measure against the
original board's idle/bias behavior and leave the separate SD card select and
SD trace free from added software drivers.

## Transaction and migration outline

1. EMOS owns bus admission and clocks. P4 posts a correlated transfer request
   through existing UART. EMOS issues a bounded positive-length burst only
   at a filesystem-safe point, with the SD CS high, no pending SD write/busy
   response, and a new READY for the matching session, direction and length.
   P4 preloads outgoing bytes for a PUT. EMOS supplies clock via dummy MOSI
   during PUT. EMOS supplies bytes on MOSI for GET and P4 ignores its dummy
   transmit lane. This is one logical direction per burst.
2. Preserve normal SD state across the transfer. Prefer identical mode 0 and
   divisor 3. For slow bring-up only, bracket saved mode/divisor changes
   around the burst using the Zilog disable/reconfigure/enable sequence
   with both selects high. Initialize PB5 as deselected across SPI activation,
   preserve unrelated Port B bits, and review PB4/PB5 updates for stale sampled
   GPIO and any interrupt race. SPI_SR has read-to-clear status, so retain
   faults from the polling loop. An ISR must not consume that status or take
   ownership of the shifter while EMOS is in a burst.
3. On completion or a fault, EMOS raises P4 CS, quiesces the shifter and returns
   ownership to the SD driver. The P4 checks exact completion and publishes a
   correlated result. A RAM-link completion cannot commit a file. Keep existing
   SD temporary-file/activation rules, independent UART control and normal
   checksum policy. Reset, partial or overlong frame and stale READY all close
   the session. Reconcile pending work before another write. UART is the
   unchanged fallback under the selected operator policy.
4. Change or add the EMOS burst, use a matched listener/P4 transport adapter and
   keep the host-visible staged upload/download semantics. Expose separately
   negotiated SPI capability and explicit carrier in receipts. Prove exact linked
   ROM and SRAM delta using the production EMOS map before claiming fit. Verify
   DMA alignment and I/O/IRQ resource use with the exact P4 build. Preserve
   boot without P4, keyboard and both VDU paths, the P4-local SD host and HDMI.

## Throughput limits and other SPI options

- The board clock is 18.432 MHz. The minimum documented eZ80 controller divisor
  of 3 gives 3.072 MHz SCK or 384 kB/s (375 KiB/s) with no inter-byte software
  time. A 1 MiB SD-backed file at equal serial clock rates takes at least two
  bus passes, or about 5.46 s before FatFS, SD wait tokens, busy time, buffer
  copies, IRQ overhead and framing. Hardware DMA on P4 does not overlap the
  eZ80's SD and Extender phases on this controller. This is a ceiling for
  bytes requiring both passes, in either direction. Short cached reads and
  RAM-only tests have different work and limits.
- The earlier capture measured 285.5 KiB/s under peripheral CS and 119.7 KiB/s
  including the inter-packet SD phase, about 122.57 kB/s on wire. Its 1,024-byte
  records include a 4-byte header, so about 122.09 kB/s is the useful file
  proxy. This implies roughly 8.59 s per 1 MiB at that sustained rate,
  without Pi spool or current transaction/SD write figures. Faster/slower
  Agon → P4 and P4 → Agon results must be measured independently.
  [Rate decomposition](https://github.com/bgates747/agon-hardware/blob/45e0f4ffce5b84cc0956d017e0a5198da5ef83bf/first_steps/stream_agm/throughput-review-2026-08-08.md)
- P4 as controller on that shared bus requires a physical arbiter, suspended
  eZ80 SD ownership and controller/peripheral switching. It also removes
  the eZ80's natural ability to withhold clocks when it cannot service its
  single-byte hardware. Do not use this route on the existing PCB.
- Independent SPI over PC4–PC7 retains the four UART wires and separates
  microSD electrically, using existing harness lanes. It needs a software
  SPI clock at the eZ80 end or an external bridge. The previous
  [four-lane proposal](../PORT-008/FOUR-LANE-REVIEW.md) evaluated software
  clocking with a P4 SPI-HD receiver and was withdrawn when eight-bit
  PARLIO was selected. At the eZ80's clock, software has only 16 CPU cycles
  per complete 1-bit SCK period to match a 115.2 kB/s raw 1.152 Mbaud UART
  link, after accounting for the eight clocks per byte. The actual GPIO loop
  needs data/clock I/O, branches and storage and would need separate proof.
  A two-lane variant doubles that symbol-cycle budget but adds turnarounds.
  An external bridge could decouple SD timing at higher cost in hardware,
  connector lanes and ownership verification.

Before SD traffic, prove a bounded loopback in each direction with the card
deselected, exact first/last bits, deasserted CS, safe attachment boot order,
and deferred P4 arm. Then alternate link bursts and SD reads/writes using
separate scratch files. Compare with bare production SD, test SD-only operation
with the P4 off or absent, and capture both selects, READY, SCK, MISO and MOSI
at the first failure. Qualify a mixed-size two-way load and network/keyboard
soak before accepting speed or reliability. Keep this experiment and its
rollback independent of production PARLIO.
