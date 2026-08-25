# SETUP-006.1.2 — Proposed object naming register

## Status and authority

The Author accepted this naming set at 2026-08-24 21:08 EDT. This register is
the task-local staging authority for one unique role-descriptive name per object
in the accepted SETUP-006.1.1 discovery inventory until those names are
promoted into a durable role-named hardware-object authority. It is not an
artifact registry, ERP import, part-number system, file-rename plan, or
authorization to change wiring.

The `I001` keys remain temporary links to the accepted discovery rows. Accepted
role names are lowercase slugs so exact uniqueness can be checked mechanically.
They are project terminology, not artifact IDs, revisioned identities, Odoo
record keys, or physical labels merely by virtue of acceptance.

## Naming rules used

1. Name the durable role, not a breadboard coordinate, wire color, experiment
   number, current desk location, or transient implementation.
2. Include endpoint identities when the endpoints define the role, such as a
   Pi-to-Agon reset attachment.
3. Keep a reusable assembly distinct from each way it can be attached.
4. Keep a group circuit distinct from its repeated channels and controls.
5. Preserve an approved artifact ID where one already exists; this register may
   give a more specific contained object a different role name.
6. Keep product wiring, bench automation, measurement fixtures, context
   equipment, and unrealized candidates in separate domains.
7. Treat legacy labels as searchable aliases, never competing canonical names.
8. Do not embed a revision, lifecycle status, specimen identity, or Odoo record
   key in a role name.

## Context hardware and endpoints

| Key | Proposed role name | Domain / class | Parent or boundary | Searchable aliases and notes |
|---|---|---|---|---|
| `I001` | `agon-light2-host` | Context / host assembly | Development bench | Agon Light 2, Light 2, main board, host. The manufacturer product name remains authoritative. |
| `I002` | `agon-onboard-vdp-endpoint` | Context / firmware-hardware endpoint | `agon-light2-host` | onboard VDP, stock VDP, Pico-D4, ESP32-PICO-D4. This endpoint is not an Extender-designed circuit. |
| `I003` | `extender-p4-development-board` | Context / development assembly | Development bench | P4 DevKit, Olimex board, EDP board, Olimex ESP32-P4-DevKit Rev D1. The product name and manufacturer revision remain authoritative. |
| `I004` | `extender-bench-control-host` | Bench / equipment | Development bench | Pi 5, Raspberry Pi 5, bench Pi, deployment host. Machine-specific identity remains local. |
| `I005` | `extender-bench-logic-analyzer` | Measurement / equipment | Development bench | logic sniffer, USB logic analyzer, Saleae-compatible analyzer. Machine-specific identity remains local. |

## Harness, carrier, and connector assemblies

| Key | Proposed role name | Domain / class | Parent or boundary | Searchable aliases and notes |
|---|---|---|---|---|
| `I010` | `light2-extender-solderless-assembly` | Product prototype / assembly | Light 2 Extender prototype | existing breadboard circuitry, current breadboard, r01 breadboard, `light2-harness-r01` implementation. This is an assembly instance, not the harness design lineage itself. |
| `I011` | `agon-expansion-interface-harness` | Product prototype / connector assembly | `light2-extender-solderless-assembly` | Agon expansion header, Agon-side harness, two ribbon harnesses, individual Agon wires. Exact construction remains unresolved. |
| `I012` | `p4-header-interface-harness` | Product prototype / connector assembly | `light2-extender-solderless-assembly` | P4 EXT1/EXT2 attachments, P4 header harness. Exact construction remains unresolved. |
| `I013` | `agon-to-p4-ext2-wire-bank` | Product prototype / wire bank | Interface harnesses | odd Agon row, board-right bank, EXT2 routing bank. The role names physical routing, not a logical byte lane. |
| `I014` | `agon-to-p4-ext1-wire-bank` | Product prototype / wire bank | Interface harnesses | even Agon row, board-left bank, EXT1 routing bank. The role names physical routing, not a logical byte lane. |
| `I015` | `light2-extender-carrier-assembly` | Proposed product / carrier assembly | Future Light 2 Extender hardware | carrier, carrier-breakout board, soldered perfboard, carrier PCB. No realization or revision is implied. |
| `I016` | `agon-carrier-interface-receptacle` | Proposed product / connector | `light2-extender-carrier-assembly` | Samtec receptacle, `SSW-117-02-T-D-RA`, Agon right-angle receptacle. Manufacturer part identity remains separate. |
| `I017` | `p4-carrier-socket-set` | Proposed product / connector set | `light2-extender-carrier-assembly` | P4 female headers, P4 sockets, removable DevKit headers. Exact product selection remains open. |
| `I018` | `carrier-test-access-field` | Proposed product / construction feature | `light2-extender-carrier-assembly` | test pads, analyzer landing area, ground test points, labeled pads. This is product test access, not the removable analyzer fixture. |

