# SETUP-006.1.1 — Object inventory

## Purpose and authority

This is the discovery inventory required before SETUP-006 assigns durable
names to Extender circuits and physical subassemblies. It enumerates objects
represented by the current tracked target, current bench record, and bounded
legacy sources without deciding their final names or permanent file structure.

`I001`-style keys are temporary task-local row identifiers. They are neither
part numbers nor proposed names and must not escape into hardware labels,
profiles, filenames, Odoo records, or user documentation.

## Evidence-state vocabulary

1. **Present-confirmed** — the current local bench record or a current-project
   run confirms that the object is attached or present within the stated
   boundary.
2. **Target-defined** — the tracked r01 target defines the object, but the
   current bench record does not independently prove its complete physical
   realization or attachment.
3. **Legacy-evidenced** — predecessor documentation or runs describe and may
   have exercised the object; current-project adoption or presence is not
   implied.
4. **Proposed-only** — documentation describes a future carrier, connector,
   test point, component population, or production provision not known to have
   been built.
5. **Unresolved** — available sources do not establish whether the object is a
   separate physical assembly, which variant is installed, or whether it is
   presently attached.

## Observed containment

```text
Light 2 / Extender development bench
├── Agon Light 2 host (presently disconnected from Extender)
│   ├── onboard VDP endpoint
│   └── expansion-header side of the target harness
├── Olimex ESP32-P4-DevKit
│   ├── EXT1/EXT2 side of the target harness
│   └── USB Serial/JTAG power, flash, and diagnostic connection
├── r01 solderless-breadboard implementation
│   ├── forward eight-bit data paths
│   ├── forward control and P4 admission paths
│   ├── shared-PC0/PC1 U1 buffer paths
│   └── signal-ground, logic-reference, and separated-power boundaries
├── removable logic-analyzer fixture
│   ├── fixed channel/color lead harness
│   ├── LA-03 endpoint assignment
│   └── qualified analyzer-ground lead
└── separately documented support or proposed assemblies
    ├── Pi-5-controlled Agon reset-actuator module (electrically unresolved)
    └── prospective soldered carrier/breakout board (not built as authority)
```

The tree records containment concepts only. It does not claim that every
functional branch occupies its own physical breadboard.

## Context hardware and endpoint inventory

These objects participate in or constrain the wiring target but are not all
project-designed circuits.

| Key | Class | Source labels or descriptions | Evidence state | Inventory finding |
|---|---|---|---|---|
| `I001` | Host assembly | Agon Light 2 | Present-confirmed, disconnected | Main-board endpoint for the future assembled test; current bench record says it is not attached to the powered P4 harness. |
| `I002` | Host component/endpoint | onboard VDP, stock VDP, ESP32-PICO-D4 | Target-defined | Existing main-board display/input endpoint. No direct VDP-to-EDP product wiring is selected for v1. |
| `I003` | Extender development assembly | Olimex ESP32-P4-DevKit Rev D1 | Present-confirmed | Current EDP development board, powered and flashed through its own USB Serial/JTAG connection. |
| `I004` | Bench host/equipment | Raspberry Pi 5, bench Pi | Present-confirmed | Hosts P4 USB Serial/JTAG and the logic analyzer. It is operational equipment, not product circuitry. |
| `I005` | Measurement equipment | eight-channel Saleae-compatible USB logic analyzer | Present-confirmed | Measurement device attached to the Pi and to the removable probe fixture. It is not part of the product harness. |

## Physical harness and carrier inventory

