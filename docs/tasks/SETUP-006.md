# SETUP-006 — Establish the Light 2 Extender wiring target

## State

- Status: Paused — naming/scaffold work retained; current electrical design
  promoted to HW-001 and `light2-harness-r02`; exact r02 construction mapping
  remains open
- Started: 2026-08-24 19:09 EDT
- Finished: --

## Intent

Develop one coherent, human-buildable electrical wiring target for the Agon
Light 2 and Olimex ESP32-P4-DevKit prototype while preserving exact provenance,
machine-readable connectivity, construction guidance, and reviewable diagrams.
Build the task incrementally as firmware requirements and electrical decisions
become concrete rather than attempting to design the complete carrier in
advance.

This task begins from the currently adopted `light2-harness-r01`, its vendored
legacy evidence, and the corresponding read-only legacy repository. Existing
files are evidence and inputs, not proof that their terminology, presentation,
mode scope, electrical design, or qualification claims are suitable for the
current product.

## Working boundary

Provisional inventories, naming records, source extracts, diagram generators,
draft diagrams, and review evidence belong under `docs/tasks/SETUP-006/` while
their permanent roles and maintained file structure are being discovered.
Accepted recurring hardware definitions will later be promoted or synthesized
into a role-named location under `hardware/`; the task directory will retain
bounded decision and development evidence.

This task does not by itself authorize moving a wire, changing a component,
advancing a harness revision, powering hardware, connecting the Agon, flashing
firmware, or executing a physical test. Those actions require their applicable
versioning, design-review, procedure, and qualification gates.

## Authority and inputs

1. `hardware/designs/light2-harness-r01/profile.yaml` and its current README.
2. The files under `hardware/designs/light2-harness-r01/legacy-evidence/`,
   especially `wiring-diagram.svg` and `carrier-breakout-design.md`.
3. The read-only legacy project's `design/README.md`, which contains the
   generically named Markdown companion text for `wiring-diagram.svg`.
4. The read-only legacy project's `design/reset-actuator-module.md`, which is
   the only recovered design-intent record for a Pi-controlled P4 `ESP_EN`
   configuration of the reusable reset breakout. It does not document the
   photographed Pi-to-Agon configuration, and its referenced SVG is missing.
5. The accepted operating-mode and hardware boundaries in REMED-001,
   SETUP-005, PORT-008, QUAL-002, and the operating-mode audit.
6. `docs/versions/README.md` for controlled wiring, profile, fixture, diagram,
   procedure, and physical-assembly identities.
7. The ignored `HARDWARE.local.md` only when current bench state is material;
   machine-local details must not enter tracked outputs.

## Prelude research — design documentation and ERP structure

Research performed before SETUP-006.1 found no single tutorial or standard
that simultaneously covers practical hardware documentation, object naming,
repository organization, configuration control, manufacturing data, and Odoo
integration. The useful sources divide into complementary roles.

### Practical hardware-documentation structure