## Product-candidate signal and conditioning circuits

| Key | Proposed role name | Domain / class | Parent or boundary | Searchable aliases and notes |
|---|---|---|---|---|
| `I020` | `forward-parallel-data-circuit` | Product / circuit group | `light2-harness` | eight-bit forward bus, parallel D0..D7, forward data conductors. This is the physical data circuit, not the `forward-parallel-transport` protocol. |
| `I021` | `forward-parallel-direct-data-channels` | Product / repeated subcircuit group | `forward-parallel-data-circuit` | direct D2..D7 paths, six series-conditioned channels. Individual net names remain D2 through D7. |
| `I022` | `pc0-forward-buffer-channel` | Product / buffer subcircuit | `forward-parallel-data-circuit` | U1 channel 4, PC0/D0, forward UART receive path. The name describes physical direction and shared-pin ownership. |
| `I023` | `pc1-forward-buffer-channel` | Product / buffer subcircuit | `forward-parallel-data-circuit` | U1 channel 1, PC1/D1 forward path. |
| `I024` | `pc1-reverse-buffer-channel` | Product / buffer subcircuit | `light2-harness` | U1 channel 2, reverse UART, P4-to-Agon PC1 path. Inclusion in a wiring design does not select or qualify a protocol. |
| `I025` | `buffer-disabled-spare-channel` | Product / disabled subcircuit | Interface buffer U1 | U1 channel 3, spare channel, grounded disabled input. |
| `I026` | `forward-buffer-enable-circuit` | Product / ownership control | Interface buffer U1 | `FWD_OE_N`, GPIO15, U1 pins 1 and 13, forward enable. The net name remains `FWD_OE_N`. |
| `I027` | `reverse-buffer-enable-circuit` | Product / ownership control | Interface buffer U1 | `REV_OE_N`, GPIO21, U1 pin 4, reverse enable. The net name remains `REV_OE_N`. |
| `I028` | `forward-parallel-clock-circuit` | Product / timing path | `light2-harness` | CLOCK, PD5, GPIO14, clock path. The logical net remains `CLOCK`. |
| `I029` | `forward-parallel-valid-circuit` | Product / qualification path | `light2-harness` | VALID_N, PD7, GPIO13, record-valid path. The logical net remains `VALID_N`. |
| `I030` | `forward-parallel-ready-circuit` | Product / admission path | `light2-harness` | READY_N, PD4, GPIO20, admission path. The logical net remains `READY_N`. |
| `I031` | `interface-buffer-supply-decoupling` | Product / IC support circuit | Interface buffer U1 | U1 power and decoupling, pin-14 supply, pin-7 ground, 100 nF bypass. |
| `I032` | `agon-logic-reference-circuit` | Product / reference and bias circuit | `light2-harness` | Agon pin 34, 3.3 V reference, U1/bias rail. This is a logic reference, not a P4 power source. |
| `I033` | `agon-p4-signal-reference` | Product / signal-reference connection | `light2-harness` | common signal ground, Agon pin 33, P4 EXT1 pin 2. This is not a general power-rail union. |
| `I034` | `p4-usb-host-connection` | Bench-support / power and diagnostics path | P4 development setup | P4 USB Serial/JTAG, VBUS power, flash cable, diagnostic connection. Product power architecture remains separate. |
| `I035` | `independent-power-domain-boundary` | Product / electrical boundary | Agon and P4 power domains | separated rails, no joined 3.3 V outputs, back-power boundary. This is a design constraint represented by circuitry still to be selected. |

## Measurement and bench-support objects

