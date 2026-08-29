# Hardware assembly configurations

This directory records reproducible physical assembly configurations. An
assembly revision selects an electrical design revision and describes how that
design is physically realized. It does not replace the selected design's
connectivity authority.

An individual board on the bench is a specimen of an assembly revision. Its
private serial identity, location, and live attachment state remain in ignored
machine-local records. Qualification manifests use safe specimen aliases and
select both the exact assembly and electrical-design revisions.

Moving a conductor or component, changing a breadboard coordinate, changing a
connector or wire construction, or making another physical change that may
affect reproduction or test results advances the assembly revision. A separate
electrical-design revision is also required when that change alters the
selected connectivity or electrical properties.
