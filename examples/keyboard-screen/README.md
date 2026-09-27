# Stock VDP text readback diagnostic

**Refresh required before deployment.** This experimental fixture is retained
source and historical evidence, not an installed utility or a current test recipe.

## Purpose and limits

Queries rendered character cells using VDU 23,0,&83,x16,y16. Maximum size is 80×60 cells, with one-second per-query and 60-second overall bounds. Graphics, alternate fonts and cursor overlays can affect recognition. This is not raw screen text RAM.

## Reuse prerequisite

The source writes `/extender/key-screen.txt`. Its historical batch loads the ordinary listener. Refresh receipt placement and Legacy-mode EMOSlet return before another run. For routine ExCom text retrieval use the [maintained screen-text guide](../../docs/screen-text.md).

[REMOTE-002 R02-EX01](../../docs/tasks/REMOTE-002.md) owns the refresh. Use
[SD layout](../../docs/sd-layout.md), [current SD operation](../../docs/mainboard-sd.md)
and [bench constraints](../../docs/qualification/bench-constraints.md). Prepare
Legacy/input admission before remote commands; select video mode only in
`/autoexec.txt`. A refreshed run needs identified bytes, preserved earlier
receipts, an explicit terminal state and its own bounded validation contract.

The [historical recipe](../../docs/tasks/AUDIT-009/retained-example-recipes/keyboard-screen.md) preserves prior build/invocation
instructions and evidence limits. It is not authorization to replay them.
See the [example index](../README.md) for the other diagnostics.
