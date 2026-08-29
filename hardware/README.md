# Hardware designs

Tracked hardware profiles, wiring definitions, and design evidence live here.
Every controlled design follows the identity and revision rules in
[`docs/versions/README.md`](../docs/versions/README.md).

The durable role vocabulary for hardware objects is maintained under
[`objects/`](objects/README.md). It owns names, classes, aliases, and containment
only. Pins, nets, components, and electrical connectivity remain authoritative
inside the applicable revisioned design or fixture profile.

The frozen current design target is
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

The current logic-analyzer attachment target is
[`la03-p4-probe-fixture-r01`](fixtures/la03-p4-probe-fixture-r01/README.md).
Its green D0 endpoint was physically verified as GPIO32 / EXT2 pin 9; the
contradictory legacy pin-10 label is retained only as provenance.

Machine-local specimen identities, bench topology, and current connection
status remain in the ignored `HARDWARE.local.md`, not this directory.
