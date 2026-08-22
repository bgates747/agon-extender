# PORT-001 first proof — VDU 22 screen-mode selection

Status: validated candidate for Review Gate 2  
Source baseline: official VDP `v2.16.0`

## Why this seed

`VDU 22, mode` was selected after the general builder existed. Among the base
VDU cases it exercises a useful cross-section without requiring an unresolved
EDU architecture: byte dispatch, argument input, parser methods, graphics mode
replacement, persistent state, context reset, double buffering, mouse coupling,
callbacks, a return packet, transport, platform APIs, and physical facilities.
The system itself remains seed-agnostic.

## Generated evidence

- [Authoritative slice](../../dependencies/generated/commands/vdu-22.yaml)
- [Markdown projection](../../dependencies/generated/commands/vdu-22.md)
- [Graphviz source](../../dependencies/generated/diagrams/vdu-22.dot)
- [SVG projection](../../dependencies/generated/diagrams/vdu-22.svg)

The depth-four slice contains 59 nodes, 105 included relationships, 59 explicit
continuation boundaries, and 71 unresolved lexical relationships. The high
unresolved count is expected: receiver types for C++ member calls are not
guessed.

## Source-validated behavior

1. The outer `VDUStreamProcessor::vdu` switch recognizes byte 22, reads one
   mode byte, and dispatches to `vdu_mode`.
2. `vdu_mode` clears and completes prior drawing, disables teletext state,
   removes VSYNC callbacks, and calls `changeMode`.
3. Failed mode selection falls back through the prior `videoMode`, then mode 1.
4. A successful or recovered change resets contexts and handles the
   double-buffered screen path.
5. Stock firmware restores mouse visibility, resets its positioner against the
   new dimensions, and refreshes mouse variables when required.
6. It invokes mode-change callbacks and calls `sendModeInformation`.
7. `sendModeInformation` returns `PACKET_MODE`, containing pixel dimensions,
   character dimensions, colour depth, and the selected mode number, over the
   active VDP packet transport.

The graph records direct reads of display dimensions, controller ownership,
mouse visibility, and `videoMode`, plus direct writes to `ttxtMode`,
`videoMode`, and mouse visibility reached within the selected depth.

## Reviewed semantic boundaries

The mechanical graph cannot infer the engineering meaning of every member
call. Reviewed claims therefore connect the command path to:

- the graphics-display subsystem and its FabGL, GPIO, I2S1, DMA, heap, and
  FreeRTOS execution dependencies;
- the stock physical-PS/2-input subsystem reached by mouse positioner reset;
- the primary VDP transport used by the returned mode packet; and
- the explicit `PACKET_MODE` protocol-packet node.

These are facts about upstream behavior, not automatic P4 dispositions. The
only port annotation in this proof is SETUP-004's accepted `retain` disposition
for the VDU 22 command itself.

## Deliberate uncertainty

Member calls through objects and pointers remain unresolved unless compiler or
reviewed receiver-type evidence identifies their target. Examples in this
slice include `context->cls()`, `_VGAController.get()`, Canvas buffer methods,
mouse methods, and container operations. This is preferable to the incorrect
bare-name edges found during the first manual review.

Depth boundaries are equally deliberate. They identify the next function,
state, subsystem, platform, or hardware relationship without pretending the
bounded view is the complete firmware closure.

## Implementation gotchas found by the proof

1. One upstream portability header defines the same macro name in many
   conditional architecture branches. Macro identity therefore includes its
   signature and definition fingerprint; identical variants merge.
2. Bare-name matching originally misidentified member calls such as
   `_VGAController.get()`. Member-access calls now remain unresolved without
   receiver-type evidence, and unqualified calls never cross source ownership
   boundaries by name alone.
3. Mechanical and merged graphs initially shared mutable in-memory node
   objects. Applying a reviewed annotation could therefore change a later
   digest calculation for an already-written file. Artifact digests are now
   frozen immediately after each write.
4. The full mechanical graph is a large reproducible ignored intermediate.
   PORT-002 later promoted and enriched its merged result as the durable
   schema-2 graph under `docs/dependencies/`.

## Validation completed

- JSON Schema draft 2020-12 validation;
- unique IDs and `(from, relation, to)` edge tuples;
- graph-wide endpoint and evidence references;
- annotation, seed, group, boundary, and stop-rule references;
- canonical ordering and YAML serialization;
- tracked input and graph fingerprints;
- source-file, source-span, and reconstructed source-tree fingerprints for all
  four source owners;
- six focused regression tests; and
- byte-identical graph, overlay, slice, Markdown, DOT, and SVG regeneration.