| Key | Class | Source labels or descriptions | Evidence state | Inventory finding |
|---|---|---|---|---|
| `I010` | Prototype assembly | existing breadboard circuitry, current breadboard, `light2-harness-r01` breadboard | Present-confirmed as an aggregate; physical partition unresolved | Current run records identify the attached breadboard and harness as r01. They do not record the number, manufacturer, dimensions, coordinates, or division of functions among solderless breadboards. |
| `I011` | Host connector assembly | Agon expansion header, two physical ribbon harnesses, individual breadboard wires | Target-defined; exact live implementation unresolved | Connects Agon GPIO/header pins to the prototype. Sources disagree in abstraction: the SVG prose describes two physical ribbon banks while the provisional overlay uses individual wires. Exact current connector and cable construction is not recorded. |
| `I012` | Extender connector assembly | P4 EXT1 and EXT2 header attachments | Present-confirmed as part of attached r01; detailed construction unresolved | Terminates product and fixture wiring at the two P4 headers. Header side and pin orientation are defined; socket, jumper, and strain-relief construction are not. |
| `I013` | Wire bank | odd-numbered Agon row to board-right P4 EXT2 | Target-defined | Physical routing bank carrying `PC0`, `PC2`, `PC4`, `PC6`, and `PD4/READY_N` toward EXT2. |
| `I014` | Wire bank | even-numbered Agon row to board-left P4 EXT1 | Target-defined | Physical routing bank carrying `PC1`, `PC3`, `PC5`, `PC7`, `PD5/CLOCK`, and `PD7/VALID_N` toward EXT1. |
| `I015` | Proposed assembly | carrier, carrier-breakout board, first soldered perfboard implementation | Proposed-only | Prospective replacement for the solderless implementation. Its legacy drawing is a layout concept, not evidence of a built board or current construction authority. |
| `I016` | Proposed connector | Samtec `SSW-117-02-T-D-RA` 34-position right-angle receptacle | Proposed-only | Intended Agon-to-carrier connector; dry-fit, board thickness, orientation, and production selection remain unqualified. |
| `I017` | Proposed connector set | removable female P4 headers/sockets | Proposed-only | Intended to mount the P4 without soldering it permanently to a future carrier. Exact parts and installed height are not frozen. |
| `I018` | Proposed construction feature | labeled test pads, analyzer landing area, ground test points | Proposed-only | Carrier provisions for signals, enables, voltage/reference nodes, reset, and measurement. No physical test-point design is current authority. |

## Product-candidate signal and conditioning circuits

The rows below identify physically distinct paths or conditioning functions.
Logical protocols and operating modes are not assigned durable physical-object
names here.

| Key | Class | Source labels or descriptions | Evidence state | Inventory finding |
|---|---|---|---|---|
| `I020` | Circuit group | eight-bit forward bus, parallel `D0..D7`, forward data conductors | Target-defined; legacy-evidenced | Eight Agon-to-P4 data paths. `D0` and `D1` traverse U1 buffer channels in the latest circuit; `D2..D7` use direct series-conditioned paths. |
| `I021` | Repeated subcircuit group | direct `D2..D7` data paths | Target-defined; legacy-evidenced | Six separate Agon-to-P4 conductors, each with its own 220-ohm series resistor. They are one repeated design pattern but six physical channels. |
| `I022` | Buffer subcircuit | U1 channel 4, `PC0/D0`, forward UART receive | Target-defined; legacy-evidenced | Agon pin 17/`PC0` enters U1 pin 12; U1 pin 11 drives P4 GPIO22 through its own 220-ohm resistor when `FWD_OE_N` enables the channel. |
| `I023` | Buffer subcircuit | U1 channel 1, `PC1/D1`, forward path | Target-defined; legacy-evidenced | Agon pin 18/`PC1` enters U1 pin 2; U1 pin 3 drives P4 GPIO12 through its own 220-ohm resistor when `FWD_OE_N` enables the channel. |
| `I024` | Buffer subcircuit | U1 channel 2, reverse UART, P4-to-Agon `PC1` path | Target-defined; legacy-evidenced at 115,200 baud | P4 GPIO12 enters U1 pin 5; U1 pin 6 drives Agon pin 18/`PC1` through a separate 220-ohm resistor when `REV_OE_N` enables the channel. This is part of the Exclusive Extended split-link target, not Exclusive Compatible stock-UART hardware. |
| `I025` | Disabled spare subcircuit | U1 channel 3 | Target-defined | U1 pin 9 input is grounded, pin 10 enable is pulled High, and pin 8 output is unconnected except for a proposed labeled test pad. |
| `I026` | Ownership-control subcircuit | `FWD_OE_N`, GPIO15, U1 pins 1 and 13 | Target-defined; legacy-evidenced | One active-Low P4-controlled net enables both Agon-to-P4 U1 channels. A 10-kilohm hardware pull-up holds them disabled while control is absent. |
| `I027` | Ownership-control subcircuit | `REV_OE_N`, GPIO21, U1 pin 4 | Target-defined; legacy-evidenced | Active-Low P4 control for the P4-to-Agon U1 channel. A 10-kilohm hardware pull-up holds it disabled while control is absent. Both ownership controls Low simultaneously is forbidden. |
| `I028` | Timing/control path | `CLOCK`, `PD5`, GPIO14 | Target-defined; legacy-evidenced | Direct Agon-to-P4 clock path with a 10-kilohm pull-down defining idle/reset state. |
| `I029` | Qualification/control path | `VALID_N`, `PD7`, GPIO13 | Target-defined; legacy-evidenced | Direct active-Low Agon-to-P4 record-valid path with a 10-kilohm pull-up. |
| `I030` | Admission/control path | `READY_N`, `PD4`, GPIO20 | Target-defined; legacy-evidenced | P4-to-Agon active-Low admission path, specified as open drain with a 10-kilohm pull-up. It presently lacks a separately inventoried external output-isolation component. |
| `I031` | IC support subcircuit | U1 power and decoupling | Target-defined; legacy-evidenced | U1 pin 14 uses Agon 3.3 V, pin 7 uses common signal ground, and a 100 nF capacitor is specified immediately across the supply. Current physical capacitor placement is not independently recorded. |
| `I032` | Logic-reference/bias circuit | Agon pin 34, 3.3 V reference, U1/bias rail | Target-defined | Supplies U1 and state-defining pulls in the documented circuit. It is not permission to power the P4 or join independently powered 3.3 V outputs. |
| `I033` | Signal-reference connection | common signal ground, Agon pin 33, P4 EXT1 pin 2 | Target-defined; legacy-evidenced | Required shared signal reference between endpoints. Exact current rail topology and number of ground jumpers are not recorded. |
| `I034` | Independent power path | P4 USB Serial/JTAG/VBUS power connection | Present-confirmed | Powers the P4 independently from the Pi-side USB connection and also carries flash/diagnostic traffic. It is not a product power source selected for the final carrier. |
| `I035` | Electrical boundary | independently powered rail separation | Target-defined, unqualified | Constraint that Agon and P4 power outputs must not be joined. Production isolation, back-power protection, and either-order power behavior are not yet implemented or qualified as a complete design. |

