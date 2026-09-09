# Light 2 harness r03 — DRAFT

This drawing records the simplified direct Port C circuit requested by the
Author on 2026-09-07 for the first **Exclusive Compatible** proof. It is a
review draft based on the reported assembly and historical pin map, not a
verified as-built record or a qualified circuit. [HW-002](../../../docs/tasks/HW-002.md)
owns the discussion, unresolved details and subsequent work.

Open the [SVG drawing](schematic.svg), [printable A3 PDF](schematic.pdf), or
the [KiCad project](schematic.kicad_pro). The editable drawing is
[`schematic.kicad_sch`](schematic.kicad_sch).

## USB keyboard addition — 2026-09-09

The Author selected the tested direct USB keyboard connection as the Extender
input path. This section is the specification for that addition. The existing
KiCad drawing, connectivity model, exports and frozen profile still describe
the Port C harness without this USB connection; they do not yet represent the
complete current assembly. The drawing update is deferred under HW-002.

One USB keyboard plugs into the female-to-female USB-A adapter on the existing
male USB-A cable. The following numbers identify the cable's reversed
breadboard header, **not** the USB connector's contact numbering:

| Cable header pin | Signal | Olimex ESP32-P4-DevKit Rev D1 endpoint |
| ---: | --- | --- |
| 1 | GND | EXT2.18, GND |
| 2 | USB D+ (old cable label KCLK) | EXT2.19, USB_DP / silkscreen USB-P |
| 3 | USB D− (old cable label KDAT) | EXT2.20, USB_DN / silkscreen USB-N |
| 4 | USB VBUS, +5 V | EXT2.1, +5V |

These are USB data signals, not PS/2 clock/data. USB-P is D+, not a power
source. This uses the dedicated native host pair, not the other exposed
GPIO27/26 pair at EXT2.16/17. The board's USB Serial/JTAG programming connection
remains separate. The keyboard's power comes from the P4 DevKit's +5 V rail;
the Agon/P4 shared signal ground and existing UART wiring remain in use. The
Agon's 3.3 V Port C pull-ups and series resistors are not USB components.

The Author reported passing continuity, short and supply-voltage checks after
construction; corrected data wiring subsequently passed USB acquisition,
ordinary EMOS CLI and gameplay with a Perixx PERIBOARD-409. EXT2.1 supplies the
board's +5 V rail directly; this record does not identify a dedicated switched
or current-limited host VBUS circuit. Remaining supply/current and wider
electrical qualification belong to [PORT-015](../../../docs/tasks/PORT-015.md).

## Electrical definition of the existing drawing

[`connectivity.yaml`](connectivity.yaml) is the sole electrical authority **for
this draft**. The maintained KiCad drawing is its checked human projection.
The model includes 16 resistors and the three existing board headers. It
accounts for all 74 header contacts, including 55 intentional no-connects.
This authority does not establish acceptance of a replacement product design.

Each PC0–PC7 lane has one retained 220 Ω series resistor and one 15 kΩ pull-up
to **Agon 3.3 V**. The draft places the pull-up junction on the Agon side of
the series resistor. J1.34 supplies the pull-ups; neither P4 positive supply
pin is connected to that rail by the harness.

| Agon GPIO header | Series / pull-up | P4 header | P4 GPIO | Initial UART role |
| --- | --- | --- | --- | --- |
| J1.17 — PC0 / TXD1 | R1 / R9 | J3.11 — EXT2.11 | GPIO22 | P4 RX receives EMOS TX |
| J1.18 — PC1 / RXD1 | R2 / R10 | J2.13 — EXT1.13 | GPIO12 | P4 TX sends to EMOS RX |
| J1.19 — PC2 / RTS1 | R3 / R11 | J3.10 — EXT2.10 | GPIO23 | P4 CTS receives EMOS RTS |
| J1.20 — PC3 / CTS1 | R4 / R12 | J2.12 — EXT1.12 | GPIO11 | P4 RTS sends to EMOS CTS |
| J1.21 — PC4 | R5 / R13 | J3.9 — EXT2.9 | GPIO32 | Connected; P4 input, unused for UART |
| J1.22 — PC5 | R6 / R14 | J2.11 — EXT1.11 | GPIO10 | Connected; P4 input, unused for UART |
| J1.23 — PC6 | R7 / R15 | J3.8 — EXT2.8 | GPIO33 | Connected; P4 input, unused for UART |
| J1.24 — PC7 | R8 / R16 | J2.10 — EXT1.10 | GPIO9 | Connected; P4 input, unused for UART |

