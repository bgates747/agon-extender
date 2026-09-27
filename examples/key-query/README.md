# Virtual-key query witness

**Refresh required before deployment.** This experimental fixture is retained
source and historical evidence, not an installed utility or a current test recipe.

## Purpose and limits

Exercises VDU 23,0,&99,vk through EMOS sysvars with controlled Shift/a events. The expected historical result is 269 passing rows, including the 8-bit event-counter wrap. It installs no alternate UART path.

## Reuse prerequisite

The source writes `/test/keyquery.csv`, replacing the prior receipt. Refresh the producer and controller paths before another run; changing the working directory cannot redirect this absolute path.

[PORT-003 P03-EX01](../../docs/tasks/PORT-003.md) owns the refresh. Use
[SD layout](../../docs/sd-layout.md), [current SD operation](../../docs/mainboard-sd.md)
and [bench constraints](../../docs/qualification/bench-constraints.md). Prepare
Legacy/input admission before remote commands; select video mode only in
`/autoexec.txt`. A refreshed run needs identified bytes, preserved earlier
receipts, an explicit terminal state and its own bounded validation contract.

The [historical recipe](../../docs/tasks/AUDIT-009/retained-example-recipes/key-query.md) preserves prior build/invocation
instructions and evidence limits. It is not authorization to replay them.
See the [example index](../README.md) for the other diagnostics.
