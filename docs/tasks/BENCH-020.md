# BENCH-020 — Audit canonical Olimex bench instructions

**Active goal, authorized by Smith on 2026-11-17.** Start with Extender’s own successful bench
work on Extender VDP (E/VDP) and Extender MOS (EMOS). Recover the exact working
commands and their receipts from routine owner runs. Then trace how Extender
and the two cold operators selected their methods, and fix the instructions
that let their paths diverge. An operator should find the latest applicable
proven method from one current starting point.

## Scope

1. Give first priority to Extender’s own E/VDP and EMOS work. For each, select
   recent real jobs with successful checkout, staging, verification and
   handback, plus the relevant flash, startup and recovery receipts. Include
   both a production-firmware job and a custom-firmware job where retained
   evidence permits. The VDPlet owner supplies equivalent mainboard VDP
   examples for steps that cross into that component.
2. Trace the shared `agon-dev-env/codex/AGENTS.md` and Extender `AGENTS.md`.
   Follow their required links into the operation index, bench and scheduler
   procedures, production selections, machine-local bindings and host tool
   guides. Include other project entry points where they repeat or contradict
   shared Olimex instructions. Use the [BENCH-018 catalog](BENCH-018/CATALOG.md)
   to locate copies and references.
3. Follow one operator cycle from reservation and checkout through post-grant
   readiness, SD staging, firmware changes, explicit fixture start, observation,
   collection, required restoration and check-in. Include the failure and
   recovery instructions that an operator would encounter along that route.
   Record who acts at each step. Cover the eZ80/EMOS, the Extender ESP32-P4 and
   the mainboard ESP32/VDPlet as distinct flash and startup paths.
4. Use the [first rehearsal evidence](BENCH-019/REHEARSAL-R01-RESULT.md) and
   the [second rehearsal evidence](BENCH-019/REHEARSAL-R02-RESULT.md) as
   a comparison against the owner examples. BENCH-020 owns instruction
   reconciliation. The rehearsal and its current disposition stay in
   [BENCH-019](BENCH-019.md).

## Audit and cleanup plan

1. **Reconstruct the owner’s working methods.** Extender will start with its
   own E/VDP and EMOS run logs, actual commands and independent receipts. For
   each phase, record the commissioned hardware, firmware profile, exact
   script revision and tool version, observed result and evidence location.
   Capture the full flash sequence through readback, restart and usable CLI.
   Select the latest proof applicable to that hardware and operation. If a
   newer method has only offline evidence, retain the last applicable proven
   route and record the gap. Produce a short worked example for each owned
   component that another operator can follow verbatim with their job inputs.
2. **Find where the three operator paths diverged.** Start with the instructions an
   agent receives, in their actual reading order. For each operation, record
   the relevant directive, where it sends the operator, and any competing
   requirement. Flag broken links, stale selectors, conflicting prerequisites,
   and places that require an operator to reconstruct a command from history.
   Compare Extender’s choices with both cold operators’ logs. Pinpoint the
   first differing instruction or tool choice for each phase. Record what
   each run actually did, which failures repeated, and which behavior changed.
   Where a wrapper replaced a CLI command, compare defaults, connection and
   reset behavior, readback, and failure handling. Use the same evidence
   standard for Extender’s own decisions as for either cold operator’s.
3. **Resolve contradictions at the instruction that sends the operator down
   the wrong path.** Extender will retain the current procedure in its maintained
   location and replace duplicate directions with a direct link. Keep local
   device settings in the commissioned binding and preserve dated evidence in
   task records or Git history. Where a named owner controls another repository,
   record the precise affected section and coordinate the correction with that
   owner. Record any conflict that needs a decision from Smith.
4. **Check the revised path as a fresh reader.** Walk from the normal agent
   entry points through a production-only job and a custom-firmware job. Every
   action must lead to an applicable, supported command and its evidence.
   Verify that the production path skips firmware operations and that the
   custom path restores the processors it changes. Check the attended stop
   and check-in instructions for one clear owner and next action. Where a new
   physical comparison is needed, specify one variable to change and pin the
   firmware, toolchain, wiring, command sequence and success checks for the
   other steps.
5. **Evaluate a curated operator checkout.** List the minimum current files
   an Extender or external operator needs, including the procedure, E/VDP and
   EMOS worked examples, runtime tools, artifact links and the commissioned
   binding. Compare following the corrected entry point in the full checkout
   with following it in a sparse view of the same maintained files. Record
   what each exposes, any dependencies the sparse view hides, and how both
   would receive updates from the same source. Use the authorized sparse
   checkout for the cold iterations and retain the full checkout for owner
   maintenance.

## Review deliverables

1. Extender’s worked E/VDP and EMOS examples, plus an evidence table with the
   instruction, actual proven command, latest
   applicable receipt, discrepancy, correction and responsible owner for each
   operation.
2. The command and instruction differences across the owner runs and cold
   runs, plus a change list for canonical and duplicate instructions. Call out
   unresolved evidence or ownership.
3. A link and walkthrough check that shows how a fresh operator reaches the
   current commands without following historical instructions. Include the
   proposed contents and tradeoffs of a sparse operator checkout.

## Unattended acceptance

Smith authorizes as many cold iterations as needed. A passing iteration is one
fresh operator that executes the same three-processor fixture through verified
production handback and scheduler check-in, with zero errors or intervention.
During a failed iteration, record the first fault and use in-scope unattended
diagnosis and recovery without waiting for Smith. Finish a justified recovery
or restore production and check in before handing the work to another operator.
Retain the normal slot grant and exclusive custody throughout. The independent
FIFO exercise remains deferred to real jobs.

Save the durable run evidence and final disposition before deleting a temporary
cold chat. The Codex service restarts at 03:00 EST and Pi5 reboots at 03:15.
The coordinator can wake the goal from 03:18 EST at the earliest. Keep a
restartable handoff and finish any armed work and its necessary bench handback
by the first interruption.
