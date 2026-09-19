# RESEARCH-004 — P4 Ethernet/HDMI sourcing assessment

## Executive summary

**September 18 purchase update:** Author has backordered P4-PC from Mouser US.
Board integration, accessories and breadboard-harness planning now belong to
[P4PC-001](../P4PC-001.md). Earlier same-GPIO rejection below is historical;
standalone usefulness and total assembled cost now justify evaluating remapping.

**Current purchasing criterion (Author clarification, September 18): a complete
assembled drop-in adapter, or the closest practical equivalent. Chip-only
listings are excluded. Custom-interposer candidates below are historical research
options, not qualified near-drop-in recommendations. An assembled reproduction
of the exact Olimex board remains within scope.**

**No confirmed product meets all requirements unchanged.** A genuine single-board
P4/Ethernet/HDMI solution exists: **Olimex ESP32-P4-PC**. However, its exposed GPIOs
and peripheral assignments differ from our DevKit, so it is not a replacement for
our existing harness. DigiKey lists it for **$28.92**, with **zero stock and one
expected September 23, 2026**. That is a US purchasing lead, not available stock.

**The best US-stocked experiment is the M5Stack U221 HDMI adapter: $9.95,
24 listed at DigiKey.** It uses the LT8912B bridge but a different connector.
Keeping our current DevKit and making a properly designed interposer is a
plausible path; electrical compatibility and firmware operation remain untested.
It is **not** a ready-made compatible adapter recommendation.

The exact Olimex MIPI-HDMI remains the lowest-integration-risk hardware, but this
search did not find a stocked US distributor listing for it. The Author's
reported EUR5000 minimum blocks direct USA orders. No order or vendor contact
was made. No firmware was changed. Prices/stock retrieved **2026-09-17**; shipping,
tax, tariffs and checkout acceptance have not been verified.

## Purchasing shortlist

