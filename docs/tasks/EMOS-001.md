# EMOS-001 — Rebase EMOS onto Eirene with asynchronous UART and OTIRX

## Executive summary

The Author selects Eirene as the future EMOS foundation, including its
asynchronous UART and OTIRX improvements. Plan a migration that preserves the
working Extender interfaces and scarce eZ80 flash/RAM rather than replacing the
installed firmware with an unrelated Eirene release. The Author subsequently authorizes isolated development and offline verification.
Keep all implementation in dedicated task branches/worktrees and task-local
artifacts. The Author subsequently requests the first experimental hardware installation.
The [installation and recovery record](EMOS-001/FLASH-R01.md) owns that added
scope; production promotion remains separate.

Offline result: [first isolated build and mandatory linked checks](EMOS-001/R01-RESULTS.md).
Source-port provenance: [integration checkpoint](EMOS-001/R01-SOURCE-PORT.md).

## State and scope

Planning task recorded 2026-11-04; task-siloed development then authorized.
Corrected r02 experimental installation is complete: full131072-byte ROM
readback, normal boot, actual keyboard/CLI and canonical listener pass. The
inherited IRQ/BSS initialization defect and recovery are retained in the
installation record. Temporary boot recovery is retired; original startup,
P4/native firmware and listeners are preserved. Full functional/async
qualification and Author acceptance/promotion remain pending. Extender retains
custody for review; no queued consumer has been granted access. Extender owns integration planning; the EMOS
owner checkout owns the eventual complete firmware. Coordinate the UART/Eirene
owner's exact contracts before integration. P4 changes require a separately
identified compatibility need and bounded implementation tranche.

EMOS remains one complete backward-compatible MOS replacement. EMOS retains
ordinary VDU routing, transport admission, activation and committed mode. Keep
Legacy mainboard VDP operation, ExCom, selected local/browser keyboard input,
controller gateway, foreground SD utilities, staged transfers and parallel
shared-pin ownership. Do not add supported application bypasses around EMOS.

## Research précis and starting identities

1. Official MOS API documentation: `agon-docs/docs/mos/API.md` defines RST10
   character and RST18 buffer output. Consult system variables and official MOS
   source when necessary; retain read-only reference checkouts and record exact
   tagged baselines before implementation research.
2. Eirene async candidate: UART handoff identifies published RC2 source
   `825eaf77176247f5b5ba2f940ae73fcace34e7e5`, release
   <https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_2>.
   Its `docs/uart0-async.md` specifies fork-local calls42h/43h, one borrowed
   immutable buffer, optional completion callback, and up-to16-byte OTIRX FIFO
   refills with a CTS check per block. Normal RST18 stays synchronous.
   This is the initial candidate to audit, not an assertion of EMOS compatibility.
3. RC2 completion releases source ownership after FIFO admission; it does not
   prove wire drain or VDP execution. Finish separately waits for transmitter
   empty and restores the UART handler. Foreground ADL1/MBASE0, enabled IRQs,
   exclusive UART ownership and live source/callback storage are caller
   requirements. RC2 omits some RC1 runtime guards. Callbacks run DI on the
   interrupt stack and must remain short; do not perform MOS output or wait.
4. Older UART experiments use a different discovery/session/ticket API. Do not
   combine their ABI, guarantees or performance claims with RC2. Distinguish
   reusable OTIRX mechanics from public API compatibility and receiver evidence.
5. Current parallel trial EMOS source
   `6ececd56ff80029523464a5027633a7b74e84cf6`, complete ROM SHA256
   `855aa732ee9bd5def7cb92b52a1521d696330a6f260ad11288f7aeab7fe7dc57`,
   retains2154 ROM bytes free and3230 static BSS bytes in its recorded build.
   This is a development comparison input, not the selected production bundle.
   Reconfirm actual owner-tree changes and all accepted features before freezing
   the migration inventory; never select whatever HEAD happens to contain.
6. Production and accepted component identities remain governed by
   [production selection](../../production/README.md), [current handbook](../README.md)
   and [parallel trial pins](../mainboard-sd-parallel-trial.json). Preserve their
   exact archives and rollback evidence independently of the new base.
7. UART's separate runtime RST-hook handoff concerns proposed syscall61h and
   PR head604640eb882c3dfeb870a8c4aaaa7e155c23d0ad. The reported RC2 release
   lacks it. Hook installation, resident RAM lifetime and VDP reply ownership
   require separate design; RST hooks are not a prerequisite or implicit scope
   addition to this migration.

## Itemized planning work

1. Freeze the Eirene upstream/fork ancestry, selected async changes, compiler,
   libraries, conversion inputs and license notices. Prefer the maintained
   AgonDev build path; explain any incompatibility before proposing a toolchain
   change. Preserve ZDS/AgonDev history without reviving obsolete symbol-mangling
   assumptions or editing official reference checkouts.
2. Inventory the existing EMOS patch set by feature and owning source: syscall
   allocations, RST gateways, sysvars, UART0/1 IRQs, shared Port C pins, CLI,
   input/parser state, controller include ABI, SD gateway and external utilities.
   Classify every delta as retained, supplied by Eirene, adapted or deliberately
   deferred. Cite source and current consumers; do not silently drop behavior.
