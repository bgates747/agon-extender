# Hardware designs

Tracked hardware profiles, wiring definitions, and design evidence live here.
Every controlled design follows the identity and revision rules in
[`docs/versions/README.md`](../docs/versions/README.md).

The durable role vocabulary for hardware objects is maintained under
[`objects/`](objects/README.md). It owns names, classes, aliases, and containment
only. Pins, nets, components, and electrical connectivity remain authoritative
inside the applicable revisioned design or fixture profile.

The active bench arrangement uses the simplified
[`light2-harness-r03`](designs/light2-harness-r03/README.md) UART wiring and
P4 USB keyboard connection. Its eight direct Port C lanes have 220 Ω series
resistors and 15 kΩ pull-ups to Agon 3.3 V. Bounded UART, keyboard and ExCom
results are recorded under [PORT-008](../docs/tasks/PORT-008.md),
[PORT-015](../docs/tasks/PORT-015.md) and the linked qualification records.
Those results do not complete circuit qualification. The KiCad draft does not
yet include the accepted USB connection, and full as-built/power/reset review
remains with [HW-002](../docs/tasks/HW-002.md). Do not infer the buffered r02
isolation guarantees from the direct r03 wiring.

The held frozen candidate is
[`light2-harness-r02`](designs/light2-harness-r02/README.md). Its
placement-independent connectivity YAML is the electrical authority. The
revision also provides a checked design BOM in maintained YAML plus generated
Markdown and flat CSV views. The
predecessor [`light2-harness-r01`](designs/light2-harness-r01/README.md)
remains unchanged for the preserved first forward-transport prototype and its
evidence.

Revisioned physical breadboard configurations live under
[`assemblies/`](assemblies/README.md). The preserved first prototype is
`light2-extender-solderless-assembly-r01`; the new r02 electrical design is
assigned to `light2-extender-solderless-assembly-r02`, whose exact construction
map remains unfinished.

The accepted r02 physical schematic provides the circuit basis; the separate
[`wiring order`](designs/light2-harness-r02/wiring-order/README.md) plans powered
incremental construction in a now-superseded draft. The resistor-addition
proposal was rejected. The r02 design, construction, and testing remain
on hold as of 2026-09-07: full wiring is incomplete and the complete circuit
is untested. Signal views remain tracing/debugging references.
HW-001 and QUAL-002 record the actual installed
subset at each step under
[staged circuit validation](../docs/qualification/staged-circuit-validation.md).
The unfinished complete assembly map is not a lack of circuit authority or a
requirement to finish the entire build before checking a bounded stage.

The retained predecessor logic-analyzer attachment reference is
[`la03-p4-probe-fixture-r01`](fixtures/la03-p4-probe-fixture-r01/README.md).
Its green D0 endpoint was physically verified as GPIO32 / EXT2 pin 9; the
contradictory legacy pin-10 label is retained only as provenance.
Each r02 stage selects and verifies its own relevant measurement attachment;
the predecessor map is not automatically the probe map for that stage.

Machine-local specimen identities, bench topology, and current connection
status remain in the ignored `HARDWARE.local.md`, not this directory.
