# AUDIT-008 — EMOS ROM headroom and SD-loaded EMOSlets

## Executive summary

Contract refreshed 2026-09-23. The Author approved a one-hour autonomous
investigation; **A08-01–A08-07 complete; first-tranche implementation authorized**. This promotes the previously deferred idea
instead of creating a duplicate task. REMOTE-005 remains the next file-access
workstream; this task determines which existing resident EMOS functions could
become SD-loaded foreground utilities, informally “EMOSlets,” to recover ROM for
features that genuinely require resident firmware.

Use existing MOSlet loading and calling conventions, not a new executable format.
The [investigation report](AUDIT-008/REPORT.md) delivers the measured shortlist
and proposed first tranche. The unchanged-source baseline confirms 16 ROM bytes
free. Retiring cancelled external-provider machinery is the largest identified
opportunity; estimated post-change savings are explicitly not measured results.
The Author approved the bounded first tranche below on 2026-09-24 UTC.

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

A08-01 [x] Establish the current ROM baseline in the project-owned EMOS checkout.
Read official MOS API/loading documentation first, then source where needed.
Record source revision, build configuration, compiler/linker versions, linker
map, occupied ROM span and free bytes. Reconcile the retained 16-byte-headroom
result against the current build; do not treat that historical result as a new
measurement. Account for alignment, shared helpers, constants, dead stripping
and fixed-address sections before attributing bytes to functions.

A08-02 [x] Inventory resident Extender-specific commands and support routines.
For each candidate record its callers, code/data contribution, runtime state,
interrupt dependencies, frequency, and whether applications or startup require
it outside a CLI invocation. Inspect diagnostics, status/help formatting,
one-shot configuration/install tooling and unused scaffolding as candidate
classes, not predetermined removals. Distinguish moving code, deleting proven
unused code, and reusing existing stock MOS code.

A08-03 [x] Classify each candidate as must remain resident, suitable foreground
EMOSlet, split resident mechanism/SD utility, or unresolved. Keep UART interrupt
handling, keyboard reception, ordinary VDU routing, transport admission, committed
mode state and APIs needed during applications resident. Evaluate command parsing
separately from the state transition it requests. Preserve usable boot, input,
mode recovery and error reporting when the SD card or utility is unavailable.

A08-04 [x] Investigate the smallest dispatcher for case-insensitive
`emos <command> [arguments]` loading `/emos/<command>.bin` through the stock
MOSlet loader. Specify built-in precedence, unknown-command behavior, arguments,
return codes, maximum path/command lengths and missing/corrupt/incompatible-file
handling. Compare incremental dispatcher cost against savings; don't add a
plugin registry, relocator, general module framework or background service.

A08-05 [x] Check RAM and ABI feasibility for shortlisted candidates. Include
MOSlet load extent, stack/heap, shared runtime state, loaded application
preservation, caller-memory admission, callbacks and pointers retained after
exit. Specify version compatibility between resident EMOS and SD utilities and
how an interrupted update recovers. Reuse existing version/SD placement policies;
no executable migration or new installation scheme during investigation.

A08-06 [x] Produce a ranked table: candidate, current linked ROM contribution,
remaining resident portion, added dispatcher/shared cost, estimated net bytes
recovered, RAM cost, behavior/dependencies, risk and recommendation. Avoid double
counting shared code. Express net headroom in bytes and percent of 128 KiB.
Clearly separate estimates from measured before/after link results. Prefer a
small first tranche with useful net savings and straightforward validation.
A finding that no safe extraction is worthwhile is an acceptable outcome.

A08-07 [x] Present the shortlist and first-tranche implementation contract for
Author review. Include explicit resident/SD ownership, proposed files and commands,
net ROM target, deployment/rollback, and validation. Stop before product changes.

## Authorized implementation and validation

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

D01 — Accepted 2026-09-24: built-ins first, then fixed-address
stock-format MOSlet loading from `/emos`, restricted to idle/Core invocation.
Case, name/path limits, failure and ABI behavior are specified in the report.
Use existing sdserve as the first launcher validation; preserve prior entry paths.

D02 — Constraint: preserve stock executable/loading idioms and EMOS ownership
of routing and transports. SD utilities remain foreground programs; this proposal
does not create background services or permit bypassing the resident owner.

D03 — Accepted 2026-09-24: retire the cancelled external `.emo`
provider path rather than relocate it. Preserve the resident gateway, mode,
keyboard, console and SD services. Its still-present provisional contract and
fixture behavior require explicit disposition before removal. UART diagnostic
extraction is not recommended for the first tranche because its private API
dependencies make net savings uncertain.

The research and local baseline build are complete. First-tranche implementation
and local validation are authorized. Physical SD changes and bench operations
are prohibited during this run; another agent owns the bench. REMOTE-005 retains ownership of file-access work and its provisional
MOSlet evidence; this task owns only ROM simplification and CLI utility placement.

## Frozen first-tranche execution contract — 2026-09-24

One-hour execution window: 01:47:10–02:47:10 UTC. Commit coherent increments
without waiting for human emulator review, as expressly authorized for this run.
Do not push, flash, reset, connect to the bench, or access physical SD media.
Use isolated generated build and emulator profiles. Preserve previous firmware.
The detailed behavior and cost target are in [the report](AUDIT-008/REPORT.md).

A08-I01 [x] Freeze research, accepted decisions and this phased contract before
product edits. Scope is retirement of the cancelled external `.emo` machinery
and a minimal `/emos` stock-MOSlet dispatcher, not extraction of UART diagnostics.

A08-I02 [ ] Remove external-provider discovery, registry, load/swap/CRC execution
and arbitrary command fallback. Keep gateway ABI 0x51 / C slot 0x20, resident
services, request validation, busy admission, lifecycle, modes and keyboard.
Retired discover/clear requests return unavailable; unknown providers return
not found. Mark historical provider fixtures as historical, not current gates.

A08-I03 [ ] Add built-ins-first, case-insensitive `emos <name> [args]` dispatch to
`/emos/<name>.bin`. Admit only Core/idle CLI; use fixed 0xB0000 MOSlet region and
stock load/run ABI. Validate leaf and file size, invalidate stale header before
load, preserve application RAM and global search paths. No new executable ABI.

A08-I04 [ ] Add focused automated checks for dispatch, case/argument handling,
return/re-entry, invalid/missing/oversize files and denied nested invocation.
Run maintained firmware checks and linked guards. Exercise the candidate in an
isolated emulator where feasible, including the existing sdserve MOSlet.
Distinguish emulator filesystem limits from target behavior.

A08-I05 [ ] Account candidate ROM/RAM against the retained 131056-byte baseline,
targeting at least 4096 net ROM bytes recovered. Record exact provenance,
validation, residual limits and physical gates. Commit source and documentation
as coherent increments; stop at the time budget with incomplete gates explicit.

Hardware acceptance remains a later gate, including native keyboard and ExCom
service continuity. Local checks cannot certify physical UART behavior. No
physical installation or retirement of existing utility entry paths this run.
