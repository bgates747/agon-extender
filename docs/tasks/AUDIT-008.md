# AUDIT-008 — EMOS ROM headroom and SD-loaded EMOSlets

## Executive summary

Contract refreshed 2026-09-23 at the Author's request; **awaiting review before
investigation or implementation**. This promotes the previously deferred idea
instead of creating a duplicate task. REMOTE-005 remains the next file-access
workstream; this task determines which existing resident EMOS functions could
become SD-loaded foreground utilities, informally “EMOSlets,” to recover ROM for
features that genuinely require resident firmware.

Use existing MOSlet loading and calling conventions, not a new executable format.
The investigation must deliver a ranked, measured shortlist and a minimal
implementation proposal. No code movement is approved by this write-up.

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

## Investigation contract

A08-01 [ ] Establish the current ROM baseline in the project-owned EMOS checkout.
Read official MOS API/loading documentation first, then source where needed.
Record source revision, build configuration, compiler/linker versions, linker
map, occupied ROM span and free bytes. Reconcile the retained 16-byte-headroom
result against the current build; do not treat that historical result as a new
measurement. Account for alignment, shared helpers, constants, dead stripping
and fixed-address sections before attributing bytes to functions.

A08-02 [ ] Inventory resident Extender-specific commands and support routines.
For each candidate record its callers, code/data contribution, runtime state,
interrupt dependencies, frequency, and whether applications or startup require
it outside a CLI invocation. Inspect diagnostics, status/help formatting,
one-shot configuration/install tooling and unused scaffolding as candidate
classes, not predetermined removals. Distinguish moving code, deleting proven
unused code, and reusing existing stock MOS code.

A08-03 [ ] Classify each candidate as must remain resident, suitable foreground
EMOSlet, split resident mechanism/SD utility, or unresolved. Keep UART interrupt
handling, keyboard reception, ordinary VDU routing, transport admission, committed
mode state and APIs needed during applications resident. Evaluate command parsing
separately from the state transition it requests. Preserve usable boot, input,
mode recovery and error reporting when the SD card or utility is unavailable.

A08-04 [ ] Investigate the smallest dispatcher for case-insensitive
`emos <command> [arguments]` loading `/emos/<command>.bin` through the stock
MOSlet loader. Specify built-in precedence, unknown-command behavior, arguments,
return codes, maximum path/command lengths and missing/corrupt/incompatible-file
handling. Compare incremental dispatcher cost against savings; don't add a
plugin registry, relocator, general module framework or background service.

A08-05 [ ] Check RAM and ABI feasibility for shortlisted candidates. Include
MOSlet load extent, stack/heap, shared runtime state, loaded application
preservation, caller-memory admission, callbacks and pointers retained after
exit. Specify version compatibility between resident EMOS and SD utilities and
how an interrupted update recovers. Reuse existing version/SD placement policies;
no executable migration or new installation scheme during investigation.

A08-06 [ ] Produce a ranked table: candidate, current linked ROM contribution,
remaining resident portion, added dispatcher/shared cost, estimated net bytes
recovered, RAM cost, behavior/dependencies, risk and recommendation. Avoid double
counting shared code. Express net headroom in bytes and percent of 128 KiB.
Clearly separate estimates from measured before/after link results. Prefer a
small first tranche with useful net savings and straightforward validation.
A finding that no safe extraction is worthwhile is an acceptable outcome.

A08-07 [ ] Present the shortlist and first-tranche implementation contract for
Author review. Include explicit resident/SD ownership, proposed files and commands,
net ROM target, deployment/rollback, and validation. Stop before product changes.

## Conditional implementation and validation — not yet authorized

A08-08 [ ] After approval, extract only the selected tranche, retaining stock
MOS idioms and thin resident services. Measure total linked before/after ROM;
retaining duplicate implementations is not a saving. Preserve the previous image
and matching SD utilities as a rollback set.

A08-09 [ ] Validate normal/invalid command invocation, case handling, arguments,
return/re-entry, missing SD/utility and version mismatch. Verify application RAM
preservation and no live callbacks into unloaded MOSlet memory. Exercise ordinary
MOS behavior, Legacy/ExCom switching and both keyboard sources where affected.
Use focused emulator checks before separately authorized physical deployment;
update canonical installation/recovery documentation only for accepted behavior.

## Deliverables and boundaries

The research deliverable is a compact report under `AUDIT-008/` with a pinned
baseline, candidate table and recommended first extraction. Shared provider ABI
and firmware changes belong in the project-owned agon-emos checkout, coordinated
with its task records; official MOS remains a read-only reference. This task does
not redesign the SD protocol, implement networking features, remove stock MOS
capabilities or revive the cancelled relocatable-module development path.

The investigation is not a prerequisite to every REMOTE-005 improvement. It
becomes a dependency when a proposed change needs resident ROM beyond measured
headroom. Moving the already disk-resident sdserve executable between directories
is organization, not ROM recovery.

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

For this turn, documentation preparation only is authorized. After research
approval, local baseline builds may support A08-01; implementation, SD changes
and bench operations still require their own approved tranche. REMOTE-005 retains ownership of file-access work and its provisional
MOSlet evidence; this task owns only ROM simplification and CLI utility placement.
