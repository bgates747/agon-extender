# Light 2 Extender solderless assembly r02

`light2-extender-solderless-assembly-r02` is the second prototype breadboard
configuration and the initial physical construction target for
`light2-harness-r02`.

Its electrical design is frozen, but its exact breadboard coordinates,
conductor routes, connector construction, and as-built inspection record are
still under development. The assembly therefore remains `draft` even though
its selected electrical design is a frozen `candidate`.

Construction may proceed against the frozen
`hardware/designs/light2-harness-r02/connectivity.yaml` electrical authority
and its checked `bom.yaml`. As construction choices are made, exact breadboard,
wire, socket, connector, and test-access materials belong in this assembly's
future construction authority rather than being inferred into the design BOM.

The maintained r02 `schematic.kicad_sch` is the authoritative human circuit
construction drawing, checked against `connectivity.yaml`. Its ordered
[`signal views`](../../designs/light2-harness-r02/signal-views/README.md)
guide incremental installation and checks. HW-001 and QUAL-002 record each
cumulative installed subset, including actual terminal/contact mappings and
omissions, under the
[staged validation process](../../../docs/qualification/staged-circuit-validation.md).

The profile's `construction_authority: null` describes the unfinished exact
whole-assembly record; it does not mean that the circuit or its construction
drawings lack authority. Bounded stages may proceed with sufficient reviewed
as-built records and their applicable procedures. Construction progress does
not change this assembly's draft status or authorize a powered operation.
