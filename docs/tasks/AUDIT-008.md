# AUDIT-008 — EMOS ROM simplification and SD-loaded utilities

## Executive summary

Deferred at the Author's request until a fresh token allotment and explicit
resumption. Review whether EMOS contains unnecessary general-purpose machinery,
and investigate loading foreground Extender utilities from `/emos` through the
`emos` CLI prefix. Keep the resident replacement MOS small and reuse stock MOS
code wherever practical. This records a direction for investigation, not an
approved implementation or filesystem migration.

## Origin and scope

The [REMOTE-005 MOSlet work](REMOTE-005/MOSLET-CHECK.md) prompted this separate
question. Its provisional EMOS image occupies 131056 of 131072 ROM bytes, versus
130936 for the preserved installed predecessor: 120 bytes of growth and 16 bytes
remaining. The listener itself already resides on SD; relocating it from `/mos`
to `/emos` would not itself recover ROM. Verify linked-size attribution before
blaming particular source changes or claiming savings.

The Author wants Extender-specific utilities separated from stock `/mos`, invoked
as `emos <command>`, and unnecessary resident complexity removed where justified.
The eZ80's resident EMOS remains responsible for ordinary VDU routing, keyboard
reception, Extender transports and committed operating mode. P4/EDP changes and
new file-transfer protocols are outside this task.

## Deferred work items

A08-01 [ ] Account for resident ROM from the actual linked image and map. Identify
used service dispatch, dormant module machinery, diagnostics and command setup
code. Separate necessary behavior from historical scaffolding; identify stock
MOS code that can be reused. Do not assume a restriction is unnecessary merely
because a recent test did not exercise it.

A08-02 [ ] Propose a minimal resident/SD split. Classify code by whether it must
remain available while applications run, not speed alone. Quantify plausible
ROM savings and dispatcher cost; preserve boot and recovery without an SD card.

A08-03 [ ] Investigate resident EMOS CLI dispatch of `emos <command> [arguments]`
to `/emos/<command>.bin`, reusing the stock MOSlet loader and calling convention.
Specify case-insensitive lookup, resident-command precedence, arguments, return
codes, missing-card/file behavior, RAM ownership and preservation of loaded
applications. No new relocatable module format or plugin framework.

A08-04 [ ] Present the bounded implementation contract and open decisions to the
Author before coding. If subsequently authorized, compare ROM size and ordinary
MOS/EMOS behavior, test utility invocation and failure returns, and preserve the
working firmware as rollback. Move only justified foreground utility code.

## Decision register and gates

D01 — Proposed, unresolved: resident EMOS checks its built-in commands first,
then loads an Extender MOSlet from `/emos`. Example: `emos sdserve /`.
Exact fallback behavior and eligible commands require the source review.

D02 — Constraint: preserve stock executable/loading idioms and EMOS ownership
of routing and transports. SD utilities remain foreground programs; this proposal
does not create background services or permit bypassing the resident owner.

D03 — Unresolved: which resident code can move to SD without breaking APIs,
application execution, boot or recovery. Account for shared services and MOSlet
RAM conflicts before selecting candidates.

No implementation, builds, SD changes or bench operations are authorized by this
record. REMOTE-005 retains ownership of file-access work and its provisional
MOSlet evidence; this task owns only ROM simplification and CLI utility placement.