| Product | Meets P4 + Ethernet + onboard HDMI? | GPIO/connector verdict | US purchasing evidence |
| --- | --- | --- | --- |
| Olimex ESP32-P4-PC | Yes | Fails unchanged DevKit GPIO requirement | [DigiKey 1188-ESP32-P4-PC-ND](https://www.digikey.com/en/products/detail/olimex-ltd/ESP32-P4-PC/29208985): $28.92, 0 stock, 1 expected Sep 23 |
| M5Stack U221 AddOn Display Out | Adapter only; retain existing board | Potential custom interposer; not plug-compatible | [DigiKey 2221-U221-ND](https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/U221/29784159): $9.95, 24 stock; tariff notice shown |
| Olimex MIPI-HDMI | Adapter only; retain existing board | Manufacturer explicitly supports our DevKit | [Olimex](https://www.olimex.com/Products/IoT/ESP32-P4/MIPI-HDMI/open-source-hardware): EUR14.95 in stock, but no verified US buying route |
| ST B-LCDAD-HDMI1 | Adapter only | Different interface/bridge; custom integration required | [DigiKey](https://www.digikey.com/en/products/detail/stmicroelectronics/B-LCDAD-HDMI1/6193105): indexed $44.65, 115 stock; indexed result two months old, recheck before ordering |

Mouser also lists ESP32-P4-PC as **909-ESP32-P4-PC**. Its accessible
[Spanish storefront](https://www.mouser.es/es/ProductDetail/Olimex-Ltd/ESP32-P4-PC?qs=sGAEpiMZZMu3sxpa5v1qrv5RC3LFtvYYN6%2FGFZqgshE%3D)
reported zero stock and incoming quantities, including 83 expected September 28.
That does not establish US stock or shipping. DigiKey's US listing is the stronger
US evidence. Neither incoming date is a delivery guarantee.

## What must be preserved

Local authority:
[DevKit Rev D1 pinout](../../../hardware/designs/light2-harness-r01/legacy-evidence/esp32-p4-devkit-rev-d1-pinout.md).
The requirement is all existing exposed GPIOs, not merely enough remappable pins.

| Current header | Exposed numbered GPIOs |
| --- | --- |
| EXT1 | 2–19 inclusive |
| EXT2 | 54, 53, 48, 47, 46, 33, 32, 23, 22, 21, 20, 27, 26 |

The headers also expose power/ground, ESP_EN and native USB DP/DN. Pin functions
are not universally free: the existing schematic and harness remain authoritative.
Current UART uses GPIO22/12/11/23; the parallel data group uses
22/12/23/11/32/10/33/9; its control group includes 14/13/20/15/21. ZDI recovery uses
46/47. Replacing the board must preserve these functions or explicitly redesign
the harness and firmware. Pi reset GPIO17 is on the Pi, not P4 GPIO17.

## ESP32-P4-PC: why it falls short

[Official product](https://www.olimex.com/Products/IoT/ESP32-P4/ESP32-P4-PC/open-source-hardware),
[Rev B schematic](https://github.com/OLIMEX/ESP32-P4-PC/blob/main/HARDWARE/ESP32-P4-PC-Rev.B/ESP32-P4-PC_Rev_B.pdf),
[manual](https://github.com/OLIMEX/ESP32-P4-PC/blob/main/DOCUMENTS/ESP32-P4-PC-user-manual.pdf).

The board integrates LT8912B HDMI, Ethernet and USB hosts. This is actual HDMI
output, not an unpopulated DSI connector or HDMI capture input.

Schematic inspection finds EXT1 numbered signals:
**2, 14, 15, 16, 17, 18, 19, 20, 26, 27, 32, 33, 36, 46, 47, 48**.
UEXT supplies **4, 5, 22, 23, 53, 54**, plus UART0. That is not the DevKit's
header set. In particular **GPIO9–13 are assigned to I2S audio**, including our
UART TX/RTS and parallel signals. These pins are not ordinary EXT1/UEXT breakouts.
GPIO22/23 also have I2C pullups. GPIO20/32 have optional battery/power sensing
connections; the manual says these sensing links are disconnected by default.

Thus the PC is attractive for a fresh design, but a soldering/remapping project
would be required here. Its “all free GPIOs” description does not mean all the
GPIOs exposed on the DevKit. No claim is made that every lost signal could be
recovered while preserving all onboard functions.

## Adapter route: preserve the current board

### Exact Olimex adapter

[Official compatibility and cable information](https://www.olimex.com/Products/IoT/ESP32-P4/MIPI-HDMI/open-source-hardware)
identifies the DevKit and a **15-pin, 1.0 mm FPC**, cable **FPC-15-1.0-150**.
[Adapter Rev B schematic](https://github.com/OLIMEX/MIPI-HDMI/blob/main/HARDWARE/MIPI-HDMI-Rev.B/MIPI-HDMI_Rev_B.pdf)
is available for comparison and open-hardware reproduction.

This is the preferred electrical starting point if a distributor can source it.
A distributor special order or another seller shipping to the US is a follow-up
lead, not a verified solution. Search covered exact model/name and US distributor
queries; failing to find a listing is not proof none exists.

### M5Stack U221: available, but requires an interposer

[Manufacturer documentation](https://docs.m5stack.com/en/addon/AddOn_Display_Out_For_PoE-P4)
shows LT8912B, two DSI lanes, **24-pin 0.5 mm FPC**, I2C and reset. Published
examples support 720p60 and 1080p30. Its documented power arrangements include
5 V and 3.3 V, with additional expansion connections; do not assume the supplied
ribbon alone provides everything on an Olimex board.

[Manufacturer schematic](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1253/SCH_Unit_PoE-P4_Display_OUT_V0.2_SCH_PDF_20260319_2026_03_19_16_32_08.pdf)
provides the needed circuit details. The connector and auxiliary power/control
signals must be mapped explicitly. Matching bridge silicon makes reuse plausible;
it does not prove board-level compatibility.

Before buying this as a working solution, the next engineering step is:

1. Draft and review a complete 15-to-24-pin interposer net table, including cable
   contact orientation, DSI lane polarity, grounds, reset, I2C and power.
2. Resolve 5 V/3.3 V supply routing and reset behavior without sacrificing active
   harness GPIOs. Do not connect unused USB/SD/touch signals speculatively.
3. Use short, impedance-controlled differential routing; loose breadboard wires
   are not a suitable substitute for the DSI connection.
4. Adapt and qualify an LT8912B driver and DSI timing, then integrate EDP scanout.

No interposer was designed or hardware qualified in this research task.

### Other products screened

- [ST B-LCDAD-HDMI1](https://www.st.com/en/evaluation-tools/b-lcdad-hdmi1.html):
  ADV7533 supports two to four DSI lanes and HDMI output. Its STM32 interface and
  driver assumptions differ; it offers no demonstrated drop-in advantage here.
- [NXP IMX-MIPI-HDMI](https://www.nxp.com/design/design-center/development-boards-and-designs/IMX-MIPI-HDMI):
  i.MX adapter rather than an Olimex plug-in; not shortlisted over the cheaper
  LT8912B path.
- [Waveshare ESP32-P4-Module-DEV-KIT](https://www.waveshare.com/product/mcu-tools/development-boards/esp32-p4-module-dev-kit.htm):
  Ethernet and display expansion do not amount to onboard HDMI conversion.
- Espressif's Function EV board likewise needs an external bridge. Its
  [LT8912B component](https://github.com/espressif/esp-bsp/tree/master/components/lcd/esp_lcd_lt8912b)
  and [HDMI rendering example](https://github.com/espressif/esp-iot-solution/tree/master/examples/display/lcd/hdmi_video_renderer)
  are useful software starting points, not evidence of a stocked adapter.
- HDMI-to-CSI capture boards, including M5Stack Display **In**, are the wrong
  direction. “MIPI” alone does not establish compatibility.

## Recommendation and remaining uncertainty

**Keep the present P4 DevKit.** First preference remains obtaining the exact
Olimex adapter through a distributor. If that remains unavailable, evaluate a
small interposer for the US-stocked M5Stack U221. The ESP32-P4-PC is worth knowing
about, but does not satisfy the stated same-GPIO requirement.

None of these purchases alone implements EDP HDMI output. We still need a DSI
scanout path, bridge setup, pixel-format conversion and mode/timing validation.
A bridge's advertised output timing is not a measured EDP rendering frame rate.
For our indexed framebuffer, the display path must supply a supported RGB format;
monitor-compatible scaling/timings require separate qualification.

This concludes sourcing research with explicit non-matches and a conditional
engineering path, rather than claiming an exact solution was found. No purchases,
firmware builds, resets, flashes or wiring changes were made. Hardware CLI is
used only for the requested attention lifecycle.

## Evidence retention

Original PDFs and extraction/crop aids are in ignored `agents/hdmi-search/`:
`pc.pdf`, `pc-manual.pdf`, `adapter.pdf`, `m5.pdf`. Official source links above
are the durable references. The schematic EXT header was visually inspected,
not inferred solely from product advertising. Stock readings describe seller
pages on the retrieval date, not a completed checkout.

## 2026-09-17 addendum — Pico and PiCowbell inventory correction

The Author supplied the exact parts after initially recalling a Pico 2:

| Status | Part | Meaning |
| --- | --- | --- |
| Reported on hand | [Raspberry Pi SC0915](https://www.digikey.com/en/products/detail/raspberry-pi/SC0915/13624793) | Original Pico, RP2040; no HSTX peripheral |
| Reported on hand | [Adafruit 6363](https://www.adafruit.com/product/6363) | PiCowbell HSTX DVI Output, mini-HDMI connector, GPIO12–19 |
| Recommended order | [Raspberry Pi SC1632](https://www.digikey.com/en/products/detail/raspberry-pi/SC1632/26241102), DigiKey **2648-SC1632-ND** | Pico 2 with presoldered headers, RP2350; correct HSTX-capable board |
| Unsoldered alternative | [Raspberry Pi SC1631](https://www.digikey.com/en/products/detail/raspberry-pi/SC1631/24627142), DigiKey **2648-SC1631CT-ND** | Pico 2 without headers; useful if choosing a custom stacking arrangement |

The [Adafruit assembly guide](https://learn.adafruit.com/adafruit-picowbell-hstx-dvi-output/pico)
covers socket/stacking options. Check the Cowbell's existing assembly before
ordering headers: the presoldered Pico still requires mating female sockets on
the Cowbell. Also check for a mini-HDMI-to-HDMI cable and a Micro-USB data cable.
No wireless model is needed. Price and stock should be checked at checkout.

Correction to the conversation: the Pico and Cowbell are not a supported HSTX
pair when the Pico is SC0915. They physically share the form factor, but RP2040
cannot run the RP2350 HSTX output path. This is not proof that all video use is
impossible: [PicoDVI](https://github.com/Wren6991/PicoDVI) generates DVI using
RP2040 PIO/DMA and software encoding, with overclocking. Compatibility with this
specific Cowbell pinout has **not** been qualified. Do not turn that possibility
into a purchasing or performance guarantee.

The potential new video architecture is P4 rendering, then a separately designed
P4-to-Pico transport, then Pico 2 framebuffer storage and HSTX scanout through the
Cowbell. The Cowbell is not a MIPI receiver or a standalone conversion processor.
At 512x384 and one byte per pixel, one framebuffer is 192 KiB, two are 384 KiB,
and 60 complete updates per second require 11.79648 MB/s payload before overhead.
The RP2040 has 264 KiB SRAM, versus the RP2350's 520 KiB; video working buffers
and code/data also need space. These arithmetic budgets are not measured
throughput or proof of a supported display timing. P4-to-Pico transfer, palette
handling, scanout and concurrent operation remain unimplemented and untested.
See [RP2040 specifications](https://www.raspberrypi.com/products/rp2040/) and
[Pico 2 specifications](https://www.raspberrypi.com/products/raspberry-pi-pico-2/).

The Author favours retaining the original RP2040 for **bench automation**.
Potential uses discussed: USB-controlled bus capture/timing, repeatable parallel
or handshake stimulus, reset/recovery control, and controlled fault injection.
These are proposals, not installed capabilities; signal voltage, pin allocation,
capture capacity and integration with existing recovery tools require a separate
work contract. No current bench wiring or firmware was changed for this addendum.
No Pico/Cowbell experiment has been started or authorized by this shopping note.

## 2026-09-18 — Broader adapter search

The wider search adds **Toradex Verdin DSI-to-HDMI** and **Ezurio DB_DSIHD**
to the purchasing leads, but still establishes no new plug-compatible US-stocked
adapter. Toradex has the strongest new direct distributor evidence: Mouser lists
15 at $33.86. Its control interface and connector require adaptation. No orders,
firmware changes or bench operations were performed.

### Likely article and its limitations

The [CNX Software Olimex adapter article](https://www.cnx-software.com/2025/12/04/olimex-lt8912b-based-mipi-hdmi-adapter-board-adds-hdmi-output-to-the-esp32-p4-devkit-board/)
links to ESP-HDMI-Bridge. It also contains an explicit correction to its original
cross-board compatibility claims. Treat its board list as discovery leads, not
schematic qualification. This may be the Author's article; identity is unconfirmed.
The [earlier bridge article](https://www.cnx-software.com/2025/04/20/esp-hdmi-bridge-esp32-p4-hdmi-streaming-adapter-usb-ethernet-wifi-microsd-card/)
said the bridge was unavailable at publication and linked reproducible design
files. That historical statement does not establish current availability.

### Newly screened purchasing leads

| Candidate | Purchasing evidence retrieved September 18 | Compatibility assessment |
| --- | --- | --- |
| [Toradex Verdin DSI to HDMI, Mouser 145-0157](https://www.mouser.com/en/ProductDetail/Toradex/Verdin-DSI-to-HDMI-Adapter?qs=2FehpBK1j95WFkdv5AfHGg%3D%3D) | US storefront lists 15, $33.86 each; checkout not verified | LT8912B; custom interposer and control-voltage qualification required, not a ribbon replacement |
| [Ezurio DB_DSIHD](https://www.ezurio.com/system-on-module/accessories/db-dsihd) | Manufacturer distributor feed lists DigiKey 25 and Mouser 2; direct price not established | Manufacturer targets Nitrogen8M/i.MX8M; no verified Olimex pinout or P4 driver qualification |
| ESP-HDMI-Bridge | Open design/software lead; no confirmed stocked US retail source found | Relevant P4 reference implementation, not yet a purchasing solution |

The [Toradex manufacturer datasheet](https://docs.toradex.com/109491-toradex-dsi-to-hdmi-adapter.pdf)
documents a 60-contact DSI adapter connector and 1.8 V I2C/reset/power-enable
control signals. The LT8912B chip in common with Olimex does not make the board
plug-compatible. Confirm the exact sold board revision against its matching
schematic before designing an interposer; this is a screening observation, not
an approved wiring table.

Ezurio's [manufacturer demonstration](https://www.ezurio.com/documentation/mipi-dsi-to-hdmi-for-i-mx8-boards-with-db-8mm-dsihd)
confirms DSI input to HDMI output, rather than capture in the reverse direction.
Its [DigiKey US listing](https://www.digikey.com/en/products/detail/ezurio/DB-DSIHD/19242856)
exists. Manufacturer inventory feeds may lag seller stock. This board currently
has less established integration detail than the M5Stack or Toradex candidates.

Searches included review-site cross-links, LT8912B bridge boards, Raspberry Pi
DSI adapters, industrial SoM accessories, and exact Olimex part/distributor
queries. No additional verified US-stocked exact Olimex adapter emerged.
M5Stack remains the inexpensive interposer candidate from the first pass;
Toradex is a new documented alternative, not a demonstrated improvement over it.
The Olimex open hardware files also permit investigating PCB assembly, but no
fabrication quote or parts-availability assessment was obtained.

## 2026-09-18 — Contract-manufacturer repeat-build search

**No public evidence found that PCBWay, JLCPCB, Seeed Fusion or AISLER has
previously assembled the exact Olimex MIPI-HDMI board.** This is a limited public
catalogue/index search, not access to private order histories or proof that no
such run exists. No vendor was contacted and no files were submitted for quotation.

1. [PCBWay Shared Projects](https://www.pcbway.com/project/) is readable through
   the web tool. Searches for Olimex MIPI-HDMI, LT8912/LT8912B and DSI-to-HDMI
   found no exact matching shared project. A direct LT8912B tag-filter request
   failed, so internal catalogue coverage is incomplete. Its
   [sharing guide](https://www.pcbway.com/blog/help_center/Shared_Projects_PCBWay_Community_PCBWay_Website_Exploration_05_17c562d8.html)
   allows projects to be created independently or shared from orders. Therefore
   catalogue presence alone would not establish a prior assembly run.
2. [OSHWLab ESP-HDMI-Bridge](https://oshwlab.com/hawaii0707/esp-hdmi-bridge)
   is a real related shared design, attributed to the Espressif OSHWHub project.
   It is not the Olimex board and its Completed label is not factory assembly
   evidence. Connector compatibility and manufacturing history remain unverified.
3. The chip-only LT8912B catalogue entry was removed from purchasing leads at
   the Author's request. Individual components do not meet the requirement for
   a complete assembled adapter.
4. JLCPCB's [SMT reorder procedure](https://jlcpcb.com/help/article/smt-reorder-process-overview)
   explicitly supports reuse of stored stencils/fixtures when the original order
   included storage. That substantiates the Author's tooling-reuse idea, but
   does not establish permission or availability to reuse another customer's
   tooling and production data.
5. Domain-restricted Seeed and AISLER searches found no exact prior-run evidence.
   Unrelated CSI camera, reverse-direction HDMI-to-MIPI and RGB-to-HDMI projects
   were excluded.

Next useful inquiry, if the Author elects to contact vendors: identify the exact
Olimex revision and repository, ask whether a previous assembled run exists,
whether its stencil/panel/CPL/BOM/inspection setup can be reused for a new customer,
and request itemized quotations for 2, 5 and 10 fully assembled units delivered
to the USA. Separate setup/tooling, parts, PCB/assembly, functional testing and
shipping. A prior PCB fabrication order does not establish assembly or HDMI
functional validation. No inquiry has been sent.