The [Open.Make Hardware Documentation
Guide](https://open-make.github.io/Hardware-template-guide/) and its incremental
and full repository templates are the closest general tutorial for the current
project stage. The guide organizes documentation across ideation,
specification, concept development, prototyping, replication, hardware
production, project history, and user guidance. It explicitly addresses
projects that already have a prototype and recommends growing documentation
with the design rather than imposing a complete final structure at the outset.

The guide is a strong source for deciding what information belongs in the
repository and when it becomes useful. It is not, by itself, a formal naming,
configuration-item, or ERP-integration system.

### Functional, physical, and location naming

[IEC 81346-1](https://www.iso.org/cms/%20render/live/en/sites/isoorg/contents/data/standard/08/22/82229.html?browse=tc)
defines general structuring and reference-designation principles for technical
objects. Its most useful concept for this task is keeping separate views of an
object:

1. **Function** — what the object does.
2. **Product** — what physical item implements the function.
3. **Location** — where the physical item is installed now.
4. **Type** — the reusable class or design from which an instance is realized.

That separation prevents a transient name such as “breadboard 2” from becoming
the identity of a circuit whose function survives movement to perfboard, a
carrier PCB, or another host variant. The complete standard is paid and much
heavier than this project presently needs. SETUP-006 may adopt a documented,
simplified subset of its principles but must not claim IEC 81346 compliance
without reviewing and implementing the applicable standard.

Related formal references include IEC 81346-2 object classes, IEC 81355
information classification, IEC 82045 document management, IEC 61175 signal
designations, and IEC 61666 terminal identification. These are possible later
references, not selected task requirements.

### Configuration identification and control

The freely available [NASA Configuration Management
Standard](https://standards.nasa.gov/standard/NASA/NASA-STD-0005) provides a
clear model for:

1. selecting configuration items;
2. assigning unique identifiers to products, components, and documents;
3. keeping product/configuration-item identity distinct from document and
   drawing identity;
4. relating revisions to products and controlled baselines;
5. configuration control and status accounting; and
6. verification and configuration audits.

NASA marks this edition inactive for new NASA designs, so it is a conceptual
and procedural reference rather than a current compliance target. Its
configuration-identification model is nevertheless directly relevant to the
project's existing artifact, revision, baseline, build, and run vocabulary.

ASME Y14.100 and its related Y14.24, Y14.34, Y14.35, and Y14.41 standards cover
engineering drawings, drawing types, associated lists, revisions, and digital
product definition. They are paid, drawing-oriented standards and are likely
excessive for the current breadboard stage. They may become useful when a
production carrier or formal manufacturing drawing package exists.

The Open Compute Project design-package guidance is a useful manufacturing
handoff checklist: a complete package should include original editable design
files, schematics, layouts, bills of material, manufacturing files, and
associated source code in a form sufficient for another competent party to
manufacture or modify the product. It provides package-completeness guidance,
not the project's object-naming system.

### Assembly documentation and bills of material as code

[GitBuilding](https://gitbuilding.io/usage/getting-started/) extends Markdown
with structured part, quantity, tool, supplier, specification, and assembly
links. It can generate bills of material from assembly instructions rather
than maintaining those documents independently. Its
[complex-project model](https://gitbuilding.io/usage/complex-projects) supports
reusable subassemblies and product variants while sharing common instruction
pages.

GitBuilding may eventually serve either as a project tool or as prior art for
project-owned deterministic generators. No native GitBuilding-to-Odoo
integration was found during this research. Its structured YAML/Markdown data
could, however, feed deterministic Odoo CSV exports without making generated
CSV another source of truth.

### Odoo object mapping

Odoo 19 documentation supports the following preliminary mapping:

1. A purchased or manufactured part is an Odoo **Product**. Its **Internal
   Reference** is the practical place for a stable, unique project part number;
   Odoo's [product-import
   guide](https://www.odoo.com/documentation/19.0/applications/sales/sales/products_prices/products/import.html)
   recommends unique internal references.
2. An assembly or subassembly is a product with a possibly multilevel **Bill
   of Materials**. A BoM can include components, quantities, manufacturing
   operations, and instructions. See the [BoM setup
   guide](https://www.odoo.com/documentation/master/applications/inventory_and_mrp/manufacturing/basic_setup/bill_configuration.html).
3. The PLM application uses **Engineering Change Orders** to create, review,
   compare, approve, and apply revised products and BoMs without changing the
   production BoM prematurely. See [engineering change
   orders](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/plm/manage_changes/engineering_change_orders.html).
4. Odoo PLM can attach CAD files, PDFs, diagrams, images, specifications, and
   assembly documents to a BoM and carry changed files through an ECO. See
   [PLM version
   control](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/plm/manage_changes/version_control.html).
5. Physical inventory instances can be tracked by **lot** or unique **serial
   number**, retaining movement and traceability history. See [product
   tracking](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/product_management/product_tracking.html).
6. The electronics bench can be represented as an Odoo **Work Center**, with
   manufacturing operations, schedules, capacity, costs, and assigned
   equipment. See [work
   centers](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing/advanced_configuration/using_work_centers.html).
7. Reusable Pi hosts, logic analyzers, microscopes, meters, programmers, and
   other tools can be Odoo **Maintenance Equipment** assigned to a work center,
   with model, vendor reference, serial number, location, maintenance, cost,
   and warranty data. See [maintenance
   equipment](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/maintenance/add_new_equipment.html).
8. Odoo can import records from CSV or XLSX and preserve stable relationships
   through **External IDs**. Generated Odoo exchange data should use stable
   external IDs distinct from human-facing internal part references.

An electrical net, signal, logical protocol, or abstract circuit function is
not automatically an Odoo stocked product. Only procurable, manufacturable,
maintained, serialized, or operationally scheduled objects should be mapped to
the corresponding ERP object merely because the ERP can store arbitrary
records.

### Provisional direction for SETUP-006

The recommended architecture is an ERP-neutral, machine-readable authority in
Git from which project documents, diagrams, checks, bills of material, and
Odoo import/update records can be generated. Odoo would manage procurement,
inventory, physical lots and serials, released manufacturing BoMs, ECOs, work
centers, and maintained bench equipment. Odoo would not be the sole authority
for electrical connectivity, signal behavior, qualification evidence, or
unreleased design work.

The naming inventory should evaluate fields for:

1. stable project object identity;
2. concise descriptive name;
3. object class, such as function, circuit, subcircuit, assembly, fixture,
   equipment, component, connector, terminal, signal, net, or document;
4. parent or containing object;
5. function, product/type, and present location as separate relationships;
6. revision and lifecycle state where applicable;
7. searchable legacy aliases;
8. Odoo External ID where synchronization is selected;
9. Odoo Internal Reference where the object is a product or maintained part;
   and
10. links to specifications, diagrams, BoMs, procedures, evidence, and
    qualification state.

These are research conclusions and candidate fields, not accepted naming
rules, a frozen schema, an Odoo implementation, or authority to begin the
SETUP-006.1 inventory.

### Applied naming-scheme synthesis

The accepted SETUP-006.1 naming scheme applies the research through the
following bounded influences and project rules:

1. IEC 81346 supplies the conceptual separation of function, physical product,
   present location, and reusable type. The project borrows that separation but
   does not claim IEC 81346 compliance.
2. NASA configuration-management guidance supplies the separation between
   stable object identity, document or drawing identity, revision, lifecycle
   status, physical specimen, baseline, and qualification evidence.
3. `docs/versions/README.md` supplies the project's authoritative distinction
   among software versions, physical and documentary revisions, builds, runs,
   variants, fixtures, profiles, and specimens. A role name embeds none of
   those changing identities.
4. Open.Make guidance supplies the incremental workflow: document the existing
   prototype first, retain task-local discovery while structure is uncertain,
   and promote accepted recurring definitions when their permanent role is
   understood.
5. GitBuilding and Open Compute Project guidance supply the emphasis on
   reusable assemblies, reproducible construction information, structured
   parts and instructions, and complete eventual manufacturing handoff.
6. Odoo's Product, Internal Reference, BoM, ECO, attachment, lot/serial,
   equipment, work-center, and External ID models constrain future ERP mapping.
   Git remains authoritative for electrical connectivity, qualification, and
   unreleased design; role names do not masquerade as Odoo record keys.
7. Existing Extender authorities take precedence over newly coined terms.
   Approved IDs such as `light2-harness`, `forward-parallel-transport`, and
   `la03-p4-probe-fixture` remain intact.

The resulting operational rules are to name durable roles rather than
temporary coordinates; separate product, bench, measurement, and proposed
domains; separate reusable modules from endpoint-specific attachments; keep
physical circuits distinct from protocols, modes, nets, and firmware behavior;
retain legacy terminology only as searchable aliases; and use mechanically
unique lowercase slugs without treating those slugs as revisions, part numbers,
or ERP identities.

## Decision register

### Accepted

1. `SETUP-006-D001` — Use the accepted SETUP-006.1 role names and naming rules
   as project terminology, preserving existing artifact IDs and keeping role
   names distinct from revisions, specimens, parts, and ERP identities.
2. `SETUP-006-D002` — Register the durable authority as artifact ID
   `hardware-object-registry`, first identity `hardware-object-registry-r01`,
   revision identity scheme, and `draft` lifecycle status. The Author accepted
   the recommended resolution of `SETUP-006-Q001` at 2026-08-24 21:34 EDT.
3. `SETUP-006-D003` — For the first beta carrier, trade availability of the
   eleven eZ80 transport GPIOs for circuit simplicity: dedicate them to the
   Exclusive Extended transport while it is active and omit passthrough
   switching, event capture, signal replay, and GPIO virtualization. Preserve
   the possibility of a v1 multiplexed design in requirements, net naming, and
   layout review, but do not burden beta with unselected circuitry or claim
   electrical transparency. The Author accepted this beta scoping rule on
   2026-08-25.
4. `SETUP-006-D004` — For the first beta carrier, provisionally preserve the
   six presently uncommitted exposed P4 candidates GPIO6, GPIO18, GPIO19, and
   GPIO46--GPIO48 for user experimentation, subject to electrical and
   capability verification; reserve GPIO37/GPIO38 for the optional
   MOD-WIFI-ESP8266 UART; make no beta pin reservation for the post-v1
   VDP/EDP link; and expose the eleven transport-owned eZ80 contacts only as
   labeled test points rather than a replicated user header. Permanent v1
   reserve and passthrough policy is deferred.
5. `SETUP-006-D005` — Use P4 GPIO16/EXT1-17 as the dedicated return-UART TX for
   the Exclusive Extended beta and keep GPIO12/EXT1-13 permanently assigned to
   PARLIO D1 input. This removes P4 direction and pin-mux turnaround without
   changing the Agon PC1 ownership contract.
6. `SETUP-006-D006` — Omit `EE-UART-ALLOW-N` from the first General Poll beta.
   Keep PD6/GPIO17 unassigned and preserve practical routing space until
   PORT-008 establishes whether bounded EMOS buffering needs a physical return-
   pacing signal.
7. `SETUP-006-D007` — Retain P4 GPIO23/EXT2-10 as forward data bit D2. The
   Olimex Rev D1 design marks optional Ethernet-clock link R31 DNP, and the
   Author visually inspected the underside of the current Rev D1 bench board
   on 2026-08-25: the footprint has soldered pads but no bridging component.

`SETUP-006-D005` and `SETUP-006-D006` apply only to the predecessor-circuit
General Poll experiment. They do not override the common four-wire UART and
control allocation frozen in `light2-harness-r02`.

### Promoted hardware decisions

SETUP-006.4's split-power buffering, READY control, and series-population
questions were promoted into HW-001 once the firmware-led requirements became
concrete. `HW-001-D004` through `HW-001-D008` now own their disposition:
`light2-harness-r02` freezes the four-chip candidate and R1--R13 at 220 ohms,
while reset recovery, Legacy electrical absence, and physical qualification
remain open under HW-001 and QUAL-002.

## Work

### SETUP-006.1 — Name every circuit and physical subassembly

1. [x] Inventory every distinct circuit, subcircuit, breakout breadboard,
   carrier section, connector assembly, conditioning path, power/reference
   boundary, and measurement-only attachment represented by the current bench
   and source documents. The bounded discovery result is
   [`SETUP-006.1.1-object-inventory.md`](SETUP-006/SETUP-006.1.1-object-inventory.md).
2. [x] Assign each item one unique, concise, role-descriptive name that remains
   meaningful independently of its present breadboard location or historical
   experiment number. Proposals are in
   [`SETUP-006.1.2-naming-register.md`](SETUP-006/SETUP-006.1.2-naming-register.md).
3. [x] Record aliases and ambiguous legacy names so existing evidence remains
   searchable without allowing those names to remain competing authority.
4. [x] Distinguish logical buses and protocols from the physical circuits that
   carry them, and distinguish product wiring from test fixtures and probes.
5. [x] Present the naming inventory to the Author for review before renaming
   files, revising diagrams, changing hardware profiles, or proceeding to the
   next work item. The Author accepted the proposed naming set at 2026-08-24
   21:08 EDT.

### SETUP-006.2 — Establish the durable hardware-object authority

1. [x] Define the authority boundary: global object data owns names, classes,
   aliases, and containment, while revisioned design and fixture profiles own
   pins, nets, components, electrical connectivity, and qualification scope.
2. [x] Promote all 41 accepted role names to
   `hardware/objects/objects.yaml` without retaining temporary `I001` task keys
   as production identifiers.
3. [x] Add a JSON Schema and durable README describing the data contract,
   change control, versioning boundary, ERP boundary, and validation command.
4. [x] Add the routine `scripts/validate-hardware-objects.py` validator for
   schema conformance, deterministic ordering, canonical uniqueness, alias
   hygiene, parent existence and acyclicity, and registered artifact links.
5. [x] Add six regression tests covering the accepted authority and negative
   duplicate, alias, parent, cycle, and artifact-reference cases.
6. [x] Confirm the 41 promoted IDs exactly match the accepted naming register;
   run the object validator, its regression suite, and the existing version-
   record validator successfully.
7. [x] Resolve `SETUP-006-Q001` as `SETUP-006-D002`, register the approved
   `hardware-object-registry-r01` draft identity, and bind validation to the
   central artifact record.
8. [x] Present the complete SETUP-006.2 change set for Author acceptance and
   commit. The Author committed and pushed the accepted result as `0becfd5`.

### SETUP-006.3 — Establish the Fritzing breadboard wiring-diagram scaffold

1. [x] Record the current physical arrangement as two BusBoard BB630 terminal
   areas from a BB1460 kit with both BB100R distribution strips installed: one
   at the top edge and one shared between the terminal areas. Treat this as a
   mechanical observation pending physical review, not an electrically
   qualified assembly definition.
2. [x] Create a deterministic, project-local Fritzing generator rather than
   relying on hand placement in the Fritzing GUI.
3. [x] Generate a custom composite breadboard part with a 63-column, 0.1-inch
   terminal grid and both top-edge and shared central distribution strips.
   Center each strip's two contact rows and place its polarity-color legends
   outside those rows rather than through their centers. Preserve the accepted
   left-to-right column orientation and place blue/GND above red/hot on both
   strips without rotating the established drawing. Put outer column indices
   immediately above and below the Agon headers, remove the unnecessary BB630
   center-groove titles, and add diagram-only column-index series in both
   grooves as drafting orientation aids.
4. [x] Generate an Olimex ESP32-P4-DevKit Rev D1 part from the official board
   dimensions and 20-pin EXT1/EXT2 header geometry.
5. [x] Place P4 EXT1 and EXT2 across the shared strip with header pin 1 at
   breadboard column 1, USB Serial/JTAG overhanging that end, and two free
   terminal holes on either side of each header row.
6. [x] Package the sketch and custom parts into a portable `.fzz`; package the
   accepted P4 and accepted composite breadboard independently as My
   Parts-compatible `.fzpz` files; render a review preview; and validate
   archive, XML, connector, pitch, placement, and regeneration invariants.
7. [x] Keep P4 signal interconnects explicitly unassigned until the firmware-
   driven electrical design review selects the required nets, conditioning,
   protections, and test points. This does not prohibit reproducing the
   recovered Agon-side harness contacts as evidence.
8. [x] Add two separate color-coded Agon 1x16 harness headers to the same
   generated sketch: even pins 2–32 on the top row beginning at column 6 and
   odd pins 1–31 on the bottom row beginning at column 4. Explicitly exclude
   pins 33 and 34 from both headers, and defer their separate power wiring.
   Keep both header parts label-free. Add two independent movable label-bank
   parts, one containing exactly 16 odd-pin labels and one containing exactly
   16 even-pin labels. Use matching colors, exact 0.1-inch breadboard-hole
   pitch, 0.5-inch label depth, and left-justified `number name` text. Bake the
   required clockwise rotation into each SVG rather than storing a Fritzing
   instance transform. Place each bank outside and aligned with its matching
   1x16 header, following the Author's `_usermod` review evidence.
   Identify only official physical Agon names and immutable eZ80 mux roles:
   `PC0 / TXD1`, `PC1 / RXD1`, `PC2 / RTS1`, and `PC3 / CTS1` on Agon pins
   17--20 respectively. Pins 13 and 14 remain `PD4` and `PD5`. Never embed
   mutable Extender harness-function mappings in these labels.
   Use one plain SVG text node per label: Fritzing 1.0.1 visibly mangles
   adjacent `<tspan>` elements even when standard SVG renderers do not.
   Include one invisible, unconnected, explicitly non-electrical connector as
   a loader workaround: Fritzing 1.0.1 substitutes another bundled part's
   artwork when a normal custom part has no connectors. Give each label bank a
   unique Fritzing module identity and advance it whenever changing integration
   metadata.
9. [x] Present the generated scaffold and all assumptions for Author review.
   The Author accepted and froze it on 2026-08-25 as the canonical mechanical
   and diagrammatic base for subsequent SETUP-006 wiring design. It remains
   task-local until the electrical design establishes the correct permanent
   artifact boundary; acceptance does not qualify or preserve the legacy
   harness wiring.
10. [x] Execute `CA-2026-08-25-001`: correct the four misassigned Agon UART1
    pin labels in the authoritative generator, every current generated or
    derived Fritzing artifact, and every affected current document; refresh
    hash-bound audit evidence; prove that physical connectivity is unchanged;
    and stop with an exact corrected-file manifest before commit.

### SETUP-006.4 — Establish the firmware-driven electrical requirements

1. [x] Define the scope, authorities, outputs, and stop boundary in
   [`SETUP-006.4-wiring-design/README.md`](SETUP-006/SETUP-006.4-wiring-design/README.md).
   The immediate candidate was the Exclusive Extended beta transport. HW-001
   now owns the separate firmware-led design of the common V1 four-signal UART
   and forward-parallel circuit; its proposal does not revise this harness.
2. [x] Inventory every Agon/P4 transport signal required by the bounded beta,
   including direction, actor, idle and reset ownership, exact firmware use,
   and application-visible contract.
3. [x] Audit each candidate P4 pin against the Olimex Rev D1 schematic and the
   board's Ethernet, microSD, USB, MIPI, user-control, and expansion functions.
4. [x] Determine the required direction control, buffering, pull resistors,
   series resistance, power/reference boundary, reset behavior, protection,
   and test points without changing the physical bench.
5. [x] Produce a candidate pin/net allocation, explicit reservations and
   deferrals, qualification dependencies, and numbered unresolved questions.
6. [x] Correct the SETUP-006.3 P4 part's swapped GPIO16/GPIO17 labels under a
   new Fritzing module identity and regenerate the canonical scaffold without
   modifying the Author's active wiring draft. Reconcile that draft only after
   the Author finishes editing or explicitly authorizes the operation.
7. [x] Preserve the Author's completed wiring draft unchanged and derive the
   deterministic `draft_v1` review copy. Replace its embedded P4 `r04` part
   with corrected `r05`; migrate the upside-down composite breadboard to a new
   part identity with reversed A--J connector names and visible row letters;
   and place the documented current `SN74HC125N` U1 across the upper groove
   rotated 180 degrees in the landscape view, spanning columns 30--36 with pin
   1 at the upper-right corner at F36. Do not treat the diagrammatic U1
   artwork as package or PCB geometry.
8. [x] Present the electrical result, `draft_v1`, and numbered questions to the
   Author before changing the authoritative harness or authorizing bench work.
   Q000--Q002 and Q005 were resolved; Q003, Q004, and Q006 were deferred behind
   ported-firmware forward evidence. No harness change or bench operation was
   authorized by this review.

## Stop condition

SETUP-006 is paused while the critical path returns to the retained VDP port
and its bounded forward test. SETUP-006.1.1 is accepted and frozen in commit
`b38b445`. SETUP-006.1.2 is accepted review provenance, and SETUP-006.2 has promoted its names into
`hardware-object-registry-r01`. The Author resolved the registry-identity gate
as `SETUP-006-D002`. SETUP-006.3 is accepted as the canonical unwired
breadboard scaffold. SETUP-006 remains open because the firmware-driven
electrical design, connectivity, construction definition, and qualification
are not established. Do not rename existing files, change a hardware profile,
advance another artifact revision, synchronize ERP records, or modify physical
wiring without the applicable Author approval.
