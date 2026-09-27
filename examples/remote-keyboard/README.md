# Remote keyboard receiver witness

**Refresh required before deployment.** This experimental fixture is retained
source and historical evidence, not an installed utility or a current test recipe.

## Purpose and limits

Records MOS keyboard sysvars and the 128-bit physical-key map without installing a callback or resident code. It returns after Enter release or a 90-second timeout. Virtual-key numbers are not direct physical-map indices.

## Reuse prerequisite

The receiver writes `/extender/key-seen.txt`; qualify_keyboard.py reads that path and generates LOAD/RUN of the ordinary listener. Refresh producer, consumer, helper batches and evidence paths together before reuse.

[REMOTE-002 R02-EX01](../../docs/tasks/REMOTE-002.md) owns the refresh. Use
[SD layout](../../docs/sd-layout.md), [current SD operation](../../docs/mainboard-sd.md)
and [bench constraints](../../docs/qualification/bench-constraints.md). Prepare
Legacy/input admission before remote commands; select video mode only in
`/autoexec.txt`. A refreshed run needs identified bytes, preserved earlier
receipts, an explicit terminal state and its own bounded validation contract.

The [historical recipe](../../docs/tasks/AUDIT-009/retained-example-recipes/remote-keyboard.md) preserves prior build/invocation
instructions and evidence limits. It is not authorization to replay them.
See the [example index](../README.md) for the other diagnostics.
