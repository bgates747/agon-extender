# Light 2 Extender solderless assembly r02

**On hold — incomplete (Author direction, 2026-09-07).** The present
hardware design, construction, and testing are paused pending review of stock
MOS/VDP communications and interface requirements. Full wiring of the r02
circuit as drawn is incomplete, and the complete circuit has not been tested.
The September 4 power-domain observations retain only their recorded scope.
The frozen candidate identity preserves the design checkpoint; it does not
claim design completion, complete assembly, or qualification. Earlier stage
instructions below are retained references and do not authorize further work.

`light2-extender-solderless-assembly-r02` is the second prototype breadboard
configuration and the initial physical construction target for
`light2-harness-r02`.

Its electrical design is frozen, but its exact breadboard coordinates,
conductor routes, connector construction, and as-built inspection record are
still under development. The assembly therefore remains `draft` even though
its selected electrical design is a frozen `candidate`.

The suspended construction basis is the frozen
`hardware/designs/light2-harness-r02/connectivity.yaml` electrical authority
and its checked `bom.yaml`. As construction choices are made, exact breadboard,
wire, socket, connector, and test-access materials belong in this assembly's
future construction authority rather than being inferred into the design BOM.

The maintained r02 `schematic.kicad_sch` is the authoritative human circuit
construction drawing, checked against `connectivity.yaml`. Its
[`signal views`](../../designs/light2-harness-r02/signal-views/README.md)
isolate functions for tracing; the separate
[`wiring order`](../../designs/light2-harness-r02/wiring-order/README.md)
retains the superseded intermediate-assembly plan and current connection
ledger. The permanent-input-bias proposal was rejected; it does not change
this r02 profile. HW-001 and QUAL-002 record each
cumulative installed subset, including actual terminal/contact mappings and
omissions, under the
[staged validation process](../../../docs/qualification/staged-circuit-validation.md).

The profile's `construction_authority: null` describes the unfinished exact
whole-assembly record; it does not mean that the circuit or its construction
drawings lack authority. Bounded stages remain suspended under the current
Author hold. Construction progress does
not change this assembly's draft status or authorize a powered operation.