| Key | Proposed role name | Domain / class | Parent or boundary | Searchable aliases and notes |
|---|---|---|---|---|
| `I040` | `transport-logic-analyzer-harness` | Measurement / fixture assembly | Development bench | logic-analyzer harness, analyzer leads, probe harness. This is the reusable lead assembly, not an endpoint map. |
| `I041` | `analyzer-even-data-ribbon` | Measurement / lead subassembly | `transport-logic-analyzer-harness` | even analyzer ribbon, D0/D2/D4/D6 ribbon. Colors remain channel attributes, not names. |
| `I042` | `analyzer-odd-data-ribbon` | Measurement / lead subassembly | `transport-logic-analyzer-harness` | odd analyzer ribbon, D1/D3/D5/D7 ribbon. Colors remain channel attributes, not names. |
| `I043` | `p4-transport-probe-attachment` | Measurement / attachment profile | `la03-p4-probe-fixture` | LA-03 P4 probe map, P4 endpoint assignment. `la03-p4-probe-fixture` remains the approved artifact lineage. |
| `I044` | `analyzer-signal-reference-lead` | Measurement / reference path | `transport-logic-analyzer-harness` | analyzer ground, qualified black ground lead, analyzer reference. This is separate from product signal ground even when attached to it. |
| `I045` | `reusable-open-collector-reset-module` | Bench / support module | Development bench | reset breakout, reset-actuator module, movable 2N2222 module. The module is distinct from every endpoint attachment. |
| `I046` | `gpio-reset-pulldown-circuit` | Bench / reset subcircuit | `reusable-open-collector-reset-module` | 2N2222 reset circuit, transistor and passive wiring, open-collector reset actuator. Present assembly is probably nonconforming. |
| `I047` | `pi-reset-control-lead-set` | Bench / control lead set | `reusable-open-collector-reset-module` | A-side leads, Pi header attachment, GPIO17/GND pair. The Pi 5 is the controller; the selected reset endpoint is separate. |
| `I048` | `pi5-agon-reset-attachment` | Bench / current attachment | `reusable-open-collector-reset-module` | Pi-to-Agon reset, unattended Agon reset, current visible black/white output pair. Exact Agon reset pin remains unresolved. |
| `I049` | `pi5-p4-reset-attachment` | Bench / alternate attachment | `reusable-open-collector-reset-module` | Pi-to-P4 reset, P4 ESP_EN actuator, legacy B1/B2 assignment. It is legacy-evidenced, not current. |
| `I050` | `p4-agon-reset-attachment` | Proposed product / reset path | Future Extender hardware | P4-to-Agon reset, Agon reset-actuator control. This was never built and is not a selected v1 capability. |

## Logical and physical separation

The following logical objects intentionally do not receive `I` rows or names
as physical circuits. They either retain an existing project identity or remain
an unresolved protocol contract.

| Logical object | Existing or provisional name | Physical realization in this inventory | Boundary |
|---|---|---|---|
| eZ80-to-EDP byte protocol | `forward-parallel-transport` | `I020`, `I028`, `I029`, and `I030` | Existing draft protocol artifact; not a harness or wire bank. |
| Official VDP-compatible UART contract | official VDP UART transport | Requires a selected and qualified PC0/PC1 physical design | Exclusive Compatible must reproduce the stock wire contract; current r01 circuitry is only a design input. |
| Enhanced EDP return contract | enhanced return UART, final name unresolved | Candidate physical use of `I024` plus ownership controls | Exclusive Extended protocol capabilities remain a PORT-008 decision. |
| Operating selections | Legacy, Exclusive Compatible, Exclusive Extended, Dual | Select actors, routes, and eligible circuits | Modes are architecture states, never physical objects. |
| Data and control nets | D0..D7, CLOCK, VALID_N, READY_N | Carried by `I020`-`I030` as applicable | Net identities remain concise electrical labels; circuit role names do not replace them. |
| Buffer ownership nets | FWD_OE_N, REV_OE_N | Controlled by `I026` and `I027` | Net identities are distinct from the pull-up and fan-out circuits carrying them. |
| EMOS route and mode ownership | EMOS normative behavior | Uses selected transports and hardware but is not circuitry | EMOS authorizes routes; P4 firmware drives only P4-owned pins under that contract. |

## Review findings

1. All 41 accepted discovery rows have one proposed role name.
2. Proposed role names are unique within this register.
3. Approved artifact IDs `light2-harness`, `forward-parallel-transport`, and
   `la03-p4-probe-fixture` are preserved rather than silently renamed.
4. The reset module, its transistor circuit, its Pi control leads, two realized
   or documented bench attachments, and the never-realized product candidate
   are separately named.
5. The current register deliberately leaves enhanced-return protocol naming,
   exact current breadboard partition, exact connector construction, and the
   Agon reset endpoint unresolved; a role name does not fabricate those facts.

## Accepted disposition

Acceptance permits a later explicit work item to promote these role names into
a durable structured hardware-object authority and prepare corresponding file
and diagram changes. It does not itself approve an artifact revision, physical
wiring change, profile change, ERP synchronization, or hardware test.
