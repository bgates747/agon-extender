# Agon Extender

Cross-project authority is defined in [OWNERSHIP.md](OWNERSHIP.md).

Agon Extender is an experimental hardware and firmware project for extending
the capabilities of the Agon computer family with an external Espressif ESP32-P4
coprocessor, by way of the Olimex ESP32-P4-DevKit (rev. D1). The intent is for Extender to operate as a wholly-independent video display processor (VDP) with enhanced performance and extended functionality over the stock VDP, while remaining fully backward-compatible with existing Agon software, but not limited to legacy software capabilities.

## Current capability and development queue

The foreground mainboard SD service now supports host directory listing, reads,
staged writes, verification and recoverable replacement over Ethernet, P4 and
the EMOS-owned UART1 link. Ten unattended physical transfer cycles and native
Extender keyboard interruption/restart checks pass. See the
[operating guide](docs/mainboard-sd.md), [wire contract](docs/protocols/mainboard-sd.md)
and [scoped acceptance](docs/qualification/mainboard-sd/2026-09-13.md).
The service and games run at different times; remote game launching is not part
of this interface. Candidate qualification is distinct from general release.

Native USB keyboard input and the ordinary ExCom console remain working
foundations. Browser input is deferred. [TODO.md](TODO.md) owns the remaining
queue; SD acceptance does not automatically start another development task.

For the community TRS-OS discussion, start with the
[source guide and portable sample kits](docs/tasks/TRS-80-002/COMMUNITY-GUIDE.md).
TRS-OS integration remains an investigation; the kits run on a development host.

## Hardware