The drawing includes the required common ground from **J1.33 to EXT1.2
(J2.2)**. The Author subsequently confirmed that Agon and P4 grounds are tied
together; the exact fitted ground contacts have not been independently traced.
UART data directions have now passed the bounded test linked below. The
remaining roles and reset behavior still require their declared checks.

PD4/J1.13, PD5/J1.14 and PD7/J1.16 have no onward harness connection. The
Author reports that their ribbon-cable conductors terminate on isolated
breadboard rows. The former three 10 kΩ handshake-bias resistors are absent.
There are no tri-state buffers or parallel-handshake circuits in this draft.

Onboard VDP retains the existing board connection from VSync to eZ80 PB1,
using a known 60 Hz mode for the first proof. That board trace is described
in a drawing note; it is not an added harness wire. P4 frame timing remains
independent. Forward parallel transfer belongs to Exclusive Extended and
is outside this initial proof, although all eight Port C lanes remain wired.

## Reading and editing the drawing

Header symbols are grouped by function to give each connected lane a direct
wire path. **Every contact appears once and retains its physical pin number.**
J1A/J1B/J1C are units of the same Agon GPIO header; J2A/J2B are EXT1 and
J3A/J3B are EXT2. Their rectangles are schematic groupings, not a physical
header orientation or breadboard placement map. The `NC_n` names merely mark
contacts outside the harness scope, not manufacturer pin functions.

The right-hand units account for supply, ground and all remaining contacts.
An X means **no external harness wire**; it does not claim the contact has no
connection inside its board. `AGON_3V3` labels join only the Agon supply and
eight pull-ups; `GND` joins the two specified ground contacts.

The [local symbol library](Harness.kicad_sym) and `sym-lib-table` support
editing these header units in KiCad. The schematic also embeds the symbols.
Pin identities and the standard resistor symbol were borrowed from r02;
the custom units and layout are specific to this simpler circuit. The held
r02 files, construction records and tests remain unchanged.

The component count is eight 220 Ω resistors (R1–R8) and eight 15 kΩ resistors
(R9–R16), plus interfaces to the existing boards. Values reflect the Author's
report; fitted tolerance, power rating and package have not been recorded.
This is a component summary, not a frozen procurement specification.

## Review and evidence limits

The historical PC-to-P4 map, the actual pull-up junction placement and the
exact common-ground contacts require assembly confirmation under HW-002-Q001.
GPIO startup/reset states, unequal-power behavior, contention, target-rate
UART/flow control and lifecycle requirements remain under Q002/Q003. The
initial pinwalk supplies only the bounded observations linked below; it does
not authenticate the complete r03 assembly or qualify its electrical behavior.
The drawing does not establish Legacy electrical absence or Extended-mode
qualification. Existing task holds are unaffected.

The Author accepted committing this schematic checkpoint with the passed
eight-line pinwalk on 2026-09-07. The [profile](profile.yaml) freezes the model
and drawing inputs by hash. The electrical replacement remains a review
`draft`, not an accepted complete production design or qualified assembly.
No assembly profile or prior result is relabeled as r03.

The [initial pinwalk test sheet](tests/README.md) records the separately
prepared keyboard-free diagnostic and capture sequence. The first capture
contains all eight expected pulse counts and was accepted by the Author as a
passed pinwalk. The result record retains the shortened acquisition and its
original automated verdict separately.

The [acknowledged UART test](tests/PORT-010-2026-09-08-04-39-39Z/README.md)
subsequently passed both data directions at 115200/8N1 without flow control,
with EMOS success and prompt return confirmed by the Author. The preceding
no-reply case also returned to the prompt. These are bounded runtime results;
they do not complete the assembly review or qualify RTS/CTS and power/reset
behavior. The [test index](tests/README.md) holds the current evidence.

## Export and check

From the repository root, using KiCad CLI 7.0.11 and the project Python
environment:

```text
.venv/bin/python hardware/designs/light2-harness-r03/export_schematic.py --write
.venv/bin/python hardware/designs/light2-harness-r03/export_schematic.py
```

The first command checks the model with the existing electrical-model schema
validator, exports the maintained KiCad drawing, compares every component
reference/value and connected/no-connect endpoint partition, then writes the
[XML netlist](schematic.xml), SVG and PDF. The second also rejects stale
exports. Neither command changes drawing geometry or the model. Update the
model and drawing together for an authorized electrical revision.

Export metadata dates are normalized to the drawing date for reproducible
review artifacts; they are not build, capture or test timestamps. The SVG
has an explicit white background. The review exports omit KiCad's standard
page frame, retaining the drawing's visible title, revision and scope notes.
KiCad 7's CLI does not provide schematic ERC; these checks establish model
agreement, not driver-state correctness or electrical qualification.