## Measurement and bench-support inventory

| Key | Class | Source labels or descriptions | Evidence state | Inventory finding |
|---|---|---|---|---|
| `I040` | Measurement fixture assembly | USB logic-analyzer harness, analyzer leads | Present-confirmed | Reusable eight-channel lead set plus ground. It remains separate from product wiring even while attached. |
| `I041` | Measurement subassembly | even analyzer ribbon, channels `D0,D2,D4,D6` | Present-confirmed | One fixed color/channel ribbon whose measured endpoints are assigned by a fixture or run. |
| `I042` | Measurement subassembly | odd analyzer ribbon, channels `D1,D3,D5,D7` | Present-confirmed | Second fixed color/channel ribbon whose measured endpoints are assigned by a fixture or run. |
| `I043` | Measurement attachment profile | LA-03 P4 probe map | Present-confirmed as an aggregate; mixed per-lead evidence | Maps analyzer leads to P4 data, control, and U1-enable endpoints. Green D0/GPIO32 was physically verified; other leads retain the evidence states recorded by the fixture profile. |
| `I044` | Measurement reference path | qualified black analyzer ground lead/position | Present-confirmed | Dedicated analyzer-ground attachment. Legacy evidence warns that the alternate nominal ground position did not behave equivalently. |
| `I045` | Support module | reusable 2N2222 reset-actuator module | Present-confirmed; electrical conformance unresolved | The photographed breakout is configured for Pi-5-controlled Agon reset during unattended bench work. It is absent from the current tracked harness and fixture profiles. Legacy text documents an alternate Pi-to-P4 use of the same actuator topology, not this endpoint assignment. |
| `I046` | Reset subcircuit | 2N2222 and associated passive wiring | Present-confirmed; probable nonconformance | The shared intended topology is GPIO17 through 10 kOhm to base, emitter to common endpoint ground, and collector to the active-Low reset net. The supplied photograph shows the recorded left/emitter lead one internally separate terminal strip to the right of the reported ground strip, with no visible bridge. The lower resistor appears to pull the base to ground without grounding the emitter. This is a probable assembly omission pending component identification and continuity testing. |
| `I047` | Terminal/header breakout | legacy labels `A1..A5` and `B1..B5`; present Pi-header attachment | Present-confirmed; endpoint terminations unresolved | In the reported Pi orientation, the black upper wire at the fifth left-column position occupies physical pin 9/GND and the white lower wire at the sixth occupies physical pin 11/GPIO17, matching both the intended Pi positions and expected ground/control color roles. White is a switched 3.3 V GPIO control through the base resistor, not a supply rail. The removed Pi leads' former module positions are now described, but continuity remains unverified. |
| `I048` | Bench reset attachment | Pi-5-controlled Agon reset path | Present-confirmed; exact Agon endpoint unresolved | The visible black and white pair goes to the Agon and was intended to let unattended agents reset it. Black is reported as endpoint ground; the exact Agon connector and reset pin used by white have not yet been recovered. This is bench automation, not an Extender product capability. |
| `I049` | Alternate bench reset attachment | Pi-5-controlled P4 `ESP_EN` path | Legacy-evidenced; not current | The surviving legacy text maps the same actuator topology to P4 EXT2 pin 14/`ESP_EN` and EXT2 pin 15/GND. Its missing SVG and weak reset evidence prevent treating it as a qualified current assembly. |
| `I050` | Product-candidate reset path | P4-controlled Agon reset actuator | Proposed-only; explicitly never realized | A P4-to-Agon reset path was contemplated but not built because safe VDP/MOS-compliant reverse communication was never established on the P4. Whether Extender should ever own this capability is unresolved and must not be inferred from `I048`. |