- [Espressif ESP32-P4 product page](https://www.espressif.com/en/producttype/esp32-p4)
  - Dual-core 32-bit RISC-V high-performance processor running at up to 400
    MHz, plus a low-power 32-bit RISC-V core running at up to 40 MHz.
  - 768 KB of high-performance L2 memory, 32 KB of low-power SRAM, and package
    variants with 16 MB or 32 MB of PSRAM.
  - Multimedia acceleration including an image signal processor, pixel
    processing accelerator, JPEG codec, H.264 encoder, and MIPI-CSI and
    MIPI-DSI interfaces.
  - 55 programmable GPIOs and peripheral support including Ethernet MAC,
    high-speed and full-speed USB 2.0 OTG, USB Serial/JTAG, SD/MMC, PARLIO,
    UART, SPI, I2C, I3C, I2S, and TWAI.
  - Hardware security facilities including secure boot, external-memory
    encryption, cryptographic accelerators, digital signatures, and a true
    random-number generator.
  - No integrated Wi-Fi or Bluetooth radio; wireless operation requires a
    companion device.
- [Olimex ESP32-P4-DevKit product page](https://www.olimex.com/Products/IoT/ESP32-P4/ESP32-P4-DevKit/open-source-hardware)
  - ESP32-P4NRW32 SoC with dual 400 MHz RISC-V application cores, 32 MB of
    in-package PSRAM, and 16 MB of SPI flash.
  - USB-C power, programming, and debugging through the ESP32-P4 USB
    Serial/JTAG interface.
  - Onboard Ethernet PHY and RJ45 connector, with optional Power over Ethernet
    through an expansion module.
  - MIPI-DSI display and MIPI-CSI camera connectors, a microSD card slot, and a
    pUEXT expansion connector.
  - All available GPIOs exposed on two 20-pin, 2.54 mm expansion headers, plus
    dedicated Boot and Reset buttons.
  - Open-source hardware certified as OSHWA UID `BG000145`, with published
    KiCad design files, schematics, and software examples.

## Firmware

The base firmware will be a port of the
[official ESP32-PICO-based Agon VDP firmware](https://github.com/AgonPlatform/agon-vdp),
used by the Agon Light and Console8, to the ESP32-P4. The port will retain the
existing VDP's functionality and compatibility while taking advantage of the
P4 to deliver higher performance and add new capabilities beyond those of the
original hardware and firmware.

All supported Extender operation requires the project-provided Extender MOS
(EMOS). EMOS exclusively owns Extender activation, operating-mode changes,
ordinary VDU routing, and the Agon-facing transport hardware. Applications and
extensions must use the documented EMOS interfaces and must not manipulate
those GPIO, UART, interrupt, or routing resources directly. This is a normative
software and integration contract, not a hardware privilege boundary: code
that bypasses EMOS is unsupported, may corrupt or brick either system, and is
used entirely at the operator's risk.

Example programs for Extended Compatible mode are currently curated and
emulator-tested in the sibling `agon-utils` repository under
`examples/extender`. The Author may move examples into this project as they
mature.

## Extended Capabilities

Core extended functionality will be provided directly by the ESP32-P4-DevKit
and its onboard interfaces and peripherals. Optional firmware configurations
will support additional capabilities when compatible external hardware is
connected, allowing an Extender system to grow beyond the base DevKit without
making that hardware mandatory for standard operation.

### Core Functionality

- The guaranteed initial and near-term primary video and digital-audio output
  path will stream both over the DevKit's onboard Ethernet connection to a web
  interface. This will allow a browser-equipped computer or other compatible
  network client to act as the Extender's display and digital-audio endpoint
  without requiring additional display or audio hardware on the Extender. All
  audio generated by the ESP32-P4 will use this Ethernet streaming path; the
  only initially supported alternative for physical audio output will be the
  Agon's onboard VDP. Other network-streaming protocols and consumers may be
  supported as the firmware develops, but are not part of this initial
  guarantee.
- Stock-compatible communication with MOS and eZ80 programs over the same
  1,152,000-baud, 8-N-1 UART protocol used by the Agon's onboard VDP.
- Enhanced one-way communication from the Agon to the Extender over an 8-bit
  parallel GPIO protocol. Transfers from an existing eZ80 memory buffer
  approach 900 KiB/s, approximately eight times the theoretical 112.5 KiB/s
  payload ceiling of the stock 1,152,000-baud UART link under 8-N-1 framing.
  End-to-end streaming from the Agon's SD card through MOS approaches 200
  KiB/s, or approximately 1.8 times that UART ceiling. Useful application
  throughput depends on the work the eZ80 must perform to read, generate, or
  transform the data before transmission.

> **Note:** A high-speed reverse parallel transport from the Extender to the
> Agon is not presently contemplated. Supporting it would materially complicate
> both the hardware and firmware, and the expected utility is not considered
> sufficient to justify the additional cost and complexity.

### Hardware-Expanded Capabilities

The following planned capabilities extend the VDP with optional Olimex display
hardware. They are not required for the guaranteed Ethernet-based video and
digital-audio path and will be enabled by future firmware development.

- Direct MIPI-DSI output to the
  [Olimex MIPI-LCD2.8-640x480](https://www.olimex.com/Products/RaspberryPi/MIPI-LCD2.8-640x480/)
  display is planned. The compatible 2.8-inch IPS panel has a 640-by-480
  resolution, 286 PPI pixel density, 300 cd/m² rated brightness, and a
  single-lane MIPI-DSI interface. Olimex publishes ESP32-P4 display examples
  for this hardware. At the time of writing, stock was confirmed at Olimex in
  Bulgaria; DigiKey and Mouser list the display, but no stocked U.S. source was
  confirmed.
- Video output through the
  [Olimex MIPI-HDMI](https://www.olimex.com/Products/IoT/ESP32-P4/MIPI-HDMI/open-source-hardware)
  adapter is also planned as an extended VDP function. Connected to the
  DevKit's MIPI-DSI interface with the required 15-pin FPC cable, the adapter
  provides HDMI 1.4 video output in RGB666 or RGB888 formats. Its hardware is
  specified for resolutions up to 1080p at 60 Hz, although the modes and frame
  rates ultimately supported by Extender firmware may be more limited. The
  adapter provides video only; digital audio will continue to use the network
  output path, or applications may continue to use the Agon's onboard VDP for
  audio. At the time of writing, the adapter was available directly from
  Olimex in Bulgaria, and no stocked U.S. supplier was confirmed.
- Optional wireless networking will be provided through the
  [Olimex MOD-WIFI-ESP8266](https://www.olimex.com/Products/IoT/ESP8266/MOD-WIFI-ESP8266/open-source-hardware)
  module. This ESP8266EX-based UEXT expansion module includes 2 MB of SPI flash
  and communicates over a UART using the first four UEXT signals: 3.3 V,
  ground, receive, and transmit. The Extender board will provide a small,
  dedicated header for attaching and communicating with this module without
  consuming the general-purpose expansion headers.

Later hardware revisions may provide an optional local audio-output expansion,
but its form and interface have not yet been determined. At minimum, the
Extender hardware will expose GPIOs through headers so users can develop and
connect their own peripherals and experimental expansions.

### Future Software Capabilities

MicroPython scripting within EDP on the ESP32-P4 is a planned long-term
capability, including potential uses in automation and repeatable test control.
Its inclusion in v1 is undecided; it is not restricted to a post-v1 release.
Scope and scheduling are tracked in [PORT-016](docs/tasks/PORT-016.md) and
the authoritative [TODO](TODO.md#future-software-capabilities).

The P4 DevKit's own microSD card will provide EDP-managed storage readable
from EMOS, with future MicroPython scripts sharing that storage service.
[PORT-007](docs/tasks/PORT-007.md) retains the existing v1 storage target,
independently of MicroPython's release timing.

## Licensing

Agon Extender is distributed under the **GNU General Public License, version 3
only** (`GPL-3.0-only`), except where individual files or third-party material
carry their own compatible license notices.

See [LICENSING.md](LICENSING.md) for the project licensing and attribution policy.

See [LICENSE](LICENSE) for the complete GNU GPL version 3 text.

Important upstream licensing includes:

- FabGL/vdp-gl-derived material: GPLv3-family licensing with original Fabrizio
  Di Vittorio attribution preserved;
- official Agon VDP-derived material: MIT License with its original notice
  preserved.

Third-party provenance must remain visible even when the combined Extender
project is distributed under GPLv3-only.
