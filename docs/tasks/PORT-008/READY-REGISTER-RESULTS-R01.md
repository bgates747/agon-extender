# PORT-008 — Live READY register check

The DevKit GPIO20 input still reads low despite the Author's preceding 3.27 V
measurement at the DevKit end of blue READY_N. Live configuration confirms
input enabled, GPIO function selected, open-drain mode and a high output latch.
No pad hold or disabled GPIO/IOMUX clock was found. This narrows the discrepancy
but does not establish a defective board, wrong wire or software remedy.

## Bounded procedure and identities

Author approved a separate GPIO-only probe after the unchanged historical
receiver reported zero. The [probe source](fixtures/ready-gpio-r01/main.c) uses
the same READY initialization and retained ESP-IDF v5.5.5 configuration. It
has no PARLIO setup or arm command. Both probe installations were independently
verified, including all three flash segments; Agon was never reset. EMOS,
mainboard VDP, wiring and SD startup were unchanged. USB collectors are closed.

Initial build `ready-gpio-r01-b2026-10-10-10-20-18Z` added the SDK dump and raw
input/IO_MUX/output registers. Follow-up `ready-gpio-r02-b2026-10-10-10-23-32Z`
added read-only hold, clock and PMU-active registers; its app SHA-256 is
`3d006da15e5307accd3ce8578a8db35dc7db0155c167a2aaac27eedfc822ad33`.
The initial source/image/manifests are retained separately in local evidence.
The first build took 79.90 host seconds; each independently verified installation
took about 7.8 seconds. These are preparation times, not transfer measurements.

## Observations

| Item | Live result | Interpretation |
|---|---|---|
| Author's preceding meter reading | 3.27 V, DevKit end | Measured header signal was high; not a simultaneous chip-pad measurement |
| SDK read / raw input bit20 | 0 / 0, all three samples | Low is present in raw input, not merely a status-formatting error |
| IO_MUX | `0x00001a02`: input enabled, function1/GPIO | Expected active GPIO input setup |
| Output latch / enable | Both `0x00100000` | GPIO20 latch is high and output enable bit set |
| Pin register | `0x00000004` | Open-drain selected |
| Output route | `0x00000100`, signal256 | SDK's default simple GPIO route; SDK dump labels enable control peripheral-controlled |
| Pad hold register | `0x00000000` | No individual digital-pad hold indicated |
| GPIO clock / IOMUX clock | `0x1` / `0x200` | Both clock-enable bits set |
| Sleep selection / PMU active control | 1 / `0x00000000` | Sleep selection is enabled by normal SDK startup; active-state pad-sleep/hold settings read zero |

The retained SDK's `esp_sleep_startup_init` deliberately enables per-pin sleep
selection after configuring isolated sleep pads. Therefore `SleepSelEn=1` alone
is not a fault. Automatic power management is disabled in this build.
Relevant local SDK sources are `components/esp_hw_support/sleep_gpio.c`,
`components/hal/esp32p4/include/hal/gpio_ll.h` and the matching `soc` GPIO,
IO_MUX, HP_SYSTEM, HP_SYS_CLKRST and PMU register definitions.

## Discussion boundary

The approved readback is complete. A possible next controlled experiment is
GPIO20 input-only with sleep selection explicitly disabled, retaining external
bias and adding no drive-low, data or clock operations. That changes pin
configuration and has **not** been performed. Discuss before proceeding.
The current readback probe remains installed and idle, READY open-drain latch
high. Normal Extender keyboard/network services are unavailable until restored.
Exact normal-firmware restoration is prepared; no automatic restoration/reset
occurs at this discussion boundary. No parallel payload or DMA verdict exists.

## Approved input-only comparison — r03

Author approved the next comparison. Build
`ready-gpio-r03-b2026-10-10-10-28-45Z` was installed and independently verified
at all three flash segments; app SHA-256
`15cc547f67916b3908a0dba66d5fb568ca01ced057137f7677c7b524013f4d39`.
Boot capture records three consecutive stages, three samples each:

| Stage | Output enable | Open drain | Sleep selection | Raw input bit20 / SDK read |
|---|---:|---:|---:|---|
| Historical released setup | 1 | 1 | 1 | 0 / 0 |
| Input-only | 0 | 0 | 1 | 0 / 0 |
| Input-only, sleep selection disabled | 0 | 0 | 0 | 0 / 0 |

Live readback confirms both requested configuration changes took effect;
neither corrected the low input reading. Thus these changes are not a remedy
for the observed discrepancy. GPIO20 remains input-only, sleep selection off,
with no internal pull and unchanged external bias. No Agon reset, SD mutation,
parallel arm or payload occurred; the flash collector is closed.

A next possible diagnostic is to enable only GPIO20's weak internal pull-up
while retaining input-only mode, to test whether that input can report high.
It would introduce internal bias and is **not** part of this completed approval.
No such test has been performed. Do not infer a wiring or silicon fault yet.

## Approved weak pull-up comparison — r04

Author approved the internal pull-up test. Build
`ready-gpio-r04-b2026-10-10-10-31-12Z` was installed and independently verified
at all three flash segments; app SHA-256
`de77cd92ac919071896f453319014e31ab84883cbf48a661c7d472cf08afe7c1`.
GPIO20 remained input-only, sleep selection disabled, with external bias unchanged.

| Stage | SDK/raw input bit20, three samples | IO_MUX |
|---|---|---|
| Internal pull-up off, before | 0, 0, 0 | `0x00001a00` |
| Internal pull-up on | 1, 1, 1 | `0x00001b00` |
| Internal pull-up off, after | 1, 0, 0 | `0x00001a00` |

The SDK and raw input agree at each stage. Live output enable stayed zero.
The final stage clears the internal pull-up, restoring the preceding baseline.
GPIO20 can report high: a permanently stuck-low input or status formatting
error does not explain this test. The delayed fall after pull-up removal is
consistent with a floating or weakly biased input; it is not a voltage trace.

The external 10 kΩ pull-up reportedly holds the measured DevKit-end header
point at 3.27 V, but the chip input is not held high after internal bias is
removed. This strongly suggests a physical contact/continuity or pin-identity
discrepancy; a fresh pad-level/continuity check is needed before declaring the
exact cause. An internal pull-up is **not** a handshake repair: it does not
prove the Agon and P4 are connected or can signal one another.

The retained schematic-derived DevKit pinout still maps GPIO20 to EXT2-13,
between EXT2-14/ESP_EN and EXT2-12/GPIO21. No conflicting mapping found in that
reference. Physical agreement remains to be verified. No new wiring or meter
operation has been requested/performed by this procedure.

Probe r04 remains installed idle with GPIO20 input-only, sleep selection off
and internal pull-up off. Collectors closed. No Agon reset, SD mutation, other
pin configuration, PARLIO arm or data transfer occurred. Exact normal-firmware
recovery remains prepared. Pause for discussion of the physical check.
