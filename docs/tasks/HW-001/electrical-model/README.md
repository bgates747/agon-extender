# HW-001 placement-independent electrical model

## Scope

This directory defines the task-local canonical source format for electrical
connectivity. It deliberately represents no schematic placement, breadboard
holes, wire routing, conductor colors, package geometry, PCB layout, or
firmware behavior.

The format answers only these questions:

1. Which component instances are in scope?
2. Which stable terminals belong to each component?
3. Which terminals are electrically common on each net?
4. Which declared terminals are intentionally unconnected?
5. What minimal electrical identity is required to interpret those facts?

No product circuit is stored in this task-local schema directory. The example
is illustrative and must not be used as a wiring plan. The first controlled
consumer is the frozen
`hardware/designs/light2-harness-r02/connectivity.yaml` authority.

## Authority

For a controlled circuit, one `connectivity.yaml` document validated by
this directory's schema and semantic validator will be the
placement-independent electrical authority. A schematic, connection table,
graph, breadboard drawing, harness map, PCB, and BOM will be projections or
consumers of that authority unless an accepted later decision assigns a
narrower role differently.

Authority order for this task-local format is:

1. `schema/circuit.schema.json` defines document shape and field types.
2. `validate.py` defines cross-reference, uniqueness, terminal-accounting, and
   canonical-order rules that JSON Schema cannot express conveniently.
3. This README defines electrical meaning and maintenance policy.
4. `examples/` demonstrates syntax only and carries no product authority.

The Author approved the first product `connectivity.yaml`, its durable
destination, and `light2-harness-r02` identity on 2026-08-29. This task-local
format and validator still cannot silently create or revise a hardware
artifact; changes to the accepted model require normal revision control.

## Electrical model

### Components and terminals

A component instance has a stable reference such as `U1`, `R1`, or `J1`.
Every in-scope terminal has a stable `pin` string. Its compact identity is the
ordered pair `(component reference, pin)`, conventionally displayed as `U1.3`.
The pair—not a prose name or position—is the identity used by validation.

Terminal `name`, `role`, and `electrical_type` describe a terminal without
replacing its pin identity. IC and connector pin numbers follow the selected
part or interface definition. Passive terminal numbering follows the selected
symbol and footprint.

Nonpolar parts still retain numbered terminals. For a resistor, `R1.1` and
`R1.2` remain stable even though exchanging them may leave the circuit
electrically equivalent. `interchangeable_group` records that equivalence; it
does not permit a tool to rename or silently swap accepted terminals.

Polarized parts record explicit terminal roles such as `positive`, `negative`,
`anode`, or `cathode`. Keyed multi-pin devices use their manufacturer pin
numbers and pin names rather than pretending every pin has a polarity.

`terminal_scope: complete` means every physical/electrical terminal of the
component is declared. `terminal_scope: in_scope` means the document declares
only terminals participating in the bounded model, which is useful for boards
and modules with many unrelated pins. Every terminal that is declared must
still be assigned to exactly one net or exactly one intentional-unconnected
record.

### Nets

A net is a named set of two or more terminals that are electrically common. It
is a graph hyperedge, not a chronological path. These statements are therefore
equivalent:

```text
wire U1 pin 3 to P4 pin 32
net uart-tx members U1.3 and P4.32
```

Additional test points or connector pins on the same conductor become more
members of that one net. There is no electrically meaningful first or last
member.

A series component separates nets. If a signal passes through `R1`, one net
contains the source and `R1.1`; another contains `R1.2` and the destination.
The resistor instance relates its two terminals through the behavior implied
by its kind and value. Collapsing both resistor terminals into one net would
describe a short circuit around the resistor.

Net IDs describe durable electrical roles rather than locations. A net may
record signal, control, power, ground, or reference class and a power-domain
association, but spatial routing remains outside this model.

### Intentional disconnections

An unused declared terminal appears in `unconnected` with a reason. It must not
also appear on a net. Omitting a declared terminal entirely is a validation
error rather than an implicit no-connect.

### Ordering

Connectivity is determined by IDs and membership, never YAML ordering.
Nevertheless, canonical documents use deterministic natural order to make Git
diffs and human review predictable:

1. components by reference;
2. terminals by pin within each component;
3. nets by net ID;
4. members by component reference and pin; and
5. intentional disconnections by component reference and pin.

The validator enforces this presentation order. Reordering alone cannot change
electrical meaning, but a noncanonical document is rejected until normalized.

## Files

1. `schema/circuit.schema.json` — JSON Schema Draft 2020-12 structural rules.
2. `validate.py` — schema and semantic validation entry point.
3. `examples/topology-example.yaml` — non-product syntax and topology example.
4. `tests/test_validate.py` — regression tests for accepted and rejected
   models.
5. `kicad-projection.yaml` — non-authoritative mapping from example component
   references to installed KiCad 7 symbols.
6. `generate_kicad.py` — deterministic SKiDL projection of the validated model
   into an editable KiCad 7 schematic.
