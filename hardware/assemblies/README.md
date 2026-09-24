# Hardware assembly configurations

This directory records reproducible physical assembly configurations. An
assembly revision selects an electrical design revision and describes how that
design is physically realized. It does not replace the selected design's
connectivity authority.

## Recorded assemblies and current applicability

| Record | Applicability |
|---|---|
| [r01](light2-extender-solderless-assembly-r01/README.md) | Preserved first prototype, not the current r03 wiring map |
| [r02](light2-extender-solderless-assembly-r02/README.md) | Held incomplete buffered construction; no complete-circuit qualification |

The active simplified r03 wiring has no complete replacement assembly record
here. [HW-002](../../docs/tasks/HW-002.md) owns that gap and the deferred USB
drawing update; the [hardware index](../README.md) owns current applicability.
Do not label the live bench as either recorded assembly merely because those
are the available profile files.

## Specimens and revisions

An individual board on the bench is a specimen of an assembly revision. Its
private serial identity, location, and live attachment state remain in ignored
machine-local records. Qualification manifests use safe specimen aliases and
select both the exact assembly and electrical-design revisions.

Moving a conductor or component, changing a breadboard coordinate, changing a
connector or wire construction, or making another physical change that may
affect reproduction or test results advances the assembly revision. A separate
electrical-design revision is also required when that change alters the
selected connectivity or electrical properties.