## Components and alternatives that are not separate circuits

1. The documented current bench population is an on-hand `SN74HC125N` U1.
   A purchased pin-compatible `SN74LV125AN` is an intended partial-power-down-
   safe replacement, but changing the installed component affects electrical
   behavior and requires revision and qualification. These are population
   alternatives for one circuit, not two circuit identities.
2. The individual 220-ohm and 10-kilohm resistors and the 100 nF bypass
   capacitor will eventually require component/BOM identities. At this
   discovery level, repeated passives are recorded as parts of their owning
   subcircuits rather than promoted into independently named circuits.
3. The Agon Light 2, onboard VDP silicon, P4 DevKit, Pi, and analyzer require
   equipment/product identities for configuration and inventory purposes, but
   their manufacturer-internal circuits are outside this wiring design.

## Logical objects deliberately not classified as physical circuits

1. The forward parallel transport protocol and its VDU byte stream are logical
   contracts carried by `I020` and control paths `I028`-`I030`.
2. The return UART packet protocol is a logical contract carried physically by
   `I024` during the selected ownership epoch.
3. Legacy, Exclusive Compatible, Exclusive Extended, and Dual are operating
   modes, not wires or circuit assemblies.
4. `D0..D7`, `CLOCK`, `VALID_N`, `READY_N`, `FWD_OE_N`, and `REV_OE_N` are
   signal/net identities. Their physical paths and conditioning circuits are
   separate inventory objects above.
5. Firmware pin configuration, open-drain selection, break-before-make timing,
   and EMOS route ownership are behavioral requirements, not additional
   physical subcircuits.

## Source-only and current-state gaps exposed by the inventory

1. The number, type, dimensions, and functional partition of the currently
   attached solderless breadboards are not recorded. The legacy shopping list
   names BusBoard `BB1460` boards but does not prove that either purchased unit
   is the board currently on the bench.
2. The exact current Agon-side connector and “two physical ribbon harnesses”
   construction is not documented well enough to reproduce. The current bench
   has the Agon disconnected, so its detached state cannot resolve this.
3. Current tracked records do not independently verify whether U1 is the HC or
   LV part, the exact placement of every resistor/capacitor, or the complete
   live continuity map.
4. The reset breakout is now operator-confirmed as a Pi-5-to-Agon bench-reset
   configuration, but it is not included in `light2-harness-r01`,
   `la03-p4-probe-fixture-r01`, or the latest run manifest. Its two observed Pi
   positions agree with pin-9 GND and pin-11/GPIO17 intent, but breakout-side
   terminations and continuity are unverified. The photograph indicates that
   the intended emitter is one terminal strip away from ground with no visible
   bridge, while the base pull-down does reach ground. The module is held from
   use pending a dedicated unpowered inspection.
5. The reset-module SVG cited by two legacy Markdown files never existed in any
   recovered Git tree or SVG blob. Its surviving text documents a different
   Pi-to-P4 `ESP_EN` configuration, not the photographed Pi-to-Agon wiring.
6. A contemplated P4-to-Agon reset path was never realized. Whether that should
   become an Extender capability is an open product decision rather than a gap
   to silently fill during reconstruction.
7. The prospective carrier drawing and Samtec/P4 socket design must not be
   mistaken for an as-built assembly.
8. The tracked r01 README/profile still contain the stale
   `legacy_uart_candidate` interpretation. Accepted current architecture limits
   this physical circuit to Exclusive Extended split-link work; naming and
   later profile remediation must preserve that boundary.
9. `READY_N` is documented as a direct P4 open-drain path. The inventory found
   no separate hardware driver-disable or isolation component for that output;
   QUAL-002 and the firmware-driven electrical design review must disposition
   this rather than SETUP-006.1 silently adding circuitry.

The exact 2026-08-24 operator observation and its non-inference boundary are
preserved in
[`SETUP-006.1.1-reset-breakout-observation.md`](SETUP-006.1.1-reset-breakout-observation.md).

## SETUP-006.1.1 disposition

The inventory is complete against the bounded sources listed in SETUP-006.
Completeness means that every distinct represented object or unresolved
physical partition has a row; it does not mean the live bench has been opened,
traced, measured, or qualified. No descriptive name, file rename, profile
change, harness revision, Odoo identity, or physical action is authorized by
this inventory.