7. `compare_kicad_netlist.py` — exact comparison of the authoritative model
   with KiCad's exported XML netlist, including intentional no-connects.
8. `generated/topology-example.kicad_sch` — editable illustrative schematic.
9. `generated/topology-example.xml` and `generated/svg/` — derived comparison
   evidence and human preview; neither is electrical authority.

## Validation

From the project root:

```sh
.venv/bin/python docs/tasks/HW-001/electrical-model/validate.py \
  docs/tasks/HW-001/electrical-model/examples/topology-example.yaml

.venv/bin/python -m unittest discover \
  -s docs/tasks/HW-001/electrical-model/tests -p 'test_*.py'
```

The validator rejects at least:

1. schema/type violations;
2. duplicate component references, terminal pins, or net IDs;
3. references to undeclared component terminals;
4. a terminal assigned to two nets or to both a net and `unconnected`;
5. any declared terminal that is not accounted for;
6. duplicate members inside one net;
7. invalid polarity metadata; and
8. noncanonical ordering.

## KiCad projection spike

The sample can be projected into an editable KiCad 7 schematic without making
the schematic electrical authority:

```sh
.venv/bin/python docs/tasks/HW-001/electrical-model/generate_kicad.py

kicad-cli sch export netlist --format kicadxml \
  -o docs/tasks/HW-001/electrical-model/generated/topology-example.xml \
  docs/tasks/HW-001/electrical-model/generated/topology-example.kicad_sch

.venv/bin/python docs/tasks/HW-001/normalize_kicad_netlist.py \
  docs/tasks/HW-001/electrical-model/generated/topology-example.xml

.venv/bin/python \
  docs/tasks/HW-001/electrical-model/compare_kicad_netlist.py \
  docs/tasks/HW-001/electrical-model/examples/topology-example.yaml \
  docs/tasks/HW-001/electrical-model/generated/topology-example.xml
```

The comparator requires exact named-net membership and exact intentional
no-connect membership. It does not accept anonymous-net aliases as equivalent.
The generated schematic uses labeled stubs rather than long wires; labels make
the graph readable and preserve canonical net IDs while allowing KiCad to
arrange ordinary symbols.

The spike exposed two inherited tool limitations:

1. SKiDL 2.3.0's full-wire router could not route this small example reliably,
   and its placement depends on both a pseudo-random seed and Python set
   iteration. The generator therefore selects explicit labeled stubs, a fixed
   seed, and a controlled `PYTHONHASHSEED` re-execution.
2. SKiDL 2.3.0's `kicad7` writer emits several KiCad-8-era fields and schematic
   format `20230409`; local KiCad 7.0.11 rejects that syntax. The generator's
   prominently documented bounded compatibility pass rewrites only those
   known constructs to KiCad 7 format `20230121`, stabilizes the root UUID, and
   then requires successful KiCad XML export and exact netlist comparison.
3. SKiDL's embedded generic connectors show redundant `Pin_N` names and hide
   the useful immutable pin numbers. The same bounded pass discovers mapped
   generic connector symbols and reverses those display flags; this changes
   presentation only and is covered by the exact netlist comparison.
4. Importing SKiDL 2.3.0 creates `skidl.log` and `skidl.erc` in the caller's
   working directory even when this task requests neither artifact. The
   generator contains that inherited side effect in an owned temporary
   directory, disables file logging there, and never deletes a caller-owned
   similarly named file.
5. SKiDL 2.3.0 attempts `kicad-cli sch erc` after generation, but the selected
   KiCad 7.0.11 CLI has no schematic ERC subcommand. The generator suppresses
   only that unsupported probe after feature detection; KiCad load/export and
   exact netlist comparison remain mandatory.

These limitations make generated SKiDL placement a projection and bootstrap,
not electrical authority. The accepted integration keeps YAML authoritative,
uses deterministic KiCad generation and exported-netlist comparison for exact
connectivity, and permits human layout work only when the checked endpoint
partition remains unchanged.

KiCad or SKiDL upgrades are qualified on an unchanged model before project
artifacts move:

1. record the proposed KiCad and projection-tool versions;
2. regenerate the example twice and require byte-identical schematics;
3. require KiCad to load the result by exporting its XML netlist;
4. require exact model/netlist comparison;
5. review the rendered SVG and editable schematic for legibility; and
6. remove compatibility workarounds only when the upgraded baseline accepts
   the unmodified generator output and the preceding checks still pass.

KiCad 7.0.11 does not expose schematic ERC through `kicad-cli`; successful
load/export and exact comparison are the automated claims made here. Product
schematic ERC remains a separate required check through KiCad or a later CLI
baseline.

## Outside this format

1. Physical conductor, harness, breadboard, PCB, or probe representation.
2. Firmware transport, mode, pacing, or ownership implementation.
3. Qualification or release status beyond the metadata recorded by the
   selected controlled design.
