# Hardware designs

Tracked hardware profiles, wiring definitions, and design evidence live here.
Every controlled design follows the identity and revision rules in
[`docs/versions/README.md`](../docs/versions/README.md).

The current first design target is
[`light2-harness-r01`](designs/light2-harness-r01/README.md). Its YAML profile
and accompanying README are normative. Vendored predecessor documents preserve
provenance and test evidence; diagrams are advisory when they disagree with
the text or profile.

The current logic-analyzer attachment target is
[`la03-p4-probe-fixture-r01`](fixtures/la03-p4-probe-fixture-r01/README.md).
Its green D0 endpoint was physically verified as GPIO32 / EXT2 pin 9; the
contradictory legacy pin-10 label is retained only as provenance.

Machine-local specimen identities, bench topology, and current connection
status remain in the ignored `HARDWARE.local.md`, not this directory.
