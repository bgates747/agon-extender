# Olimex bench production firmware maintenance

Extender owns EMOS and the Extender VDP on the P4. VDPlet owns the mainboard
VDP. The owners supply the exact restore images and coordinate changes so that
ordinary operators can rely on the bench's production baseline at checkout.
The [operator procedure](../docs/operations/olimex-bench/README.md) lists the current artifacts.

1. Confirm the production build for each affected processor with its owner.
   The owner retains the binary at a durable location with its exact SHA-256,
   source revision, and write scope. Check that operators can fetch it using
   the same access they have for bench work.
2. Between test slots, establish the intended baseline under exclusive
   custody. Install the affected production images, verify the writes and
   startup, and record the resulting baseline.
3. Publish the current direct binary links and hashes in the bench procedure
   before the next ordinary slot opens.

The [current release](current.yaml) selects the qualified Olimex bundle.
The [bundle manifest](bundles/olimex-parlio-v0.3.0/bundle.yaml) records the
P4 app0 write scope, EMOS ROM, SD listener, production VDPlet companion
and prior restore set. Operators get their direct binary links from the
bench procedure above.
