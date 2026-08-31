# Light 2 harness r02

`light2-harness-r02` is the frozen candidate electrical design for the second
Light 2 Extender solderless prototype. It combines one common four-signal UART
circuit for Exclusive Compatible and Exclusive Extended with the one-way
eight-bit forward-parallel transport used by Exclusive Extended.

The placement-independent [`connectivity.yaml`](connectivity.yaml) is the sole
electrical authority. It fixes every component instance, component value,
terminal, net, intentional no-connect, pin assignment, power domain, bias, and
series element. [`schematic.kicad_sch`](schematic.kicad_sch) is the maintained
authoritative human electrical drawing. Its checked
[`schematic.xml`](schematic.xml) and explicit-white
[`schematic.svg`](schematic.svg) projections make that drawing machine- and
human-reviewable. The schematic remains a checked projection; its geometry
does not override the connectivity model.

The Author accepted the maintained schematic on 2026-08-30 after manually
arranging the complete circuit and clarifying each local bypass-capacitor
assignment. KiCad's exported endpoint partition exactly matches every r02 net
and intentional no-connect. Regenerate and validate the maintained projections
from the repository root with:

```text
.venv/bin/python \
  hardware/designs/light2-harness-r02/generate_schematic_views.py --write
.venv/bin/python \
  hardware/designs/light2-harness-r02/generate_schematic_views.py
```

The first command deliberately replaces the checked XML and SVG after exact
topology validation. The second fails if either generated view is stale, if
the schematic changes connectivity, or if intentional no-connects differ.

## Identity and lineage

1. Artifact ID: `light2-harness`.
2. Revision: `light2-harness-r02`.
3. Variant: `light2`.
4. Lifecycle status: `candidate`.
5. Predecessor: `light2-harness-r01`, retained unchanged as the design used by
   the preserved first forward-transport prototype.
6. Initial construction target:
   `light2-extender-solderless-assembly-r02`.

The matching `r02` suffixes do not imply compatibility by themselves. The
assembly profile explicitly selects this harness revision.

## Bill of materials

The checked design BOM has three representations:

1. [`bom.yaml`](bom.yaml) is the maintained procurement input for one circuit
   build. It groups references by interchangeable purchasing specification and
   records exact IC identities, passive requirements, packages, and scope.
2. [`BOM.md`](BOM.md) is the generated human-readable view.
3. [`bom.csv`](bom.csv) is the generated flat import view for inventory or ERP
   field mapping.

The design BOM covers all 41 fitted circuit components. J1--J3 are accounted
for as interfaces to one supplied Agon Light 2 and one supplied Olimex
ESP32-P4-DevKit rather than as three independently purchased parts. Breadboard,
wire, sockets, physical connector construction, and test-access hardware remain
excluded until the r02 assembly map fixes their exact form and quantity.

The Author froze this BOM on 2026-08-29 as the controlled component-selection
input for constructing `light2-extender-solderless-assembly-r02`. Changes to a
fitted reference, quantity, nominal value, part-number requirement, package, or
procurement constraint require normal r02 change control. Inventory status,
supplier choice for generic passives, and order quantities above the required
build quantity do not alter the design BOM.

`connectivity.yaml` remains authoritative for component references, nominal
values, and electrical topology. The BOM adds procurement constraints and must
agree mechanically with that authority. Regenerate or check its views with:

```text
.venv/bin/python \
  hardware/designs/light2-harness-r02/generate_bom.py --write
.venv/bin/python \
  hardware/designs/light2-harness-r02/generate_bom.py
```

## Frozen candidate scope

The revision fixes:

1. two Agon-powered `SN74LVC244AN` forward buffers;
2. one Agon-powered `SN74LV125AN` UART-return buffer;
3. one P4-powered `SN74LV125AN` implementing four isolated low-only controls;
4. separate `AGON_3V3` and `P4_3V3` domains with common signal ground;
5. the accepted Agon and P4 pin allocation;
6. 220-ohm series resistance on all thirteen driven transport outputs;
7. all pull-up, pull-down, bypass, and bulk-capacitor values represented in the
   connectivity authority; and
8. the fail-safe released driver defaults represented by that topology.

## Known unqualified boundaries

Candidate status does not claim that the circuit is electrically qualified.
The following remain open work:

1. eZ80-only reset recovery while the P4 remains active;
2. the final V1 requirement for Legacy electrical absence;
3. UART operation at 1,152,000 baud and complete RTS/CTS behavior;
4. the EMOS/eZ80 and EDP/P4 break-before-make epoch protocol;
5. continuity, passive, either-order-power, contention, reset, fault, and
   recovery qualification; and
6. an exact breadboard construction map for the r02 assembly target.

Construction is permitted only as a controlled prototype under the applicable
bench and qualification procedures. These open boundaries cannot be cited as
passed merely because the connectivity is frozen.

## Revision control

Formatting, spelling, colors, page layout, line routing, and explanatory
clarifications may be corrected without changing r02 only when they cannot
change construction, interpretation, electrical behavior, or test results.

Any change to connectivity, pin assignment, component or fitted value, control
polarity, pull state, power domain, protection, intended electrical behavior,
or physically significant routing requires Author approval and a new
`light2-harness` revision. When in doubt, advance the revision. Never rewrite
r02 after it has been used as a committed qualification input.

Regenerate or verify the exact authority from the repository root with:

```text
.venv/bin/python \
  docs/tasks/HW-001/v1-draft-schematic/generate_draft_inputs.py --check
```

`--write-authority` exists only to materialize this already approved revision.
It must not be used to revise r02 in place.