3. Audit collisions in Eirene calls42h/43h, extension discovery, jump tables,
   callback/context conventions, memory reservations and UART vectors. Compare
   RC1 versus RC2 only where an actual EMOS ownership obligation needs a guard.
   Reuse existing routing/admission and cleanup instead of layering duplicate
   schedulers, buffers, packet parsers or diagnostic services.
4. Design EMOS-owned UART0 async integration first. Preserve synchronous source
   lifetime/ordering for unaware RST10/RST18 callers. Explicit async callers may
   reuse storage only after defined release and finish before conflicting output,
   route change or exit. Resolve early callback completion, BUSY ownership,
   queued exit, input callbacks and recovery without unrequested defensive bulk.
5. Separately assess reuse on UART1, naming eZ80/P4 endpoints and UART1's shared
   Port C wiring. Existing parking during parallel payload phases remains a
   requirement. Do not assume UART0 CTS margin or a16-byte batch is qualified on
   UART1/P4. Avoid per-byte handshakes/checksums; add no EMOS–P4 CRC or substitute
   software checksum. Keep blocking compatibility distinct from async admission.
6. Prepare baseline/candidate ROM, static RAM and interrupt-stack budgets with
   feature-attributed deltas. Keep diagnostics, calibration, controller policy
   and test algorithms in applications/utilities. Report minimum resident
   mechanisms and opportunities to reuse existing code; no speculative service
   framework or default firmware-space expansion.
7. Produce an incremental migration sequence, dependency/consumer table and
   explicit stop/rollback gates. Coordinate with the UART owner through the
   standard mailbox when implementation is assigned. Preserve the existing
   filter benchmark and physical FIFO; this planning task requests no bench slot.
8. Implement and offline-verify the isolated rebase, retaining exact provenance,
   API collision disposition and memory comparison for Author review. Do not
   merge, deploy or alter consumers under this offline tranche.

## Decision register

| ID | Decision | State |
|---|---|---|
| E01-D01 | Use Eirene as future EMOS base and include async UART/OTIRX improvements; retain EMOS ownership | Accepted by Author, 2026-11-04 |
| E01-D02 | Exact integration commit and public async ABI after collision audit | Open; recommend audited RC2 starting point, retaining synchronous legacy calls |
| E01-D03 | UART1 reuse and CTS/batch policy for P4, including parallel admission | Open; resolve after UART0 mapping; no presumed receiver qualification |

For each open decision, present one concrete recommendation at a time, with
alternatives, prerequisites, memory/runtime costs and consumer effects. Runtime
RST-hook experiments remain separate until assigned.

## Planned validation gates — not execution authorization

1. Reproducible source/toolchain provenance, attribution, map/size comparison,
   API/register/sysvar collision review and source-lifetime/IRQ tests.
2. Offline functional checks for retained EMOS routing, admission, controllers,
   utilities and cleanup; select actual fixtures only after the migration delta
   is known. Follow the test-appliance procedure before designing a runnable suite.
3. Separately authorized exact-image hardware installation with retained backup
   and recovery readiness; ordinary Legacy boot, input and synchronous output
   first. No startup edits or reset-triggered tests.
4. Matched native VDP/P4 receiver checks for ordered bytes, bidirectional replies,
   CTS pauses, callback/release/drain distinctions, route/parallel conflicts and
   clean exit. Reuse evidence only for its exact pair and declared scope.
5. Performance tables separate elapsed transport, useful CPU work and rendering;
   stock/current EMOS versus rebased synchronous versus opt-in async/OTIRX.
   Include ROM/RAM cost. Never infer a faster wire from additional foreground
   work, nor compare unmatched receiver/builds as though equivalent.
6. Author acceptance, complete applicable qualification, updated current guides,
   immutable bundle and agreed release version/tag precede production selection.
   Retain a verified rollback to the exact incoming installation throughout.

## Current execution checkpoint

Corrected experimental r02 is installed and fully read back; normal boot, input
and foreground SD service pass. All five linked validators pass. The Author
now authorizes the next tranche, explicitly reusing both Extender and UART's
existing tests. [Reuse/readiness tranche](EMOS-001/TEST-REUSE-R01.md) owns the
selected coverage, adapters, resource limits and full-suite readiness stop.
The [bounded reuse result](EMOS-001/TEST-REUSE-RESULTS-R01.md) passes nine
existing host methods and three physical UART0/native-VDP cases. No broad
compatibility, performance, full-pair qualification or production acceptance is
implied. Canonical fixture/installation-provenance preparation remains next.

## Full paired qualification authorization

On2026-11-04 the Author explicitly authorizes preparation and full invocation
without another readiness notification. This supersedes the earlier stop before
invocation for this task. [Paired qualification plan](EMOS-001/QUALIFICATION-R01.md)
owns the finite preparation, existing runner, evidence and restoration scope.

The [first full attempt](EMOS-001/QUALIFICATION-RESULT-R01.md) completes14/25
checks: all13 integrated services and mode8. Existing P4 HDMI budget failure
blocks the remaining mode checks and raw-SD. No firmware/startup changes occur.
Standing recovery and explicit cleanup restore healthy mode0/Legacy for the
Author-priority FSIM mainboard work. Qualification remains failed/open; this is
not an EMOS regression diagnosis or acceptance/promotion.
